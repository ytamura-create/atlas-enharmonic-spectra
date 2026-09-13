import os
import json
import csv
import hashlib

import numpy as np
import pandas as pd
import librosa


# ==================================================
# 設定
# ==================================================

ROOT_DIR = os.path.expanduser("./wav/")

TARGET_SR = 96000

WASSERSTEIN_MODE = "L1"

OUT_DIR = f"./distanceMatrix_{WASSERSTEIN_MODE}"

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
    "basstrb_mute-harmonNOstemOPENED",
    "basstrb_mute-harmonNOstemCLOSED",
    "basstrb_mute-harmonStemmedOPENED",
    "basstrb_mute-harmonStemmedCLOSED",
    "basstrb_mute-bucket",
    "basstrb_tube-F",
    "basstrb_tube-F_mute-straightMetal",
    "basstrb_tube-F_mute-bucket",
    "basstrb_tube-Ges",
    "basstrb_tube-D",
    "va",
    "gauss_sigma-002.5%"
]

KEYWORD = ""

NORMALIZE_DISTANCE_MATRIX = False

REBUILD_CACHE = True

DISPLAY_GROUPS_JSON = os.path.join(
    OUT_DIR,
    "display_groups.json"
)


# ==================================================
# RAM対策設定
# ==================================================

# 距離行列をRAMに置かずmemmapで扱う
USE_MEMMAP = True

# --------------------------------------------------
# Wasserstein計算用の周波数方向チャンクサイズ
#
# 1回にこの本数の周波数binだけ処理する。
#
# 小さくするとRAM使用量は減るが遅くなる。
# 大きくすると速くなるがRAM使用量が増える。
# --------------------------------------------------

CDF_CHUNK_SIZE = 16384

# --------------------------------------------------
# 距離計算時に一度に保持するCDF本数
#
# 1本あたり、524289 bin × float64 ≈ 4 MB。
# 16本なら約67 MBなので、WSLで安全側に寄せる。
# --------------------------------------------------
CDF_BLOCK_SIZE = 16

# --------------------------------------------------
# REBUILD_CACHE=False の差分計算で、今回新規に追加された
# ファイルのCDFをRAMに保持する上限。
#
# 新規ファイルが少ない場合は、ここにあるCDFを全距離計算で
# 使い回す。これにより、例えばEを1本追加した場合、
# A-E, B-E, C-E, ... でCDF(E)を作り直さない。
# --------------------------------------------------
NEW_CDF_CACHE_MAX_MB = 512


# ==================================================
# 出力ファイル
# ==================================================

os.makedirs(OUT_DIR, exist_ok=True)

ROOT_DIR_ABS = os.path.abspath(ROOT_DIR)
OUT_DIR_ABS = os.path.abspath(OUT_DIR)


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

SHA256_CACHE_JSON = os.path.join(
    OUT_DIR,
    "sha256_cache.json"
)

OLD_CSV_MEMMAP = os.path.join(
    OUT_DIR,
    "_old_distance_matrix_from_csv.npy"
)

RAW_TMP_NPY = os.path.join(
    OUT_DIR,
    "_distance_matrix_raw_work.npy"
)


# ==================================================
# パス判定
# ==================================================

def is_path_inside(path, directory):

    path = os.path.abspath(path)
    directory = os.path.abspath(directory)

    try:

        return (
            os.path.commonpath(
                [path, directory]
            )
            == directory
        )

    except ValueError:

        return False


# ==================================================
# SHA256
# ==================================================

def compute_sha256(
    file_path,
    chunk_size=1024 * 1024
):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        while True:

            chunk = f.read(
                chunk_size
            )

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ==================================================
# relative_name 正規化
# ==================================================

def normalize_relative_name(name):

    name = str(name).replace(
        "\\",
        "/"
    )

    while name.startswith("./"):

        name = name[2:]

    name = name.lstrip("/")

    root_prefix = (
        ROOT_DIR_ABS
        .replace("\\", "/")
        .rstrip("/")
        + "/"
    )

    out_prefix = (
        OUT_DIR_ABS
        .replace("\\", "/")
        .rstrip("/")
        + "/"
    )

    if name.startswith(root_prefix):

        name = name[
            len(root_prefix):
        ]

    if name.startswith(out_prefix):

        name = name[
            len(out_prefix):
        ]

    return name


# ==================================================
# Wasserstein mode解析
# ==================================================

def parse_wasserstein_mode(mode):

    mode_lower = mode.lower()

    if "2" in mode_lower:

        order = 2

    else:

        order = 1

    if mode_lower.startswith("lb"):

        use_log_axis = True

    else:

        use_log_axis = False

    return order, use_log_axis


WASSERSTEIN_ORDER, USE_LOG_AXIS = (
    parse_wasserstein_mode(
        WASSERSTEIN_MODE
    )
)


# ==================================================
# スペクトル計算
# ==================================================

def compute_spectrum_distribution(
    file_path
):

    y, sr = librosa.load(
        file_path,
        sr=None
    )

    if sr != TARGET_SR:

        y = librosa.resample(
            y,
            orig_sr=sr,
            target_sr=TARGET_SR
        )

        sr = TARGET_SR

    spectrum = np.abs(
        np.fft.rfft(y)
    )

    spectrum += 1e-12

    total = np.sum(
        spectrum,
        dtype=np.float64
    )

    spectrum /= total

    return spectrum


# ==================================================
# 1次元 Wasserstein距離
#
# CDF方式
#
# W1(p,q)
#   = integral |CDF_p(x) - CDF_q(x)| dx
#
# quantileは一切使わない。
#
# さらに、巨大なCDF配列を作らないため、
# 周波数軸をチャンクごとに処理する。
# ==================================================

def wasserstein_distance_cdf(
    spectrum1,
    spectrum2,
    df,
    chunk_size=CDF_CHUNK_SIZE
):

    n = min(
        len(spectrum1),
        len(spectrum2)
    )

    cumulative1 = 0.0
    cumulative2 = 0.0
    distance = 0.0

    for start in range(0, n, chunk_size):

        end = min(
            start + chunk_size,
            n
        )

        s1 = np.asarray(
            spectrum1[start:end],
            dtype=np.float64
        )
        s2 = np.asarray(
            spectrum2[start:end],
            dtype=np.float64
        )

        cdf1 = cumulative1 + np.cumsum(
            s1,
            dtype=np.float64
        )
        cdf2 = cumulative2 + np.cumsum(
            s2,
            dtype=np.float64
        )

        if WASSERSTEIN_ORDER == 1:
            distance += np.sum(
                np.abs(cdf1 - cdf2),
                dtype=np.float64
            ) * df
        elif WASSERSTEIN_ORDER == 2:
            distance += np.sum(
                (cdf1 - cdf2) ** 2,
                dtype=np.float64
            ) * df
        else:
            raise ValueError(
                "Wasserstein order must be 1 or 2."
            )

        cumulative1 = float(cdf1[-1])
        cumulative2 = float(cdf2[-1])

        del s1, s2, cdf1, cdf2

    if WASSERSTEIN_ORDER == 1:
        return float(distance)

    return float(np.sqrt(distance))


def make_cdf_block(
    spectra,
    indices
):
    """
    spectraの指定indicesについてCDFを一度だけ作る。

    返り値は shape=(len(indices), spectrum_length) のfloat64配列。
    全1532本を保持せず、最大CDF_BLOCK_SIZE本だけを一時保持する。
    """

    count = len(indices)

    if count == 0:
        return np.empty(
            (0, spectra.shape[1]),
            dtype=np.float64
        )

    cdf_block = np.empty(
        (count, spectra.shape[1]),
        dtype=np.float64
    )

    for local_i, global_i in enumerate(indices):

        row = np.asarray(
            spectra[global_i, :],
            dtype=np.float64
        )

        np.cumsum(
            row,
            dtype=np.float64,
            out=cdf_block[local_i]
        )

        del row

    return cdf_block


def wasserstein_distance_from_cdf(
    cdf1,
    cdf2,
    df,
    chunk_size=CDF_CHUNK_SIZE
):
    """既に作成済みのCDF同士からWasserstein距離を計算する。"""

    n = min(
        len(cdf1),
        len(cdf2)
    )

    distance = 0.0

    for start in range(0, n, chunk_size):

        end = min(
            start + chunk_size,
            n
        )

        a = cdf1[start:end]
        b = cdf2[start:end]

        if WASSERSTEIN_ORDER == 1:
            distance += np.sum(
                np.abs(a - b),
                dtype=np.float64
            ) * df
        elif WASSERSTEIN_ORDER == 2:
            distance += np.sum(
                (a - b) ** 2,
                dtype=np.float64
            ) * df
        else:
            raise ValueError(
                "Wasserstein order must be 1 or 2."
            )

    if WASSERSTEIN_ORDER == 1:
        return float(distance)

    return float(np.sqrt(distance))


# ==================================================
# WAVファイル探索
# ==================================================

current_files = []

for group_index, group_name in enumerate(
    TARGET_DIRS
):

    group_dir = os.path.join(
        ROOT_DIR,
        group_name
    )

    if not os.path.isdir(
        group_dir
    ):

        print(
            f"WARNING: directory not found: "
            f"{group_dir}"
        )

        continue

    filenames = sorted(
        filename
        for filename in os.listdir(
            group_dir
        )
        if filename.lower().endswith(
            ".wav"
        )
    )

    for filename in filenames:

        file_path = os.path.join(
            group_dir,
            filename
        )

        if is_path_inside(
            file_path,
            OUT_DIR_ABS
        ):

            continue

        if KEYWORD and KEYWORD not in filename:

            continue

        relative_name = (
            f"{group_name}/{filename}"
        )

        current_files.append(
            {
                "group_name": group_name,
                "filename": filename,
                "relative_name": relative_name,
                "path": file_path
            }
        )


if len(current_files) == 0:

    raise RuntimeError(
        "No WAV files were found."
    )


print()
print(
    f"Current WAV files: "
    f"{len(current_files)}"
)


# ==================================================
# 現在のファイル名
# ==================================================

current_names = [
    item["relative_name"]
    for item in current_files
]

current_name_to_index = {
    name: i
    for i, name in enumerate(
        current_names
    )
}


# ==================================================
# 以前の file_info.csv
# ==================================================

old_file_info_names = []

if (
    not REBUILD_CACHE
    and os.path.exists(
        FILE_INFO_CSV
    )
):

    try:

        old_file_info_df = pd.read_csv(
            FILE_INFO_CSV,
            usecols=["relative_name"]
        )

        old_file_info_names = [
            normalize_relative_name(
                name
            )
            for name in
            old_file_info_df[
                "relative_name"
            ].astype(str)
        ]

    except Exception as e:

        print(
            "WARNING: failed to read old "
            f"file_info.csv: {e}"
        )

        old_file_info_names = []


old_name_to_index = {
    name: i
    for i, name in enumerate(
        old_file_info_names
    )
}


# ==================================================
# SHA256キャッシュ読み込み
# ==================================================

old_sha256_cache = {}

if (
    not REBUILD_CACHE
    and os.path.exists(
        SHA256_CACHE_JSON
    )
):

    try:

        with open(
            SHA256_CACHE_JSON,
            "r",
            encoding="utf-8"
        ) as f:

            old_sha256_cache = json.load(f)

        old_sha256_cache = {
            normalize_relative_name(k): v
            for k, v in
            old_sha256_cache.items()
        }

    except Exception as e:

        print(
            "WARNING: failed to read "
            f"sha256_cache.json: {e}"
        )

        old_sha256_cache = {}


# ==================================================
# 現在のSHA256
# ==================================================

print()
print(
    "Calculating SHA256..."
)

current_sha256 = {}

for i, item in enumerate(
    current_files
):

    name = item["relative_name"]

    current_sha256[name] = (
        compute_sha256(
            item["path"]
        )
    )

    if (
        (i + 1) % 50 == 0
        or i + 1 == len(current_files)
    ):

        print(
            f"\r  SHA256: "
            f"{i + 1}/{len(current_files)}",
            end="",
            flush=True
        )

print()


# ==================================================
# 新規・削除・既存
# ==================================================

old_names_set = set(
    old_file_info_names
)

current_names_set = set(
    current_names
)

new_names = sorted(
    current_names_set
    - old_names_set
)

removed_names = sorted(
    old_names_set
    - current_names_set
)

existing_names = sorted(
    current_names_set
    & old_names_set
)


print()
print(
    f"New files     : "
    f"{len(new_names)}"
)

print(
    f"Removed files : "
    f"{len(removed_names)}"
)

print(
    f"Existing files: "
    f"{len(existing_names)}"
)


# ==================================================
# SHA256によるrename検出
# ==================================================

old_hash_to_names = {}

for name, sha256 in (
    old_sha256_cache.items()
):

    old_hash_to_names.setdefault(
        sha256,
        []
    ).append(name)


renamed_pairs = []

for name in new_names:

    sha256 = current_sha256.get(
        name
    )

    if sha256 is None:
        continue

    candidates = (
        old_hash_to_names.get(
            sha256,
            []
        )
    )

    for old_name in candidates:

        if old_name in old_names_set:

            renamed_pairs.append(
                (
                    old_name,
                    name
                )
            )

            break


if renamed_pairs:

    print()
    print(
        "Detected renamed files:"
    )

    for old_name, new_name in (
        renamed_pairs
    ):

        print(
            f"  {old_name} -> {new_name}"
        )


# ==================================================
# 旧spectra.npyをmemmapで読む
# ==================================================

old_spectra = None
old_spectra_names = []

if (
    not REBUILD_CACHE
    and os.path.exists(
        SPECTRA_NPY
    )
):

    try:

        old_spectra = np.load(
            SPECTRA_NPY,
            mmap_mode="r"
        )

        old_spectra_names = list(
            old_file_info_names
        )

        if (
            old_spectra.ndim != 2
            or old_spectra.shape[0]
            != len(old_spectra_names)
        ):

            print(
                "WARNING: spectra.npy and "
                "file_info.csv size mismatch."
            )

            old_spectra = None
            old_spectra_names = []

        else:

            print()
            print(
                "Loaded old spectra as "
                "memory-mapped array:"
            )

            print(
                f"  shape = "
                f"{old_spectra.shape}"
            )

    except Exception as e:

        print(
            "WARNING: failed to load old "
            f"spectra.npy: {e}"
        )

        old_spectra = None
        old_spectra_names = []


# ==================================================
# 旧spectraのhash -> index
# ==================================================

old_spectrum_hash_to_index = {}

if old_spectra is not None:

    for i, name in enumerate(
        old_spectra_names
    ):

        sha256 = old_sha256_cache.get(
            name
        )

        if sha256 is None:
            continue

        if (
            sha256
            not in old_spectrum_hash_to_index
        ):

            old_spectrum_hash_to_index[
                sha256
            ] = i


# ==================================================
# スペクトルキャッシュ準備
#
# 重要:
#
# 以前:
#
# computed_spectrum_cache[i] = spectrum
#
# として全新規スペクトルをRAMに保存していた。
#
# 今回は絶対に保存しない。
#
# 新規スペクトルは、
#
#   1本計算
#   ↓
#   spectra.npyへ書く
#   ↓
#   Python変数を解放
#
# とする。
# ==================================================

N = len(
    current_files
)

print()
print(
    "Preparing spectra cache..."
)


spectrum_sources = []

new_spectrum_count = 0
reused_spectrum_count = 0


for i, item in enumerate(
    current_files
):

    name = item["relative_name"]

    sha256 = current_sha256[name]

    source = None

    # --------------------------------------------------
    # 1. 同じファイル名 + SHA一致
    # --------------------------------------------------

    if (
        old_spectra is not None
        and name in old_name_to_index
        and name in old_sha256_cache
        and old_sha256_cache[name]
        == sha256
    ):

        old_i = old_name_to_index[
            name
        ]

        if (
            old_i
            < old_spectra.shape[0]
        ):

            source = (
                "old_index",
                old_i
            )

    # --------------------------------------------------
    # 2. SHA一致によるrename再利用
    # --------------------------------------------------

    if source is None:

        old_i = (
            old_spectrum_hash_to_index.get(
                sha256
            )
        )

        if old_i is not None:

            source = (
                "old_index",
                old_i
            )

    # --------------------------------------------------
    # 3. 新規計算
    # --------------------------------------------------

    if source is None:

        source = (
            "compute",
            None
        )

        new_spectrum_count += 1

    else:

        reused_spectrum_count += 1

    spectrum_sources.append(
        source
    )


print(
    f"  Reused spectra: "
    f"{reused_spectrum_count}"
)

print(
    f"  New spectra   : "
    f"{new_spectrum_count}"
)


# ==================================================
# スペクトル長を決める
#
# 新規スペクトルを全部保存しない。
# 最初の1本だけ計算して長さを確認する。
# ==================================================

old_spectrum_length = None

if old_spectra is not None:

    old_spectrum_length = (
        old_spectra.shape[1]
    )


min_len = old_spectrum_length


if min_len is None:

    min_len = None


for i, item in enumerate(
    current_files
):

    source_type, source_index = (
        spectrum_sources[i]
    )

    if source_type == "compute":

        spectrum = (
            compute_spectrum_distribution(
                item["path"]
            )
        )

        spectrum_length = len(
            spectrum
        )

        if min_len is None:

            min_len = spectrum_length

        else:

            min_len = min(
                min_len,
                spectrum_length
            )

        # ------------------------------------------
        # 最初の新規スペクトル長が分かった時点で
        # 目的を達成しているので終了。
        #
        # 全ファイルを計算しない。
        # ------------------------------------------

        del spectrum

        break


if min_len is None:

    raise RuntimeError(
        "Could not determine spectrum length."
    )


print()
print(
    f"Spectrum length: "
    f"{min_len}"
)


# ==================================================
# spectra.npy作成
# ==================================================

if os.path.exists(
    SPECTRA_NPY
):

    try:

        os.remove(
            SPECTRA_NPY
        )

    except PermissionError:

        raise RuntimeError(
            "Could not overwrite spectra.npy. "
            "Please close any program using it."
        )


spectra = np.lib.format.open_memmap(
    SPECTRA_NPY,
    mode="w+",
    dtype=np.float32,
    shape=(
        N,
        min_len
    )
)


print()
print(
    "Writing spectra.npy..."
)


for i, item in enumerate(
    current_files
):

    source_type, source_index = (
        spectrum_sources[i]
    )

    if source_type == "old_index":

        spectrum = old_spectra[
            source_index,
            :min_len
        ]

        spectra[i, :] = spectrum

    else:

        # ------------------------------------------
        # 新規スペクトルはここで1本だけ計算。
        # 書き込んだら保持しない。
        # ------------------------------------------

        spectrum = (
            compute_spectrum_distribution(
                item["path"]
            )
        )

        spectra[i, :] = spectrum[
            :min_len
        ]

        del spectrum

    if (
        (i + 1) % 20 == 0
        or i + 1 == N
    ):

        print(
            f"\r  spectra: "
            f"{i + 1}/{N}",
            end="",
            flush=True
        )

print()


spectra.flush()


# ==================================================
# 古いspectraを解放
# ==================================================

old_spectra = None


# ==================================================
# 周波数軸
# ==================================================

freqs = np.linspace(
    0,
    TARGET_SR / 2,
    min_len,
    dtype=np.float64
)

np.save(
    FREQS_NPY,
    freqs
)


# ==================================================
# コスト軸
# ==================================================
#
# CDF方式でも、距離を積分する軸は必要。
#
# 線形周波数:
#
#   df = freqs[k+1] - freqs[k]
#
# log軸を使う場合:
#
#   x = log(f + 1)
#
# として積分する。
# ==================================================

if USE_LOG_AXIS:

    cost_axis = np.log(
        freqs + 1.0
    )

else:

    cost_axis = freqs


if min_len > 1:

    df = float(
        cost_axis[1]
        - cost_axis[0]
    )

else:

    df = 1.0


# ==================================================
# SHA256 cache保存
# ==================================================

with open(
    SHA256_CACHE_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        current_sha256,
        f,
        ensure_ascii=False,
        indent=2
    )


# ==================================================
# file_info / group_info
# ==================================================

file_info_rows = []

for i, item in enumerate(
    current_files
):

    file_info_rows.append(
        {
            "index": i,
            "group_index": -1,
            "group_name": item[
                "group_name"
            ],
            "filename": item[
                "filename"
            ],
            "relative_name": item[
                "relative_name"
            ],
            "path": item[
                "path"
            ]
        }
    )


group_info_rows = []

for group_index, group_name in enumerate(
    TARGET_DIRS
):

    indices = [
        i
        for i, item in enumerate(
            current_files
        )
        if item["group_name"]
        == group_name
    ]

    if not indices:

        continue

    start = min(
        indices
    )

    end = max(
        indices
    )

    size = len(
        indices
    )

    group_info_rows.append(
        {
            "group_index": group_index,
            "group_name": group_name,
            "size": size,
            "start": start,
            "end": end
        }
    )

    for i in indices:

        file_info_rows[i][
            "group_index"
        ] = group_index


file_info_df = pd.DataFrame(
    file_info_rows
)

group_info_df = pd.DataFrame(
    group_info_rows
)


file_info_df.to_csv(
    FILE_INFO_CSV,
    index=False
)

group_info_df.to_csv(
    GROUP_INFO_CSV,
    index=False
)


# ==================================================
# グループ情報
# ==================================================

file_to_group = np.full(
    N,
    -1,
    dtype=np.int32
)

group_starts = []
group_sizes = []

for row in group_info_rows:

    group_index = row[
        "group_index"
    ]

    start = row[
        "start"
    ]

    size = row[
        "size"
    ]

    group_starts.append(
        start
    )

    group_sizes.append(
        size
    )

    file_to_group[
        start:start + size
    ] = group_index


GROUP_COUNT = len(
    group_info_rows
)


# ==================================================
# display_groups.json
# ==================================================

if not os.path.exists(
    DISPLAY_GROUPS_JSON
):

    display_groups = []

    for row in group_info_rows:

        display_groups.append(
            {
                "group_name": row[
                    "group_name"
                ],
                "group_index": row[
                    "group_index"
                ]
            }
        )

    with open(
        DISPLAY_GROUPS_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            display_groups,
            f,
            ensure_ascii=False,
            indent=2
        )

else:

    try:

        with open(
            DISPLAY_GROUPS_JSON,
            "r",
            encoding="utf-8"
        ) as f:

            display_groups = json.load(
                f
            )

    except Exception as e:

        print(
            "WARNING: failed to read "
            f"display_groups.json: {e}"
        )

        display_groups = []


# ==================================================
# 旧距離行列
# ==================================================

old_D = None
old_D_names = []


def read_csv_names_only(
    csv_path
):

    if not os.path.exists(
        csv_path
    ):

        return []

    try:

        df_names = pd.read_csv(
            csv_path,
            usecols=[0]
        )

        return [
            normalize_relative_name(
                name
            )
            for name in
            df_names.iloc[
                :,
                0
            ].astype(str)
        ]

    except Exception as e:

        print(
            "WARNING: failed to read distance "
            f"CSV names: {e}"
        )

        return []


def get_csv_column_count(
    csv_path
):

    try:

        with open(
            csv_path,
            "r",
            encoding="utf-8",
            newline=""
        ) as f:

            reader = csv.reader(
                f
            )

            header = next(
                reader
            )

        return len(
            header
        ) - 1

    except Exception:

        return -1


# ==================================================
# 旧CSVの名前だけ取得
# ==================================================

if (
    not REBUILD_CACHE
    and os.path.exists(
        RAW_CSV
    )
):

    old_D_names = (
        read_csv_names_only(
            RAW_CSV
        )
    )


# ==================================================
# 旧NPYをmemmapで読む
# ==================================================

if (
    not REBUILD_CACHE
    and os.path.exists(
        RAW_NPY
    )
):

    try:

        candidate_D = np.load(
            RAW_NPY,
            mmap_mode="r"
        )

        if (
            candidate_D.ndim == 2
            and candidate_D.shape[0]
            == candidate_D.shape[1]
            and candidate_D.shape[0]
            == len(old_D_names)
        ):

            old_D = candidate_D

            print()
            print(
                "Loaded old distance matrix "
                "as memory-mapped array:"
            )

            print(
                f"  shape = "
                f"{old_D.shape}"
            )

        else:

            print()
            print(
                "WARNING: cached NPY matrix "
                "size mismatch:"
            )

            print(
                f"  matrix = "
                f"{candidate_D.shape}"
            )

            print(
                f"  names  = "
                f"{len(old_D_names)}"
            )

            old_D = None

    except Exception as e:

        print()
        print(
            "WARNING: failed to load "
            f"distance_matrix_raw.npy: {e}"
        )

        old_D = None


# ==================================================
# CSVしかない場合
# ==================================================

if (
    not REBUILD_CACHE
    and old_D is None
    and os.path.exists(
        RAW_CSV
    )
    and len(old_D_names) > 0
):

    csv_size = get_csv_column_count(
        RAW_CSV
    )

    if csv_size == len(
        old_D_names
    ):

        print()
        print(
            "Converting cached CSV distance "
            "matrix to disk-backed NPY..."
        )

        if os.path.exists(
            OLD_CSV_MEMMAP
        ):

            try:

                os.remove(
                    OLD_CSV_MEMMAP
                )

            except PermissionError:

                pass

        csv_D = np.lib.format.open_memmap(
            OLD_CSV_MEMMAP,
            mode="w+",
            dtype=np.float64,
            shape=(
                csv_size,
                csv_size
            )
        )

        with open(
            RAW_CSV,
            "r",
            encoding="utf-8",
            newline=""
        ) as f:

            reader = csv.reader(
                f
            )

            header = next(
                reader
            )

            for i, row in enumerate(
                reader
            ):

                if len(row) != (
                    csv_size + 1
                ):

                    raise RuntimeError(
                        "Malformed distance CSV at "
                        f"row {i + 1}: "
                        f"expected "
                        f"{csv_size + 1} "
                        f"columns, got "
                        f"{len(row)}"
                    )

                csv_D[i, :] = (
                    np.asarray(
                        row[1:],
                        dtype=np.float64
                    )
                )

                if (
                    (i + 1) % 20 == 0
                    or i + 1 == csv_size
                ):

                    print(
                        f"\r  CSV -> NPY: "
                        f"{i + 1}/{csv_size}",
                        end="",
                        flush=True
                    )

        print()

        csv_D.flush()

        old_D = np.load(
            OLD_CSV_MEMMAP,
            mmap_mode="r"
        )

        print(
            "Using CSV-derived disk-backed "
            "distance matrix."
        )

    else:

        print()
        print(
            "WARNING: old distance CSV is "
            "not internally square."
        )

        print(
            f"  CSV columns = "
            f"{csv_size}"
        )

        print(
            f"  CSV names   = "
            f"{len(old_D_names)}"
        )


# ==================================================
# 距離キャッシュindex
# ==================================================

old_distance_name_to_index = {}

if old_D is not None:

    old_distance_name_to_index = {
        name: i
        for i, name in enumerate(
            old_D_names
        )
    }


old_distance_hash_to_index = {}

if old_D is not None:

    for i, name in enumerate(
        old_D_names
    ):

        sha256 = old_sha256_cache.get(
            name
        )

        if sha256 is None:

            continue

        if (
            sha256
            not in old_distance_hash_to_index
        ):

            old_distance_hash_to_index[
                sha256
            ] = i


# ==================================================
# 距離行列作成
# ==================================================

if os.path.exists(
    RAW_NPY
):

    if REBUILD_CACHE:

        try:

            os.remove(
                RAW_NPY
            )

        except PermissionError:

            raise RuntimeError(
                "Could not remove existing "
                "distance_matrix_raw.npy."
            )


if os.path.exists(
    RAW_TMP_NPY
):

    try:

        os.remove(
            RAW_TMP_NPY
        )

    except PermissionError:

        raise RuntimeError(
            "Could not remove temporary "
            "distance matrix."
        )


D = np.lib.format.open_memmap(
    RAW_TMP_NPY,
    mode="w+",
    dtype=np.float64,
    shape=(
        N,
        N
    )
)


D[:, :] = 0.0


# ==================================================
# 進捗表示
# ==================================================

block_total_pairs = {}

block_done_pairs = {}

for gi in range(
    GROUP_COUNT
):

    for gj in range(
        gi,
        GROUP_COUNT
    ):

        size_i = group_sizes[
            gi
        ]

        size_j = group_sizes[
            gj
        ]

        if gi == gj:

            pair_count = (
                size_i
                * (size_i - 1)
            ) // 2

        else:

            pair_count = (
                size_i
                * size_j
            )

        key = (
            gi,
            gj
        )

        block_total_pairs[
            key
        ] = pair_count

        block_done_pairs[
            key
        ] = 0


def progress_symbol(
    done,
    total
):

    if total <= 0:

        return ""

    ratio = (
        done / total
    )

    width = 20

    filled = int(
        ratio * width
    )

    if filled > width:

        filled = width

    return (
        "["
        + "#" * filled
        + "-" * (
            width - filled
        )
        + "]"
    )


def render_block_progress(
    gi,
    gj
):

    key = (
        gi,
        gj
    )

    done = block_done_pairs[
        key
    ]

    total = block_total_pairs[
        key
    ]

    print(
        f"\r"
        f"block ({gi},{gj}) "
        f"{progress_symbol(done, total)} "
        f"{done}/{total}",
        end="",
        flush=True
    )


# ==================================================
# 距離計算
# ==================================================

cache_hit_name = 0
cache_hit_hash = 0
zero_distance_count = 0
new_distance_count = 0

print()
print(
    "Calculating distance matrix..."
)


# ==================================================
# 距離キャッシュ検索
# ==================================================

def get_cached_distance(
    i,
    j,
    name_i,
    name_j,
    sha_i,
    sha_j
):
    """
    既存距離を探す。

    優先順位:
      1. 名前 + SHA一致
      2. SHAによるrename再利用
      3. 同一SHAなら0
      4. None = 新規計算
    """

    global cache_hit_name
    global cache_hit_hash
    global zero_distance_count

    if old_D is not None:

        old_i = old_distance_name_to_index.get(
            name_i
        )
        old_j = old_distance_name_to_index.get(
            name_j
        )

        if old_i is not None and old_j is not None:

            old_sha_i = old_sha256_cache.get(
                name_i
            )
            old_sha_j = old_sha256_cache.get(
                name_j
            )

            if (
                old_sha_i is not None
                and old_sha_j is not None
                and old_sha_i == sha_i
                and old_sha_j == sha_j
            ):

                cache_hit_name += 1

                return float(
                    old_D[old_i, old_j]
                )

        old_i = old_distance_hash_to_index.get(
            sha_i
        )
        old_j = old_distance_hash_to_index.get(
            sha_j
        )

        if old_i is not None and old_j is not None:

            cache_hit_hash += 1

            return float(
                old_D[old_i, old_j]
            )

    if sha_i == sha_j:

        zero_distance_count += 1
        return 0.0

    return None


# ==================================================
# REBUILD_CACHE=False 用の新規CDFキャッシュ
# ==================================================
#
# ここが今回の重要な追加部分。
#
# 既存距離行列に対して新規ファイルを追加した場合、
# 新規ファイルのCDFは「列側」に回ったときにも再利用する。
#
# 例:
#
#   A B C D F が既存
#   E が新規
#
# CDF(E)を一度作ったら、
#
#   A-E, B-E, C-E, D-E, E-E, E-F
#
# の全てで同じCDF(E)を使う。
# ==================================================

new_cdf_cache = {}

if not REBUILD_CACHE and old_D is not None:

    new_indices = []

    for idx, name in enumerate(current_names):

        sha = current_sha256[name]

        # SHAが旧距離行列に存在しないものだけが、
        # 距離計算上の本当の新規ファイル。
        if old_distance_hash_to_index.get(sha) is None:
            new_indices.append(idx)

    if new_indices:

        bytes_per_cdf = (
            min_len * np.dtype(np.float64).itemsize
        )

        max_cdf_count = max(
            1,
            int(
                NEW_CDF_CACHE_MAX_MB
                * 1024
                * 1024
                // bytes_per_cdf
            )
        )

        cache_indices = new_indices[:max_cdf_count]

        print()
        print(
            "Preparing incremental CDF cache..."
        )
        print(
            f"  New distance files: {len(new_indices)}"
        )
        print(
            f"  CDFs kept in RAM  : {len(cache_indices)}"
        )
        print(
            f"  CDF cache limit   : {NEW_CDF_CACHE_MAX_MB} MB"
        )

        # CDFを1本ずつ作って保存する。
        # 一度に全新規CDFを生成することで巨大な一時配列を作らない。
        for count, idx in enumerate(cache_indices, 1):

            cdf = make_cdf_block(
                spectra,
                [idx]
            )[0]

            new_cdf_cache[idx] = cdf

            if (
                count % 10 == 0
                or count == len(cache_indices)
            ):

                print(
                    f"\r  new CDF cache: "
                    f"{count}/{len(cache_indices)}",
                    end="",
                    flush=True
                )

        print()

    else:

        print()
        print(
            "No new files requiring incremental CDF cache."
        )


# ==================================================
# ブロック内のCDF取得
# ==================================================

def get_cdf_for_indices(indices):
    """
    指定indicesについてCDFを作る。

    incremental cacheにあるindexは既存CDFを再利用する。
    それ以外はこのブロック用に一度だけ生成する。

    戻り値:
      cdf_block, cached_mask

    cached_mask=Trueの行はnew_cdf_cache由来であり、
    呼び出し側で解放してはいけない。
    """

    count = len(indices)
    spectrum_length = spectra.shape[1]

    cdf_block = np.empty(
        (count, spectrum_length),
        dtype=np.float64
    )

    cached_mask = np.zeros(
        count,
        dtype=bool
    )

    for local_i, global_i in enumerate(indices):

        cached = new_cdf_cache.get(
            int(global_i)
        )

        if cached is not None:

            cdf_block[local_i, :] = cached
            cached_mask[local_i] = True

        else:

            row = np.asarray(
                spectra[global_i, :],
                dtype=np.float64
            )

            np.cumsum(
                row,
                dtype=np.float64,
                out=cdf_block[local_i]
            )

            del row

    return cdf_block, cached_mask


# ==================================================
# ブロック間距離計算
# ==================================================
#
# iブロックのCDFを保持したまま、jブロックを順番に処理する。
#
#   i-block CDF
#       |
#       +-- j-block CDF -> 全ペア
#       +-- j-block CDF -> 全ペア
#       +-- j-block CDF -> 全ペア
#       ...
#
# したがって、同じi-blockについてi側CDFを作り直さない。
# さらにincremental CDF cacheに入った新規ファイルは、
# i/jのどちら側にいても実行中ずっと再利用される。
# ==================================================

def calculate_block_pair(
    gi,
    gj,
    start_i,
    end_i,
    start_j,
    end_j
):

    global new_distance_count

    key = (gi, gj)

    same_group = (
        gi == gj
    )

    # --------------------------------------------------
    # i方向をCDF_BLOCK_SIZEずつ処理。
    # 各iブロックのCDFは、そのiブロックに対する
    # 全jブロックの処理が終わるまで保持する。
    # --------------------------------------------------

    for block_i_start in range(
        start_i,
        end_i,
        CDF_BLOCK_SIZE
    ):

        block_i_end = min(
            block_i_start + CDF_BLOCK_SIZE,
            end_i
        )

        indices_i = np.arange(
            block_i_start,
            block_i_end,
            dtype=np.int64
        )

        # --------------------------------------------------
        # このiブロックについて、計算が必要なペアが
        # 少なくとも1つあるかを先に確認する。
        # 全てキャッシュ済みならCDFを一切作らない。
        # --------------------------------------------------

        cdf_i = None

        # i-block CDFを使うj-blockを順番に処理。
        for block_j_start in range(
            start_j,
            end_j,
            CDF_BLOCK_SIZE
        ):

            block_j_end = min(
                block_j_start + CDF_BLOCK_SIZE,
                end_j
            )

            indices_j = np.arange(
                block_j_start,
                block_j_end,
                dtype=np.int64
            )

            # --------------------------------------------------
            # このサブブロックで新規計算が必要なペアを列挙。
            # キャッシュ済み値はここでDへ書き込む。
            # --------------------------------------------------

            missing_pairs = []

            for local_i, i in enumerate(indices_i):

                i = int(i)
                name_i = current_names[i]
                sha_i = current_sha256[name_i]

                j_start = int(indices_j[0]) if len(indices_j) else 0

                for local_j, j in enumerate(indices_j):

                    j = int(j)

                    if same_group and j <= i:
                        continue

                    name_j = current_names[j]
                    sha_j = current_sha256[name_j]

                    value = get_cached_distance(
                        i,
                        j,
                        name_i,
                        name_j,
                        sha_i,
                        sha_j
                    )

                    if value is not None:

                        D[i, j] = value
                        D[j, i] = value
                        block_done_pairs[key] += 1

                    else:

                        missing_pairs.append(
                            (local_i, local_j, i, j)
                        )

            # --------------------------------------------------
            # 新規距離がなければCDFを作らず終了。
            # --------------------------------------------------

            if not missing_pairs:

                render_block_progress(gi, gj)
                del indices_j
                continue

            # --------------------------------------------------
            # i側CDFは最初に必要になった時だけ作る。
            # --------------------------------------------------

            if cdf_i is None:

                cdf_i, _ = get_cdf_for_indices(
                    indices_i
                )

            # --------------------------------------------------
            # j側CDFをこのj-blockについて一度だけ作る。
            # --------------------------------------------------

            # i-blockとj-blockが完全に同じ場合は、
            # cdf_iそのものを使う。
            same_cdf_block = (
                same_group
                and block_i_start == block_j_start
                and block_i_end == block_j_end
            )

            if same_cdf_block:

                cdf_j = cdf_i

            else:

                cdf_j, _ = get_cdf_for_indices(
                    indices_j
                )

            # --------------------------------------------------
            # CDF同士からmissing pairだけ計算。
            # 16×16×524289の巨大な3次元差分配列は作らない。
            # --------------------------------------------------

            for local_i, local_j, i, j in missing_pairs:

                value = wasserstein_distance_from_cdf(
                    cdf_i[local_i],
                    cdf_j[local_j],
                    df
                )

                D[i, j] = value
                D[j, i] = value

                new_distance_count += 1
                block_done_pairs[key] += 1

            # --------------------------------------------------
            # j側CDFはこのj-block終了時に破棄。
            # incremental cacheそのものは保持される。
            # --------------------------------------------------

            if not same_cdf_block:
                del cdf_j

            render_block_progress(gi, gj)

            del indices_j

        # --------------------------------------------------
        # このi-blockについて全j-blockが終わった。
        # ここで初めてi側CDFを破棄する。
        # --------------------------------------------------

        if cdf_i is not None:
            del cdf_i

        del indices_i

    render_block_progress(gi, gj)


# ==================================================
# 全group pair
# ==================================================

for gi in range(GROUP_COUNT):

    start_i = group_starts[gi]
    size_i = group_sizes[gi]
    end_i = start_i + size_i

    for gj in range(gi, GROUP_COUNT):

        start_j = group_starts[gj]
        size_j = group_sizes[gj]
        end_j = start_j + size_j

        key = (gi, gj)

        block_done_pairs[key] = 0

        calculate_block_pair(
            gi,
            gj,
            start_i,
            end_i,
            start_j,
            end_j
        )

        print()


# ==================================================
# 新規CDFキャッシュ解放
# ==================================================

new_cdf_cache.clear()

# ==================================================
# RAW NPY保存
# ==================================================

D.flush()


if os.path.exists(
    RAW_NPY
):

    try:

        os.remove(
            RAW_NPY
        )

    except PermissionError:

        raise RuntimeError(
            "Could not replace existing "
            "distance_matrix_raw.npy."
        )


os.replace(
    RAW_TMP_NPY,
    RAW_NPY
)


D = np.load(
    RAW_NPY,
    mmap_mode="r+"
)


# ==================================================
# RAW CSV
# ==================================================

print()
print(
    "Writing raw distance CSV..."
)


with open(
    RAW_CSV,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(
        f
    )

    writer.writerow(
        [""] + current_names
    )

    for i in range(
        N
    ):

        row = np.asarray(
            D[i, :],
            dtype=np.float64
        )

        writer.writerow(
            [current_names[i]]
            + row.tolist()
        )

        if (
            (i + 1) % 20 == 0
            or i + 1 == N
        ):

            print(
                f"\r  raw CSV: "
                f"{i + 1}/{N}",
                end="",
                flush=True
            )

print()


# ==================================================
# 正規化
# ==================================================

if NORMALIZE_DISTANCE_MATRIX:

    print()
    print(
        "Normalizing distance matrix..."
    )

    d_min = float(
        np.min(D)
    )

    d_max = float(
        np.max(D)
    )

    normalized_D = (
        np.lib.format.open_memmap(
            NORMALIZED_NPY,
            mode="w+",
            dtype=np.float64,
            shape=(
                N,
                N
            )
        )
    )

    if d_max == d_min:

        normalized_D[
            :, :
        ] = 0.0

    else:

        scale = (
            d_max - d_min
        )

        for i in range(
            N
        ):

            normalized_D[
                i, :
            ] = (
                D[i, :]
                - d_min
            ) / scale

            if (
                (i + 1) % 20 == 0
                or i + 1 == N
            ):

                print(
                    f"\r  normalize: "
                    f"{i + 1}/{N}",
                    end="",
                    flush=True
                )

        print()

    normalized_D.flush()

    # ----------------------------------------------
    # normalized CSV
    # ----------------------------------------------

    print()
    print(
        "Writing normalized distance CSV..."
    )

    with open(
        NORMALIZED_CSV,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.writer(
            f
        )

        writer.writerow(
            [""] + current_names
        )

        for i in range(
            N
        ):

            row = np.asarray(
                normalized_D[i, :],
                dtype=np.float64
            )

            writer.writerow(
                [current_names[i]]
                + row.tolist()
            )

            if (
                (i + 1) % 20 == 0
                or i + 1 == N
            ):

                print(
                    f"\r  normalized CSV: "
                    f"{i + 1}/{N}",
                    end="",
                    flush=True
                )

    print()

    del normalized_D


# ==================================================
# 不要になったmemmapを解放
# ==================================================

del D
del spectra


# ==================================================
# 完了表示
# ==================================================

print()
print(
    "=" * 60
)

print(
    "Completed."
)

print(
    "=" * 60
)

print(
    f"Files                 : {N}"
)

print(
    f"Spectrum bins         : {min_len}"
)

print(
    f"Wasserstein mode      : "
    f"{WASSERSTEIN_MODE}"
)

print(
    f"Distance method       : "
    f"CDF integral"
)

print(
    f"CDF chunk size        : "
    f"{CDF_CHUNK_SIZE}"
)

print(
    f"Cache hit (name)      : "
    f"{cache_hit_name}"
)

print(
    f"Cache hit (SHA/rename): "
    f"{cache_hit_hash}"
)

print(
    f"Zero distance         : "
    f"{zero_distance_count}"
)

print(
    f"New calculations      : "
    f"{new_distance_count}"
)

print()
print(
    f"Raw NPY               : "
    f"{RAW_NPY}"
)

print(
    f"Raw CSV               : "
    f"{RAW_CSV}"
)

print(
    f"Spectra NPY           : "
    f"{SPECTRA_NPY}"
)

print(
    f"File info             : "
    f"{FILE_INFO_CSV}"
)

print(
    f"Group info            : "
    f"{GROUP_INFO_CSV}"
)

print(
    f"SHA256 cache          : "
    f"{SHA256_CACHE_JSON}"
)

print()
