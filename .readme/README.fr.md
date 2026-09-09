Language: | [English](../README.md) | [日本語](README.ja.md) | Français | [Deutsch](README.de.md)

> *Klangfarbenmelodien! Welche feinen Sinne, die hier unterscheiden, welcher hochentwickelte Geist, der an so subtilen Dingen Vergnügen finden mag!*
>
> *Wer wagt hier Theorie zu fordern!*
>
> — Arnold Schönberg, *Harmonielehre* (1911)

> *« Mélodies de timbre ! Quelle finesse des sens peut distinguer de telles différences ! Quel esprit hautement cultivé peut trouver du plaisir dans d'aussi subtiles nuances sonores ! »*
>
> *« Qui osera poursuivre ici une théorie nouvelle ? »*
>
> — A. Schönberg, *Traité d'harmonie* (1911)

Le compositeur **Arnold Schönberg** écrivit ces lignes à la fin de *Harmonielehre* (1911), publié en mémoire de son maître et ami proche, le compositeur et chef d'orchestre **Gustav Mahler**.

Face à ce défi, **Alban Berg**, **Anton Webern**, puis après la Seconde Guerre mondiale **Luigi Nono**, **Pierre Boulez** et **Karlheinz Stockhausen** y consacrèrent leur vie sans jamais parvenir à établir une méthode satisfaisante. Eux — et la musique elle-même — avaient devancé l'histoire des sciences.

Au XXIe siècle, la théorie de la **géométrie de l'information** de **Shun-ichi Amari** (1982/85–) permet de mesurer la **distance entre les timbres** comme une grandeur physique exacte exprimée en hertz. Dès lors deviennent possibles les géodésiques de timbre, une géométrie des accords et de l'harmonie, et finalement cette **harmonie des timbres** imaginée par Schönberg au-delà de l'harmonie fondée sur les hauteurs. Ce dépôt développe ce cadre comme une tentative d'ouvrir un nouveau chapitre de l'histoire musicale.

# Atlas Enharmonic Spectra

*« Klangfarbenharmonie » — Invitation à l'accordage spectral pour les ensembles harmoniques.*

*« Harmonie des timbres » — Accordage spectral pour les ensembles harmoniques.*

---

**Atlas Enharmonic Spectra** est un jeu de données chromatique de sons tenus instrumentaux et vocaux, accompagné d'un système de calcul en géométrie de l'information musicale, développé pour faire progresser **Klangfarbenharmonie** et **Klangfarbenakkord** dans la pratique des ensembles.

Outre des enregistrements normalisés couvrant toute l'étendue pratique de chaque instrument, le dépôt comprend l'extraction spectrale par FFT, l'entropie intrinsèque de Shannon des spectres normalisés, les scripts de calcul des distances de Wasserstein et des matrices de distances précalculées. Il constitue la base expérimentale du cadre présenté pour la première fois dans [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026), où les relations entre timbres sont décrites par le transport optimal entre spectres normalisés.

Il est conçu comme un outil pratique destiné à la composition, à l'orchestration et à l'interprétation, permettant de comparer les timbres au-delà des différences de hauteur, d'instrument et de technique de jeu.

![L1 Wasserstein distance matrix](distanceMatrix_L1/distance_matrix_selected_heatmap.png)

## ✨ Caractéristiques

- **24 catégories d'instruments** (bois, cuivres, cordes, signaux de référence, etc. ; extension continue)

- **1 141 enregistrements WAV** (sons tenus chromatiques ; extension continue)

  - Fréquence d'échantillonnage : $f_s=96\ \mathrm{kHz}$

  - Nombre d'échantillons : $N=2^{20}$

  - Durée normalisée : $N/f_s=10.922666\ldots\ \mathrm{sec}$

  - Voir [*Sparse FFT: A New High-Resolution Frequency Analysis and Its Applications*](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/).

- Convention uniforme de nommage des fichiers incluant hauteur notée, hauteur réelle et conditions d'exécution

- Scripts de calcul des distances de Wasserstein L1 et L2 entre spectres

- Matrices de distances de Wasserstein précalculées

## 📁 Structure du dépôt

```text
atlas-enharmonic-spectra/
├── wav/
│   ├── fl/          # Flûte
│   ├── ob/          # Hautbois
│   ├── cl-inEs/     # Clarinette en mi♭
│   ├── cl-inB/      # Clarinette en si♭
│   ├── basscl/      # Clarinette basse
│   ├── va/          # Alto
│   └── ...          # etc.
│
├── distanceMatrix_L1/    # Matrices L1 précalculées
├── distanceMatrix_L2/    # Matrices L2 précalculées
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py
```

Chaque dossier d'instrument contient des enregistrements de sons tenus chromatiques. Certains instruments comprennent également des doigtés alternatifs, des sourdines et d'autres variantes d'exécution.

## 🏷️ Nommage des fichiers

Exemples :

```text
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

Selon l'instrument, le nom de fichier peut contenir :

- hauteur réelle (`conc-*`)
- hauteur notée (`writ-*`)
- numéro d'harmonique (`ovt-*`)
- position ou doigté (`pos-*`)
- type de sourdine (`mute-*`)
- autre condition d'exécution

## ▶️ Procédure d'exécution

Exécutez les programmes Python en suivant l'organigramme ci-dessous afin de générer des matrices de distances de Wasserstein sous forme de fichiers CSV et de cartes thermiques PNG.

![Procédure d'exécution](.readme/flowchart.svg)

## 🎼 Contexte de la recherche

Dans *Harmonielehre* (1911), Arnold Schönberg écrivait qu'il devrait devenir possible

> *« ...solche **Folgen** herzustellen, deren Beziehung untereinander mit einer Art Logik wirkt, ganz äquivalent jener Logik, die uns bei der Melodie der Klanghöhen genügt. »*

> *« ...de créer de telles **successions** dont les relations mutuelles fonctionnent selon une logique entièrement équivalente à celle qui nous satisfait dans la mélodie des hauteurs. »*

Il reconnaissait en même temps qu'il s'agissait encore, à son époque, d'une vision de l'avenir.

> *« Das scheint eine Zukunftsphantasie und ist es wahrscheinlich auch. Aber eine, von der ich fest glaube, daß sie sich verwirklichen wird. »*

> *« Cela semble être un fantasme d'avenir, et c'en est probablement un. Mais je crois fermement qu'il finira par se réaliser. »*

Cette **vision d'avenir** fut ensuite reprise par **Webern**, **Messiaen**, **Nono**, **Boulez**, **Stockhausen** et bien d'autres compositeurs. Le sérialisme d'après-guerre étendit l'organisation au-delà des hauteurs vers les durées, les dynamiques et le timbre lui-même. Pourtant, aucune méthode ne permit d'organiser le timbre selon un principe commun comparable à celui des hauteurs.

Ce contraste reflète les histoires différentes de la hauteur et du timbre. Les rapports de fréquences de **Pythagore**, l'intonation juste de **Gioseffo Zarlino** et la dérivation mathématique du tempérament égal à douze sons par **Zhu Zaiyu** appartiennent à une époque où musique et mathématiques étaient beaucoup moins séparées qu'aujourd'hui, établissant des moyens quantitatifs de relier les hauteurs par les nombres. Ces systèmes d'accord décrivent toutefois les relations entre les hauteurs ; ils ne décrivent ni les différences de timbre entre instruments, ni les transformations continues du timbre pendant l'exécution. Ainsi, tandis que la hauteur s'est dotée d'un cadre théorique précis, le timbre n'a jamais reçu un système d'organisation d'une portée comparable.

Au lieu de considérer les spectres individuels comme objets premiers, **Atlas Enharmonic Spectra** prend les **distances entre spectres** comme objet fondamental. À partir de ces relations mesurables, il construit un espace des timbres, quantifie la **Klangfarbenmelodie** de Schönberg et prolonge son idée vers la **Klangfarbenharmonie**, offrant une base commune pour comparer les convergences et divergences de timbre au sein des ensembles et soutenir les décisions d'interprétation, d'orchestration et de composition.

---

L'analyse repose exclusivement sur des **grandeurs physiquement observables**, jusqu'au moment immédiatement antérieur à la perception auditive. Chaque enregistrement est décomposé en spectre de fréquences, dont la forme normalisée est interprétée comme une fonction de densité de probabilité selon **l'interprétation probabiliste de Born**. Ce modèle s'inspire du mécanisme biologique par lequel la cochlée sépare spatialement les composantes fréquentielles et les cellules ciliées de la membrane basilaire les détectent. Afin d'assurer la reproductibilité tout en éliminant les choix arbitraires de traitement, la décomposition spectrale est réalisée au moyen de la **Transformée de Fourier Rapide (FFT)**.

Ces dernières années, la **géométrie de Wasserstein** s'est imposée en géométrie de l'information, en statistique et en apprentissage automatique comme un cadre conférant une structure géométrique aux distributions de probabilité par le transport optimal. Les travaux de **Shun-ichi Amari** et de ses collaborateurs ont notamment joué un rôle majeur dans la mise en évidence de nouveaux liens entre transport optimal et géométrie de l'information. Ce dépôt applique ce cadre à l'analyse du timbre en décrivant les transformations de timbre comme **le coût minimal de transport nécessaire pour déplacer la masse spectrale d'une distribution spectrale normalisée vers une autre**.

Bien que le dépôt comprenne également des distances de Wasserstein L2 et des variantes en fréquence logarithmique, les recherches associées adoptent systématiquement la **distance de Wasserstein L1**, car elle préserve la masse spectrale tout en exprimant directement le transport le long de l'axe des fréquences comme une distance.

Pour des distributions de probabilité unidimensionnelles $P$ et $Q$, la distance de Wasserstein L1 est définie par

$$
W_1(P,Q)=\int_{-\infty}^{\infty}\Bigl\lvert F_P(x)-F_Q(x)\Bigr\rvert\ \mathrm dx,
$$

où $F_P$ et $F_Q$ sont les fonctions de répartition

$$
F_P(x)=\int_{-\infty}^{x}P(y)\ \mathrm dy,\qquad
F_Q(x)=\int_{-\infty}^{x}Q(y)\ \mathrm dy.
$$

Comme **Atlas Enharmonic Spectra** travaille sur des spectres FFT discrets, ces distributions cumulées sont calculées comme

$$
F_P[i]=\sum_{j=0}^{i}P[j],\qquad
F_Q[i]=\sum_{j=0}^{i}Q[j].
$$

```python
cdf_P = np.cumsum(spectrum_P)
cdf_Q = np.cumsum(spectrum_Q)
```

La distance discrète de Wasserstein L1 est ensuite calculée par

$$
W_1(P,Q)=\sum_i\Bigl\lvert F_P[i]-F_Q[i]\Bigr\rvert\Delta f,
$$

```python
return np.sum(np.abs(cdf_P - cdf_Q)) * df
```

où

$$
\Delta f=\frac{f_s}{N}\approx0.092\ \mathrm{Hz}
$$

est la résolution fréquentielle de la FFT.

Cette formulation préserve la probabilité spectrale tout en mesurant la quantité de masse spectrale à déplacer et la distance sur laquelle elle doit être transportée. Les différences de timbre sont ainsi représentées non comme des écarts entre pics isolés, mais comme le travail minimal nécessaire pour réorganiser l'ensemble de la distribution spectrale.

De ce cadre émergent des modèles d'espace métrique pour **Klangfarbenakkord** et **Klangfarbenharmonie**. En plaçant les timbres instrumentaux dans un espace métrique commun, le dépôt favorise l'évaluation quantitative des fusions et séparations orchestrales tout en prolongeant la **Klangfarbenmelodie** vers une **Klangfarbenharmonie** applicable en pratique.

Le dépôt vise ainsi à fournir une base physique commune pour comparer les timbres, soutenant la pratique de la Klangfarbenmelodie et de la Klangfarbenharmonie, ainsi que leurs applications à la conception d'ensembles et à l'orchestration.

## 📖 Citation

Si vous utilisez ce jeu de données, veuillez citer l'article correspondant.

```bibtex
@misc{tamura2026klangfarbenklangfarbenharmonien,
  title={Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1},
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

5. [Yusei Tamura, Shigekazu Ishihara et Ken Ito. *Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*. *arXiv*, arXiv:2608.28026 (2026).](https://arxiv.org/abs/2608.28026)