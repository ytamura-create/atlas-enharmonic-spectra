Language: English | [日本語](.readme/README.ja.md) | [Français](.readme/README.fr.md) | [Deutsch](.readme/README.de.md)

> *Melodies of timbre!* What refined senses are able to distinguish these differences! What highly cultivated mind can find delight in such subtle nuances of sound!
>
> Who would dare pursue a new theory here!
>
> — A. Schönberg, *Theory of Harmony* (1911)

Composer **Arnold Schönberg** wrote these words at the end of *Harmonielehre* (1911), published in memory of his mentor and close friend, the composer-conductor **Gustav Mahler**.

To this challenge, **Alban Berg**, **Anton Webern**, and later **Luigi Nono**, **Pierre Boulez**, and **Karlheinz Stockhausen** devoted their lives, yet none succeeded in establishing an adequate method. They—and music itself—had advanced too far ahead of the history of science.

In the twenty-first century, **Shun-ichi Amari's** theory of **Information Geometry** (1982/85–) enables us to measure the **distance between timbres** as an exact physical quantity expressed in [Hz]. From this become possible timbral geodesics, a geometry of chords and harmony, and ultimately the **Harmony of Timbres** dreamt by Schönberg beyond conventional pitch-based harmony. The following develops this framework as an attempt to open another door in the history of music.

# Atlas Enharmonic Spectra

*“Klangfarbenharmonie” — Invitation to the spectral tuning for harmonic ensembles.*

---

**Atlas Enharmonic Spectra** is a chromatic long-tone dataset for instrumental and vocal sounds, together with a system of computational methods in musical information geometry, developed to advance **Klangfarbenharmonie** and **Klangfarbenakkord** in ensemble practice.

In addition to standardized recordings covering the practical range of each instrument, the repository includes FFT-based spectral extraction, intrinsic Shannon entropy of normalized spectra, Wasserstein-distance computation scripts, and precomputed distance matrices. It provides the experimental foundation for the framework first introduced in [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026), where timbral relationships are described through optimal transport between normalized spectra.

It is intended as a practical resource for composition, orchestration, performance, rehearsal, practice, and even mute selection, enabling musicians to compare timbres across pitch, instrument, and playing technique.

![L1 Wasserstein distance matrix](distanceMatrix_L1/distance_matrix_selected_heatmap.png)

## ✨ Features

- **24 instrument categories** (woodwinds, brass, strings, reference signals, and more; continuously expanding)

- **1,141 WAV recordings** (chromatic long tones; continuously expanding)

  - Sampling rate: $f_s=96\ \mathrm{kHz}$
  - Number of samples: $N=2^{20}$
  - Standardized duration: $N/f_s=10.\ 922\ 666\ldots\ \mathrm{sec}$
  - See [*Sparse FFT: A New High-Resolution Frequency Analysis and Its Applications*](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/).

- Unified file-naming conventions including written pitch, concert pitch, and performance conditions

- Scripts for computing L1 and L2 Wasserstein distances between spectra

- Precomputed Wasserstein distance matrices

## 📁 Repository Structure

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
├── distanceMatrix_L1/    # Precomputed L1 Wasserstein matrices
├── distanceMatrix_L2/    # Precomputed L2 Wasserstein matrices
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py
```

Each instrument directory contains chromatic long-tone recordings. Some instruments additionally include alternative fingerings, mute conditions, and other performance variants.

## 🏷️ File Naming

Examples:

```text
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

Depending on the instrument, filenames may encode:

- concert pitch (`conc-*`)
- written pitch (`writ-*`)
- overtone number (`ovt-*`)
- position or fingering (`pos-*`)
- mute type (`mute-*`)
- other performance condition

## ▶️ Execution Workflow

Run the Python programs according to the flowchart below to generate Wasserstein distance matrices as CSV files and PNG heatmaps.

![Execution Workflow](.readme/flowchart.svg)

## 🎼 Research Background

In *Harmonielehre* (1911), Arnold Schönberg wrote that it should become possible

> *“...solche **Folgen** herzustellen, deren Beziehung untereinander mit einer Art Logik wirkt, ganz äquivalent jener Logik, die uns bei der Melodie der Klanghöhen genügt.”*

> *“…to create such **successions** whose mutual relations operate according to a kind of logic entirely equivalent to that which satisfies us in the melody of pitches.”*

At the same time, he acknowledged that this remained, in his own day, a vision of the future.

> *“Das scheint eine Zukunftsphantasie und ist es wahrscheinlich auch. Aber eine, von der ich fest glaube, daß sie sich verwirklichen wird.”*

> *“It seems like a fantasy of the future, and probably it is. Yet I firmly believe that it will one day become reality.”*

This **fantasy** was later inherited by **Webern**, **Messiaen**, **Nono**, **Boulez**, **Stockhausen**, and many other composers. Postwar serialism extended organization beyond pitch to duration, dynamics, and timbre itself. Yet no common principle emerged that could treat timbre across instruments in the same systematic way that pitch had long been organized.

This contrast reflects the different histories of pitch and timbre. The frequency ratios of **Pythagoras**, the just intonation of **Gioseffo Zarlino**, and **Zhu Zaiyu's** mathematical derivation of so-called “well-tempered tuning system” (in Mersennes' and Chinese case “twelve-tone equal temperament”) all arose during periods when music and mathematics were far less separated than they are today, establishing quantitative ways of relating pitches through numbers. These tuning systems, however, describe relationships among pitches; they do neither describe differences between instrumental timbres, nor the continuous timbral changes that occur during performance. Thus, while pitch acquired a precise theoretical framework, timbre never received an equally general system of organization.

Instead of treating INDIVIDUAL SPECTRUM as primary, **Atlas Enharmonic Spectra** takes **distances** BETWEEN SPECTRA as its fundamental object. From these measurable relationships it constructs a timbral space, quantifies Schönberg's **Klangfarbenmelodie**, and extends its underlying idea toward **Klangfarbenharmonie**, providing a common basis for comparing timbral convergence and divergence within ensembles and supporting decisions in performance, orchestration, and composition.

---

The analysis relies exclusively on **physical observables** up to the point immediately before auditory perception. Each recording is decomposed into its frequency spectrum, whose normalized form is interpreted as a probability density function following **Born's probabilistic interpretation** of wave functions in quantum mechanics. This model is inspired by the biological mechanism through which the cochlea spatially separates frequency components and hair cells on the basilar membrane detect them. To ensure reproducibility while eliminating arbitrary processing choices, spectral decomposition is performed using the **Fast Fourier Transform (FFT)**.

In recent years, **Wasserstein geometry** has become widely established in information geometry, statistics, and machine learning as a framework that endows probability distributions with geometric structure through optimal transport. The work of **Shun-ichi Amari** and collaborators has been particularly influential in revealing new connections between optimal transport and information geometry. Here this framework is applied to timbre, describing timbral change as **the minimum transport cost required to move spectral mass from one normalized spectral distribution to another**.

Although the repository also includes L2-Wasserstein distances and logarithmic-frequency variants, the accompanying research consistently adopts the **L1-Wasserstein distance**, since it preserves spectral mass while expressing transport along the frequency axis directly as a distance.

For one-dimensional probability distributions $P$ and $Q$, the L1-Wasserstein distance is defined by

$$
W_1(P,Q)=\int_{-\infty}^{\infty}\Bigl\lvert F_P(x)-F_Q(x)\Bigr\rvert\ \mathrm dx,
$$

where $F_P$ and $F_Q$ are the cumulative distribution functions

$$
F_P(x)=\int_{-\infty}^{x}P(y)\ \mathrm dy,\qquad
F_Q(x)=\int_{-\infty}^{x}Q(y)\ \mathrm dy.
$$

Because **Atlas Enharmonic Spectra** operates on DISCRETE FFT spectra, these cumulative distributions are computed as

$$
F_P[i]=\sum_{j=0}^{i}P[j],\qquad
F_Q[i]=\sum_{j=0}^{i}Q[j].
$$

```python
cdf_P = np.cumsum(spectrum_P)
cdf_Q = np.cumsum(spectrum_Q)
```

The discrete L1-Wasserstein distance is then calculated as

$$
W_1(P,Q)=\sum_i\Bigl\lvert F_P[i]-F_Q[i]\Bigr\rvert\Delta f,
$$

```python
return np.sum(np.abs(cdf_P - cdf_Q)) * df
```

where

$$
\Delta f=\frac{f_s}{N}\approx0.092\ \mathrm{Hz}
$$

is the FFT frequency resolution.

This formulation preserves spectral probability while measuring how much spectral mass must be moved, and over what distance. Timbral differences are therefore represented not as isolated peak differences but as the minimum work (cost) required to rearrange the entire spectral distribution.

From this framework emerge metric-space models of **Klangfarbenakkord** and **Klangfarbenharmonie**. By placing instrumental timbres within a common metric space, the repository supports quantitative evaluation of orchestral blending and segregation, while extending **Klangfarbenmelodie** toward practical **Klangfarbenharmonie**.

The repository ultimately aims to provide a shared physical basis for comparing timbres, supporting the practice of Klangfarbenmelodie and Klangfarbenharmonie as well as applications in ensemble design and orchestration.

## 📖 Citation

If you use this dataset, please cite the accompanying paper.

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

Paper: [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026)

## 📖 References

1. Arnold Schönberg. *Harmonielehre*. Universal Edition, Vienna (1911).
2. Shun-ichi Amari. *Differential Geometry of Curved Exponential Families—Curvatures and Information Loss.* *The Annals of Statistics* **10**(2), pp.357–385 (1982).
3. Shun-ichi Amari. *Differential-Geometrical Methods in Statistics* (Lecture Notes in Statistics, **28**). Springer-Verlag (1985).
4. [Jinyong Lee and Ken Ito. *Sparse FFT: A New High-Resolution Frequency Analysis and Its Applications.* *JASTICE* **8**(2), pp.188–193 (2021/2022).](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/)
5. [Yusei Tamura, Shigekazu Ishihara, and Ken Ito. *Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1.* *arXiv*, arXiv:2608.28026 (2026).](https://arxiv.org/abs/2608.28026)