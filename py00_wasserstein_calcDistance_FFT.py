#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wav群 -> スペクトル分布 -> 1次元Wasserstein距離行列(CDF積分方式)

【この版の設計方針】 クラッシュしても「間違った結果が静かに混ざる」ことを構造的に無くす

旧版の問題:
  * spectra.npy / file_info.csv / sha256_cache.json / distance_matrix_raw.* を
    別々の時刻に書いていたため、クラッシュ後は「互いに食い違った世代」が残った。
  * spectra.npy は毎回ゼロ埋めで作り直しており、書き込み途中で落ちると
    「行数だけ合っていて後半がゼロ」のファイルが有効なキャッシュとして採用された。
  * 距離キャッシュの有効性を、すでに今回の値で上書き済みのsha256_cache.jsonと
    比較していたため、検証が実質的に常に通った。
  * 距離計算の途中経過は保存されず、落ちるたびに全ペアをやり直しになった。

この版:
  1. スペクトルは「wavのSHA256をファイル名にした1ファイル1スペクトル」で保存する。
     (内容アドレス方式。位置(行番号)に依存しないので、ファイルを足す/消す/並べ替えても
      古い行を取り違えようがない。ファイル数が増えても新規分だけ計算する。)
  2. 距離のキャッシュは distance_state.npz 1ファイルだけ。
     中身 = (各行のSHA256, 距離行列D, 各要素が計算済みかのvalidマスク, 計算条件)。
     行列と「それが何の内容に対する値か」が同じファイルに入っているので食い違わない。
     計算途中でも定期的に保存するので、落ちても続きから再開できる。
  3. 書き込みは全て 一時ファイル -> fsync -> os.replace(原子的置換)。
     途中で落ちても「完成した旧版」か「完成した新版」のどちらかしか存在しない。
  4. distance_matrix_raw.npy/csv, file_info.csv, spectra.npy 等は「出力(エクスポート)」であり、
     次回実行でキャッシュとして読み戻すことは一切ない。壊れていても結果を汚染しない。
  5. 読み込むスペクトルは長さとCDF終端(≈1)を毎回検査し、ゼロ行などの破損を検出する。
  6. 最後に、ランダムに選んだファイルをwavから計算し直して、行列の値と突き合わせる(自己検証)。

WASSERSTEIN_MODE:
  ""  : L1, L2, lbL1, lbL2 の4モードをすべて実行(共通部分は1回だけ計算)。
  それ以外 : 指定した1モードだけ実行。

REBUILD_CACHE:
  True  : このスクリプトのキャッシュ(スペクトルキャッシュ・distance_state.npz)を削除して全部作り直す。
          途中で落ちた場合は False に戻して再実行すると、作成済みの分から再開できる。
  False : 内容(SHA256)が同じものは再利用、新規/変更分だけ計算する。
"""

import os
import sys
import csv
import json
import time
import hashlib
import datetime

import numpy as np
import librosa
from scipy.spatial.distance import cdist


# ==================================================
# 設定
# ==================================================

ROOT_DIR = os.path.expanduser("./wav/")

TARGET_SR = 96000

# 計算するモード。
#   ""                            : L1, L2, lbL1, lbL2 のすべてを順に実行する
#   "L1" / "L2" / "lbL1" / "lbL2" : そのモードだけ実行する
#     L1 / L2     : 線形周波数軸(L1 = Wasserstein-1、L2 = CDFの差のL2)
#     lbL1 / lbL2 : 対数軸 x = lb(f / f0)(lb = 底2の対数。単位はオクターブ)
# 全モード実行のとき、WAV探索・SHA256・スペクトル計算は1回だけ行い、
# モードごとに距離行列を作る。途中で落ちても、完了したモードはそのまま再利用され、
# 未完了のモードは保存済みの進捗から再開する。
WASSERSTEIN_MODE = ""

ALL_MODES = ["L1", "L2", "lbL1", "lbL2"]

# 対数軸モード("lbL1" / "lbL2")の軸は x = lb(f / f0)。
#
# f0 は各ビンの重みには影響しない(刻み幅 dx = lb((k+1)/k) で f0 は消える)。
# f0 が決めるのは「下限カットオフ」だけ: f0 未満のビン(DC含む)は捨て、
# 残りのスペクトルを総和1に再正規化してから距離を計算する。
# 目安: 全楽器の最低基音(バストロンボーンのペダル音 B♭0 ≈ 29 Hz)より少し下 -> 20 Hz。
LOG_F0_HZ = 20.0

# 出力先は {OUT_DIR_PREFIX}_{モード}(対数軸モードは末尾に _f0-20Hz などが付く)。
OUT_DIR_PREFIX = "./distanceMatrix"

# スペクトルキャッシュの置き場。モード(L1/L2…)が違っても共通で使える。
SPECTRA_CACHE_ROOT = "./spectra_cache"

TARGET_DIRS = [
    "picc",
    "fl",
    "fl_lip-tight",
    "altofl",
    "bassfl",
    "kbfl",
    "ob",
    "ci",
    "cl-inEs",
    "cl-inB",
    "cl-inA",
    "basscl",
    "fg",
    "fh_tube-F",
    "fh_tube-B",
    "fh_bell-cuivre_tube-F",
    "fh_bell-straightMute_tube-F",
    "fh_bell-gestopftMute_tube-F",
    "tenortrb",
    "tenortrb_mute-straight",
    "basstrb",
    "basstrb_mute-straight",
    "basstrb_mute-straightMetal",
    "basstrb_mute-cup",
    "basstrb_mute-harmonNOstemOPENED",
    "basstrb_mute-harmonNOstemCLOSED",
    "basstrb_mute-harmonStemmedOPENED",
    "basstrb_mute-harmonStemmedCLOSED",
    "basstrb_mute-bucket",
    "basstrb_tube-F",
    "basstrb_tube-F_mute-harmonNOstemOPENED",
    "basstrb_tube-F_mute-harmonNOstemCLOSED",
    "basstrb_tube-F_mute-straightMetal",
    "basstrb_tube-F_mute-bucket",
    "basstrb_tube-Ges",
    "basstrb_tube-D",
    "va",
    "gauss_sigma-002.5%",
    "gauss_FWHM-wholetone",
    "gauss_FWHM-halftone",
    "gauss_FWHM-quartertone",
    "gauss_FWHM-eighthtone",
    "gauss_FWHM-sixteenthtone",
]

# ファイル名にこの文字列を含むものだけを対象にする("" なら全部)。
# 注意: 絞り込むと、絞り込み外のファイルの距離キャッシュは次回保存時に捨てられる。
KEYWORD = ""

NORMALIZE_DISTANCE_MATRIX = False

REBUILD_CACHE = False

# 旧版互換の spectra.npy(N x L, float32, 約4GB) を出力するか。
# このスクリプト自身は読まない(下流の解析・描画用)。不要なら False で数分と4GB書き込みを節約。
EXPORT_SPECTRA_NPY = False

# 計算が終わった後、キャッシュ(不要になった古いスペクトル)を削除するか。
PRUNE_UNUSED_SPECTRA = True


# ==================================================
# 計算量・メモリ設定
# ==================================================

# 一度に保持するCDF本数。1本 = L x 8 byte (L=524289 なら約4MB)。
# 同時に最大 2 ブロック + 作業用コピーを持つので、16なら約200〜300MB。
CDF_BLOCK_SIZE = 16

# 距離計算の途中経過(distance_state.npz)を保存する間隔[秒]。
CHECKPOINT_SECONDS = 120

# 完了後に、ランダムに選んだこの本数のwavを計算し直して行列と突き合わせる(0で無効)。
VERIFY_FILES = 6


# ==================================================
# 内部定数
# ==================================================

# スペクトル/距離の計算式を変えたら必ず上げる(古いキャッシュが自動で使われなくなる)。
CODE_VERSION = 3        # スペクトル(および線形軸L1/L2の距離)の定義を変えたときだけ上げる。対数軸の定義はfingerprint側で区別する
SPECTRUM_VERSION = 3    # スペクトル自体の計算式(変えない限りキャッシュを再利用)

TMP_MARK = ".tmp-"


# ==================================================
# 原子的な書き込み
# ==================================================

def _fsync_dir(directory):

    try:

        fd = os.open(directory or ".", os.O_RDONLY)

    except OSError:

        return

    try:

        os.fsync(fd)

    except OSError:

        pass

    finally:

        os.close(fd)


def atomic_write(path, writer, text=False):
    """
    path に直接書かず、同じディレクトリの一時ファイルに書いて
    fsync してから os.replace する。途中で落ちても path は
    「古い完成品」か「新しい完成品」のどちらかのまま。
    """

    path = os.path.abspath(path)
    directory = os.path.dirname(path)

    os.makedirs(directory, exist_ok=True)

    tmp = f"{path}{TMP_MARK}{os.getpid()}"

    try:

        if text:

            with open(tmp, "w", encoding="utf-8", newline="") as f:

                writer(f)
                f.flush()
                os.fsync(f.fileno())

        else:

            with open(tmp, "wb") as f:

                writer(f)
                f.flush()
                os.fsync(f.fileno())

        os.replace(tmp, path)

    except BaseException:

        try:

            os.remove(tmp)

        except OSError:

            pass

        raise

    _fsync_dir(directory)


def atomic_save_npy(path, array):

    atomic_write(
        path,
        lambda f: np.save(f, array, allow_pickle=False)
    )


def atomic_save_json(path, obj):

    atomic_write(
        path,
        lambda f: json.dump(obj, f, ensure_ascii=False, indent=2),
        text=True
    )


def _pid_alive(pid):

    if pid == os.getpid():

        return True

    if os.name != "posix":

        # Windowsのos.killは「終了」を意味してしまうので使わない。
        return True

    try:

        os.kill(pid, 0)

    except ProcessLookupError:

        return False

    except OSError:

        return True

    return True


def cleanup_stale_tmp(directory):
    """前回クラッシュで残った一時ファイル(生きていないPIDのもの)を削除する。"""

    removed = 0

    for dirpath, _, filenames in os.walk(directory):

        for filename in filenames:

            if TMP_MARK not in filename:

                continue

            pid_text = filename.rsplit(TMP_MARK, 1)[1]

            if not pid_text.isdigit():

                continue

            if _pid_alive(int(pid_text)):

                continue

            try:

                os.remove(os.path.join(dirpath, filename))
                removed += 1

            except OSError:

                pass

    if removed:

        print(
            f"Removed {removed} stale temp file(s) in {directory}"
        )


# ==================================================
# パス判定 / SHA256
# ==================================================

def is_path_inside(path, directory):

    path = os.path.abspath(path)
    directory = os.path.abspath(directory)

    try:

        return os.path.commonpath([path, directory]) == directory

    except ValueError:

        return False


def compute_sha256(file_path, chunk_size=1024 * 1024):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        while True:

            chunk = f.read(chunk_size)

            if not chunk:

                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ==================================================
# Wasserstein mode解析
# ==================================================

def parse_wasserstein_mode(mode):

    mode_lower = mode.lower()

    order = 2 if "2" in mode_lower else 1

    use_log_axis = mode_lower.startswith("lb")

    return order, use_log_axis


_MODE_ALIASES = {
    "l1": "L1",
    "l2": "L2",
    "lbl1": "lbL1",
    "lbl2": "lbL2",
    "lb1": "lbL1",
    "lb2": "lbL2",
}


def canonical_mode(mode):

    key = str(mode).strip().lower()

    if key not in _MODE_ALIASES:

        raise ValueError(
            f"Unknown WASSERSTEIN_MODE {mode!r}. "
            f"Use \"\" (all modes) or one of {ALL_MODES}."
        )

    return _MODE_ALIASES[key]


def modes_to_run():
    """WASSERSTEIN_MODE が空なら全モード、そうでなければ指定の1モード。"""

    if str(WASSERSTEIN_MODE).strip() == "":

        return list(ALL_MODES)

    return [canonical_mode(WASSERSTEIN_MODE)]


def out_dir_for_mode(mode):

    _, use_log = parse_wasserstein_mode(mode)

    suffix = f"_f0-{LOG_F0_HZ:g}Hz" if use_log else ""

    return f"{OUT_DIR_PREFIX}_{mode}{suffix}"


# ==================================================
# スペクトル計算
# ==================================================

def compute_spectrum_distribution(file_path):
    """wav -> 総和1のスペクトル分布(float64)。"""

    y, sr = librosa.load(file_path, sr=None)

    if sr != TARGET_SR:

        y = librosa.resample(
            y,
            orig_sr=sr,
            target_sr=TARGET_SR
        )

    # numpyのバージョンによりrfftが float32 のまま計算されることがあるので、
    # 再現性のため明示的にfloat64で計算する。
    y = np.asarray(y, dtype=np.float64)

    spectrum = np.abs(np.fft.rfft(y))

    spectrum += 1e-12

    spectrum /= np.sum(spectrum, dtype=np.float64)

    return spectrum


# ==================================================
# スペクトルキャッシュ(SHA256ごとに1ファイル)
# ==================================================

def spectra_dir():

    return os.path.join(
        SPECTRA_CACHE_ROOT,
        f"sr{TARGET_SR}_v{SPECTRUM_VERSION}"
    )


def spectrum_path(sha):

    return os.path.join(
        spectra_dir(),
        sha[:2],
        sha + ".npy"
    )


class CorruptSpectrum(Exception):

    def __init__(self, sha, name, reason):

        super().__init__(f"{name} ({sha[:12]}...): {reason}")

        self.sha = sha
        self.name = name
        self.reason = reason


def ensure_spectra(current_files, current_sha256):
    """キャッシュに無いSHA256のスペクトルだけを計算して保存する(1本ずつ原子的)。"""

    todo = {}
    unique = set()

    for item in current_files:

        sha = current_sha256[item["relative_name"]]

        unique.add(sha)

        if sha in todo:

            continue

        if not os.path.exists(spectrum_path(sha)):

            todo[sha] = item

    print()
    print(
        f"Spectra: reused {len(unique) - len(todo)}, "
        f"to compute {len(todo)}"
    )

    for k, (sha, item) in enumerate(todo.items(), 1):

        spectrum = compute_spectrum_distribution(item["path"])

        atomic_save_npy(
            spectrum_path(sha),
            spectrum.astype(np.float32)
        )

        del spectrum

        if k % 10 == 0 or k == len(todo):

            print(
                f"\r  spectra: {k}/{len(todo)}",
                end="",
                flush=True
            )

    if todo:

        print()


def validate_spectra(current_files, current_sha256):
    """全スペクトルの形状・dtypeを(ヘッダだけ読んで)確認する。"""

    lengths = {}
    bad = []
    seen = set()

    for item in current_files:

        name = item["relative_name"]
        sha = current_sha256[name]

        if sha in seen:

            continue

        seen.add(sha)

        try:

            arr = np.load(
                spectrum_path(sha),
                mmap_mode="r",
                allow_pickle=False
            )

            if arr.ndim != 1 or arr.dtype != np.float32:

                raise ValueError("unexpected shape/dtype")

            lengths.setdefault(int(arr.shape[0]), []).append(name)

            del arr

        except Exception:

            bad.append(sha)

    return lengths, bad


def load_cdf_rows(
    indices,
    current_shas,
    current_names,
    spectrum_len,
    weight,
    k0=0
):
    """
    指定ファイルのCDFを (本数, L-k0) のfloat64で返す。
    k0 > 0 のときはビン k0 未満を捨て、残りを総和1に再正規化したCDFにする。
    重み(積分の刻み幅)を掛け済みなので、あとは cdist で距離が出る。
    """

    width = spectrum_len - k0

    out = np.empty((len(indices), width), dtype=np.float64)

    scratch = np.empty(spectrum_len, dtype=np.float64) if k0 > 0 else None

    for k, gi in enumerate(indices):

        gi = int(gi)

        sha = current_shas[gi]
        name = current_names[gi]

        try:

            row = np.load(spectrum_path(sha), allow_pickle=False)

        except (OSError, ValueError, EOFError) as e:

            raise CorruptSpectrum(sha, name, f"cannot read: {e}")

        if row.shape != (spectrum_len,):

            raise CorruptSpectrum(sha, name, f"bad shape {row.shape}")

        if k0 == 0:

            np.cumsum(row, dtype=np.float64, out=out[k])

            end = out[k, -1]

        else:

            np.cumsum(row, dtype=np.float64, out=scratch)

            end = scratch[-1]

        # 正しいスペクトルなら総和≒1。ゼロ行・欠損・NaNはここで必ず落ちる。
        if not (0.99 < end < 1.01):

            raise CorruptSpectrum(sha, name, f"CDF end = {end!r}")

        if k0 > 0:

            base = scratch[k0 - 1]

            kept = end - base

            if not kept > 1e-6:

                raise CorruptSpectrum(
                    sha,
                    name,
                    f"almost no energy above f0 (kept mass {kept!r})"
                )

            np.subtract(scratch[k0:], base, out=out[k])

            out[k] /= kept

        out[k] *= weight

    return out


# ==================================================
# 距離キャッシュ状態(1ファイル)
# ==================================================

def save_state(path, shas, D, valid, fingerprint):

    def writer(f):

        np.savez(
            f,
            shas=np.array(shas, dtype="U64"),
            D=D,
            valid=valid,
            fingerprint=np.array(json.dumps(fingerprint, sort_keys=True))
        )

    atomic_write(path, writer)


def load_state(path, fingerprint):
    """壊れている/条件が違う場合は None(= 使わない)。"""

    if not os.path.exists(path):

        return None

    try:

        with np.load(path, allow_pickle=False) as z:

            saved_fp = json.loads(str(z["fingerprint"]))
            shas = [str(s) for s in z["shas"]]
            D = np.array(z["D"], dtype=np.float64)
            valid = np.array(z["valid"], dtype=bool)

    except Exception as e:

        print(f"WARNING: ignoring unreadable distance_state.npz: {e}")

        return None

    if saved_fp != fingerprint:

        print(
            "NOTE: distance_state.npz was made with different settings; "
            "ignored."
        )
        print(f"  saved  : {saved_fp}")
        print(f"  current: {fingerprint}")

        return None

    n = len(shas)

    if D.shape != (n, n) or valid.shape != (n, n):

        print("WARNING: distance_state.npz has inconsistent shapes; ignored.")

        return None

    # 非対称/非有限の要素は「未計算」とみなす
    valid &= valid.T
    valid &= np.isfinite(D)

    return shas, D, valid


def build_initial_matrices(current_shas, prior):
    """
    現在のファイル順の (D, valid) を作る。
    以前の状態に同じSHA256の行があれば、その行・列の値を持ってくる(位置ではなく内容で対応)。
    """

    n = len(current_shas)

    D = np.zeros((n, n), dtype=np.float64)
    valid = np.zeros((n, n), dtype=bool)

    if prior is not None:

        prior_shas, prior_D, prior_valid = prior

        prior_index = {}

        for i, sha in enumerate(prior_shas):

            prior_index.setdefault(sha, i)

        new_idx = []
        old_idx = []

        for i, sha in enumerate(current_shas):

            j = prior_index.get(sha)

            if j is not None:

                new_idx.append(i)
                old_idx.append(j)

        if new_idx:

            ni = np.asarray(new_idx, dtype=np.int64)
            oi = np.asarray(old_idx, dtype=np.int64)

            D[np.ix_(ni, ni)] = prior_D[np.ix_(oi, oi)]
            valid[np.ix_(ni, ni)] = prior_valid[np.ix_(oi, oi)]

    # 内容が同一(SHA256一致)なら距離は定義上0
    _, codes = np.unique(
        np.asarray(current_shas),
        return_inverse=True
    )

    codes = codes.reshape(-1)

    same = codes[:, None] == codes[None, :]

    D[same] = 0.0
    valid[same] = True

    valid &= valid.T

    D[~valid] = 0.0

    return D, valid


# ==================================================
# 距離計算(未計算のペアだけ)
# ==================================================

def compute_missing_distances(
    D,
    valid,
    current_shas,
    current_names,
    spectrum_len,
    weight,
    k0,
    metric,
    state_path,
    fingerprint
):

    n = len(current_shas)
    block = CDF_BLOCK_SIZE

    total = int(np.count_nonzero(~valid)) // 2

    if total == 0:

        print("  all distances are already cached.")

        return 0

    print(f"  pairs to compute: {total}")

    done = 0
    t_start = time.time()
    t_ckpt = t_start

    try:

        for bi in range(0, n, block):

            ei = min(bi + block, n)

            row_missing = ~valid[bi:ei, bi:].all(axis=1)

            if not row_missing.any():

                continue

            need_rows = np.flatnonzero(row_missing)

            row_pos = np.full(ei - bi, -1, dtype=np.int64)
            row_pos[need_rows] = np.arange(len(need_rows))

            cdf_i = load_cdf_rows(
                bi + need_rows,
                current_shas,
                current_names,
                spectrum_len,
                weight,
                k0
            )

            for bj in range(bi, n, block):

                ej = min(bj + block, n)

                missing = ~valid[bi:ei, bj:ej]

                if bj == bi:

                    # 対角タイルは上三角だけ計算して鏡映する
                    missing = np.triu(missing, 1)

                if not missing.any():

                    continue

                rows = np.flatnonzero(missing.any(axis=1))
                cols = np.flatnonzero(missing.any(axis=0))

                a = cdf_i[row_pos[rows]]

                if bj == bi:

                    pos = row_pos[cols]

                    if (pos < 0).any():

                        raise RuntimeError(
                            "internal error: asymmetric validity mask"
                        )

                    b = cdf_i[pos]

                else:

                    b = load_cdf_rows(
                        bj + cols,
                        current_shas,
                        current_names,
                        spectrum_len,
                        weight,
                        k0
                    )

                sub = cdist(a, b, metric=metric)

                ii, jj = np.nonzero(missing)

                values = sub[
                    np.searchsorted(rows, ii),
                    np.searchsorted(cols, jj)
                ]

                gi = bi + ii
                gj = bj + jj

                D[gi, gj] = values
                D[gj, gi] = values
                valid[gi, gj] = True
                valid[gj, gi] = True

                done += len(ii)

                del a, b, sub

            del cdf_i

            elapsed = time.time() - t_start

            rate = done / elapsed if elapsed > 0 else 0.0

            eta = (total - done) / rate if rate > 0 else float("nan")

            print(
                f"\r  distances: {done}/{total} "
                f"({100.0 * done / total:5.1f}%) "
                f"ETA {eta / 60:6.1f} min   ",
                end="",
                flush=True
            )

            if time.time() - t_ckpt >= CHECKPOINT_SECONDS:

                save_state(state_path, current_shas, D, valid, fingerprint)

                t_ckpt = time.time()

    except BaseException:

        # Ctrl-Cや例外のときも、ここまでの計算結果は残す
        # (OOM killなどSIGKILLのときは定期チェックポイントが効く)。
        try:

            save_state(state_path, current_shas, D, valid, fingerprint)

        except Exception:

            pass

        raise

    print()

    return done


# ==================================================
# 自己検証(キャッシュを使わずwavから計算し直して照合)
# ==================================================

def reference_distance(spec_a, spec_b, order, use_log, df, dx_eff, k0):
    """cdistを使わない素朴な参照実装(float32保存値 -> k0未満を捨てて再正規化 -> float64 CDF)。"""

    sa = np.asarray(spec_a, dtype=np.float64)[k0:]
    sb = np.asarray(spec_b, dtype=np.float64)[k0:]

    # 距離計算本体(load_cdf_rows)と同じ扱いにする: 再正規化するのは低域を捨てたとき(k0>0)だけ。
    # k0=0 でも再正規化すると、float32保存による総和の1からのずれ(約1e-9)が
    # 距離に約1e-7の相対差として出てしまい、正しい行列を誤って不一致と判定する。
    if k0 > 0:

        sa = sa / np.sum(sa)
        sb = sb / np.sum(sb)

    fa = np.cumsum(sa)
    fb = np.cumsum(sb)

    diff = np.abs(fa - fb)

    if order == 1:

        if use_log:

            return float(np.sum(diff * dx_eff))

        return float(np.sum(diff) * df)

    if use_log:

        return float(np.sqrt(np.sum(diff ** 2 * dx_eff)))

    return float(np.sqrt(np.sum(diff ** 2) * df))


def verify_random_files(
    current_files,
    current_shas,
    D,
    order,
    use_log,
    df,
    dx_eff,
    k0
):

    n = len(current_files)

    k = min(VERIFY_FILES, n)

    if k <= 0:

        return

    rng = np.random.default_rng()

    picked = sorted(int(i) for i in rng.choice(n, size=k, replace=False))

    print()
    print(f"Verifying {k} random file(s) against fresh wav computation...")

    fresh = {}

    for i in picked:

        spec = compute_spectrum_distribution(
            current_files[i]["path"]
        ).astype(np.float32)

        cached = np.load(spectrum_path(current_shas[i]))

        err = float(
            np.sum(
                np.abs(
                    spec.astype(np.float64) - cached.astype(np.float64)
                )
            )
        )

        if err > 1e-5:

            raise RuntimeError(
                "VERIFY FAILED: cached spectrum differs from fresh "
                f"computation: {current_files[i]['relative_name']} "
                f"(L1 diff {err:.3e}). "
                "Set REBUILD_CACHE=True and run again."
            )

        fresh[i] = spec

    others = [i for i in range(n) if i not in fresh]

    if others:

        extra = rng.choice(others, size=min(10, len(others)), replace=False)

    else:

        extra = []

    checked = 0
    worst = 0.0

    def check(i, j, spec_i, spec_j):

        nonlocal checked, worst

        ref = reference_distance(spec_i, spec_j, order, use_log, df, dx_eff, k0)

        got = float(D[i, j])

        rel = abs(ref - got) / max(abs(ref), 1e-300)

        worst = max(worst, rel)

        checked += 1

        if rel > 1e-7 and abs(ref - got) > 1e-12:

            raise RuntimeError(
                "VERIFY FAILED: "
                f"D[{current_files[i]['relative_name']}, "
                f"{current_files[j]['relative_name']}] = {got!r}, "
                f"recomputed = {ref!r}"
            )

    for a_pos, i in enumerate(picked):

        for j in picked[a_pos + 1:]:

            check(i, j, fresh[i], fresh[j])

        for j in extra:

            j = int(j)

            check(i, j, fresh[i], np.load(spectrum_path(current_shas[j])))

    print(
        f"  OK: {checked} pair(s) match "
        f"(worst relative error {worst:.2e})"
    )


# ==================================================
# 出力(エクスポート)。キャッシュとしては読み戻さない。
# ==================================================

def write_matrix_csv(path, names, matrix):

    def writer(f):

        w = csv.writer(f)

        w.writerow([""] + names)

        for i in range(len(names)):

            w.writerow([names[i]] + np.asarray(matrix[i], dtype=np.float64).tolist())

    atomic_write(path, writer, text=True)


def export_spectra_npy(path, current_shas, spectrum_len):
    """spectra.npy(N x L, float32)を1行ずつ書き出す。メモリマップは使わない。"""

    n = len(current_shas)

    def writer(f):

        header = {
            "descr": np.lib.format.dtype_to_descr(np.dtype("<f4")),
            "fortran_order": False,
            "shape": (n, spectrum_len),
        }

        np.lib.format.write_array_header_1_0(f, header)

        for k, sha in enumerate(current_shas):

            row = np.load(spectrum_path(sha), allow_pickle=False)

            f.write(np.ascontiguousarray(row, dtype="<f4").tobytes())

            if (k + 1) % 100 == 0 or k + 1 == n:

                print(
                    f"\r  spectra.npy: {k + 1}/{n}",
                    end="",
                    flush=True
                )

    atomic_write(path, writer)

    print()


# ==================================================
# 低域カット(対数軸)・スペクトル出力の共有
# ==================================================

def link_or_copy_spectra_npy(path, current_shas, spectrum_len, ctx):
    """
    spectra.npy(約4GB)を、モードごとの出力フォルダにそれぞれ置く。
    最初の1回だけ実際に書き出し、2回目以降は同じファイルへのハードリンク
    (できなければコピー、それも駄目なら書き出し直し)にして、書き込みを節約する。
    各フォルダの spectra.npy は、更新時は os.replace で別ファイルに置き換わるので、
    リンクを共有していても他のフォルダの内容が書き換わることはない。
    """

    path = os.path.abspath(path)

    src = ctx.get("spectra_npy_src")

    if src and os.path.exists(src) and os.path.abspath(src) != path:

        tmp = f"{path}{TMP_MARK}{os.getpid()}"

        try:

            if os.path.exists(tmp):

                os.remove(tmp)

            os.link(src, tmp)

            os.replace(tmp, path)

            _fsync_dir(os.path.dirname(path))

            print("  spectra.npy: hard-linked from an earlier mode")

            return

        except OSError:

            try:

                os.remove(tmp)

            except OSError:

                pass

        try:

            import shutil

            def copier(f):

                with open(src, "rb") as g:

                    shutil.copyfileobj(g, f, 16 * 1024 * 1024)

            atomic_write(path, copier)

            print("  spectra.npy: copied from an earlier mode")

            return

        except OSError:

            pass

    export_spectra_npy(path, current_shas, spectrum_len)

    ctx["spectra_npy_src"] = path


# ==================================================
# 共通の準備(WAV探索・SHA256・スペクトル)。全モードで1回だけ。
# ==================================================

def prepare_inputs(modes):

    out_dirs = [out_dir_for_mode(m) for m in modes]
    out_abs_list = [os.path.abspath(d) for d in out_dirs]

    for d in out_dirs:

        os.makedirs(d, exist_ok=True)

        # 前回クラッシュの残骸(一時ファイル)を掃除
        cleanup_stale_tmp(d)

    if os.path.isdir(SPECTRA_CACHE_ROOT):

        cleanup_stale_tmp(SPECTRA_CACHE_ROOT)

    # ------------------------------------------------
    # REBUILD_CACHE: このスクリプトのキャッシュを破棄
    # ------------------------------------------------

    if REBUILD_CACHE:

        import shutil

        print()
        print("REBUILD_CACHE=True: discarding cached spectra and distance state.")

        if os.path.isdir(spectra_dir()):

            shutil.rmtree(spectra_dir())

        for d in out_dirs:

            state = os.path.join(d, "distance_state.npz")

            if os.path.exists(state):

                os.remove(state)

        print(
            "  (If this run is interrupted, set REBUILD_CACHE=False and "
            "run again to resume from what was already built.)"
        )

    # ------------------------------------------------
    # WAV探索
    # ------------------------------------------------

    current_files = []

    for group_name in TARGET_DIRS:

        group_dir = os.path.join(ROOT_DIR, group_name)

        if not os.path.isdir(group_dir):

            print(f"WARNING: directory not found: {group_dir}")

            continue

        filenames = sorted(
            filename
            for filename in os.listdir(group_dir)
            if filename.lower().endswith(".wav")
        )

        for filename in filenames:

            file_path = os.path.join(group_dir, filename)

            if any(is_path_inside(file_path, o) for o in out_abs_list):

                continue

            if KEYWORD and KEYWORD not in filename:

                continue

            current_files.append(
                {
                    "group_name": group_name,
                    "filename": filename,
                    "relative_name": f"{group_name}/{filename}",
                    "path": file_path,
                }
            )

    if len(current_files) == 0:

        raise RuntimeError("No WAV files were found.")

    N = len(current_files)

    current_names = [item["relative_name"] for item in current_files]

    print()
    print(f"Current WAV files: {N}")

    # ------------------------------------------------
    # SHA256(毎回、実ファイルの中身から計算する)
    # ------------------------------------------------

    print()
    print("Calculating SHA256...")

    current_sha256 = {}

    for i, item in enumerate(current_files):

        current_sha256[item["relative_name"]] = compute_sha256(item["path"])

        if (i + 1) % 50 == 0 or i + 1 == N:

            print(f"\r  SHA256: {i + 1}/{N}", end="", flush=True)

    print()

    current_shas = [current_sha256[name] for name in current_names]

    # ------------------------------------------------
    # スペクトル(SHA256ごとにキャッシュ)
    # ------------------------------------------------

    ensure_spectra(current_files, current_sha256)

    lengths, bad = validate_spectra(current_files, current_sha256)

    if bad:

        print(
            f"WARNING: {len(bad)} cached spectrum file(s) are unreadable; "
            "recomputing them."
        )

        for sha in bad:

            try:

                os.remove(spectrum_path(sha))

            except OSError:

                pass

        ensure_spectra(current_files, current_sha256)

        lengths, bad = validate_spectra(current_files, current_sha256)

        if bad:

            raise RuntimeError(
                f"{len(bad)} spectrum file(s) could not be created."
            )

    if len(lengths) != 1:

        lines = []

        for length, names in sorted(lengths.items()):

            lines.append(
                f"  length {length}: {len(names)} file(s), e.g. "
                + ", ".join(names[:3])
            )

        raise RuntimeError(
            "Spectrum lengths differ between files. "
            "All wav files must have the same length after resampling.\n"
            + "\n".join(lines)
        )

    L = next(iter(lengths))

    print()
    print(f"Spectrum length: {L}")

    freqs = np.linspace(0, TARGET_SR / 2, L, dtype=np.float64)

    df = float(freqs[1] - freqs[0]) if L > 1 else 1.0

    return {
        "current_files": current_files,
        "current_names": current_names,
        "current_sha256": current_sha256,
        "current_shas": current_shas,
        "N": N,
        "L": L,
        "freqs": freqs,
        "df": df,
    }


# ==================================================
# 1つのモードの距離行列を作る
# ==================================================

def run_mode(ctx, mode):

    t_mode = time.time()

    order, use_log = parse_wasserstein_mode(mode)

    metric = "cityblock" if order == 1 else "euclidean"

    current_files = ctx["current_files"]
    current_names = ctx["current_names"]
    current_sha256 = ctx["current_sha256"]
    current_shas = ctx["current_shas"]
    N = ctx["N"]
    L = ctx["L"]
    freqs = ctx["freqs"]
    df = ctx["df"]

    out_dir = out_dir_for_mode(mode)

    os.makedirs(out_dir, exist_ok=True)

    p_state = os.path.join(out_dir, "distance_state.npz")
    p_raw_npy = os.path.join(out_dir, "distance_matrix_raw.npy")
    p_raw_csv = os.path.join(out_dir, "distance_matrix_raw.csv")
    p_norm_npy = os.path.join(out_dir, "distance_matrix_normalized.npy")
    p_norm_csv = os.path.join(out_dir, "distance_matrix_normalized.csv")
    p_spectra_npy = os.path.join(out_dir, "spectra.npy")
    p_freqs = os.path.join(out_dir, "freqs.npy")
    p_file_info = os.path.join(out_dir, "file_info.csv")
    p_group_info = os.path.join(out_dir, "group_info.csv")
    p_sha_json = os.path.join(out_dir, "sha256_cache.json")
    p_display = os.path.join(out_dir, "display_groups.json")
    p_manifest = os.path.join(out_dir, "export_manifest.json")

    print()
    print("#" * 60)
    print(f"# Mode: {mode}    ->  {out_dir}")
    print("#" * 60)

    # ------------------------------------------------
    # 周波数軸・積分の刻み幅
    # ------------------------------------------------

    if use_log:

        if not LOG_F0_HZ > 0:

            raise ValueError("LOG_F0_HZ must be > 0 for log-axis modes.")

        # f0 以上のビンだけを使う(DC=0Hzは常に除外)
        k0 = max(1, int(np.searchsorted(freqs, LOG_F0_HZ, side="left")))

        if L - k0 < 2:

            raise ValueError("LOG_F0_HZ is too high: fewer than 2 bins remain.")

        x = np.log2(freqs[k0:] / LOG_F0_HZ)

        dx_eff = np.diff(x)
        dx_eff = np.append(dx_eff, dx_eff[-1])

        w = dx_eff

        print(
            f"Log axis: x = lb(f / {LOG_F0_HZ:g} Hz); "
            f"dropping bins 0..{k0 - 1} (< {freqs[k0]:.4f} Hz), "
            f"using {L - k0} of {L} bins"
        )

    else:

        k0 = 0
        dx_eff = None
        w = df

    # L1: sum |dF| * w          -> cityblock( F*w )
    # L2: sqrt( sum dF^2 * w )  -> euclidean( F*sqrt(w) )
    weight = w if order == 1 else np.sqrt(w)

    # ------------------------------------------------
    # 距離キャッシュ状態の読み込み(内容=SHA256で対応付け)
    # ------------------------------------------------

    fingerprint = {
        "code_version": CODE_VERSION,
        "target_sr": TARGET_SR,
        "order": order,
        "log_axis": bool(use_log),
        "spectrum_len": int(L),
    }

    if use_log:

        # 軸の定義: x = lb(f / f0)、f0未満を捨てて再正規化。
        # 旧版の x = lb(f + 1) で作った状態とはこのキーの有無で区別され、自動的に使われなくなる。
        fingerprint["log_f0_hz"] = float(LOG_F0_HZ)
        fingerprint["log_k0"] = int(k0)

    prior = None if REBUILD_CACHE else load_state(p_state, fingerprint)

    D, valid = build_initial_matrices(current_shas, prior)

    reused_pairs = (int(np.count_nonzero(valid)) - N) // 2

    print()
    print("Distance matrix:")
    print(f"  reused pairs (cache / identical content): {reused_pairs}")

    # ------------------------------------------------
    # 距離計算
    # ------------------------------------------------

    new_pairs = 0

    for attempt in range(2):

        try:

            new_pairs = compute_missing_distances(
                D,
                valid,
                current_shas,
                current_names,
                L,
                weight,
                k0,
                metric,
                p_state,
                fingerprint
            )

            break

        except CorruptSpectrum as e:

            print()
            print(f"WARNING: corrupt spectrum cache: {e}")

            if attempt == 1:

                raise

            try:

                os.remove(spectrum_path(e.sha))

            except OSError:

                pass

            ensure_spectra(current_files, current_sha256)

    if not valid.all():

        raise RuntimeError("internal error: some distances were not computed")

    # 完成した状態を保存(次回はこれがキャッシュになる)
    save_state(p_state, current_shas, D, valid, fingerprint)

    # ------------------------------------------------
    # 自己検証
    # ------------------------------------------------

    verify_random_files(
        current_files,
        current_shas,
        D,
        order,
        use_log,
        df,
        dx_eff,
        k0
    )

    # ------------------------------------------------
    # ここから出力(エクスポート)。キャッシュとしては読み戻さない。
    # ------------------------------------------------

    print()
    print("Writing outputs...")

    atomic_save_npy(p_freqs, freqs)

    atomic_save_npy(p_raw_npy, D)

    write_matrix_csv(p_raw_csv, current_names, D)

    # file_info / group_info
    file_info_rows = []

    for i, item in enumerate(current_files):

        file_info_rows.append(
            {
                "index": i,
                "group_index": -1,
                "group_name": item["group_name"],
                "filename": item["filename"],
                "relative_name": item["relative_name"],
                "path": item["path"],
            }
        )

    group_info_rows = []

    for group_index, group_name in enumerate(TARGET_DIRS):

        indices = [
            i
            for i, item in enumerate(current_files)
            if item["group_name"] == group_name
        ]

        if not indices:

            continue

        group_info_rows.append(
            {
                "group_index": group_index,
                "group_name": group_name,
                "size": len(indices),
                "start": min(indices),
                "end": max(indices),
            }
        )

        for i in indices:

            file_info_rows[i]["group_index"] = group_index

    def write_dict_csv(path, rows, columns):

        def writer(f):

            w_ = csv.DictWriter(f, fieldnames=columns)

            w_.writeheader()

            w_.writerows(rows)

        atomic_write(path, writer, text=True)

    write_dict_csv(
        p_file_info,
        file_info_rows,
        ["index", "group_index", "group_name", "filename", "relative_name", "path"]
    )

    write_dict_csv(
        p_group_info,
        group_info_rows,
        ["group_index", "group_name", "size", "start", "end"]
    )

    atomic_save_json(p_sha_json, current_sha256)

    if not os.path.exists(p_display):

        atomic_save_json(
            p_display,
            [
                {
                    "group_name": row["group_name"],
                    "group_index": row["group_index"],
                }
                for row in group_info_rows
            ]
        )

    if NORMALIZE_DISTANCE_MATRIX:

        d_min = float(np.min(D))
        d_max = float(np.max(D))

        if d_max == d_min:

            normalized = np.zeros_like(D)

        else:

            normalized = (D - d_min) / (d_max - d_min)

        atomic_save_npy(p_norm_npy, normalized)

        write_matrix_csv(p_norm_csv, current_names, normalized)

        del normalized

    if EXPORT_SPECTRA_NPY:

        link_or_copy_spectra_npy(p_spectra_npy, current_shas, L, ctx)

    # 最後に「この出力一式が完成した」ことを示すマニフェストを書く。
    digest = hashlib.sha256(
        "\n".join(
            f"{name}\t{sha}" for name, sha in zip(current_names, current_shas)
        ).encode("utf-8")
    ).hexdigest()

    atomic_save_json(
        p_manifest,
        {
            "complete": True,
            "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "n_files": N,
            "spectrum_bins": int(L),
            "wasserstein_mode": mode,
            "fingerprint": fingerprint,
            "files_digest": digest,
            "spectra_npy_exported": bool(EXPORT_SPECTRA_NPY),
        }
    )

    elapsed = time.time() - t_mode

    print()
    print(f"[{mode}] completed: {N} files, reused {reused_pairs} pairs, "
          f"computed {new_pairs} pairs, {elapsed / 60:.1f} min")
    print(f"  Raw NPY        : {p_raw_npy}")
    print(f"  Raw CSV        : {p_raw_csv}")
    print(f"  File info      : {p_file_info}")
    print(f"  Group info     : {p_group_info}")
    print(f"  Distance state : {p_state}")

    return {
        "mode": mode,
        "out_dir": out_dir,
        "reused_pairs": reused_pairs,
        "new_pairs": new_pairs,
        "elapsed": elapsed,
    }


# ==================================================
# 使われなくなったスペクトルキャッシュの整理(全モード成功後に1回)
# ==================================================

def report_unused_spectra(ctx, prune_allowed):

    keep = {spectrum_path(sha) for sha in ctx["current_shas"]}

    unused = []

    if os.path.isdir(spectra_dir()):

        for dirpath, _, filenames in os.walk(spectra_dir()):

            for filename in filenames:

                path = os.path.join(dirpath, filename)

                if filename.endswith(".npy") and path not in keep:

                    unused.append(path)

    if not unused:

        return

    if PRUNE_UNUSED_SPECTRA and prune_allowed:

        for path in unused:

            try:

                os.remove(path)

            except OSError:

                pass

        print(f"Pruned {len(unused)} unused cached spectrum file(s).")

    else:

        print(
            f"NOTE: {len(unused)} cached spectrum file(s) are not used by "
            "the current file set (PRUNE_UNUSED_SPECTRA=True to delete)."
        )


# ==================================================
# メイン
# ==================================================

def main():

    started = time.time()

    modes = modes_to_run()

    print()
    print("Modes to run: " + ", ".join(modes))

    ctx = prepare_inputs(modes)

    results = []
    failures = []

    if len(modes) == 1:

        # 単一モードのときは、エラーはそのまま送出する(トレースバックを見やすくするため)
        results.append(run_mode(ctx, modes[0]))

    else:

        for mode in modes:

            try:

                results.append(run_mode(ctx, mode))

            except Exception as e:

                import traceback

                print()
                print(f"!!! Mode {mode} FAILED: {type(e).__name__}: {e}")
                traceback.print_exc()

                failures.append((mode, e))

    report_unused_spectra(ctx, prune_allowed=not failures)

    print()
    print("=" * 60)
    print("Completed." if not failures else "Finished WITH FAILURES.")
    print("=" * 60)
    print(f"Files                 : {ctx['N']}")
    print(f"Spectrum bins         : {ctx['L']}")

    for r in results:

        print(
            f"  {r['mode']:<5} OK    reused {r['reused_pairs']:>9}  "
            f"new {r['new_pairs']:>9}  {r['elapsed'] / 60:6.1f} min  {r['out_dir']}"
        )

    for mode, e in failures:

        print(f"  {mode:<5} FAILED {type(e).__name__}: {e}")

    print(f"Spectra cache         : {spectra_dir()}")
    print(f"Elapsed (total)       : {(time.time() - started) / 60:.1f} min")
    print()

    if failures:

        print(
            "Re-run the script: finished modes are reused as they are, and "
            "failed modes resume from their saved progress."
        )

        sys.exit(1)


if __name__ == "__main__":

    main()