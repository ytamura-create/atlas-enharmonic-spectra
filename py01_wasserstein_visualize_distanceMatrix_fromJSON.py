import os
import json

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns


# ==================================================
# 設定
# ==================================================

DISTANCE_MATRIX = (
    "./distanceMatrix_L1/"
    "distance_matrix_raw.csv"
)

GROUP_JSON = (
    "./distanceMatrix_L1/"
    "display_groups.json"
)

OUT_DIR = "./colormap_L1"


# ==================================================
# 表示するグループ
#
# [] なら全グループ
#
# JSONの groups 直下の name を指定する。
# ==================================================

DISPLAY_GROUPS = [
    # "fl",
    # "cl-inB"
]


# ==================================================
# 表示する個別音源
#
# [] なら個別指定なし
#
# group_name/filename の形式。
#
# 例：
#
# DISPLAY_FILES = [
#     "bassfl/bassfl000_C3.wav",
#     "bassfl/bassfl001_Cis3.wav"
# ]
#
# グループ指定と併用可能。
# ==================================================

DISPLAY_FILES = [
]


# ==================================================
# ヒートマップ設定
# ==================================================

SHOW_HEATMAP_VALUES = True

NUMBER_FONTSIZE = 12


# ==================================================
# 出力ディレクトリ
# ==================================================

os.makedirs(
    OUT_DIR,
    exist_ok=True
)


# ==================================================
# パスを展開
# ==================================================

DISTANCE_MATRIX = os.path.expanduser(
    DISTANCE_MATRIX
)


# ==================================================
# JSON読み込み
# ==================================================

if not os.path.exists(
    GROUP_JSON
):

    raise FileNotFoundError(
        "JSON file not found:\n"
        f"{GROUP_JSON}"
    )


with open(
    GROUP_JSON,
    "r",
    encoding="utf-8"
) as f:

    group_data = json.load(f)


if "groups" not in group_data:

    raise ValueError(
        'JSON does not contain "groups".'
    )


json_groups = group_data[
    "groups"
]


# ==================================================
# JSON構造確認
#
# 各要素：
#
# {
#     "name": "...",
#     "files": [...]
# }
# ==================================================

for group in json_groups:

    if "name" not in group:

        raise ValueError(
            'Each group must contain "name".'
        )


    if "files" not in group:

        raise ValueError(
            'Each group must contain "files".'
        )


    if not isinstance(
        group["files"],
        list
    ):

        raise ValueError(
            f'"files" of group '
            f'"{group["name"]}" '
            f"must be a list."
        )


# ==================================================
# 利用可能なグループ
#
# ★ JSONの順序をそのまま使用
# ==================================================

available_groups = [
    group["name"]
    for group in json_groups
]


print()
print(
    "Available groups:"
)


for i, group in enumerate(
    json_groups
):

    print(
        f"  {i}: "
        f"{group['name']} "
        f"({len(group['files'])} files in JSON)"
    )


# ==================================================
# JSONに記載された全ファイル
#
# ★ここが重要
#
# JSONの
#
# groups
#   ↓
# files
#
# の順序を完全に維持する。
# ==================================================

all_json_file_names = []

file_to_group_name = {}


for group in json_groups:

    group_name = group[
        "name"
    ]


    for filename in group[
        "files"
    ]:

        if filename in file_to_group_name:

            raise ValueError(
                "Duplicate filename found "
                f"in JSON: {filename}"
            )


        all_json_file_names.append(
            filename
        )


        file_to_group_name[
            filename
        ] = group_name


# ==================================================
# 距離行列読み込み
# ==================================================

if not os.path.exists(
    DISTANCE_MATRIX
):

    raise FileNotFoundError(
        "Distance matrix not found:\n"
        f"{DISTANCE_MATRIX}"
    )


df = pd.read_csv(
    DISTANCE_MATRIX,
    index_col=0
)


all_names = df.index.tolist()


D = df.values.astype(
    float
)


N = len(
    all_names
)


print()
print(
    "Total files in distance matrix =",
    N
)


print(
    "Total files in JSON =",
    len(all_json_file_names)
)


# ==================================================
# 距離行列の基本確認
# ==================================================

if df.shape[0] != df.shape[1]:

    raise ValueError(
        "Distance matrix must be square. "
        f"Shape = {df.shape}"
    )


if list(df.index) != list(df.columns):

    raise ValueError(
        "Row names and column names of "
        "the distance matrix do not match."
    )


# ==================================================
# CSVファイル名 → 距離行列上のindex
# ==================================================

csv_index_map = {
    filename: i
    for i, filename
    in enumerate(all_names)
}


# ==================================================
# JSONにあるがCSVにないファイル
#
# 警告してスキップ。
# ==================================================

distance_file_set = set(
    all_names
)


json_file_set = set(
    all_json_file_names
)


missing_from_distance = (
    json_file_set
    -
    distance_file_set
)


if len(
    missing_from_distance
) > 0:

    print()
    print(
        "Warning:"
    )

    print(
        "The following files are listed "
        "in JSON but not found in the "
        "distance matrix:"
    )

    for filename in all_json_file_names:

        if filename in missing_from_distance:

            print(
                f"  {filename}"
            )


# ==================================================
# CSVにあるがJSONにないファイル
#
# 無視する。
# ==================================================

missing_from_json = (
    distance_file_set
    -
    json_file_set
)


if len(
    missing_from_json
) > 0:

    print()
    print(
        "Ignoring files that are not "
        "listed in JSON:"
    )

    print(
        f"  {len(missing_from_json)} files"
    )


# ==================================================
# 表示対象グループ決定
# ==================================================

if len(
    DISPLAY_GROUPS
) == 0:

    # ----------------------------------------------
    # []ならJSONの全グループ
    #
    # ★ JSONの順序
    # ----------------------------------------------

    selected_groups = (
        available_groups.copy()
    )

else:

    selected_groups = (
        DISPLAY_GROUPS.copy()
    )


# ==================================================
# グループ名の妥当性確認
# ==================================================

for group_name in selected_groups:

    if group_name not in available_groups:

        raise ValueError(
            f"Unknown group: "
            f"{group_name}\n"
            f"Available groups: "
            f"{available_groups}"
        )


# ==================================================
# 表示対象ファイル決定
#
# ★重要
#
# setは「選択対象」の管理だけに使い、
# 最終的な順序には絶対に使わない。
# ==================================================

selected_file_set = set()


# ==================================================
# グループ指定
# ==================================================

for group in json_groups:

    group_name = group[
        "name"
    ]


    if group_name not in selected_groups:

        continue


    for filename in group[
        "files"
    ]:

        if filename not in csv_index_map:

            # JSONにはあるがCSVにない
            continue


        selected_file_set.add(
            filename
        )


# ==================================================
# 個別音源指定
# ==================================================

for filename in DISPLAY_FILES:

    if filename not in json_file_set:

        raise ValueError(
            f"File is not listed in JSON: "
            f"{filename}"
        )


    if filename not in csv_index_map:

        raise ValueError(
            f"File is listed in JSON but "
            f"not found in distance matrix: "
            f"{filename}"
        )


    selected_file_set.add(
        filename
    )


# ==================================================
# ★★★ 最重要部分 ★★★
#
# JSONの順序で選択ファイルを構築
#
# all_json_file_names は
#
# JSON:
#
# groups[0]
#   files[0]
#   files[1]
#   ...
#
# groups[1]
#   files[0]
#   files[1]
#   ...
#
# の順序。
#
# したがって、この順番をそのまま
# 行列の行・列の順番にする。
# ==================================================

selected_names = []

selected_indices = []


for filename in all_json_file_names:

    if filename not in selected_file_set:

        continue


    selected_names.append(
        filename
    )


    selected_indices.append(
        csv_index_map[filename]
    )


# ==================================================
# 選択ファイル数確認
# ==================================================

if len(
    selected_indices
) == 0:

    raise RuntimeError(
        "No files selected."
    )


# ==================================================
# 選択後の距離行列
#
# ★ JSON順
# ==================================================

D_selected = D[
    np.ix_(
        selected_indices,
        selected_indices
    )
]


# ==================================================
# 選択結果表示
# ==================================================

print()
print(
    "Selected files =",
    len(selected_names)
)


print()
print(
    "Selected files in JSON order:"
)


for i, filename in enumerate(
    selected_names
):

    print(
        f"  {i}: {filename}"
    )


# ==================================================
# 選択されたグループのファイル数
#
# JSON順を維持して表示する。
# ==================================================

print()
print(
    "Selected groups:"
)


for group in json_groups:

    group_name = group[
        "name"
    ]


    if group_name not in selected_groups:

        continue


    count = 0


    for filename in group[
        "files"
    ]:

        if filename in selected_file_set:

            count += 1


    print(
        f"  {group_name}: "
        f"{count} files"
    )


# ==================================================
# 個別指定結果
# ==================================================

if len(
    DISPLAY_FILES
) > 0:

    print()
    print(
        "Individually selected files:"
    )


    for filename in DISPLAY_FILES:

        print(
            f"  {filename}"
        )


# ==================================================
# 選択された距離行列をDataFrame化
#
# ★ index / columns ともにJSON順
# ==================================================

df_selected = pd.DataFrame(
    D_selected,
    index=selected_names,
    columns=selected_names
)


# ==================================================
# CSV保存
# ==================================================

selected_csv_path = os.path.join(
    OUT_DIR,
    "distance_matrix_selected.csv"
)


df_selected.to_csv(
    selected_csv_path
)


print()
print(
    "Selected distance matrix saved:"
)


print(
    selected_csv_path
)


# ==================================================
# 距離行列ヒートマップ
# ==================================================

plt.figure(
    figsize=(12, 10)
)


sns.heatmap(
    df_selected,
    annot=SHOW_HEATMAP_VALUES,
    fmt=".0f",
    annot_kws={
        "color": "red",
        "size": NUMBER_FONTSIZE
    },
    cmap="viridis",
    xticklabels=True,
    yticklabels=True,
    cbar_kws={
        "label": "Distance"
    }
)


plt.title(
    "Distance Matrix"
)


plt.xlabel(
    "Files"
)


plt.ylabel(
    "Files"
)


plt.xticks(
    rotation=45,
    ha="right"
)


plt.yticks(
    rotation=0
)


plt.tight_layout()


heatmap_path = os.path.join(
    OUT_DIR,
    "distance_matrix_selected_heatmap.png"
)


plt.savefig(
    heatmap_path,
    dpi=300
)


plt.show()


print(
    "Distance matrix heatmap saved:"
)


print(
    heatmap_path
)


# ==================================================
# 完了
# ==================================================

print()
print(
    "=========================================="
)


print(
    "Code 1 completed."
)


print(
    "=========================================="
)
