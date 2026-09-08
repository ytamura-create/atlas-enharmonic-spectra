import os
import json
import hashlib
from collections import Counter

import numpy as np
import pandas as pd

import librosa


# ==================================================
# 設定
# ==================================================

ROOT_DIR = os.path.expanduser(
    "./wav/"
)

TARGET_SR = 96000


# ==================================================
# Wasserstein距離
#
# "L1"   : 線形周波数 × 1-Wasserstein
# "L2"   : 線形周波数 × 2-Wasserstein
# "lbL1" : log-frequency × 1-Wasserstein
# "lbL2" : log-frequency × 2-Wasserstein
# ==================================================

WASSERSTEIN_MODE = "L1"
OUT_DIR = f"./distanceMatrix_{WASSERSTEIN_MODE}"


# ==================================================
# 対象ディレクトリ
#
# この順番が、そのままグループ順になる。
#
# [] なら ROOT_DIR 以下の全ディレクトリを対象。
# ==================================================

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
    "basstrb",
    "basstrb_mute-straight",
    "basstrb_mute-straightMetal",
    "basstrb_mute-cup",
    "basstrb_mute-harmonNOstem",
    "basstrb_mute-harmonStemmed",
    "basstrb_mute-bucket",
    "va",
    "gauss_sigma-002.5%"
]


# ==================================================
# ファイル名フィルタ
#
# 空文字列なら全ファイル
# ==================================================

KEYWORD = ""


# ==================================================
# 距離行列の正規化
# ==================================================

NORMALIZE_DISTANCE_MATRIX = False

# ==================================================
# キャッシュ再構築
#
# True:
#   既存の spectra.npy や distance_matrix_raw.npy を
#   無視して全件再計算する。
#   再構築後は新しいキャッシュを保存する。
#
# False:
#   SHA-256一致のキャッシュのみ再利用する。
# ==================================================

REBUILD_CACHE = False


# ==================================================
# グループ表示設定JSON
# ==================================================

DISPLAY_GROUPS_JSON = os.path.join(
    OUT_DIR,
    "display_groups.json"
)


# ==================================================
# 出力ディレクトリ
# ==================================================

os.makedirs(
    OUT_DIR,
    exist_ok=True
)


# ==================================================
# パスを絶対パス化
# ==================================================

ROOT_DIR_ABS = os.path.abspath(
    ROOT_DIR
)

OUT_DIR_ABS = os.path.abspath(
    OUT_DIR
)


# ==================================================
# OUT_DIRがROOT_DIR以下に存在するか確認
# ==================================================

def is_path_inside(
    path,
    directory
):

    path = os.path.abspath(
        path
    )

    directory = os.path.abspath(
        directory
    )

    try:

        return os.path.commonpath(
            [
                path,
                directory
            ]
        ) == directory

    except ValueError:

        return False


OUT_DIR_IS_INSIDE_ROOT = is_path_inside(
    OUT_DIR_ABS,
    ROOT_DIR_ABS
)


# ==================================================
# SHA-256計算
#
# WAVファイルのバイナリそのものを対象にする。
# ==================================================

def compute_sha256(
    file_path,
    chunk_size=1024 * 1024
):

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as f:

        while True:

            chunk = f.read(
                chunk_size
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ==================================================
# データベース内のファイル名を統一する関数
#
# すべて
#
#     group_name/filename
#
# の形式にする。
# ==================================================

def normalize_relative_name(
    name
):

    name = str(
        name
    )

    name = name.replace(
        "\\",
        "/"
    )

    name = name.lstrip(
        "/"
    )

    # ----------------------------------------------
    # ROOT_DIRからの相対パスとして解釈できる場合
    # ----------------------------------------------

    root_prefix = (
        ROOT_DIR_ABS
        .replace("\\", "/")
        .rstrip("/")
        + "/"
    )

    normalized_root_prefix = (
        root_prefix.lower()
    )

    normalized_name = (
        name.lower()
    )

    if normalized_name.startswith(
        normalized_root_prefix
    ):

        name = name[
            len(root_prefix):
        ]

    # ----------------------------------------------
    # OUT_DIRを含んでいる古い形式への対応
    # ----------------------------------------------

    out_dir_abs_slash = (
        OUT_DIR_ABS
        .replace("\\", "/")
        .rstrip("/")
    )

    out_dir_name = os.path.basename(
        out_dir_abs_slash
    )

    prefixes = [
        out_dir_name + "/"
    ]

    if OUT_DIR_IS_INSIDE_ROOT:

        out_dir_relative = os.path.relpath(
            OUT_DIR_ABS,
            ROOT_DIR_ABS
        ).replace(
            "\\",
            "/"
        )

        if out_dir_relative != ".":

            prefixes.append(
                out_dir_relative.rstrip("/")
                + "/"
            )

    for prefix in prefixes:

        if name.startswith(
            prefix
        ):

            name = name[
                len(prefix):
            ]

            break

    return name


# ==================================================
# 出力ファイル
# ==================================================

RAW_NPY = os.path.join(
    OUT_DIR,
    "distance_matrix_raw.npy"
)

RAW_CSV = os.path.join(
    OUT_DIR,
    "distance_matrix_raw.csv"
)

NORMALIZED_NPY = os.path.join(
    OUT_DIR,
    "distance_matrix_normalized.npy"
)

NORMALIZED_CSV = os.path.join(
    OUT_DIR,
    "distance_matrix_normalized.csv"
)

SPECTRA_NPY = os.path.join(
    OUT_DIR,
    "spectra.npy"
)

FREQS_NPY = os.path.join(
    OUT_DIR,
    "freqs.npy"
)

FILE_INFO_CSV = os.path.join(
    OUT_DIR,
    "file_info.csv"
)

GROUP_INFO_CSV = os.path.join(
    OUT_DIR,
    "group_info.csv"
)

# ★ SHA-256はCSVとは完全に分離
SHA256_CACHE_JSON = os.path.join(
    OUT_DIR,
    "sha256_cache.json"
)


# ==================================================
# FFTベース分布
# ==================================================

def compute_spectrum_distribution(
    file_path
):

    y, sr = librosa.load(
        file_path,
        sr=None
    )

    # ----------------------------------------------
    # SR統一
    # ----------------------------------------------

    if sr != TARGET_SR:

        y = librosa.resample(
            y,
            orig_sr=sr,
            target_sr=TARGET_SR
        )

        sr = TARGET_SR

    # ----------------------------------------------
    # FFT
    # ----------------------------------------------

    spectrum = np.abs(
        np.fft.rfft(y)
    )

    # ----------------------------------------------
    # 数値安定化
    # ----------------------------------------------

    spectrum += 1e-12

    # ----------------------------------------------
    # 確率分布化
    # ----------------------------------------------

    spectrum /= np.sum(
        spectrum
    )

    return spectrum


# ==================================================
# Wasserstein距離
# ==================================================

def wasserstein_distance_quantile(
    q1,
    q2,
    order,
    du
):

    diff = np.abs(q1 - q2)

    if order == 1:

        return np.sum(diff) * du

    elif order == 2:

        return np.sqrt(
            np.sum(diff ** 2) * du
        )

    else:

        raise ValueError(
            "order must be 1 or 2"
        )


# ==================================================
# 現在のデータベースを走査
# ==================================================

print()
print(
    "Scanning database..."
)


if len(TARGET_DIRS) == 0:

    TARGET_DIRS = sorted(
        [
            d
            for d in os.listdir(
                ROOT_DIR_ABS
            )
            if (
                os.path.isdir(
                    os.path.join(
                        ROOT_DIR_ABS,
                        d
                    )
                )
                and
                not (
                    OUT_DIR_IS_INSIDE_ROOT
                    and
                    os.path.abspath(
                        os.path.join(
                            ROOT_DIR_ABS,
                            d
                        )
                    )
                    == OUT_DIR_ABS
                )
            )
        ]
    )

else:

    TARGET_DIRS = list(
        TARGET_DIRS
    )


print()
print(
    "Target directories:"
)

for i, dirname in enumerate(
    TARGET_DIRS
):

    print(
        f"  {i}: {dirname}"
    )


# ==================================================
# 現在存在する全音源
#
# TARGET_DIRSの順
#     ↓
# 各ディレクトリ内のファイル名順
# ==================================================

current_files = []


for dirname in TARGET_DIRS:

    wav_dir = os.path.join(
        ROOT_DIR_ABS,
        dirname
    )

    # ----------------------------------------------
    # OUT_DIR自身は除外
    # ----------------------------------------------

    if (
        OUT_DIR_IS_INSIDE_ROOT
        and
        os.path.abspath(
            wav_dir
        )
        == OUT_DIR_ABS
    ):

        print(
            f"Skipping OUT_DIR: "
            f"{wav_dir}"
        )

        continue

    # ----------------------------------------------
    # ディレクトリ存在確認
    # ----------------------------------------------

    if not os.path.isdir(
        wav_dir
    ):

        print(
            f"Warning: directory not found: "
            f"{wav_dir}"
        )

        continue

    # ----------------------------------------------
    # ファイル名順
    # ----------------------------------------------

    wavs = sorted(
        [
            f
            for f in os.listdir(
                wav_dir
            )
            if f.lower().endswith(
                ".wav"
            )
        ]
    )

    for filename in wavs:

        if (
            KEYWORD
            and
            KEYWORD not in filename
        ):

            continue

        relative_name = (
            f"{dirname}/{filename}"
        )

        relative_name = normalize_relative_name(
            relative_name
        )

        current_files.append(
            {
                "group_name":
                    dirname,

                "filename":
                    filename,

                "relative_name":
                    relative_name,

                "path":
                    os.path.join(
                        wav_dir,
                        filename
                    )
            }
        )


# ==================================================
# 現在のファイル数
# ==================================================

if len(current_files) == 0:

    raise RuntimeError(
        "No wav files found."
    )


print()
print(
    "Current files =",
    len(current_files)
)


# ==================================================
# 過去の file_info.csv を読み込む
#
# ★ここにはSHA-256を要求しない。
#
# 旧コードで作られたfile_info.csvでも
# そのまま利用できるようにする。
# ==================================================

old_file_info = None


if os.path.exists(
    FILE_INFO_CSV
):

    try:

        old_file_info = pd.read_csv(
            FILE_INFO_CSV
        )

        print()
        print(
            "Existing file_info.csv found."
        )

    except Exception as e:

        print()
        print(
            "Could not read existing "
            "file_info.csv:"
        )

        print(e)

        old_file_info = None


# ==================================================
# 過去のファイル名一覧
# ==================================================

old_names = []


if (
    old_file_info is not None
    and
    "relative_name"
    in old_file_info.columns
):

    old_names = [
        normalize_relative_name(
            name
        )
        for name
        in old_file_info[
            "relative_name"
        ]
        .astype(str)
        .tolist()
    ]


elif (
    old_file_info is not None
    and
    "group_name"
    in old_file_info.columns
    and
    "filename"
    in old_file_info.columns
):

    for _, row in old_file_info.iterrows():

        name = (
            f"{row['group_name']}/"
            f"{row['filename']}"
        )

        old_names.append(
            normalize_relative_name(
                name
            )
        )


old_name_set = set(
    old_names
)


# ==================================================
# 現在のファイル名
# ==================================================

current_names = [
    item["relative_name"]
    for item in current_files
]

current_name_set = set(
    current_names
)


# ==================================================
# SHA-256キャッシュを読み込む
#
# ★ file_info.csvとは完全に独立。
#
# 初回は存在しなくてもよい。
# ==================================================

old_sha256_cache = {}


if os.path.exists(
    SHA256_CACHE_JSON
):

    try:

        with open(
            SHA256_CACHE_JSON,
            "r",
            encoding="utf-8"
        ) as f:

            old_sha256_cache = json.load(
                f
            )

        if not isinstance(
            old_sha256_cache,
            dict
        ):

            old_sha256_cache = {}

        print()
        print(
            "Existing SHA-256 cache found."
        )

        print(
            "Cached SHA-256 entries =",
            len(old_sha256_cache)
        )

    except Exception as e:

        print()
        print(
            "Could not read SHA-256 cache:"
        )

        print(e)

        old_sha256_cache = {}

else:

    print()
    print(
        "No SHA-256 cache found."
    )

    print(
        "This is compatible with "
        "the old database."
    )


# ==================================================
# 現在のファイルのSHA-256を計算
#
# ★重要
#
# SHA-256キャッシュにある場合でも、
# ファイルの内容が変更されていない保証がないため、
# 現在存在するWAVについては毎回SHA-256を計算する。
#
# これにより
#
#   同名だが中身が変更された
#
# というケースも正しく検出できる。
# ==================================================

print()
print(
    "Calculating SHA-256..."
)


for index, item in enumerate(
    current_files,
    start=1
):

    item["sha256"] = compute_sha256(
        item["path"]
    )

    print(
        f"\rHashing: "
        f"{index} / "
        f"{len(current_files)}",
        end="",
        flush=True
    )


print()


# ==================================================
# 新しいSHA-256キャッシュ
#
# 現在存在するファイルだけを保存する。
# ==================================================

new_sha256_cache = {
    item["relative_name"]:
        item["sha256"]

    for item in current_files
}

# ==================================================
# SHA-256 → 旧ファイル名
# ==================================================

old_hash_to_names = {}


for name, sha256 in old_sha256_cache.items():

    name = normalize_relative_name(
        name
    )

    sha256 = str(
        sha256
    ).strip()

    if not sha256:
        continue

    old_hash_to_names.setdefault(
        sha256,
        []
    ).append(
        name
    )


# ==================================================
# 差分検出
# ==================================================

new_names = sorted(
    current_name_set
    -
    old_name_set
)

removed_names = sorted(
    old_name_set
    -
    current_name_set
)

existing_names = sorted(
    current_name_set
    &
    old_name_set
)


# ==================================================
# SHA-256による名前変更検出
# ==================================================

renamed_files = []


for item in current_files:

    new_name = item[
        "relative_name"
    ]

    sha256 = item[
        "sha256"
    ]

    # 既存名なら名前変更ではない
    if new_name in old_name_set:
        continue

    # SHA-256キャッシュに同じ内容があるか
    if sha256 not in old_hash_to_names:
        continue

    for old_name in old_hash_to_names[
        sha256
    ]:

        # 古い名前が現在も存在するなら、
        # 単なる重複ファイルなので
        # 「リネーム」とは扱わない。
        if old_name in current_name_set:
            continue

        renamed_files.append(
            {
                "old_name":
                    old_name,

                "new_name":
                    new_name,

                "sha256":
                    sha256
            }
        )

        break


print()
print(
    "Existing files =",
    len(existing_names)
)

print(
    "New files      =",
    len(new_names)
)

print(
    "Removed files  =",
    len(removed_names)
)

print(
    "Renamed files  =",
    len(renamed_files)
)


if len(renamed_files) > 0:

    print()
    print(
        "Files with identical contents "
        "but different names:"
    )

    for item in renamed_files:

        print(
            f"  {item['old_name']}"
            f" -> "
            f"{item['new_name']}"
        )


# ==================================================
# 過去スペクトルを読み込む
# ==================================================

old_spectra = None
old_freqs = None

if REBUILD_CACHE:

    print()
    print("REBUILD_CACHE=True")
    print("Ignoring existing spectra cache.")

else:

    if os.path.exists(SPECTRA_NPY):

        try:

            old_spectra = np.load(SPECTRA_NPY)

            print()
            print("Existing spectra.npy found.")

        except Exception as e:

            print()
            print("Could not load spectra.npy:")

            print(e)

            old_spectra = None

    if os.path.exists(FREQS_NPY):

        try:

            old_freqs = np.load(FREQS_NPY)

        except Exception:

            old_freqs = None


if os.path.exists(
    FREQS_NPY
):

    try:

        old_freqs = np.load(
            FREQS_NPY
        )

    except Exception:

        old_freqs = None


# ==================================================
# 過去スペクトルキャッシュ
#
# ★旧コードとの互換性のため、
#   まずファイル名でキャッシュする。
# ==================================================

spectra_cache_by_name = {}


if (
    old_spectra is not None
    and
    len(old_names)
    == len(old_spectra)
):

    for i, name in enumerate(
        old_names
    ):

        spectra_cache_by_name[
            name
        ] = old_spectra[i]


# ==================================================
# SHA-256によるスペクトルキャッシュ
#
# old_sha256_cacheが存在する場合だけ作れる。
#
# 旧コードで作られたデータの場合、
# SHA-256キャッシュがないので空になる。
# ==================================================

spectra_cache_by_hash = {}


for old_name, sha256 in old_sha256_cache.items():

    old_name = normalize_relative_name(
        old_name
    )

    if old_name not in spectra_cache_by_name:
        continue

    spectra_cache_by_hash[
        sha256
    ] = spectra_cache_by_name[
        old_name
    ]


# ==================================================
# スペクトル計算
#
# 優先順位:
#
# 1. ファイル名で旧スペクトルを再利用
# 2. SHA-256で旧スペクトルを再利用
# 3. 今回すでに計算した同一SHA-256を再利用
# 4. 新規計算
# ==================================================

print()
print(
    "Checking spectra..."
)


spectrum_reused_by_name = 0
spectrum_reused_by_hash = 0
spectrum_reused_current = 0
spectrum_calculated = 0


for item in current_files:

    name = item[
        "relative_name"
    ]

    sha256 = item[
        "sha256"
    ]


    # ----------------------------------------------
    # 1. ファイル名で旧キャッシュを検索
    #
    # ただし、SHA-256も一致する場合だけ再利用する。
    # 同名で中身が変わった場合は再計算する。
    # ----------------------------------------------

    old_sha = old_sha256_cache.get(name)

    # 1. 同じファイル名かつSHA一致
    if (
        name in spectra_cache_by_name
        and old_sha == sha256
    ):

        spectrum_reused_by_name += 1
        continue

    # 2. SHA一致（リネーム対応）
    if sha256 in spectra_cache_by_hash:

        spectra_cache_by_name[name] = spectra_cache_by_hash[sha256]

        spectrum_reused_by_hash += 1

        continue


    # ----------------------------------------------
    # 2. SHA-256で旧キャッシュを検索
    #
    # ファイル名が変更された場合はこちら。
    # ----------------------------------------------

    if sha256 in spectra_cache_by_hash:

        spectra_cache_by_name[
            name
        ] = spectra_cache_by_hash[
            sha256
        ]

        spectrum_reused_by_hash += 1

        print(
            f"Reusing spectrum by SHA-256: "
            f"{name}"
        )

        continue


    # ----------------------------------------------
    # 3. 今回すでに同じSHA-256を計算しているか
    #
    # 同一内容のファイルが複数存在する場合、
    # FFTは1回だけ行う。
    # ----------------------------------------------

    if sha256 in spectra_cache_by_hash:

        spectra_cache_by_name[
            name
        ] = spectra_cache_by_hash[
            sha256
        ]

        spectrum_reused_current += 1

        continue


    # ----------------------------------------------
    # 4. 新規計算
    # ----------------------------------------------

    print(
        f"Calculating spectrum: "
        f"{name}"
    )

    spectrum = (
        compute_spectrum_distribution(
            item["path"]
        )
    )

    spectra_cache_by_name[
        name
    ] = spectrum

    spectra_cache_by_hash[
        sha256
    ] = spectrum

    spectrum_calculated += 1


print()
print(
    "Spectrum reused by filename =",
    spectrum_reused_by_name
)

print(
    "Spectrum reused by SHA-256 =",
    spectrum_reused_by_hash
)

print(
    "Spectrum reused within current scan =",
    spectrum_reused_current
)

print(
    "Spectrum calculated =",
    spectrum_calculated
)


# ==================================================
# スペクトル長を統一
# ==================================================

all_lengths = [
    len(spectrum)
    for spectrum
    in spectra_cache_by_name.values()
]


min_len = min(
    all_lengths
)


print()
print(
    "Spectrum length =",
    min_len
)


# ==================================================
# スペクトルを現在のファイル順に並べる
# ==================================================

spectra = np.array(
    [
        spectra_cache_by_name[
            item["relative_name"]
        ][:min_len]
        for item in current_files
    ]
)


# ==================================================
# コスト軸
# ==================================================

freqs = np.linspace(
    0,
    TARGET_SR / 2,
    min_len
)

if WASSERSTEIN_MODE.startswith("lb"):

    # 0Hz対策
    cost_axis = np.log(freqs + 1.0)

else:

    cost_axis = freqs


# ==================================================
# 量子化関数（Inverse CDF）を一度だけ計算
# ==================================================

QUANTILE_BINS = min_len

u = (
    np.arange(QUANTILE_BINS) + 0.5
) / QUANTILE_BINS

quantiles = np.empty(
    (spectra.shape[0], QUANTILE_BINS),
    dtype=np.float32
)

for i in range(spectra.shape[0]):

    cdf = np.cumsum(spectra[i])

    quantiles[i] = np.interp(
        u,
        cdf,
        cost_axis
    )

du = 1.0 / QUANTILE_BINS


# ==================================================
# 周波数軸
# ==================================================

freqs = np.linspace(
    0,
    TARGET_SR / 2,
    min_len
)


# ==================================================
# CDF（累積分布）を一度だけ計算
# ==================================================

cdf_spectra = np.cumsum(
    spectra,
    axis=1
)

dx = freqs[1] - freqs[0]


# ==================================================
# スペクトル保存
# ==================================================

np.save(
    SPECTRA_NPY,
    spectra
)

np.save(
    FREQS_NPY,
    freqs
)


print()
print(
    "Saved spectra:"
)

print(
    SPECTRA_NPY
)


# ==================================================
# SHA-256キャッシュ保存
#
# ★file_info.csvには書かない。
#
# 現在存在するファイルだけを保存する。
# ==================================================

with open(
    SHA256_CACHE_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        new_sha256_cache,
        f,
        ensure_ascii=False,
        indent=4
    )


print()
print(
    "Saved SHA-256 cache:"
)

print(
    SHA256_CACHE_JSON
)


# ==================================================
# 現在のファイル情報
#
# ★SHA-256は入れない。
#
# 旧形式のfile_info.csvと同じ構造を維持する。
# ==================================================

file_info_rows = []


for index, item in enumerate(
    current_files
):

    file_info_rows.append(
        {
            "index":
                index,

            "group_index":
                -1,

            "group_name":
                item["group_name"],

            "filename":
                item["filename"],

            "relative_name":
                item["relative_name"],

            "path":
                item["path"]
        }
    )


file_info = pd.DataFrame(
    file_info_rows
)


# ==================================================
# グループ情報作成
#
# TARGET_DIRSの入力順を維持する。
# ==================================================

group_info_rows = []

start = 0


for group_name in TARGET_DIRS:

    group_files = [
        item
        for item in current_files
        if item["group_name"]
        == group_name
    ]

    size = len(
        group_files
    )

    if size == 0:

        continue

    end = (
        start
        +
        size
    )

    group_info_rows.append(
        {
            "group_index":
                len(group_info_rows),

            "group_name":
                group_name,

            "size":
                size,

            "start":
                start,

            "end":
                end
        }
    )

    start = end


group_info = pd.DataFrame(
    group_info_rows
)


# ==================================================
# group_indexをfile_infoに反映
# ==================================================

group_index_map = {
    row["group_name"]:
        int(row["group_index"])

    for _, row
    in group_info.iterrows()
}


file_info[
    "group_index"
] = (
    file_info[
        "group_name"
    ]
    .map(
        group_index_map
    )
    .astype(int)
)

# ==================================================
# ブロック進捗表示用
# ==================================================

file_to_group = file_info["group_index"].tolist()

group_starts = group_info["start"].tolist()
group_sizes = group_info["size"].tolist()

GROUP_COUNT = len(group_info)

# ブロックごとの総ペア数
block_total_pairs = {}

for gi in range(GROUP_COUNT):
    for gj in range(gi, GROUP_COUNT):

        ni = group_sizes[gi]
        nj = group_sizes[gj]

        if gi == gj:
            total = ni * (ni - 1) // 2
        else:
            total = ni * nj

        block_total_pairs[(gi, gj)] = total

# ブロックごとの処理済み数
block_done_pairs = {
    k: 0
    for k in block_total_pairs
}

current_block = None


# ==================================================
# メタデータ保存
# ==================================================

group_info.to_csv(
    GROUP_INFO_CSV,
    index=False
)

file_info.to_csv(
    FILE_INFO_CSV,
    index=False
)


print()
print(
    "Saved group information:"
)

print(
    GROUP_INFO_CSV
)

print(
    "Saved file information:"
)

print(
    FILE_INFO_CSV
)


# ==================================================
# display_groups.json
#
# 初回のみ自動生成
#
# 既存JSONは上書きしない。
# ==================================================

print()
print(
    "Checking display_groups.json..."
)


if not os.path.exists(
    DISPLAY_GROUPS_JSON
):

    print(
        "display_groups.json does not exist."
    )

    print(
        "Generating template..."
    )

    display_groups = []


    for group_name in TARGET_DIRS:

        group_files = [
            item
            for item in current_files
            if item["group_name"]
            == group_name
        ]

        if len(group_files) == 0:

            continue

        files = [
            normalize_relative_name(
                item["relative_name"]
            )
            for item in group_files
        ]

        display_groups.append(
            {
                "name":
                    group_name,

                "files":
                    files
            }
        )


    display_config = {
        "groups":
            display_groups
    }


    with open(
        DISPLAY_GROUPS_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            display_config,
            f,
            ensure_ascii=False,
            indent=4
        )


    print(
        "Generated:"
    )

    print(
        DISPLAY_GROUPS_JSON
    )


else:

    print(
        "Existing display_groups.json found."
    )

    print(
        "Keeping existing JSON unchanged."
    )


# ==================================================
# display_groups.json の整合性確認
# ==================================================

print()
print(
    "Checking display_groups.json..."
)


try:

    with open(
        DISPLAY_GROUPS_JSON,
        "r",
        encoding="utf-8"
    ) as f:

        display_config = json.load(
            f
        )


    json_groups = display_config.get(
        "groups",
        []
    )


    json_files = []


    for group in json_groups:

        files = group.get(
            "files",
            []
        )

        if not isinstance(
            files,
            list
        ):

            print(
                "Warning: "
                f"group '{group.get('name')}' "
                "has invalid 'files'."
            )

            continue


        for filename in files:

            normalized_filename = (
                normalize_relative_name(
                    filename
                )
            )

            json_files.append(
                normalized_filename
            )


    json_file_set = set(
        json_files
    )


    json_missing_files = sorted(
        json_file_set
        -
        current_name_set
    )


    json_unregistered_files = sorted(
        current_name_set
        -
        json_file_set
    )


    file_counts = Counter(
        json_files
    )


    json_duplicate_files = sorted(
        [
            name
            for name, count
            in file_counts.items()
            if count > 1
        ]
    )


    print()
    print(
        "JSON groups =",
        len(json_groups)
    )

    print(
        "JSON files  =",
        len(json_file_set)
    )


    if len(json_missing_files) > 0:

        print()
        print(
            "Warning: files listed in JSON "
            "but not found in database:"
        )

        for name in json_missing_files:

            print(
                f"  {name}"
            )


    if len(json_unregistered_files) > 0:

        print()
        print(
            "Warning: files found in database "
            "but not registered in JSON:"
        )

        for name in json_unregistered_files:

            print(
                f"  {name}"
            )


    if len(json_duplicate_files) > 0:

        print()
        print(
            "Warning: duplicate files in JSON:"
        )

        for name in json_duplicate_files:

            print(
                f"  {name}"
            )


    if (
        len(json_missing_files) == 0
        and
        len(json_unregistered_files) == 0
        and
        len(json_duplicate_files) == 0
    ):

        print()
        print(
            "display_groups.json is "
            "consistent with the database."
        )


except Exception as e:

    print()
    print(
        "Could not read "
        "display_groups.json:"
    )

    print(e)


# ==================================================
# 距離行列の既存データを読み込む
# ==================================================

old_D = None
old_D_names = []

if REBUILD_CACHE:

    print()
    print("Ignoring existing distance matrix cache.")

else:

    if os.path.exists(RAW_NPY):

        try:

            old_D = np.load(RAW_NPY)

            print()
            print("Existing raw distance matrix found.")

        except Exception as e:

            print()
            print("Could not load existing distance matrix:")

            print(e)

            old_D = None


# ==================================================
# 旧距離行列の名前を取得
# ==================================================

if (not REBUILD_CACHE) and os.path.exists(RAW_CSV):

    try:

        old_distance_df = pd.read_csv(
            RAW_CSV,
            index_col=0
        )


        old_D_names = [
            normalize_relative_name(
                name
            )
            for name
            in old_distance_df.index
            .astype(str)
            .tolist()
        ]


        if old_D is None:

            old_D = (
                old_distance_df.values
                .astype(float)
            )


    except Exception as e:

        print()
        print(
            "Could not read old "
            "distance matrix:"
        )

        print(e)


# ==================================================
# 旧距離行列の整合性確認
# ==================================================

distance_cache_by_name = {}


if (
    old_D is not None
    and
    len(old_D_names)
    == old_D.shape[0]
    == old_D.shape[1]
):

    for i in range(
        len(old_D_names)
    ):

        for j in range(
            i + 1,
            len(old_D_names)
        ):

            key = (
                old_D_names[i],
                old_D_names[j]
            )

            distance_cache_by_name[
                key
            ] = old_D[i, j]


print()
print(
    "Cached name distances =",
    len(distance_cache_by_name)
)


# ==================================================
# SHA-256による距離キャッシュ
#
# 旧距離行列の各ファイルについて、
# SHA-256キャッシュが存在する場合だけ作る。
#
# 旧コードで計算したデータでも、
# SHA-256キャッシュがない場合はここは空になる。
# その場合は上の「名前によるキャッシュ」が使われる。
# ==================================================

distance_cache_by_hash = {}


if (
    old_D is not None
    and
    len(old_D_names)
    == old_D.shape[0]
    == old_D.shape[1]
):

    for i in range(
        len(old_D_names)
    ):

        name_i = old_D_names[i]

        if name_i not in old_sha256_cache:
            continue

        hash_i = old_sha256_cache[
            name_i
        ]

        for j in range(
            i + 1,
            len(old_D_names)
        ):

            name_j = old_D_names[j]

            if name_j not in old_sha256_cache:
                continue

            hash_j = old_sha256_cache[
                name_j
            ]

            key = (
                hash_i,
                hash_j
            )

            distance_cache_by_hash[
                key
            ] = old_D[i, j]


print(
    "Cached SHA-256 distances =",
    len(distance_cache_by_hash)
)

# ==================================================
# ブロック進捗表示
# ==================================================

def progress_symbol(done, total):
    """
    ブロック進捗率を記号に変換する。
    """

    if total == 0:
        return "■"

    frac = done / total

    if done == total:
        return "■"
    elif frac >= 0.75:
        return "▓"
    elif frac >= 0.50:
        return "▒"
    elif frac > 0:
        return "░"
    else:
        return "□"

def render_block_progress(current_block):

    # ヘッダ
    LABEL_W = max(2, len(str(GROUP_COUNT - 1)))

    header = " " * LABEL_W + "".join(
        f"{i:>{LABEL_W + 1}}"
        for i in range(GROUP_COUNT)
    )

    lines = [
        "Block progress (TARGET_DIRS)",
        header
    ]

    for r in range(GROUP_COUNT):

        cells = [f"{r:0{LABEL_W}d}"]

        for c in range(GROUP_COUNT):

            if c < r:
                ch = "×"
            else:
                done = block_done_pairs[(r, c)]
                total = block_total_pairs[(r, c)]
                ch = progress_symbol(done, total)

                if (r, c) == current_block and done < total:
                    ch = "█"

            cells.append(f"{ch:>{LABEL_W}}")

        lines.append(" ".join(cells))

    return "\n".join(lines)

# ==================================================
# 距離行列計算
#
# 優先順位:
#
# 1. ファイル名による既存距離
# 2. SHA-256による既存距離
# 3. SHA-256が同じ → 0
# 4. 新規計算
# ==================================================

N = len(
    current_files
)


D = np.zeros(
    (
        N,
        N
    ),
    dtype=float
)


total_pairs = (
    N * (N - 1)
    // 2
)


processed_pairs = 0
calculated_pairs = 0
reused_name_pairs = 0
reused_hash_pairs = 0
identical_pairs = 0

# ブロック進捗管理
current_block = None
last_drawn_block = None

UPDATE_LINES = GROUP_COUNT + 2

print()
print("Updating Wasserstein distance matrix...")

print(render_block_progress(None))
print("Progress: 0/0", end="", flush=True)


for i in range(N):
        
    gi = file_to_group[i]

    name_i = current_files[i][
        "relative_name"
    ]

    hash_i = current_files[i][
        "sha256"
    ]


    for j in range(
        i + 1,
        N
    ):
        gj = file_to_group[j]

        block = (gi, gj)
        current_block = block

        name_j = current_files[j][
            "relative_name"
        ]

        hash_j = current_files[j][
            "sha256"
        ]


        # ------------------------------------------
        # 1. ファイル名による既存キャッシュ
        #
        # ★旧コードとの互換性
        # ------------------------------------------

        key1 = (
            name_i,
            name_j
        )

        key2 = (
            name_j,
            name_i
        )


        old_sha_i = old_sha256_cache.get(name_i)
        old_sha_j = old_sha256_cache.get(name_j)

        if (
            key1 in distance_cache_by_name
            and old_sha_i == hash_i
            and old_sha_j == hash_j
        ):

            dist = distance_cache_by_name[key1]
            reused_name_pairs += 1

        elif (
            key2 in distance_cache_by_name
            and old_sha_i == hash_i
            and old_sha_j == hash_j
        ):

            dist = distance_cache_by_name[key2]
            reused_name_pairs += 1


        # ------------------------------------------
        # 2. SHA-256による既存キャッシュ
        #
        # ファイル名が変更されても
        # 同一内容なら距離を再利用できる。
        # ------------------------------------------

        elif (
            hash_i,
            hash_j
        ) in distance_cache_by_hash:

            dist = distance_cache_by_hash[
                (
                    hash_i,
                    hash_j
                )
            ]

            reused_hash_pairs += 1


        elif (
            hash_j,
            hash_i
        ) in distance_cache_by_hash:

            dist = distance_cache_by_hash[
                (
                    hash_j,
                    hash_i
                )
            ]

            reused_hash_pairs += 1


        # ------------------------------------------
        # 3. ファイル内容が完全に同じ
        #
        # 同一SHA-256なら同一バイナリなので、
        # 同じWAVである。
        #
        # → 距離は0
        # ------------------------------------------

        elif hash_i == hash_j:

            dist = 0.0

            identical_pairs += 1


        # ------------------------------------------
        # 4. 新規計算
        # ------------------------------------------

        else:

            if WASSERSTEIN_MODE.endswith("L1"):

                dist = wasserstein_distance_quantile(
                    quantiles[i],
                    quantiles[j],
                    order=1,
                    du=du
                )

            elif WASSERSTEIN_MODE.endswith("L2"):

                dist = wasserstein_distance_quantile(
                    quantiles[i],
                    quantiles[j],
                    order=2,
                    du=du
                )

            else:

                raise ValueError(
                    WASSERSTEIN_MODE
                )

            calculated_pairs += 1


        D[i, j] = dist
        D[j, i] = dist


        processed_pairs += 1

        block_done_pairs[block] += 1


        # 初回だけ表示領域を作る
        # ブロックが切り替わった時だけ表を書き換える
        if current_block != last_drawn_block:

            # Progress 行から表の先頭へ戻る
            print(f"\033[{UPDATE_LINES}F", end="")

            # 表だけ上書き
            for line in render_block_progress(current_block).splitlines():
                print("\r\033[2K" + line)

            last_drawn_block = current_block

        # Progressだけ同じ行で更新
        print(
            "\r"
            f"Progress: {processed_pairs}/{total_pairs} pairs "
            f"| new:{calculated_pairs} "
            f"| name:{reused_name_pairs} "
            f"| hash:{reused_hash_pairs} "
            f"| identical:{identical_pairs}",
            end="",
            flush=True
        )

print()

print(
    "Reused by filename  =",
    reused_name_pairs
)

print(
    "Reused by SHA-256   =",
    reused_hash_pairs
)

print(
    "Identical files     =",
    identical_pairs
)

print(
    "Calculated pairs    =",
    calculated_pairs
)

print(
    "Processed pairs     =",
    processed_pairs
)

print(
    "Total pairs         =",
    total_pairs
)


# ==================================================
# Raw距離行列保存
#
# index / columnsも
# TARGET_DIRS順を維持する。
# ==================================================

df_raw = pd.DataFrame(
    D,
    index=current_names,
    columns=current_names
)


df_raw.to_csv(
    RAW_CSV
)


np.save(
    RAW_NPY,
    D
)


print()
print(
    "Saved raw distance matrix:"
)

print(
    RAW_CSV
)


# ==================================================
# 正規化距離行列
# ==================================================

if NORMALIZE_DISTANCE_MATRIX:

    print()
    print(
        "Applying min-max normalization..."
    )


    d_min = D.min()
    d_max = D.max()


    if (
        d_max - d_min
        > 0
    ):

        D_normalized = (
            D - d_min
        ) / (
            d_max - d_min
        )

    else:

        D_normalized = (
            D.copy()
        )


    df_normalized = pd.DataFrame(
        D_normalized,
        index=current_names,
        columns=current_names
    )


    df_normalized.to_csv(
        NORMALIZED_CSV
    )


    np.save(
        NORMALIZED_NPY,
        D_normalized
    )


    print(
        "Saved normalized "
        "distance matrix:"
    )

    print(
        NORMALIZED_CSV
    )


# ==================================================
# 完了
# ==================================================

print()
print(
    "=========================================="
)

print(
    "Code 0 completed."
)

print(
    "Files:",
    N
)

print(
    "Groups:",
    len(group_info)
)

print(
    "New files:",
    len(new_names)
)

print(
    "Removed files:",
    len(removed_names)
)

print(
    "Renamed files:",
    len(renamed_files)
)

print(
    "Spectrum calculated:",
    spectrum_calculated
)

print(
    "Distance calculated:",
    calculated_pairs
)

print(
    "Distance reused by filename:",
    reused_name_pairs
)

print(
    "Distance reused by SHA-256:",
    reused_hash_pairs
)

print(
    "SHA-256 cache:"
)

print(
    SHA256_CACHE_JSON
)

print(
    "Display groups JSON:"
)

print(
    DISPLAY_GROUPS_JSON
)

print(
    "=========================================="
)
