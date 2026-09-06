import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns


# ==================================================
# 設定
# ==================================================

DISTANCE_MATRIX = (
    "~/yusei/database_chromatic-longtones/distanceMatrix_L2/"
    # "./distanceMatrix_fl_cl/"
    "distance_matrix_raw.csv"
)

OUT_DIR = "./distanceMatrix_L2"


# ==================================================
# 表示するグループ
#
# [] なら全グループ
#
# 例：
# DISPLAY_GROUPS = ["bassfl"]
#
# DISPLAY_GROUPS = [
#     "bassfl",
#     "gauss_sigma-002.5%"
# ]
# ==================================================

DISPLAY_GROUPS = [
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
    "basstrb",
    "basstrb_mute-straight",
    "basstrb_mute-cup",
    "va",
    # "gauss_sigma-002.5%"
]


# ==================================================
# 表示する個別音源
#
# [] なら個別指定なし
#
# group_name/filename の形式で指定する。
#
# 例：
#
# DISPLAY_FILES = [
#     "bassfl/fl000_C3.wav",
#     "bassfl/fl001_Cis3.wav"
# ]
#
# グループ指定と併用可能。
# ==================================================

DISPLAY_FILES = [
]


# ==================================================
# ヒートマップ設定
# ==================================================

SHOW_HEATMAP_VALUES = False
NUMBER_FONTSIZE = 10

# ==================================================
# 縦横軸のラベル表示
# ==================================================

# True  : 個別ファイル名を表示
# False : サブディレクトリ名（group_name）を表示
SHOW_FILE_NAMES = False

FILE_NAME_FONTSIZE = None
GROUP_NAME_FONTSIZE = 10

# ==================================================
# グループ情報
# ==================================================

GROUP_INFO = os.path.join(
    os.path.dirname(
        DISTANCE_MATRIX
    ),
    "group_info.csv"
)


FILE_INFO = os.path.join(
    os.path.dirname(
        DISTANCE_MATRIX
    ),
    "file_info.csv"
)


# ==================================================
# 出力ディレクトリ
# ==================================================

os.makedirs(
    OUT_DIR,
    exist_ok=True
)


# ==================================================
# 距離行列読み込み
# ==================================================

df = pd.read_csv(
    DISTANCE_MATRIX,
    index_col=0
)


# 距離行列に登場する音源名
all_names = df.index.tolist()


D = df.values.astype(
    float
)


N = len(
    all_names
)


print(
    "Total files =",
    N
)


# ==================================================
# グループ情報読み込み
# ==================================================

group_info = pd.read_csv(
    GROUP_INFO
)


required_group_columns = [
    "group_index",
    "group_name",
    "size",
    "start",
    "end"
]


for column in required_group_columns:

    if column not in group_info.columns:

        raise ValueError(
            "group_info.csv does not contain "
            f"required column: {column}"
        )


# ==================================================
# ファイル情報読み込み
# ==================================================

file_info = pd.read_csv(
    FILE_INFO
)


required_file_columns = [
    "index",
    "group_index",
    "group_name",
    "filename",
    "path"
]


for column in required_file_columns:

    if column not in file_info.columns:

        raise ValueError(
            "file_info.csv does not contain "
            f"required column: {column}"
        )


# ==================================================
# グループ名一覧
# ==================================================

available_groups = (
    group_info
    .sort_values("group_index")
    ["group_name"]
    .tolist()
)


print()
print(
    "Available groups:"
)

for group_name in available_groups:

    row = group_info[
        group_info["group_name"]
        == group_name
    ].iloc[0]

    print(
        f"  {group_name}: "
        f"{int(row['size'])} files"
    )


# ==================================================
# 表示対象の決定
#
# グループ指定と個別ファイル指定を統合する。
#
# グループ指定：
#     そのグループの全音源を表示
#
# 個別指定：
#     指定した音源を追加表示
#
# 両者は併用可能。
# ==================================================

selected_names = set()


# ==================================================
# グループ指定
# ==================================================

if len(DISPLAY_GROUPS) == 0:

    # 空なら全グループ

    selected_groups = (
        available_groups
    )

else:

    selected_groups = (
        DISPLAY_GROUPS
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
# グループ内の音源を追加
# ==================================================

for group_name in selected_groups:

    rows = file_info[
        file_info["group_name"]
        == group_name
    ]

    for _, row in rows.iterrows():

        index = int(
            row["index"]
        )

        if index < 0 or index >= N:

            raise ValueError(
                f"Invalid file index: "
                f"{index}"
            )

        selected_names.add(
            all_names[index]
        )


# ==================================================
# 個別音源指定
# ==================================================

for filename in DISPLAY_FILES:

    if filename not in all_names:

        raise ValueError(
            f"Unknown file: "
            f"{filename}\n"
            f"Check file_info.csv."
        )

    selected_names.add(
        filename
    )


# ==================================================
# 元の距離行列順序を維持して並べる
# ==================================================

selected_indices = [
    i
    for i, name in enumerate(
        all_names
    )
    if name in selected_names
]


if len(selected_indices) == 0:

    raise RuntimeError(
        "No files selected."
    )


selected_names = [
    all_names[i]
    for i in selected_indices
]


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
    "Selected groups:"
)

selected_group_counts = (
    file_info[
        file_info["index"].isin(
            selected_indices
        )
    ]
    .groupby(
        "group_name"
    )
    .size()
)


for group_name in selected_groups:

    count = int(
        selected_group_counts.get(
            group_name,
            0
        )
    )

    print(
        f"  {group_name}: "
        f"{count} files"
    )


if len(DISPLAY_FILES) > 0:

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
# ==================================================

df_selected = pd.DataFrame(
    D_selected,
    index=selected_names,
    columns=selected_names
)


# ==================================================
# 選択された距離行列のCSV保存
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
    xticklabels=False,
    yticklabels=False,
    cbar_kws={
        "label": "Distance"
    }
)

# ==================================================
# 軸ラベルの作成
# ==================================================

if SHOW_FILE_NAMES:

    # ----------------------------------------------
    # 個別ファイル名を表示
    # ----------------------------------------------

    plt.xticks(
        np.arange(len(selected_names)) + 0.5,
        selected_names,
        rotation=45,
        ha="right",
        fontsize=FILE_NAME_FONTSIZE
    )

    plt.yticks(
        np.arange(len(selected_names)) + 0.5,
        selected_names,
        rotation=0,
        fontsize=FILE_NAME_FONTSIZE
    )

else:

    # ----------------------------------------------
    # グループ名を表示
    # ----------------------------------------------

    # selected_names に対応する group_name を取得
    selected_group_names = (
        file_info
        .set_index("index")
        .loc[selected_indices, "group_name"]
        .tolist()
    )

    # 各グループの開始位置・中央位置を計算
    group_positions = []

    start = 0

    for group_name in selected_groups:

        positions = [
            i
            for i, g in enumerate(selected_group_names)
            if g == group_name
        ]

        if len(positions) == 0:
            continue

        center = (
            min(positions) + max(positions)
        ) / 2

        group_positions.append(
            (group_name, center)
        )

    # ----------------------------------------------
    # X軸
    # ----------------------------------------------

    plt.xticks(
        [
            position + 0.5
            for _, position in group_positions
        ],
        [
            group_name
            for group_name, _ in group_positions
        ],
        rotation=45,
        ha="right",
        fontsize=GROUP_NAME_FONTSIZE
    )

    # ----------------------------------------------
    # Y軸
    # ----------------------------------------------

    plt.yticks(
        [
            position + 0.5
            for _, position in group_positions
        ],
        [
            group_name
            for group_name, _ in group_positions
        ],
        rotation=0,
        fontsize=GROUP_NAME_FONTSIZE
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
    ha="right",
    fontsize=FILE_NAME_FONTSIZE
)


plt.yticks(
    rotation=0,
    fontsize=FILE_NAME_FONTSIZE
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
