Sprache: | [English](../README.md) | [日本語](README.ja.md) | [Français](README.fr.md) | Deutsch

> Klangfarbenmelodien! Welche feinen Sinne, die hier unterscheiden, welcher hochentwickelte Geist, der an so subtilen Dingen Vergnügen finden mag!
>
> Wer wagt hier Theorie zu fordern!
>
> — Arnold Schönberg, *Harmonielehre* (1911)

Der Komponist **Arnold Schönberg** schrieb diese Worte am Ende seiner *Harmonielehre* (1911), die er im Gedenken an seinen Lehrer und Freund, den Komponisten und Dirigenten **Gustav Mahler**, veröffentlichte.

Dieser Herausforderung stellten sich später **Alban Berg**, **Anton Webern** sowie nach dem Zweiten Weltkrieg **Luigi Nono**, **Pierre Boulez** und **Karlheinz Stockhausen**. Dennoch gelang es keinem von ihnen, im Laufe seines Lebens eine angemessene Methode zu entwickeln. In gewisser Weise waren sie der Wissenschaftsgeschichte voraus.

Im 21. Jahrhundert ermöglicht uns die von **Shun-ichi Amari** entwickelte **Informationsgeometrie** (1982/85–), den **Abstand zwischen Klangfarben** als exakte physikalische Größe in Hertz zu messen. Daraus ergeben sich Klangfarben-Geodäten, eine Geometrie von Akkorden und Harmonie sowie letztlich die Verwirklichung jener von Schönberg erträumten **Klangfarbenharmonie**, die über die herkömmliche, allein auf Tonhöhen gegründete Harmonie hinausgeht. Im Folgenden entfalten wir diesen Ansatz als Versuch, ein neues Kapitel der Musikgeschichte aufzuschlagen.

# Atlas Enharmonic Spectra

*„Klangfarbenharmonie“ — Invitation to the spectral tuning for harmonic ensembles.*

---

**Atlas Enharmonic Spectra** ist ein chromatischer Longtone-Datensatz instrumentaler und vokaler Klänge sowie ein informationsgeometrisches Berechnungssystem für Musik, das zur Weiterentwicklung von **Klangfarbenharmonie** und **Klangfarbenakkord** im Ensemble geschaffen wurde.

Neben standardisierten Aufnahmen über den gesamten praktischen Tonumfang jedes Instruments enthält das Repository FFT-basierte Spektralanalyse, Skripte zur Berechnung der Wasserstein-Distanz sowie vorab berechnete Distanzmatrizen. Es bildet die experimentelle Grundlage des erstmals in [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026) vorgestellten Rahmens, der Klangbeziehungen durch optimalen Transport zwischen normierten Spektren beschreibt.

Das Repository dient als praktisches Hilfsmittel für Komposition, Instrumentation und Aufführungspraxis und ermöglicht den Vergleich von Klangfarben über Tonhöhen, Instrumente und Spielweisen hinweg.

![L1 Wasserstein distance matrix](../distanceMatrix_L1/distance_matrix_selected_heatmap.png)

## ✨ Merkmale

- **24 Instrumentenkategorien** (Holzbläser, Blechbläser, Streicher, Referenzsignale u. a.; fortlaufend erweitert)
- **1.141 WAV-Aufnahmen** (chromatische Longtones; fortlaufend erweitert)
  - Abtastrate: $f_s=96\ \mathrm{kHz}$
  - Anzahl der Samples: $N=2^{20}$
  - Einheitliche Aufnahmelänge: $N/f_s=10.922666\ldots\ \mathrm{s}$
  - Siehe [*Sparse FFT: 新しい高分解能周波数解析とその応用*](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/).
- Einheitliches Benennungssystem mit notierter Tonhöhe, klingender Tonhöhe und Angaben zur Spielweise.
- Skripte zur Berechnung der L1- und L2-Wasserstein-Distanzen zwischen Spektren.
- Vorab berechnete Wasserstein-Distanzmatrizen.

## 📁 Repository-Struktur

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
├── distanceMatrix_L1/    # Vorberechnete L1-Wasserstein-Matrizen
├── distanceMatrix_L2/    # Vorberechnete L2-Wasserstein-Matrizen
├── py00_wasserstein_calcDistance_FFT.py
└── py01_wasserstein_visualize_distanceMatrix_*.py
```

Jedes Instrumentenverzeichnis enthält chromatische Longtone-Aufnahmen. Je nach Instrument sind außerdem alternative Griffe, Dämpfer und weitere Spielvarianten enthalten.

## 🏷️ Dateibenennung

Beispiele:

```text
fl012_C5.wav
altofl018_conc-Cis5_writ-Fis5.wav
basstrb045_F4_ovt-06_pos-I.wav
```

Je nach Instrument können Dateinamen folgende Informationen enthalten:

- klingende Tonhöhe (`conc-*`)
- notierte Tonhöhe (`writ-*`)
- Obertonnummer (`ovt-*`)
- Position oder Griff (`pos-*`)
- Dämpfertyp (`mute-*`)
- Spielbedingung

## ▶️ Ausführungsablauf

Führen Sie die Python-Programme gemäß dem folgenden Flussdiagramm aus, um je nach Zielsetzung Wasserstein-Distanzmatrizen als CSV-Dateien sowie als PNG-Heatmaps zu erzeugen.

![Ausführungsablauf](flowchart.svg)

## 🎼 Forschungshintergrund

Arnold Schönberg schrieb in seiner *Harmonielehre* (1911):

> *„...Folgen herzustellen, deren Beziehung untereinander mit einer Art Logik wirkt, ganz äquivalent jener Logik, die uns bei der Melodie der Klanghöhen genügt.“*

und brachte damit die Hoffnung zum Ausdruck, dass solche Klangfolgen eines Tages möglich werden könnten.

Zugleich erkannte er an, dass dies damals noch Zukunftsmusik war.

> *„Das scheint eine Zukunftsphantasie und ist es wahrscheinlich auch. Aber eine, von der ich fest glaube, daß sie sich verwirklichen wird.“*

Diese **Zukunftsphantasie** wurde später von **Webern**, **Schaeffer**, **Stockhausen**, **Ligeti** und vielen anderen Komponisten aufgegriffen. Insbesondere der Serialismus der Nachkriegszeit weitete die Organisation nicht nur auf Tonhöhen, sondern auch auf Dauern, Dynamik und Klangfarben aus. Dennoch gelang es innerhalb der musikalischen Praxis nicht, Klangfarben durch ein ebenso allgemeines Ordnungsprinzip zu behandeln wie Tonhöhen.

Dieser Gegensatz hat historische Gründe. Für Tonhöhen entstanden mathematische Beschreibungen durch die Frequenzverhältnisse des **Pythagoras**, die reine Stimmung von **Gioseffo Zarlino** und die mathematische Herleitung der Zwölfton-Gleichstufigkeit durch **Zhu Zaiyu**. In einer Zeit, in der Musik und Mathematik weit weniger getrennt waren als heute, entstanden dadurch gemeinsame quantitative Maßstäbe für Tonhöhen. Solche Stimmungssysteme beschreiben jedoch Beziehungen zwischen Tonhöhen, nicht zwischen Klangfarben, und sie erfassen weder Unterschiede zwischen Instrumenten noch kontinuierliche Klangfarbenveränderungen während des Spiels.

**Atlas Enharmonic Spectra** behandelt daher nicht einzelne Spektren als primäres Objekt, sondern **die Distanz zwischen Spektren**. Dadurch wird ein Klangfarbenraum aus messbaren Beziehungen konstruiert, Schönbergs **Klangfarbenmelodie** quantifiziert und ihr Gedanke zur **Klangfarbenharmonie** erweitert. So entsteht eine gemeinsame Grundlage, um Klangverschmelzung und Klangkontrast im Ensemble zu vergleichen und Entscheidungen in Aufführung, Instrumentation und Komposition zu unterstützen.

---

Die Analyse verwendet ausschließlich **physikalisch beobachtbare Größen** und verzichtet auf Wahrnehmungsbewertungen oder subjektive Fragebögen. Jede Aufnahme wird in ihr Frequenzspektrum zerlegt; das normierte Spektrum wird nach **Borns Wahrscheinlichkeitsinterpretation** als Wahrscheinlichkeitsdichtefunktion aufgefasst. Das Modell orientiert sich an der Physiologie der Cochlea, in der Frequenzanteile entlang der Basilarmembran räumlich getrennt und von den Haarzellen erfasst werden. Zur Gewährleistung von Reproduzierbarkeit und zur Vermeidung von Willkür erfolgt die Zerlegung mittels **Fast Fourier Transform (FFT)**.

In den letzten Jahren hat sich die **Wasserstein-Geometrie** als Rahmen etabliert, der Wahrscheinlichkeitsverteilungen durch optimalen Transport eine geometrische Struktur verleiht. Besonders die Arbeiten von **Shun-ichi Amari** und seinen Mitarbeitern haben neue Verbindungen zwischen optimalem Transport und Informationsgeometrie aufgezeigt. Dieses Repository überträgt diesen Ansatz auf die Klangfarbenanalyse und beschreibt Klangveränderungen als **minimalen Transportaufwand, der erforderlich ist, um Spektralmasse von einer normierten Spektralverteilung in eine andere zu überführen**.

Obwohl das Repository auch L2-Wasserstein-Distanzen und logarithmische Frequenzvarianten bereitstellt, verwendet die begleitende Forschung konsequent die **L1-Wasserstein-Distanz**, da sie die Spektralmasse erhält und den Transport entlang der Frequenzachse unmittelbar als Distanz ausdrückt.

Für eindimensionale Wahrscheinlichkeitsverteilungen $P$ und $Q$ ist die L1-Wasserstein-Distanz definiert als

$$
W_1(P,Q)=\int_{-\infty}^{\infty}\Bigl\lvert F_P(x)-F_Q(x)\Bigr\rvert\ \mathrm dx,
$$

wobei $F_P$ und $F_Q$ die Verteilungsfunktionen der normierten Spektren sind,

$$
F_P(x)=\int_{-\infty}^{x}P(y)\ \mathrm dy,\qquad
F_Q(x)=\int_{-\infty}^{x}Q(y)\ \mathrm dy.
$$

Da **Atlas Enharmonic Spectra** mit diskreten FFT-Spektren arbeitet, werden die kumulativen Verteilungen als

$$
F_P[i]=\sum_{j=0}^{i}P[j],\qquad
F_Q[i]=\sum_{j=0}^{i}Q[j]
$$

berechnet.

```python
cdf_P = np.cumsum(spectrum_P)
cdf_Q = np.cumsum(spectrum_Q)
```

Die diskrete L1-Wasserstein-Distanz ergibt sich anschließend zu

$$
W_1(P,Q)=\sum_i\Bigl\lvert F_P[i]-F_Q[i]\Bigr\rvert\Delta f.
$$

```python
return np.sum(np.abs(cdf_P - cdf_Q)) * df
```

Dabei ist

$$
\Delta f=\frac{f_s}{N}\approx0.092\ \mathrm{Hz}
$$

die Frequenzauflösung der FFT.

Diese Formulierung erhält die Spektralwahrscheinlichkeit und misst zugleich, wie viel Spektralmasse über welche Entfernung transportiert werden muss. Klangunterschiede erscheinen dadurch nicht als isolierte Peak-Differenzen, sondern als minimale Arbeit, die zur Umordnung des gesamten Spektrums erforderlich ist.

Aus diesem Rahmen ergeben sich metrische Modelle für **Klangfarbenakkord** und **Klangfarbenharmonie**. Durch die Einbettung instrumentaler Klangfarben in einen gemeinsamen metrischen Raum lassen sich orchestrale Verschmelzung und Divergenz quantitativ bewerten und kompositorische Ansätze unterstützen, die **Klangfarbenmelodie** zur **Klangfarbenharmonie** weiterentwickeln.

Das Repository versteht sich als gemeinsame physikalisch begründete Grundlage für den Vergleich von Klangfarben und soll Anwendungen in **Klangfarbenmelodie**, **Klangfarbenharmonie**, Ensemblegestaltung und Instrumentation unterstützen.

## 📖 Zitieren

Wenn Sie diesen Datensatz verwenden, zitieren Sie bitte die zugehörige Veröffentlichung.

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

Publikation: [*Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*](https://arxiv.org/abs/2608.28026)

## 📖 Literatur

1. Arnold Schönberg. *Harmonielehre*. Universal Edition, Wien (1911).
2. Shun-ichi Amari. *Differential Geometry of Curved Exponential Families—Curvatures and Information Loss*. *The Annals of Statistics* **10**(2), S.357–385 (1982).
3. Shun-ichi Amari. *Differential-Geometrical Methods in Statistics* (Lecture Notes in Statistics, **28**). Springer-Verlag (1985).
4. [Jinyong Lee und Ken Ito. *Sparse FFT: A New High-Resolution Frequency Analysis and Its Applications*. *JASTICE* **8**(2), S.188–193 (2021/2022).](https://jastice.org/2022/05/16/vol-8-2-pp-188-193-2021-2022/)
5. [Yusei Tamura, Shigekazu Ishihara und Ken Ito. *Klangfarbenakkord and Klangfarbenharmonien: Metric Space Models for Music on Informational Geometry 1*. *arXiv*, arXiv:2608.28026.](https://arxiv.org/abs/2608.28026)