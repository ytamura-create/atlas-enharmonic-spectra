Language: | [English](../README.md) | 日本語 | [Français](README.fr.md) | [Deutsch](README.de.md)

> Melodies of timbre! What refined senses are able to distinguish these, what a highly developed mind can take pleasure in such subtle things!
> 
> Who would dare to demand a theory here!
> 
> — Arnold Schoenberg, *Theory of Harmony* (1911)

作曲家 **A. シェーンベルク** は師友であった作曲家＝指揮者 **G. マーラー** の死を悼みつつ公刊した「和声学 Harmonielehre」(1911)の末尾に上のように記した。

この問いに、かつて **A. ベルク** も **A. ヴェーベルン** も、また第二次世界大戦後には **L. ノーノ**、**P. ブーレーズ** も **K. シュトックハウゼン** も正面から挑みつつ、生涯に亘って適切な方法を構築することが出来なかった。彼らは科学史に先んじすぎていたのだ。

21世紀、我々は **甘利俊一**教授 の「**情報幾何**」の方法（1982/85～）によって、正確な Hz 単位の量として「音色と音色の距離」を測ることができる。そこから「音色の測地線」「和音と和声の幾何学」そして本質的に、因襲的な「音高の和声」を超える、シェーンベルクが夢想した「*音色の和声学*」が可能になる。我々は以下でこれを展開し、歴史の扉を一つ大きく開くこととしよう。

# Atlas Enharmonic Spectra

*“Klangfarbenharmonie” — Invitation to the spectral tuning for harmonic ensembles.*

---

**Atlas Enharmonic Spectra** は、アンサンブルの音色作りを本質的に進展させる **Klangfarbenharmonie** および **Klangfarbenakkord** のために構築された、器楽ならびに声楽ロングトーンの半音階データセットと音楽の情報幾何演算のシステムです。

各楽器の実用音域全体にわたる標準化された録音に加え、FFTによるスペクトル抽出、Wasserstein距離の計算スクリプト、および事前計算済みの距離行列を収録しています。本リポジトリは、[*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026) で初めて導入した、正規化スペクトル間の最適輸送によって音色関係を記述する枠組みの実験基盤となるものです。

作曲・編曲・演奏の実践において、音高・楽器・奏法の違いを横断しながら音色を比較・検討するための支援ツールとして利用することを目的としています。

![L1 Wasserstein distance matrix](../distanceMatrix_L1/distance_matrix_selected_heatmap.png)

## ✨ 特徴

- **24種類の楽器カテゴリ**（木管・金管・弦楽器・基準信号など。継続的に追加予定）
- **1141件のWAV録音**（半音階ロングトーン。継続的に追加予定）
    * サンプリング周波数： $f_s=96\ \mathrm{kHz}$、
    * サンプル数： $ N = 2^{20} $、
    * ∴ データ長： $ N/f_s = 10.\ 922\ 666...\ \ \mathrm{sec}$ に統一。
    * [*Sparse FFT：新しい高分解能周波数解析とその応用*](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/) を参照のこと。
- 記譜音・実音・演奏条件などを含む統一的なファイル命名規則
- スペクトル間 L1・L2 Wasserstein距離の計算スクリプト
- 事前計算済みWasserstein距離行列

## 📁 リポジトリ構成

```text
atlas-enharmonic-spectra/
├── wav/
│   ├── fl/          # Flute
│   ├── ob/          # Oboe
│   ├── cl-inEs/     # Clarinet in E♭
│   ├── cl-inB/      # Clarinet in B♭
│   ├── basscl/      # Bass Clarinet
│   ├── va/          # Viola
│   └── ...          # and more!
│
├── distanceMatrix_L1/    # 計算済み L1 Wasserstein 距離行列
├── distanceMatrix_L2/    # 計算済み L2 Wasserstein 距離行列
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py
```

各楽器ディレクトリには半音階ごとのロングトーン録音が収録されています。楽器によっては、替え指・ミュート・その他の演奏条件の違いも含まれています。

## 🏷️ ファイル命名規則

例：

```text
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

楽器に応じて、ファイル名には以下の情報が含まれます。

- 実音 (`conc-*`)
- 記譜音 (`writ-*`)
- 倍音番号 (`ovt-*`)
- ポジション・運指 (`pos-*`)
- ミュート種別 (`mute-*`)
- 演奏条件

## ▶️ 実行手順

以下のフローチャートに従ってpythonプログラムを実行し、目的に応じて Wasserstein 距離行列を CSV 形式、および PNG カラーマップ表示で出力します。

![実行手順](flowchart.svg)

## 🎼 研究背景

Arnold Schönberg は *Harmonielehre*（1911）の中で、

> *"...Folgen herzustellen, deren Beziehung untereinander mit einer Art Logik wirkt, ganz äquivalent jener Logik, die uns bei der Melodie der Klanghöhen genügt."*

> *「……それら相互の関係が、音高の旋律において私たちを満足させる論理とまったく同等の、一種の論理として働くような連なりを作り出すこと」*

が可能になるだろうと述べた。

そして同時に、それが当時はまだ未来の構想であることも認めている。

> *"Das scheint eine Zukunftsphantasie und ist es wahrscheinlich auch. Aber eine, von der ich fest glaube, daß sie sich verwirklichen wird."*

> *「それは未来の幻想のように思われるし、おそらく実際そうなのだろう。しかし私は、それがいつか実現すると固く信じている。」*

この **未来の幻想** はその後、**Webern**、**Schaeffer**、**Stockhausen**、**Ligeti** をはじめとする多くの作曲家へ受け継がれた。特に戦後のセリエリズムは、音高だけでなく音価・強弱・音色までも組織化の対象へと押し広げた。しかし、音色を音高と同じような共通原理の上で横断的に扱う方法は、音楽的な実践の中で十分には確立されなかった。

この対照は、音高と音色の歴史の違いに由来する。音高については、**ピタゴラス** の振動数比、**G. ツァルリーノ** の純正律、**朱載堉** による12平均律の数学的導出などを通じて、音楽と数学が今日ほど分離していなかった時代から、音を数として関係づける尺度が育まれてきた。一方、こうした音律は音高の関係を定めるものであり、楽器間の音色差や演奏中に連続的に変化する音色を同じ原理で記述するものではなかった。その結果、音高には精密な体系が築かれた一方で、音色にはそれに対応する横断的な尺度が十分には与えられてこなかった。

我々は、単一のスペクトルではなく、スペクトル間の距離を一次的な対象として音色空間を記述する。Schönberg が構想した **音色旋律 Klangfarbenmelodie** を定量化するとともに、その発想を **音色和声 Klangfarbenharmonie** へ拡張し、合奏における音色の融和や乖離を共通の尺度で比較することで、演奏・編曲・作曲の判断を支援する基盤を提供する。

---

解析には認知評価や主観アンケートを用いず、**物理的に観測可能な量のみ** を扱う。各録音は周波数スペクトルへ分解し、正規化したものを、Born の確率解釈に倣い確率密度関数とみなす。このモデルは、蝸牛管が周波数成分を空間的に分波し、基底膜上の有毛細胞がそれを観測する生理機構に着想を得ている。分波には再現性と恣意性の排除のため、高速 Fourier 変換（Fast Fourier Transform, FFT）を用いる。

近年、**Wasserstein 幾何** は、確率分布に最適輸送による幾何学構造を与える枠組みとして、情報幾何学・統計学・機械学習で広く用いられている。特に **甘利俊一** らの研究は、最適輸送と情報幾何学の接点を切り開き、確率分布を幾何学的に扱う新たな視点を示した。本リポジトリはこの枠組みを音色解析へ応用し、音色変化を「一つのスペクトル分布から別の分布へスペクトル質量を移すために必要な最小輸送コスト」として記述する。

本リポジトリには L2-Wasserstein 距離や対数周波数版も含まれているが、研究では一貫して **L1-Wasserstein 距離** を採用している。これは、スペクトル質量を保存したまま、周波数軸上での輸送をそのまま距離として表現できるためである。

一次元の確率分布 $P,Q$ に対する L1-Wasserstein 距離は、

$$W_1(P,Q)=\int_{-\infty}^{\infty}\Bigl\lvert F_P(x)-F_Q(x)\Bigr\rvert\ \mathrm dx$$

で定義される。ここで $F_P,F_Q$ は、それぞれ正規化スペクトル $P,Q$ の累積分布関数

$$F_P(x) = \int_{-\infty}^x P(y)\ \mathrm dy,\qquad F_Q(x) = \int_{-\infty}^x Q(y)\ \mathrm dy$$

である。

**Atlas Enharmonic Spectra** では FFT によって得られる離散スペクトルを扱うため、累積分布を

$$F_P[i]=\sum_{j=0}^{i}P[j],\qquad F_Q[i]=\sum_{j=0}^{i}Q[j]$$

```python
cdf_P = np.cumsum(spectrum_P)
cdf_Q = np.cumsum(spectrum_Q)
```

として計算し、離散データ列による L1-Wasserstein 距離を

$$W_1(P,Q)=\sum_i\Bigl\lvert F_P[i]-F_Q[i]\Bigr\rvert\Delta f$$

```python
return np.sum(np.abs(cdf_P - cdf_Q)) * df
```

として算出している。$\Delta f$（`df`）は FFT の周波数分解能

$$
\Delta f = \frac{f_s}{N} \approx 0.092\ \mathrm{Hz}
$$

である。

この定式化では、スペクトル確率を保存したまま、「どれだけのスペクトル質量を、どれだけ移動させる必要があるか」を測ることができる。音色差は個々のピークの差ではなく、スペクトル全体を並べ替えるために必要な最小の仕事として表現される。

この枠組みから、**Klangfarbenakkord** と **Klangfarbenharmonie** の計量空間モデルが導かれる。楽器音色を共通の距離空間へ配置することで、オーケストレーション上の融和・乖離の定量化や、**Klangfarbenmelodie** を発展させた **Klangfarbenharmonie** の作曲実践を支援することを目指す。

本リポジトリは、音色を物理量に基づく共通の尺度で比較できる基盤として、Klangfarbenmelodie と Klangfarbenharmonie の実践、およびアンサンブル設計やオーケストレーションへの応用を目指す。

## 📖 引用

このデータセットを利用する場合は、対応する論文を引用してください。

```bibtex
@misc{tamura2026klangfarbenakkord,
  title={Klangfarbenakkord and Klangfarbenharmonien Metric Space Models for Music on Informational Geometry 1},
  author={Yusei Tamura and Shigekazu Ishihara and Ken Ito},
  year={2026},
  eprint={2608.28026},
  archivePrefix={arXiv},
  primaryClass={cs.SD}
}
```

論文：[*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026)

## 📖 参考文献

1. Arnold Schönberg. *Harmonielehre*. Universal Edition, Vienna (1911).
1. Shun-ichi Amari. Differential geometry of curved exponential families—curvatures and information loss. *The Annals of Statistics* **10**(2), pp. 357–385 (1982).
1. Shun-ichi Amari. Differential-geometrical methods in statistics (Lecture Notes in Statistics, **28**). *Springer-Verlag* (1985).
1. [李 珍咏，伊東 乾．Sparse FFT：新しい高分解能周波数解析とその応用．*JASTICE* **8**(2), pp.188–193 (2021/2022)](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/)
1. [Yusei Tamura, Shigekazu Ishihara, and Ken Ito. Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1. *arXiv*, arXiv:2608.28026.](https://arxiv.org/abs/2608.28026)