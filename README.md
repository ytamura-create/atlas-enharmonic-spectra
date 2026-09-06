# Klangfarbenatlas

**Klangfarbenatlas** is a research dataset of chromatic long-tone recordings from orchestral instruments, designed for timbre analysis, spectral geometry, and Wasserstein-distance-based studies of musical timbre.

The dataset provides standardized recordings across the playable range of each instrument, together with accompanying analysis scripts and distance-matrix generation tools. It serves as the experimental foundation for the geometric harmony framework introduced in [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026), where instrumental timbres are modeled as elements of a metric space using Wasserstein distances.

## Features

* **26 instrument categories**, including woodwinds, brass, strings, and reference signals.
* **973 WAV recordings** covering chromatic long tones.
* Standardized file naming with written pitch, concert pitch, and performance-condition metadata where applicable.
* Analysis scripts for:

  * FFT-based spectral extraction
  * L1 and L2 Wasserstein distance computation
* Precomputed distance matrices for multiple Wasserstein variants.

## Repository Structure

```
Klangfarbenatlas/
├── fl/                  # Flute
├── ob/                  # Oboe
├── cl-inA/              # Clarinet in A
├── cl-inB/              # Clarinet in B♭
├── basscl/              # Bass Clarinet
├── va/                  # Viola
├── ...
├── distanceMatrix_L1/
├── distanceMatrix_L2/
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py

````

Each instrument directory contains chromatic long-tone recordings. Some instruments additionally include alternative fingerings, mute conditions, or performance variants.

## File Naming

Examples:

```
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

Depending on the instrument, filenames may encode:

- concert pitch (`conc-*`)
- written pitch (`writ-*`)
- overtone number (`ovt-*`)
- fingering position (`pos-*`)
- mute type (`mute-*`)
- performance variant

## Research Background

Western music theory traditionally represents notes primarily through pitch. **Klangfarbenatlas** extends this perspective by providing a systematic corpus of instrumental timbres suitable for metric-space analyses.

The accompanying research introduces **geometric harmony**, in which normalized spectra are compared using Wasserstein distance, allowing timbral relationships between individual notes and instrumental combinations to be analyzed within a common geometric framework while remaining compatible with conventional harmonic theory.

The dataset was specifically developed to support investigations such as:

- timbral affinity between instruments
- orchestral blend and separation
- clarinet throat-tone analysis
- spectral geometry
- persistent homology of timbre spaces
- Wasserstein-based chord metrics

## Citation

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

Paper: [Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1](https://arxiv.org/abs/2608.28026)
