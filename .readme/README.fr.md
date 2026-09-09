Langue : | [English](../README.md) | [日本語](README.ja.md) | Français | [Deutsch](README.de.md)

> Melodies of timbre! What refined senses are able to distinguish these, what a highly developed mind can take pleasure in such subtle things!
>
> Who would dare to demand a theory here!
>
> — Arnold Schoenberg, *Theory of Harmony* (1911)

Le compositeur **Arnold Schönberg** écrivit ces mots à la fin de sa *Harmonielehre* (1911), publiée à la mémoire de son maître et ami, le compositeur et chef d'orchestre **Gustav Mahler**.

À cette question se sont confrontés plus tard **Alban Berg**, **Anton Webern**, puis après la Seconde Guerre mondiale **Luigi Nono**, **Pierre Boulez** et **Karlheinz Stockhausen**. Aucun d'eux, pourtant, ne parvint à construire une méthode pleinement satisfaisante au cours de sa vie. Ils avaient, en quelque sorte, devancé l'histoire des sciences.

Au XXIᵉ siècle, la méthode de **l'information géométrique** développée par le professeur **Shun-ichi Amari** (1982/85–) nous permet désormais de mesurer la **distance entre deux timbres** comme une grandeur physique exprimée en hertz. À partir de là deviennent possibles des géodésiques de timbre, une géométrie des accords et de l'harmonie et, plus profondément, cette **harmonie des timbres** imaginée par Schönberg au-delà de l'harmonie fondée uniquement sur les hauteurs. Nous développons ci-dessous cette approche comme une tentative d'ouvrir un nouveau chapitre de l'histoire de la musique.

# Atlas Enharmonic Spectra

*« Klangfarbenharmonie » — Invitation to the spectral tuning for harmonic ensembles.*

---

**Atlas Enharmonic Spectra** est un jeu de données chromatique de sons tenus instrumentaux et vocaux, accompagné d'un système de calcul en géométrie de l'information musicale, conçu pour faire progresser la **Klangfarbenharmonie** et le **Klangfarbenakkord** dans l'écriture pour ensemble.

Outre des enregistrements standardisés couvrant toute la tessiture pratique de chaque instrument, le dépôt contient l'extraction spectrale par FFT, des scripts de calcul des distances de Wasserstein ainsi que des matrices de distances précalculées. Il constitue la base expérimentale du cadre présenté pour la première fois dans [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026), où les relations entre timbres sont décrites par le transport optimal entre spectres normalisés.

Le dépôt est destiné à servir d'outil d'aide à la composition, à l'orchestration et à l'interprétation, en permettant de comparer les timbres au-delà des différences de hauteur, d'instrument et de technique de jeu.

![L1 Wasserstein distance matrix](../distanceMatrix_L1/distance_matrix_selected_heatmap.png)

## ✨ Caractéristiques

- **24 catégories d'instruments** (bois, cuivres, cordes, signaux de référence, etc.; mises à jour continues)
- **1 141 enregistrements WAV** (sons tenus chromatiques; mises à jour continues)
  - Fréquence d'échantillonnage : $f_s=96\ \mathrm{kHz}$
  - Nombre d'échantillons : $N=2^{20}$
  - Durée unifiée : $N/f_s=10.922666\ldots\ \mathrm{s}$
  - Voir [*Sparse FFT：新しい高分解能周波数解析とその応用*](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/).
- Convention de nommage unifiée intégrant hauteur notée, hauteur réelle et conditions d'exécution.
- Scripts de calcul des distances de Wasserstein L1 et L2 entre spectres.
- Matrices de distances de Wasserstein précalculées.

## 📁 Structure du dépôt

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
├── distanceMatrix_L1/    # Matrices L1 précalculées
├── distanceMatrix_L2/    # Matrices L2 précalculées
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py
```

Chaque dossier d'instrument contient des enregistrements de sons tenus chromatiques. Selon l'instrument, des doigtés alternatifs, des sourdines ou d'autres variantes d'exécution sont également inclus.

## 🏷️ Convention de nommage

Exemples :

```text
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

Selon l'instrument, les noms de fichiers peuvent contenir :

- hauteur réelle (`conc-*`)
- hauteur notée (`writ-*`)
- numéro d'harmonique (`ovt-*`)
- position ou doigté (`pos-*`)
- type de sourdine (`mute-*`)
- condition d'exécution

## ▶️ Procédure d'exécution

Exécutez les programmes Python en suivant le diagramme de flux ci-dessous afin de générer, selon vos besoins, les matrices de distances de Wasserstein au format CSV ainsi que leur représentation en carte thermique PNG.

![Procédure d'exécution](flowchart.svg)

## 🎼 Contexte de la recherche

Dans *Harmonielehre* (1911), Arnold Schönberg écrivait :

> *« …Folgen herzustellen, deren Beziehung untereinander mit einer Art Logik wirkt, ganz äquivalent jener Logik, die uns bei der Melodie der Klanghöhen genügt. »*

> *« …créer des successions dont les relations réciproques fonctionnent selon une logique entièrement équivalente à celle qui nous satisfait dans la mélodie des hauteurs. »*

Il exprimait ainsi l'espoir qu'une telle organisation des timbres puisse un jour devenir possible.

En même temps, il reconnaissait que cette idée appartenait encore au domaine de l'avenir.

> *« Das scheint eine Zukunftsphantasie und ist es wahrscheinlich auch. Aber eine, von der ich fest glaube, daß sie sich verwirklichen wird. »*

> *« Cela ressemble à une fantaisie d'avenir, et c'en est probablement une. Mais je crois fermement qu'elle finira par se réaliser. »*

Cette **Zukunftsphantasie** fut ensuite reprise par **Webern**, **Schaeffer**, **Stockhausen**, **Ligeti** et de nombreux autres compositeurs. Le sérialisme d'après-guerre étendit notamment l'organisation non seulement aux hauteurs, mais aussi aux durées, aux dynamiques et aux timbres. Pourtant, il ne parvint pas à établir, dans la pratique musicale, un principe transversal permettant de traiter le timbre de manière aussi générale que la hauteur.

Ce contraste s'explique par une différence historique entre hauteur et timbre. Pour la hauteur, les rapports de fréquences de **Pythagore**, l'intonation juste de **Gioseffo Zarlino** et la dérivation mathématique du tempérament égal à douze degrés par **Zhu Zaiyu** ont fourni, à une époque où musique et mathématiques étaient bien moins séparées qu'aujourd'hui, des repères quantitatifs communs. Ces systèmes d'accordage décrivent cependant les relations entre hauteurs; ils ne rendent compte ni des différences de timbre entre instruments ni des transformations continues du timbre au cours de l'exécution.

**Atlas Enharmonic Spectra** prend donc pour objet premier non pas les spectres isolés, mais **la distance entre spectres**. À partir de ces relations mesurables, il construit un espace des timbres, quantifie la **Klangfarbenmelodie** imaginée par Schönberg et en prolonge le principe vers la **Klangfarbenharmonie**. Il fournit ainsi une base commune pour comparer la fusion et la divergence des timbres dans l'ensemble et pour soutenir les décisions d'interprétation, d'orchestration et de composition.

---

L'analyse n'utilise que des **grandeurs physiquement observables**, sans recourir à des évaluations perceptives ni à des questionnaires subjectifs. Chaque enregistrement est décomposé en spectre de fréquences; le spectre normalisé est interprété, suivant l'interprétation probabiliste de **Born**, comme une fonction de densité de probabilité. Ce modèle s'inspire du fonctionnement de la cochlée, où les composantes fréquentielles sont séparées spatialement le long de la membrane basilaire avant d'être détectées par les cellules ciliées. Afin d'assurer la reproductibilité et d'éviter toute arbitraire, cette décomposition est réalisée par **Fast Fourier Transform (FFT)**.

Ces dernières années, la **géométrie de Wasserstein** s'est imposée comme un cadre donnant aux distributions de probabilité une structure géométrique fondée sur le transport optimal. Les travaux de **Shun-ichi Amari** et de ses collaborateurs ont notamment ouvert de nouvelles perspectives entre transport optimal et géométrie de l'information. Ce dépôt applique cette approche à l'analyse du timbre et décrit les transformations de timbre comme le **coût minimal de transport nécessaire pour déplacer la masse spectrale d'une distribution normalisée vers une autre**.

Bien que le dépôt fournisse également des distances de Wasserstein L2 et des variantes en fréquence logarithmique, la recherche associée adopte systématiquement la **distance de Wasserstein L1**, car elle conserve la masse spectrale tout en exprimant directement le transport le long de l'axe des fréquences comme une distance.

Pour deux distributions de probabilité unidimensionnelles $P$ et $Q$, la distance de Wasserstein L1 est définie par

$$
W_1(P,Q)=\int_{-\infty}^{\infty}\Bigl\lvert F_P(x)-F_Q(x)\Bigr\rvert\ \mathrm dx,
$$

où $F_P$ et $F_Q$ sont les fonctions de répartition des spectres normalisés,

$$
F_P(x)=\int_{-\infty}^{x}P(y)\ \mathrm dy,\qquad
F_Q(x)=\int_{-\infty}^{x}Q(y)\ \mathrm dy.
$$

Comme **Atlas Enharmonic Spectra** travaille sur des spectres FFT discrets, les distributions cumulées sont calculées sous la forme

$$
F_P[i]=\sum_{j=0}^{i}P[j],\qquad
F_Q[i]=\sum_{j=0}^{i}Q[j].
$$

```python
cdf_P = np.cumsum(spectrum_P)
cdf_Q = np.cumsum(spectrum_Q)
```

La distance de Wasserstein L1 discrète devient alors

$$
W_1(P,Q)=\sum_i\Bigl\lvert F_P[i]-F_Q[i]\Bigr\rvert\Delta f.
$$

```python
return np.sum(np.abs(cdf_P - cdf_Q)) * df
```

où

$$
\Delta f=\frac{f_s}{N}\approx0.092\ \mathrm{Hz}
$$

est la résolution fréquentielle de la FFT.

Cette formulation conserve la probabilité spectrale tout en mesurant la quantité de masse spectrale à déplacer ainsi que la distance de ce déplacement. Les différences de timbre apparaissent ainsi non comme de simples écarts entre pics spectraux, mais comme le travail minimal nécessaire pour réorganiser l'ensemble du spectre.

Ce cadre conduit à des modèles d'espace métrique pour le **Klangfarbenakkord** et la **Klangfarbenharmonie**. En plaçant les timbres instrumentaux dans un espace métrique commun, il devient possible de quantifier la fusion et la divergence orchestrales et de soutenir une pratique compositionnelle prolongeant la **Klangfarbenmelodie** vers la **Klangfarbenharmonie**.

Le dépôt a vocation à constituer une base commune permettant de comparer les timbres selon une échelle fondée sur des grandeurs physiques et à soutenir des applications en **Klangfarbenmelodie**, **Klangfarbenharmonie**, conception d'ensembles et orchestration.

## 📖 Citation

Si vous utilisez ce jeu de données, veuillez citer l'article correspondant.

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

Article : [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026)

## 📖 Références

1. Arnold Schönberg. *Harmonielehre*. Universal Edition, Vienne (1911).
2. Shun-ichi Amari. *Differential Geometry of Curved Exponential Families—Curvatures and Information Loss*. *The Annals of Statistics* **10**(2), pp.357–385 (1982).
3. Shun-ichi Amari. *Differential-Geometrical Methods in Statistics* (Lecture Notes in Statistics, **28**). Springer-Verlag (1985).
4. [Jinyong Lee et Ken Ito. *Sparse FFT: A New High-Resolution Frequency Analysis and Its Applications*. *JASTICE* **8**(2), pp.188–193 (2021/2022).](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/)
5. [Yusei Tamura, Shigekazu Ishihara et Ken Ito. *Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*. *arXiv*, arXiv:2608.28026.](https://arxiv.org/abs/2608.28026)