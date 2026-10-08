# Iceberg Datasets and Drift Modelling — Research Brief

**Project:** SIH26059 — AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory, and Navigation Decision Support System (MoES / NCPOR)
**Scope:** feeds the iceberg-trajectory component of `docs/ML_ARCHITECTURE.md`. The equations in section (b) are intended to be implemented directly.
**Date of verification:** 2026-09-02. Every URL in section (a) was hit live on that date; HTTP status recorded.

### Verification legend

| Tag | Meaning |
|---|---|
| **VERIFIED** | I fetched the primary source and read the claim in it, or I reproduced the number myself. Source cited inline. |
| **INFERRED** | Derived by me from a verified source (algebra, dimensional analysis, or code reading). Reasoning shown so it can be checked. |
| **UNVERIFIED** | Could not confirm against a primary source. Do not put on a slide without checking. |

> **Do not cite anything in this document tagged UNVERIFIED in the AICTE deck or the viva.** Section 5 lists every open item.

---

## (a) Antarctic iceberg datasets

### Summary table

| # | Dataset | Auth? | Format | Min. size | Coverage | Cadence | Live status (2026-09-02) |
|---|---|---|---|---|---|---|---|
| A1 | **USNIC Antarctic Icebergs** | **No** | CSV / SHP / PDF | ≥20 sq NM **or** ≥10 NM longest axis | 1976–present (operational) | Weekly | **200 OK** |
| A2 | **BYU/NIC Consolidated DB v8.0** | **No** | CSV in ZIP (4.07 MB) | Same as USNIC (NIC-seeded) | 1978 – **22 Apr 2025** | Irregular re-release | **200 OK** |
| A3 | **BYU Statistical DB v7.1** | **No** | CSV in ZIP (2.78 MB) | as above | 1978 – 25 Aug 2023 | Irregular | **200 OK** |
| A4 | **ESSD six-year circum-Antarctic iceberg dataset** | **No** | Shapefile + code (ZIP, 345 MB) | **0.04 km²** | **October only**, 2018–2023 | Static snapshot | **200 OK** |
| A5 | **Copernicus Sentinel-1 (CDSE)** | **Yes — free** | SAFE / COG, OData+STAC+S3 | n/a (raw SAR, 40 m EW) | 2014–present | Sub-daily at high S. lat | **200 OK** |
| A6 | **ALTIBERG v3.1 (Ifremer/CLS lineage)** | **No** | NetCDF-3 | length **< 3 km** (small bergs) | 1992–2021 | Static; v4 → OSI SAF | **200 OK** |
| A7 | **CLS operational iceberg service** | **Commercial** | n/a | n/a | n/a | n/a | **No public product** |

---

### A1 — U.S. National Ice Center, Antarctic Icebergs

**VERIFIED.** Product page: <https://usicecenter.gov/Products/AntarcIcebergs>

Direct, no-auth download endpoints (all returned HTTP 200 on 2026-09-02):

| Product | URL | Notes |
|---|---|---|
| CSV | `https://usicecenter.gov/File/DownloadCurrent?pId=134` | Served inline as text |
| Shapefile ZIP | `https://usicecenter.gov/File/DownloadCurrent?pId=228` | `Content-Disposition: attachment; filename=AntarcticIcebergs_20260827.zip`, 181 187 bytes |
| PDF chart | `https://usicecenter.gov/File/DownloadCurrent?pId=135` | 357 865 bytes |
| Archive search | `https://usicecenter.gov/Products/ArchiveSearchMulti?table=IcebergProducts` | Historical products |

**VERIFIED — live CSV schema and content.** Header row fetched verbatim:

```
Iceberg,Length (NM),Width (NM),Latitude,Longitude,Area (sqMI),Area (sqNM),Area (sqKM),Last Update
A76C,16,7,-53.73,-29.5,112.44,84.90,291.21,08/27/2026
A81,28,25,-58.74,-49.94,518.07,391.20,1341.79,08/27/2026
A83,12,7,-61.12,-50.36,73.29,55.34,189.82,08/27/2026
A84,12,6,-71.58,-101.73,76.06,57.43,196.99,08/27/2026
A85,10,3,-62.85,-53.38,24.18,18.26,62.62,08/27/2026
```

This is directly usable: `Length (NM)` and `Width (NM)` map straight onto the `L` and `W` of the Wagner model (section b), and `Last Update` gives the position timestamp. The file is the **current** snapshot only — building a trajectory time series requires either the archive search endpoint or A2.

**VERIFIED.** Tracking criterion, quoted from the product page: icebergs of *"20 sqNM or greater, or 10 NM on its longest axis."* USNIC *"names, tracks, and documents"* these.

**Implication for this project:** USNIC-tracked bergs are, by construction, **giant** bergs — minimum ~18.5 km on the long axis. Section (b.6) shows that this is precisely the regime where the wind term collapses and `v_iceberg ≈ v_ocean_current`. That is a real architectural constraint, not a nuisance.

---

### A2 / A3 — BYU Center for Remote Sensing, scatterometer iceberg databases

**VERIFIED.** Landing page: <https://www.scp.byu.edu/data/iceberg/database1.html>

| Product | Direct URL | Size | Coverage |
|---|---|---|---|
| Consolidated DB **v8.0** | `https://www.scp.byu.edu/data/iceberg/consolidated_database_v8.0.zip` | 4 065 659 B | 1978 → **22 Apr 2025** |
| Statistical DB **v7.1** | `https://www.scp.byu.edu/data/iceberg/stats_database_v7.1.zip` | 2 784 282 B | 1978 → 25 Aug 2023 |

Both returned HTTP 200, no authentication. Per-sensor archives are also offered (`icebergDatabase_ascat.tar.gz`, `_qscat`, `_oscat`, `_other`).

**Correction to `docs/DATASET.md`:** that document records the consolidated database as ending **August 2023**. The live consolidated release is **v8.0, running to 22 April 2025** — roughly 20 additional months of trajectory data. The Aug-2023 end date belongs to the *statistical* database (v7.1). Update `docs/DATASET.md`.

**VERIFIED — structure.** *"Each zip contains one file per iceberg, named by iceberg designation"*, CSV with self-describing header rows. The **consolidated** database gives multiple sensor readings per date; the **statistical** database gives one daily-mean position plus a surrounding-environment classification and sensor flags.

The per-iceberg-CSV layout is the ideal input shape for a trajectory model: one file = one variable-length track.

**VERIFIED — methodology reference.** Budge, J. S. and Long, D. G., "A comprehensive database for Antarctic iceberg tracking using scatterometer data," *IEEE JSTARS* **11**(2), doi:[10.1109/JSTARS.2017.2784186](https://dx.doi.org/10.1109/JSTARS.2017.2784186). Author PDF (open): <https://www.mers.byu.edu/long/papers/JSTARS2018_budge.pdf>

---

### A4 — ESSD "six-year circum-Antarctic iceberg dataset (2018–2023)" — **the 36,186 lead: CONFIRMED**

**VERIFIED — this is the right dataset.** The brief's "known good lead" (36,186 icebergs in 2022, minimum area exactly 0.04 km²) matches exactly. Read from the full text at <https://essd.copernicus.org/articles/18/147/2026/>:

Per-year detected iceberg counts:

| Year | Icebergs |
|---|---|
| 2018 | 34 825 |
| 2019 | 39 261 |
| 2020 | 38 066 |
| 2021 | 51 420 |
| **2022** | **36 186** ✅ |
| 2023 | 44 537 |

Citation: Chen, Z., Liu, X., Guan, Z., Li, T., Cheng, X., Li, T., Liu, Y., Liang, Q., Zheng, L., and Liu, J.: *A six-year circum-Antarctic icebergs dataset (2018–2023)*, **Earth Syst. Sci. Data 18, 147–166 (2026)**, doi:[10.5194/essd-18-147-2026](https://doi.org/10.5194/essd-18-147-2026).

**VERIFIED specification:**

- Sensor: **Sentinel-1 C-band SAR, Extra Wide swath, 40 m** spatial resolution.
- Extent: **whole Southern Ocean south of 55° S**.
- Minimum iceberg area: **0.04 km²**.
- Method: **incremental random-forest classification + manual correction**; accuracy, precision, recall and F1 all **> 0.90** on the test set, every year.
- Attributes per shapefile record: lat/lon, area (km²), perimeter (km), major-axis length, minor-axis length, **mass (Gt)**, and **uncertainty estimates for area and mass**.
- Named giants (A68a, D28, A69, A74, A76a) are present and were used for cross-comparison against existing databases.

**VERIFIED — data availability, Zenodo record 17165466** (queried via the Zenodo REST API):

| Field | Value |
|---|---|
| DOI | `10.5281/zenodo.17165466` (<https://doi.org/10.5281/zenodo.17165466>) |
| Licence | **CC-BY-4.0** |
| Access | **Open — no authentication.** A `HEAD` on a file content URL returned `HTTP 200`, `content-type: application/octet-stream`, correct `content-length`, with no login redirect. |
| Publication date | 2025-09-20 |

Exact file download URLs:

| File | Bytes | URL |
|---|---|---|
| `Iceberg vector outline.zip` | 345 639 142 | `https://zenodo.org/api/records/17165466/files/Iceberg%20vector%20outline.zip/content` |
| `Iceberg detection code.zip` | 345 689 182 | `https://zenodo.org/api/records/17165466/files/Iceberg%20detection%20code.zip/content` |
| `Iceberg sample set.zip` | 2 921 461 | `https://zenodo.org/api/records/17165466/files/Iceberg%20sample%20set.zip/content` |

> ⚠️ **Critical limitation — read before planning around this dataset.** **VERIFIED:** the dataset covers **October of each year only**. Quoted rationale: *"Sentinel-1 SAR data in October for each year"* was chosen because *"the backscatter coefficient of icebergs is significantly higher"* in that month.
>
> **INFERRED consequence:** six annual snapshots twelve months apart cannot be linked into trajectories. **This dataset is a distribution / detection-training resource, not a drift-training resource.** Use it for (i) training and benchmarking a small-iceberg SAR detector, (ii) climatological priors on where small bergs are, (iii) validating detected size distributions. Use A1/A2 for trajectories. The authors state an intention to move to a "living dataset" with more months, but that does not exist today.

---

### A5 — Copernicus Sentinel-1, via the Copernicus Data Space Ecosystem (CDSE)

**VERIFIED.** Portal: <https://dataspace.copernicus.eu/> — free and open data policy; browsing via the Copernicus Browser needs no account.

**VERIFIED — an account IS required to download.** From <https://documentation.dataspace.copernicus.eu/Quotas.html>: *"every user account is set a limited quota to guarantee fair sharing of free tier resources."* Registration is free.

Free-tier quotas for a "Copernicus General User" (registered), **VERIFIED** from that page:

| Quota | Value |
|---|---|
| Monthly transfer, immediately-available data (IAD) | **12 TB** |
| Monthly transfer, deferred-archive data (DAD) | **0.1 TB** |
| OData / STAC / S3 requests | **50 000 / month** |
| Sentinel Hub API requests | **50 000 / month** |
| openEO | **10 000 processing units / month** |
| Concurrent connections (S3/OData/STAC) | **4**, at 20 MB/s each |
| Post-quota behaviour | bandwidth throttled to **1 MB/s** |

Access APIs: **OData**, **STAC**, **S3**, **openEO**, **Sentinel Hub**.

**INFERRED, practical:** 12 TB/month and 4 concurrent connections are ample for a hackathon-scale AOI. The 0.1 TB DAD cap is the one that bites — older Sentinel-1 EW scenes may sit in the deferred archive, so **pull the SAR training tiles early, not on demo day**. Prefer the ESSD Zenodo bundle (A4) for detector training since the labels are already made.

---

### A6 — ALTIBERG v3.1 — small-iceberg database from satellite altimetry

This is the dataset that fills the gap USNIC leaves: **sub-3-km icebergs**, which are the ones that actually threaten a ship and which USNIC does not track at all.

**VERIFIED.** Metadata record (Ifremer Sextant): <https://sextant.ifremer.fr/record/06770b5a-b8aa-4a59-b66d-304c2bf9b548/>

| Field | Value |
|---|---|
| Detection target | small icebergs, **length < 3 km**, from high-resolution altimeter waveform analysis |
| Temporal coverage | **1992-01-01 → 2021-12-31**, monthly gridded resolution |
| Spatial coverage (Antarctic) | 90° S – 40° S, 180° W – 180° E |
| Format | **NetCDF-3** |
| DOI | `10.12770/06770b5a-b8aa-4a59-b66d-304c2bf9b548` |
| Licence | **CC-BY 4.0** |
| Auth | **None** |

Download (HTTP 200 verified 2026-09-02):

- HTTPS: `https://data-cersat.ifremer.fr/data/sea-ice/icebergs/altiberg/v3.1/`
- FTP: `ftp://ftp.ifremer.fr/ifremer/cersat/data/sea-ice/icebergs/altiberg/v3.1/`
- Technical report (verified, downloaded and read): `https://data-cersat.ifremer.fr/data/sea-ice/icebergs/altiberg/v3.1/documentation/ALTIBERG-rep_v3-1.pdf`

**VERIFIED from the technical report:**

- v3.1 extends v3.0 by adding 2021; total span **1992–2021**. HY-2A failed September 2020; six altimeters still operating in 2021. Sentinel-6 is **not** yet included ("detection algorithm is under development").
- Missions merged: ERS-1, ERS-2, Topex, Poseidon, Jason-1/2/3, ENVISAT, CryoSat-2, SARAL, HY-2A, HY-2B, Sentinel-3A, Sentinel-3B.
- Two detection algorithms: one for classical Low-Resolution Mode, one for high-resolution (SAR-mode) altimeters.
- **Level 2** = individual along-track iceberg detections. **Level 3** = gridded monthly products, in two grids: Antarctic polar stereographic at **100 km**, and geographic equirectangular at **1° lat × 2° lon**. L3 fields include monthly ice volume, probability of iceberg presence, and mean iceberg area.
- Detection sensitivity range quoted in the report: distance from nadir 0–12 km, **area 0.01–9 km²**.

**Reference paper (VERIFIED as cited by AVISO):** Tournadre, J., Bouhier, N., Girard-Ardhuin, F., and Rémy, F. (2016), *Antarctic icebergs distributions 1992–2014*, **J. Geophys. Res. Oceans 121**, 327–349, doi:[10.1002/2015JC011178](https://doi.org/10.1002/2015JC011178).

**VERIFIED — successor.** EUMETSAT **OSI SAF** is taking over ALTIBERG to produce a climate product spanning 1992 → present, as *"Iceberg from Altimetry CDR/ICDR (OSI-490 and OSI-480)"*, i.e. ALTIBERG v4. Source: <https://osi-saf.eumetsat.int/community/stories/eumetsat-osi-saf-iceberg-climate-products>. **UNVERIFIED:** I did not confirm whether OSI-490/OSI-480 are operationally released yet, nor their download URL. If a near-real-time small-iceberg feed matters to the demo, this is the single highest-value thing left to chase.

> **Coverage gap to state honestly in the deck:** ALTIBERG stops at **end 2021**. There is currently **no verified public, free, near-real-time small-iceberg (<3 km) product for the Southern Ocean**. Small-berg risk in the live system must therefore come from our own Sentinel-1 detector (A4/A5), not from an off-the-shelf feed.

---

### A7 — CLS (Collecte Localisation Satellites)

**VERIFIED — CLS runs an operational Antarctic iceberg service, but there is no public product.** CLS (a subsidiary of CNES) has supplied iceberg detection and drift for the Vendée Globe **since 2008**, and originated the race's **Antarctic Exclusion Zone (AEZ)**. Sources:

- <https://www.cls.fr/en/press/iceberg-straight-ahead-cls-ensures-vendee-globe-safety-from-space/>
- <https://www.cls.fr/en/the-ocean-race-14th-edition-iceberg-detection-from-space/>
- ESA: <https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Copernicus_satellites_keep_eyes_on_icebergs_for_Vendee_Globe>

Their operational stack, **VERIFIED** from those pages: SAR (Sentinel-1A, RADARSAT-2) + optical (MODIS, VIIRS) + **four altimeters** (Jason-3, SARAL/AltiKa, Sentinel-3A, Sentinel-3B); each detected berg is fed into a **trajectory forecast model**, and the AEZ boundary is adjusted in real time from those forecasts.

**Assessment: commercial, bespoke, per-client. No downloadable public Antarctic iceberg product exists.** Do not plan any component around CLS data.

**Two things worth taking from CLS anyway:**
1. Their architecture — multi-sensor detection → per-berg drift forecast → **dynamically-adjusted exclusion polygon** — is precisely the architecture this project is proposing. That is a strong "this is how the operational state of the art works" citation for the deck.
2. It is the clearest existing example of the *output artefact* being a **moving keep-out zone**, not a list of berg positions. See section (d).

---

## (b) Wagner, Dell & Eisenman (2017) — full implementable form

**Primary sources, both verified:**

- Wagner, T. J. W., Dell, R. W., and Eisenman, I., **"An Analytical Model of Iceberg Drift"**, *J. Phys. Oceanogr.* **47**(7), 1605–1616, doi:[10.1175/JPO-D-16-0262.1](https://doi.org/10.1175/JPO-D-16-0262.1). Preprint arXiv:[1610.06403](https://arxiv.org/abs/1610.06403) — **downloaded and read in full**; all equations below are transcribed from it.
- **Reference MATLAB implementation**, `WDE17_iceberg_model.m`, at <https://www.tillwagner.me/wde17> — **read**; used to resolve two ambiguities the paper's typesetting leaves open (see b.5 and b.9). Supporting `.mat` forcing files are on Dropbox: <https://www.dropbox.com/sh/9qc7l3yacyqgn3c/AAC69yLJUH39VsjbEwAdRRMOa?dl=0>

---

### b.1 The full classical momentum balance (what Wagner simplifies)

**VERIFIED — WDE17 eq. (1)**, the canonical form used by Bigg et al. (1997), Gladstone et al. (2001), Martin & Adcroft (2010), Roberts et al. (2014):

$$ M\frac{d\vec v_i}{dt} \;=\; -M f\,\hat k\times\vec v_i \;+\; F_w \;+\; F_a \;+\; F_p \;+\; F_r \;+\; F_i $$

| Term | Name | WDE17 treatment |
|---|---|---|
| $-Mf\,\hat k\times\vec v_i$ | Coriolis | **retained** |
| $F_w$ | water (form) drag | **retained** |
| $F_a$ | air (form) drag | **retained** |
| $F_p$ | pressure-gradient force / sea-surface tilt | **retained**, reduced to geostrophy |
| $F_r$ | **wave radiation** force | **dropped** (assumption 4) |
| $F_i$ | **sea-ice drag** | **dropped** (assumption 4) |

**VERIFIED — drag terms, eq. (2):**

$$ F_w = \tilde C_w\,|\vec v_w-\vec v_i|(\vec v_w-\vec v_i), \qquad F_a = \tilde C_a\,|\vec v_a-\vec v_i|(\vec v_a-\vec v_i) $$

with

$$ \tilde C_w \equiv \tfrac12\rho_w C_w A_w, \qquad \tilde C_a \equiv \tfrac12\rho_a C_a A_a $$

**VERIFIED — the five assumptions** (paper's own wording, condensed):

1. Instantaneous acceleration is negligible: $M\,d\vec v_i/dt \approx 0$. *(steady-state / quasi-instantaneous adjustment)*
2. The pressure-gradient force is approximated from the ocean velocity assuming geostrophy, giving $F_p = M f\,\hat k\times\vec v_w$.
3. $|\vec v_i| \ll |\vec v_a|$, so $\vec v_a - \vec v_i \simeq \vec v_a$. Justified as $V_a \sim 10$ m/s vs $V_i \sim 0.1$ m/s.
4. Sea-ice drag and wave radiation are small compared with air drag, water drag, Coriolis and pressure gradient.
5. Water drag is dominated by the **surface** current; vertical shear over the iceberg draft is ignored.

**VERIFIED caveats the paper itself flags** (quote these if a judge probes model validity):
- On assumption 2: *"Bigg et al. (1997) found a large ageostrophic component of the ocean velocity in regions of strong horizontally sheared flows, where this assumption may thus introduce substantial errors."*
- On assumption 4 (wave radiation): several prior studies found wave radiation *"typically small compared to the air and water drag terms (Bigg et al. 1997; Gladstone et al. 2001)"*; others fold it into an altered wind-drag coefficient (Smith 1993; Keghouche et al. 2009).

**VERIFIED — geometry.** Icebergs are cuboids $L\times W\times H$; drag acts only on **vertical** faces. Rather than fixing the orientation, WDE17 averages over a **uniformly random orientation angle** $\phi$:

$$ \frac{2}{\pi}\int_0^{\pi/2}\!\!\big(W\cos\phi + L\sin\phi\big)\,d\phi \;=\; \frac{2}{\pi}(L+W) $$

$$ A_w = \frac{\rho_i}{\rho_w}\cdot\frac{2}{\pi}(L+W)H, \qquad A_a = \frac{\rho_w-\rho_i}{\rho_i}A_w $$

(The $\rho_i/\rho_w$ factor is the submerged fraction; $A_a$ follows from freeboard $=(1-\rho_i/\rho_w)H$.)

**VERIFIED — reduced balance, eq. (3):**

$$ 0 = M f\,\hat k\times\Delta\vec v + \tilde C_w|\Delta\vec v|\Delta\vec v + \tilde C_a|\vec v_a|\vec v_a, \qquad \Delta\vec v \equiv \vec v_w-\vec v_i $$

**VERIFIED — nondimensional groups, eq. (4)** (analogous to an Ekman number):

$$ \Lambda_w \equiv \frac{\tilde C_w|\Delta\vec v|}{Mf}, \qquad \Lambda_a \equiv \frac{\tilde C_a|\vec v_a|^2}{Mf\,|\Delta\vec v|} $$

giving eq. (5): $\;0 = \hat k\times\Delta\hat v + \Lambda_w\Delta\hat v + \Lambda_a\hat v_a$, with $\hat v \equiv \vec v/|\vec v|$.

---

### b.2 The closed-form solution — transcribed exactly

**VERIFIED — WDE17 eq. (6):**

$$ \boxed{\;\vec v_i = \vec v_w + \gamma\big(\alpha\,\hat k\times\vec v_a + \beta\,\vec v_a\big)\;} $$

**VERIFIED — eq. (7):**

$$ \gamma \;\equiv\; \sqrt{\frac{\tilde C_a}{\tilde C_w}} \;=\; \left[\frac{\rho_a(\rho_w-\rho_i)}{\rho_w\rho_i}\cdot\frac{C_a}{C_w}\right]^{1/2} $$

**VERIFIED — eq. (8), transcribed character-for-character from the preprint:**

$$ \alpha \equiv \frac{1}{2\Lambda^3}\Big(1-\sqrt{1+4\Lambda^4}\Big) $$

$$ \beta \equiv \frac{1}{\sqrt{2}\,\Lambda^3}\Big[\big(1+\Lambda^4\big)\sqrt{1+4\Lambda^4}-3\Lambda^4-1\Big]^{1/2} $$

**VERIFIED — eq. (9):**

$$ \Lambda \equiv \sqrt{\Lambda_w\Lambda_a} = \frac{\gamma\,C_w\,|\vec v_a|}{\pi f S}, \qquad \boxed{\,S \equiv \frac{LW}{L+W}\,} $$

$S$ is the **harmonic mean horizontal length** of the iceberg — this is exactly how $L$ and $W$ map into the model, and it is the *only* way iceberg geometry enters the drift. **VERIFIED — the iceberg height $H$ cancels entirely**, *"since the drag terms and the Coriolis term scale with H linearly"*.

**INFERRED — $S$ derivation check (do this in the code's unit test).** From $A_w$, $M=\rho_i LWH$:
$$\frac{\tilde C_w}{M}=\frac{\tfrac12\rho_w C_w\cdot\frac{\rho_i}{\rho_w}\frac{2}{\pi}(L+W)H}{\rho_i LWH}=\frac{C_w(L+W)}{\pi LW}=\frac{C_w}{\pi S}$$
so $\Lambda=\sqrt{\Lambda_w\Lambda_a}=\frac{\sqrt{\tilde C_w\tilde C_a}\,|\vec v_a|}{M|f|}=\frac{\gamma C_w|\vec v_a|}{\pi|f|S}$. Reproduces eq. (9) exactly. ✅

**VERIFIED — deflection angle.** The wind drives the iceberg at $\theta \equiv \tan^{-1}(\alpha/\beta)$ to the wind (eq. 10/11 region), with asymptotics (eq. 11):

$$ \frac{\alpha}{\beta} \simeq \begin{cases}\Lambda^{-2} & \Lambda\ll1\\[2pt] \Lambda^{-1} & \Lambda\gg1\end{cases} $$

These two asymptotes cross at $\Lambda=1$, $\theta=45°$. **VERIFIED interpretation:** *"the wind drives the iceberg primarily along-wind when $\Lambda>1$ and across-wind when $\Lambda<1$."*

**VERIFIED — relative wind-vs-current importance, eq. (14):**

$$ R \equiv \gamma\,(\alpha^2+\beta^2)^{1/2}\,\frac{|\vec v_a|}{|\vec v_w|} $$

$R>1$ ⇒ wind-dominated; $R<0.1$ ⇒ current-dominated.

---

### b.3 Parameter table — every constant, with the values to actually use

**VERIFIED — from the reference MATLAB parameter block, reproduced verbatim:**

```matlab
R    = 6378*1e3;      % earth radius in m
rhow = 1027;          % density of water (kg/m^3)
rhoa = 1.2;           % density of air   (kg/m^3)
rhoi = 850;           % density of shelf ice (kg/m^3), Silva et al (2006)
drho = rhow-rhoi;
Cw   = 0.9;           % bulk coefficient water (Bigg et al 1997)
Ca   = 1.3;           % bulk coefficient air   (Bigg et al 1997)
Om   = 7.2921*1e-5;   % rotation rate of earth (rad/s)
```

| Symbol | Meaning | Value | Provenance |
|---|---|---|---|
| $\rho_a$ | air density | **1.2** kg m⁻³ | WDE17 code + text |
| $\rho_w$ | seawater density | **1027** kg m⁻³ | WDE17 code + text |
| $\rho_i$ | iceberg (shelf-ice) density | **850** kg m⁻³ | Martin & Adcroft (2010) / Silva et al. (2006); tabular Southern Ocean bergs |
| $C_w$ | bulk **water** drag coefficient | **0.9** | Bigg et al. (1997), per WDE17 code |
| $C_a$ | bulk **air** drag coefficient | **1.3** | Bigg et al. (1997), per WDE17 code |
| $\Omega$ | Earth rotation rate | **7.2921 × 10⁻⁵** rad s⁻¹ | WDE17 code |
| $f$ | Coriolis parameter | $2\Omega\sin(\text{lat})$; **code uses** $2\Omega\sin(|\text{lat}|)$ — see b.5 | WDE17 code |
| $\gamma$ | wind-vs-water drag ratio | **0.0187** (computed) / **0.018** (paper) | eq. (7) |
| $T_i$ | iceberg internal temperature | **−4 °C** | El-Tahan et al. (1987), via WDE17 |
| $\varepsilon_c$ | critical width/height ratio for capsize | **0.92** | Burton et al. (2012), as modified by WDE17 |

> ### ⚠️ b.4 — **Drag-coefficient trap: the arXiv preprint has $C_a$ and $C_w$ swapped in its text.** Get this wrong and $\gamma$ is off by 44 %.
>
> **VERIFIED — the discrepancy.** The arXiv preprint's Section 4 states: *"taking bulk coefficients $C_a = 0.9$ and $C_w = 1.3$ (Bigg et al. 1997), we find from equation (7) that $\gamma = 0.018$."* The reference MATLAB code states the **opposite**: `Cw = 0.9` (water), `Ca = 1.3` (air).
>
> **VERIFIED by my own computation — the code is right and the preprint text is wrong.** Since $\gamma \propto \sqrt{C_a/C_w}$:
>
> | Assignment | $\gamma$ from eq. (7) | Matches paper's stated $\gamma=0.018$? |
> |---|---|---|
> | $C_a=0.9,\ C_w=1.3$ (preprint text) | **0.01298** | ❌ off by 28 % |
> | $C_a=1.3,\ C_w=0.9$ (code) | **0.01875** | ✅ |
>
> Two independent cross-checks confirm the code's assignment, using the paper's *own* downstream numbers:
> - The paper derives $\Lambda \simeq c|\vec v_a|/L$ with **$c = 130$ s** (for $f=10^{-4}$ s⁻¹, $L/W=1.5$ so $S=0.4L$). I compute $c = \gamma C_w/(\pi f\cdot 0.4)$. Note $\gamma C_w \propto \sqrt{C_aC_w}$ is **invariant under the swap**, so $c = 134.3$ s either way — consistent with the paper's 130 s, and it does not discriminate. But:
> - The paper derives the critical length $L^\ast \equiv 765$ m at $\Lambda=1$ for $|\vec v_a| = 5.7$ m/s. I compute **765 m** exactly. ✅
> - $\gamma$ itself only reproduces at 0.018 with $C_a=1.3, C_w=0.9$. ✅
>
> **Action for the implementation: use $C_a = 1.3$ (air), $C_w = 0.9$ (water).** Assert `gamma == 0.0187 ± 0.0005` in a unit test so nobody silently swaps them later. **INFERRED:** I did not check whether the peer-reviewed JPO version corrects the preprint's text — this could be a preprint-only typo. Either way the code is self-consistent with the paper's stated $\gamma$, $c$ and $L^\ast$.

---

### b.5 ⚠️ **Hemisphere sign convention — the single most important implementation detail for an Antarctic project**

**VERIFIED — reference code, verbatim:**

```matlab
ff = @(lat) 2*Om*sin(abs(lat)*pi/180);              % NOTE: abs(lat)
ga = sqrt(rhoa*drho/rhow/rhoi*Ca/Cw);
La = @(u,lat,S) Cw*ga/ff(lat).*u/S/pi;
a  = @(La) 1./(2*La.^3).*(sqrt(1+4*La.^4)-1);       % NOTE: sign flipped vs paper eq. (8)
b  = @(La) 1./(sqrt(2)*La.^3).*sqrt((1+La.^4).*sqrt(1+4*La.^4)-3*La.^4-1);
ui = uw + ga*( a(LA)*va + b(LA)*ua);
vi = vw + ga*(-a(LA)*ua + b(LA)*va);
```

Three things follow, all of which matter:

**1. $\Lambda$ is built from $|f|$, not $f$.** `ff` uses `abs(lat)`. **INFERRED, and consistent with my derivation in b.2:** $\Lambda=\sqrt{\Lambda_w\Lambda_a}$ is a principal square root of a product of two quantities that are *both* $\propto 1/f$, so $\Lambda \propto 1/|f|$ and is always positive. Equation (9) as printed writes $f$, not $|f|$; **do not plug a signed southern-hemisphere $f$ into it** — you will get $\Lambda<0$, $\beta<0$, and an along-wind term pointing backwards. **Always compute $\Lambda$ with $|f|$.**

**2. The code's $\alpha$ has the opposite sign to the paper's eq. (8).** Paper: $\alpha=\frac{1}{2\Lambda^3}(1-\sqrt{1+4\Lambda^4})$, which is **negative** for all $\Lambda>0$. Code: `a = (sqrt(1+4*La^4)-1)/(2*La^3)`, which is **positive**. The code absorbs the sign into the velocity assembly instead. Both are correct and equivalent — but you must not mix the paper's $\alpha$ with the code's assembly, or you will flip the deflection.

**3. INFERRED — the reference code deflects to the right of the wind everywhere, i.e. it is hard-coded to Northern-Hemisphere behaviour.** With $(u,v)=(\text{east},\text{north})$, the wind-driven part of the code's assembly is

$$ b\,(u_a, v_a) \;+\; a\,(v_a,\,-u_a) $$

and $(v_a, -u_a)$ is $(u_a,v_a)$ rotated **−90° (clockwise)** — i.e. to the **right** of the wind. Combined with `abs(lat)` in `ff`, the published script applies right-of-wind deflection at **every** latitude. Physically, Coriolis-plus-drag deflects a wind-driven object to the right in the NH and to the **left** in the SH (the same asymmetry as Ekman transport). WDE17 is an Arctic-centred paper in its quantitative sections, so this was never exercised.

**Recommended implementation (write it this way, hemisphere-explicit):**

```python
import numpy as np

OMEGA = 7.2921e-5
RHO_A, RHO_W, RHO_I = 1.2, 1027.0, 850.0
C_A, C_W = 1.3, 0.9                      # air, water  -- see b.4, do NOT swap
GAMMA = np.sqrt(RHO_A * (RHO_W - RHO_I) / (RHO_W * RHO_I) * C_A / C_W)   # 0.018747

def alpha(lam):   # positive-definite form (matches WDE17 reference code `a`)
    return (np.sqrt(1.0 + 4.0 * lam**4) - 1.0) / (2.0 * lam**3)

def beta(lam):
    inner = (1.0 + lam**4) * np.sqrt(1.0 + 4.0 * lam**4) - 3.0 * lam**4 - 1.0
    return np.sqrt(np.maximum(inner, 0.0)) / (np.sqrt(2.0) * lam**3)      # clip: inner ~ 2*lam^12, underflows

def iceberg_velocity(u_w, v_w, u_a, v_a, lat_deg, L, W):
    """WDE17 eq. (6). Winds/currents in m/s, L,W in m, lat in degrees (negative = South).
    Returns (u_i, v_i) in m/s, eastward/northward."""
    f_abs = 2.0 * OMEGA * np.sin(np.radians(np.abs(lat_deg)))
    S     = L * W / (L + W)                       # harmonic mean horizontal length
    spd_a = np.hypot(u_a, v_a)
    lam   = GAMMA * C_W * spd_a / (np.pi * f_abs * S)     # ALWAYS |f| -> lam > 0
    a, b  = alpha(lam), beta(lam)
    # cross-wind deflection: RIGHT of wind in NH, LEFT of wind in SH
    s = np.sign(lat_deg)                          # +1 north, -1 south
    u_i = u_w + GAMMA * ( s * a * v_a + b * u_a)
    v_i = v_w + GAMMA * (-s * a * u_a + b * v_a)
    return u_i, v_i
```

> **Status of the hemisphere flip:** the `s = np.sign(lat_deg)` factor is **INFERRED** from the Coriolis sign in eq. (3)–(5), *not* read from the reference code (which omits it). **Verify it before the deck.** Practical mitigation: it is nearly moot for USNIC-tracked giants (b.6 shows $R \approx 0.03$–$0.12$, i.e. wind contributes ~1 % of drift there), but it matters for sub-kilometre bergs where $R > 1$. Two ways to settle it cheaply: (i) fit the sign as a free parameter against BYU/USNIC observed tracks and see which one reduces error; (ii) email the authors. Do **not** present it as established.

---

### b.6 Numerical reference table — regenerate these in a unit test

Computed by me from the equations above ($\gamma = 0.018747$). Use as golden values.

| $\Lambda$ | $\alpha$ | $\beta$ | $\sqrt{\alpha^2+\beta^2}$ | $\theta=\tan^{-1}(\alpha/\beta)$ |
|---:|---:|---:|---:|---:|
| 0.01 | 0.01000 | 0.00000 | 0.01000 | 90.00° |
| 0.1 | 0.09999 | 0.00100 | 0.10000 | 89.43° |
| 0.5 | 0.47214 | 0.11470 | 0.48587 | 76.35° |
| **1.0** | **0.61803** | **0.48587** | **0.78615** | **51.83°** |
| 2.0 | 0.44139 | 0.82943 | 0.93956 | 28.02° |
| 5.0 | 0.19604 | 0.97045 | 0.99005 | 11.42° |
| 10.0 | 0.09950 | 0.99253 | 0.99750 | 5.72° |
| 100.0 | 0.01000 | 0.99993 | 0.99998 | 0.57° |

Asymptotic behaviour (**INFERRED**, series-expanded and numerically confirmed): $\alpha\to\Lambda$, $\beta\to\Lambda^3$ as $\Lambda\to0$; $\alpha\to1/\Lambda$, $\beta\to1$ as $\Lambda\to\infty$.

> **Numerical hazard.** For $\Lambda\lesssim0.05$ the bracket inside $\beta$ is $\approx 2\Lambda^{12}$ — it underflows and can go slightly negative in float64, producing `NaN`. **Clip to zero** (as in the snippet above) or switch to the asymptote $\beta\approx\Lambda^3$ below $\Lambda=0.05$. This *will* bite: the table below shows every USNIC-tracked berg sits at $\Lambda<0.07$.

**Regime table for real Antarctic icebergs** (computed at 65° S, $|\vec v_a|=10$ m/s, $|\vec v_w|=0.1$ m/s):

| Iceberg | $L\times W$ | $S$ (m) | $\Lambda$ | $\alpha$ | $\beta$ | $R$ | Wind-driven speed |
|---|---|---:|---:|---:|---:|---:|---:|
| A23A-class giant | 70 × 40 km | 25 455 | 0.0160 | 0.0160 | ~0 | **0.030** | 0.30 cm/s |
| A76-class | 30 × 13 km | 9 070 | 0.0448 | 0.0448 | 0.0001 | **0.084** | 0.84 cm/s |
| **USNIC minimum** (10 × 5 NM) | 18.5 × 9.3 km | 6 173 | 0.0658 | 0.0658 | 0.0003 | **0.123** | 1.23 cm/s |
| Medium berg | 1000 × 600 m | 375 | 1.0835 | 0.6101 | 0.5374 | **1.524** | 15.2 cm/s |
| Small berg / bergy bit | 200 × 120 m | 75 | 5.4176 | 0.1815 | 0.9748 | **1.859** | 18.6 cm/s |

**This is the single most important architectural finding in this brief.**

- **Every iceberg USNIC tracks is in the $R<0.13$, current-dominated regime.** WDE17's own conclusion, **VERIFIED**: *"for large tabular icebergs as observed in Antarctica, the wind drag can be assumed negligible and equation (6) reduces to the relation $\vec v_i=\vec v_w$, i.e., large icebergs move with the surface ocean current."* Also **VERIFIED**: wind drag *"becomes negligible compared to water drag ($R<0.1$) for icebergs larger than $L\sim12$ km."*
- **Therefore: for the USNIC/BYU catalogue, forecast skill is dominated by the quality of your surface-current field, not by the drift equations.** Spending effort on drag-coefficient tuning is misdirected; spending it on the ocean-current product (and on a learned residual, section c) is not.
- **Conversely, the 2 % wind rule is wrong for exactly the bergs we care about.** **VERIFIED** WDE17 result: the 2 % rule is an asymptotic limit valid only for $\Lambda\gg1$, i.e. *"a good approximation for iceberg drift only when the surface air speed in m/s is much greater than ca. 1 % of the length of the iceberg in m."* A 20 km berg would need a 200 m/s wind. **Any competitor who applies the 2 % rule to Antarctic giants is making a physics error you can name specifically.** That is a strong differentiation point for the viva.

---

### b.7 Icebergs embedded in pack ice

**WDE17 does not handle this.** Assumption 4 explicitly drops the sea-ice drag term $F_i$, and the paper states plainly (**VERIFIED**) that *"we ignore the drag and reduced melting effects of sea ice."* Since roughly the whole Weddell and Ross Sea iceberg population spends part of the year embedded in pack ice, this is a real gap for an Antarctic system — and one worth stating openly in the deck.

The canonical treatment, cited by WDE17 itself:

- **VERIFIED (Crossref):** Lichey, C. and Hellmer, H. H. (2001), *"Modeling giant-iceberg drift under the influence of sea ice in the Weddell Sea, Antarctica"*, **Journal of Glaciology 47**(158), 452–460, doi:[10.3189/172756501781832133](https://doi.org/10.3189/172756501781832133). This is *the* Antarctic-specific sea-ice/iceberg coupling reference and is the one to cite.
- **VERIFIED (in WDE17 reference list):** Hunke, E. C. and Comeau, D. (2011), *"Sea ice and iceberg dynamic interaction"*, **J. Geophys. Res. 116**, C05008.

**UNVERIFIED — I did not fetch either paper's full text.** The standard formulation, as generally described, adds a sea-ice drag term of the same quadratic form, $F_i = \tfrac12\rho_i C_i A_i |\vec v_{si}-\vec v_i|(\vec v_{si}-\vec v_i)$, and switches to a **"locked-in" regime** once sea-ice concentration and internal ice pressure exceed thresholds, at which point the iceberg is advected with the pack-ice velocity field rather than the ocean current. **Confirm the exact thresholds and coefficient against Lichey & Hellmer (2001) before implementing.** Do not quote numbers for this from memory.

**Two consequences worth designing around, both INFERRED but well-founded:**

1. **A concentration-gated blend is the honest minimum.** Something like: for sea-ice concentration $A$ below a low threshold, use WDE17 free drift; above a high threshold, advect with the sea-ice velocity field; blend in between. Whatever thresholds you choose, **label them as tuned, not as physics**, and fit them against observed BYU tracks.
2. **This is where the learned residual earns its keep.** A physics core that has *no* sea-ice term will show a large, systematic, seasonally-varying residual in the Weddell Sea. That is precisely the structure a residual network can absorb (section c) — and it gives you a defensible answer to "why hybrid rather than pure physics?"

---

### b.8 Deterioration / melt model (Bigg et al. 1997, as modified by WDE17 following Martin & Adcroft 2010)

**VERIFIED — WDE17 Appendix eq. (A1)**, three melt processes, transcribed from the preprint. All terms are in **metres per day** of change in the iceberg's dimensions, with $T_w, T_i$ in °C and $L$ in metres.

**(i) Wind-driven wave erosion** $M_e$ (lateral):

$$ M_e = 0.5\,S_s = 0.75\,|\vec v_a-\vec v_w|^{0.5} + 0.05\,|\vec v_a-\vec v_w| $$

where $S_s$ is the **Douglas Sea State**, parameterised as in Martin & Adcroft (2010): $S_s = 1.5|\Delta\vec v|^{1/2} + 0.1|\Delta\vec v|$.

**(ii) Turbulent basal melt** $M_b$ (vertical):

$$ M_b = 0.58\,|\vec v_w-\vec v_i|^{0.8}\,(T_w-T_i)\,L^{-0.2} $$

**(iii) Thermal side-wall erosion from buoyant convection** $M_v$ (lateral):

$$ M_v = 0.0076\,T_w + 0.0013\,T_w^2 $$

**VERIFIED — the constants cross-check exactly against the reference code.** The MATLAB melt block is:

```matlab
Ti = -4;
a1 = 8.7e-6;  a2 = 5.8e-7;
b1 = 8.8e-8;  b2 = 1.5e-8;
c  = 6.7e-6;
```

These are (A1)'s coefficients converted from m/day to m/s — I verified all five:

| Code constant | (A1) coefficient | ÷ 86400 | Code value | Match |
|---|---|---|---|---|
| `a1` | 0.75 (wave erosion, $\sqrt{}$ term) | 8.68e-6 | 8.7e-6 | ✅ |
| `a2` | 0.05 (wave erosion, linear term) | 5.787e-7 | 5.8e-7 | ✅ |
| `b1` | 0.0076 (buoyant convection, linear) | 8.796e-8 | 8.8e-8 | ✅ |
| `b2` | 0.0013 (buoyant convection, quadratic) | 1.505e-8 | 1.5e-8 | ✅ |
| `c` | 0.58 (turbulent basal melt) | 6.713e-6 | 6.7e-6 | ✅ |

This independently confirms the (A1) transcription above is correct — the two sources agree to the code's stated precision.

**VERIFIED — how melt changes size along the trajectory:**

- $T_w$ (water temperature) is approximated by **SST**.
- Iceberg temperature is held constant at $T_i = -4\ °\text{C}$ (El-Tahan et al. 1987).
- Melt processes are assumed **linearly additive**, and the volume evolves as $dV/dt = d(LWH)/dt$ with

$$ \frac{dL}{dt} = \frac{dW}{dt} = M_e + M_v, \qquad \frac{dH}{dt} = M_b $$

- **VERIFIED:** *"Other processes, such as surface melt, have been found to be small compared to these terms (Savage 2001)."*

**This is the coupling back into drift.** Because $\alpha$ and $\beta$ depend on $S = LW/(L+W)$, melt shrinks $S$, which raises $\Lambda$, which increases the wind's share of the drift. **VERIFIED (WDE17):** *"Since the coefficients $\alpha$ and $\beta$ depend on iceberg length $S$, which is a function of $L$ and $W$, iceberg motion under given winds and currents will also depend on $L$ and $W$, and will therefore be affected by the decay of the iceberg."* So drift and decay must be integrated together, not run as separate passes — a 20 km berg that decays past ~765 m (the $L^\ast$ scale) crosses from current-dominated to wind-dominated.

**VERIFIED — capsize / rollover.** WDE17 replaces the Weeks & Mellor (1978) rollover criterion with Burton et al. (2012). With aspect ratio $\varepsilon \equiv W/H$, a rectangular iceberg is unconditionally unstable below

$$ \varepsilon_c = \sqrt{6\,\frac{\rho_i}{\rho_w}\left(1-\frac{\rho_i}{\rho_w}\right)} $$

With $\rho_i/\rho_w = 0.83$ this gives $\varepsilon_c = 0.92$ (I reproduced 0.923 — ✅). Burton et al. (2012) themselves use $\varepsilon_c = 0.75$. When $\varepsilon<\varepsilon_c$ the model **swaps $W$ and $H$**.

**VERIFIED and worth flagging in the viva:** WDE17 explicitly reports that *"Weeks and Mellor (1978) appear to have a sign error in their equation (9), where the last term should be positive,"* and that *"this sign error is adopted by Bigg et al. (1997)"* and several subsequent studies. If you copy a rollover criterion out of an older iceberg paper, you may be copying a known-bad equation. Use the Burton/WDE17 form above.

**VERIFIED — deletion/melt-out in operational practice** (from the IIP 2024 report, section c): an iceberg *"deleted at 100 % by deterioration calculations has theoretically melted to nothing, while an iceberg that has melted to 500 % has endured enough environmental factors... that it could have melted five times over. IIP typically deletes icebergs at **125 % or 150 %** based on their proximity to the iceberg limit." That asymmetric threshold — keep a berg on the books past its modelled death, in proportion to how much it matters — is a good operational pattern to copy.

---

### b.9 Two known errata in the WDE17 preprint (summary)

Both found by cross-checking the paper against its own reference implementation and against its own downstream numbers. Worth one slide if a judge asks how deeply you read the source.

| # | Issue | Resolution |
|---|---|---|
| 1 | Section 4 text states $C_a = 0.9$, $C_w = 1.3$; reference code states `Ca = 1.3`, `Cw = 0.9`. | **Code is right.** Only the code's assignment reproduces the paper's own $\gamma=0.018$. See b.4. |
| 2 | Eq. (9) writes $\Lambda = \gamma C_w|\vec v_a|/(\pi f S)$ with signed $f$; the code uses $|f|$ via `abs(lat)`. | **Use $|f|$.** $\Lambda=\sqrt{\Lambda_w\Lambda_a}$ is positive by construction. See b.5. |
| — | (Not an erratum) Eq. (8)'s $\alpha$ is negative; the code's `a` is positive, with the sign moved into the velocity assembly. | Equivalent. Don't mix conventions. |

---

## (c) Published accuracy of iceberg drift prediction at 1 / 3 / 7-day leads

> **Headline honest finding: there is no clean, public, peer-reviewed table of Antarctic iceberg drift separation distance at 1/3/7-day leads that I could verify.** The Arctic/North-Atlantic literature is much richer than the Antarctic literature here, and several of the most-cited verification studies are behind Elsevier/OnePetro paywalls. What follows is what I could actually verify, plus an explicit list of what I could not.

### c.1 Wagner, Dell & Eisenman (2017) — **no quantitative skill scores**

**VERIFIED.** The paper's own validation wording is: *"We qualitatively validate the model against Antarctic..."* large icebergs catalogued in the Antarctic Iceberg dataset (bergs with diameter > 10 nm over 1999–2009). It compares trajectory *patterns* driven by ECCO2 fields; it does **not** report separation distance vs. lead time, RMSE, or a skill score.

**Do not claim WDE17 has a published accuracy number. It does not.** Its contribution is the analytical solution and the regime analysis, not forecast verification.

### c.2 IDRIFTNET (2025) — **verified numbers, but the lead time is not stated**

Source: arXiv:[2507.00036](https://arxiv.org/abs/2507.00036) — downloaded and read. Already logged in `docs/COMPETITIVE_ANALYSIS.md` as the SOTA hybrid pattern; the numbers below are new.

**VERIFIED — setup:** USNIC positions for icebergs **A23A** and **B22A**, 2014 → 21 Feb 2025, merged with reanalysis wind (u10, v10) and ocean current (uo, vo) on a **daily** grid. Seven input features (lat, lon, area, u10, v10, uo, vo), sliding window of **five consecutive daily timesteps**, predicting the next step. Physics branch is **WDE17**; a Gabor Spectral Network encoder-decoder learns the **residual** correction. **Autoregressive rollout at test time** — predictions are fed back as inputs, so errors compound realistically.

**VERIFIED — results.** ADE = Average Displacement Error, FDE = Final Displacement Error, geodesic (km):

| Model | A23A ADE | A23A FDE | B22A ADE | B22A FDE |
|---|---:|---:|---:|---:|
| **IDRIFTNET** | **49.06** | **63.32** | **22.87** | **10.87** |
| Trajectron++ | 56.26 | 102.10 | 40.89 | 25.82 |
| GroupNet | 53.17 | 103.18 | — | 40.52 |
| AgentFormer | 51.83 | 99.96 | — | — |
| PECNet | — | 294.41 | — | 481.73 |
| **Physics-only (WDE17 alone)** | **147.10** | **117.54** | **127.23** | **39.50** |

**The physics-only row is the important one for us.** Adding a learned residual to the WDE17 core cuts geodesic ADE from **147.10 → 49.06 km** on A23A (−67 %) and **127.23 → 22.87 km** on B22A (−82 %). That is direct, quotable evidence for the hybrid architecture over either pure physics or pure ML.

Also **VERIFIED:** IDRIFTNET achieves this with only **0.29 M trainable parameters / 1.14 MB**, which the authors argue suits *"resource-constrained or real-time"* deployment — a useful point given SIH Grand-Finale hardware.

> ⚠️ **UNVERIFIED — the forecast horizon.** I read the paper's dataset, implementation and inference sections in full and **the number of forecast days over which ADE/FDE are computed is never stated**, nor is the train/validation/test split ratio. These figures are therefore **not** 1/3/7-day numbers and **must not be presented as such**. They are whole-rollout errors over an unspecified test horizon. If you cite them, cite them as "over the paper's full autoregressive test rollout, horizon unstated."

**VERIFIED — a genuine lead-time statement from IDRIFTNET's own literature review**, useful as a calibration anchor: hybrid/semi-empirical methods (they cite Yulmetov et al. 2011, GPS-tagged bergs, gradient-boosted trees over an explicit Coriolis term) *"compares well to pure ML or physics-based methods for short forecast lead times (**up to 24 hours**)"*, and such approaches are *"limited to short temporal windows (24 hours) and usually depend on constant access to GPS-tagged observations, which are impractical for larger non-geotagged icebergs."*

**INFERRED, and a good honest slide:** the field's *reliable* verified horizon is ~24 h; everything beyond that degrades fast, and Antarctic giants are forecast on multi-day-to-weekly cadence largely because they move slowly and are current-dominated, not because the models are good at long leads.

### c.3 International Ice Patrol — operational practice, verified, but no published error table

Source: **Report of the International Ice Patrol in the North Atlantic, 2024**, U.S. Coast Guard — downloaded and read (<https://www.navcen.uscg.gov/international-ice-patrol-annual-reports>). North Atlantic, not Antarctic, but it is the world's longest-running operational iceberg drift service and the methodology transfers.

**VERIFIED:**
- IIP runs **BAPS — the IceBerg Analysis and Prediction System**. Iceberg positions in the database are *"predicted for the same times (0000Z and 1200Z) daily via iceberg drift and deterioration computer models using BAPS"*, i.e. a **12-hour** model cycle.
- The forecast product is not a position — it is a **limit**: *"iceberg limits are generated to contain the modeled iceberg positions for 0000Z the next day and distributed to mariners and the public within the NAIS daily warning products."* Broadcast over SafetyNET, NAVTEX, SITOR and radiofax.
- Uncertainty is represented as an explicit **"error circle"**: each modelled iceberg carries a *"modeled positional circle of uncertainty ('error circle')"*. An iceberg is deleted only when the **whole error circle** is declared iceberg-free by high-confidence reconnaissance — not when the modelled point position is checked.
- Three deletion criteria, **VERIFIED**: (1) error circle declared iceberg-free by recent reconnaissance; (2) *"its 'time on drift' must exceed **30 days**"*; (3) predicted melt between **125–150 %**.
- Satellite imagery is generally **not** trusted for deletion — *"IIP rarely deletes database icebergs using satellite imagery"* — because of cloud cover, resolution, ocean wave radar backscatter and target ambiguity; the exception is cloud-free high-resolution optical (Sentinel-2).
- Scale of the limit: in Ice Year 2024 the iceberg limit at maximum extent stretched **356 NM east of St. John's**.

> **UNVERIFIED:** the 2024 IIP report does **not** publish an error-circle radius, a drift-model verification statistic, or separation distance vs. lead time. I searched the full report text for "radius", "verification", "advised to", "remain outside" — no numeric result. If a verification table exists it is in a separate IIP technical publication I did not locate.

**Two design lessons that ARE verified and are worth more than a number:**
1. **The operational output is an uncertainty region, not a point forecast.** A demo that draws a single predicted berg position is *less* operationally credible than one that draws a growing error circle. Build the uncertainty envelope into the product from the start.
2. **The "time on drift ≤ 30 days" rule is a hard, citable bound on how long an unrefreshed drift forecast is trusted by the world's reference iceberg service.** Use it to justify your own forecast-staleness policy.

### c.4 What I could NOT verify

| Claim | Status | Why |
|---|---|---|
| "Absolute position error grows ~12 km per day" (→ ~12/24/36 km at 24/48/72 h) | **UNVERIFIED — DO NOT USE** | This surfaced only in a search-engine summary, not in a source I could open. Attributed loosely to Canadian Ice Service operational model verification. **A fabricated or mis-sourced number here would be fatal in a judged presentation.** Treat as a lead to chase, not a fact. |
| Turnbull, I., Fournier, N., Stolwijk, M., Fosnaes, T., McGonigal, D. (2015), *"Operational iceberg drift forecasting in Northwest Greenland"*, **Cold Reg. Sci. Technol. 110**, doi:[10.1016/j.coldregions.2014.10.006](https://doi.org/10.1016/j.coldregions.2014.10.006) | **Citation VERIFIED (Semantic Scholar); content UNVERIFIED** | ScienceDirect returned **HTTP 403**; Semantic Scholar has the record but **no abstract**. Most likely single best source for lead-time verification numbers. Chase via institutional access. |
| Kubat, Sayed, Savage, Carrieres, *"An Operational Model of Iceberg Drift"*, IJOPE 2005; and *"Preliminary Verification of an Operational Iceberg Drift Model"* | **UNVERIFIED** | OnePetro / ResearchGate only; not openly accessible. |

---

## (d) Iceberg CPA / safe stand-off distance for ships

### d.1 The IMO requirement — **exact text, verified**

**VERIFIED — full verbatim text.** Source document: **MSC.1/Circ.1519**, *Guidance on Methodologies for Assessing Operational Capabilities and Limitations in Ice* (**POLARIS**), Annex. Retrieved as PDF via The Nautical Institute's public copy of the IMO circular: <https://www.nautinst.org/uploads/assets/uploaded/2f01665c-04f7-4488-802552e5b5db62d9.pdf> (the PDF's own header cites `https://edocs.imo.org/Final Documents/English/MSC.1-CIRC.1519 (E).docx`).

Section **1.7, "Operations in ice regimes containing glacial ice"**, quoted in full:

> **1.7.1** The presence of glacial ice represents additional risks to the ship. Areas containing glacial ice should be approached with caution.
>
> **1.7.2** Appropriate training should be provided to the Master and officers in charge of a navigational watch when navigating in ice on identification and avoidance of glacial ice and the consequences of collision. Measures to avoid glacial ice should be documented in the PWOM.
>
> **1.7.3** Where glacial ice is encountered, in addition to the RIO, a safe stand-off distance should be observed by the ship. This stand-off distance should be recorded in the PWOM.

**The critical, and genuinely useful, finding: IMO specifies NO number.** 1.7.3 requires that a stand-off distance *exist*, that it be *observed*, and that it be *recorded in the PWOM* (Polar Water Operational Manual). The value is left to the ship and operator. There is no IMO-mandated nautical-mile figure to quote.

**VERIFIED context on POLARIS itself:** the **RIO** (Risk Index Outcome) is POLARIS's numeric ice-regime score. Section 1.7 is explicit that glacial ice sits **outside** the RIO framework — the stand-off distance is required *"in addition to the RIO"*. **INFERRED:** this is because POLARIS scores *sea ice* regimes by concentration and ice type; icebergs are a discrete-obstacle hazard that a concentration-based index cannot represent. That distinction is worth stating on a slide — it explains why a separate iceberg decision-support layer (i.e. this project) is needed alongside any POLARIS/RIO calculator, rather than being folded into it.

### d.2 What is actually used in practice

> **Honest finding: I could not verify a single authoritative numeric stand-off distance.** No number appears in POLARIS 1.7, none in the IIP 2024 annual report, and none in the ice-navigator training material I could reach. This appears to be genuinely operator-specific rather than something I merely failed to find — 1.7.3's construction ("recorded in the PWOM") implies a per-ship value by design.

Verified operational patterns that *substitute* for a fixed distance:

| Practice | Form of the stand-off | Verified source |
|---|---|---|
| **IIP / North American Ice Service** | A published **iceberg limit** (a polygon, "Limit of All Known Ice") that mariners navigate outside of; built to *contain* modelled positions for the next 0000Z, refreshed daily and broadcast on SafetyNET/NAVTEX/SITOR. Individual bergs carry an **error circle**. | IIP Annual Report 2024 (read) |
| **Vendée Globe / The Ocean Race (CLS)** | A **dynamically adjusted Antarctic Exclusion Zone (AEZ)** — a race-mandated keep-out boundary moved in real time from per-berg trajectory forecasts. | <https://www.cls.fr/en/press/iceberg-straight-ahead-cls-ensures-vendee-globe-safety-from-space/> |
| **POLARIS / Polar Code** | A ship-specific distance **defined by the operator and recorded in the PWOM**; training in *"identification and avoidance of glacial ice"* is separately mandated. | MSC.1/Circ.1519 §1.7 (read) |

**Design recommendation for this project (INFERRED, but well-supported by all three rows above):**

The right output is **not** "iceberg at CPA 4.2 NM." Every operational system verified here expresses iceberg risk as a **time-evolving keep-out region built to contain the forecast uncertainty**, and then treats the stand-off as a user-configurable margin on top of it. Concretely:

1. Propagate each berg with the WDE17 core (b.5) plus the learned residual (c.2).
2. Grow a **per-berg uncertainty radius** with lead time — the IIP "error circle" concept — rather than emitting a point.
3. Union the circles into a keep-out polygon, IIP-"iceberg limit"-style, and recompute it on a fixed cycle (IIP uses **12 h**; we can do better with Sentinel-1 revisit).
4. Expose the stand-off margin as a **user-set parameter**, defaulting to whatever the operator's PWOM says — and say on the slide that this is exactly what Polar Code 1.7.3 requires, quoting the text. **A judge who knows the Polar Code will recognise that as the correct answer, and there is no number we could have quoted instead.**
5. Compute CPA/TCPA against the *polygon*, not the point.

This also converts a research gap into a differentiator: "IMO requires a stand-off distance but deliberately does not fix one, so we make it a first-class configurable input and show the keep-out zone it produces."

---

## 5. Open items — everything UNVERIFIED, paywalled, or dead

| # | Item | Status | Impact if unresolved |
|---|---|---|---|
| 1 | **IDRIFTNET forecast horizon** (days) behind its ADE/FDE figures — never stated in the paper; train/test split also unstated. | Unstated in source | **High.** The 49/63 km and 22/10 km figures cannot be presented as 1/3/7-day errors. Cite with the horizon caveat or not at all. |
| 2 | **Hemisphere sign flip** for the cross-wind term in the Southern Ocean (`s = np.sign(lat)` in b.5). Derived by me; the reference code uses `abs(lat)` and a fixed right-of-wind rotation. | INFERRED, not confirmed | **Medium.** Negligible for USNIC giants ($R<0.13$); material for sub-km bergs. Resolve empirically against BYU tracks, or ask the authors. |
| 3 | **"~12 km/day position error growth"** (→12/24/36 km at 24/48/72 h). | UNVERIFIED — search summary only | **High if used.** Do not put on a slide. |
| 4 | **Turnbull et al. (2015)**, *Operational iceberg drift forecasting in NW Greenland*, Cold Reg. Sci. Technol. 110. | ScienceDirect **HTTP 403**; Semantic Scholar record has **no abstract** | **Medium.** Best remaining candidate for real lead-time verification numbers. |
| 5 | **Kubat et al., IJOPE 2005** and *Preliminary Verification of an Operational Iceberg Drift Model*. | Paywalled (OnePetro / ResearchGate) | Medium. Same gap as #4. |
| 6 | **Lichey & Hellmer (2001)** sea-ice-coupled drift — citation verified via Crossref, **full text not read**. Sea-ice drag coefficient and lock-in thresholds not confirmed. | Citation VERIFIED, content UNVERIFIED | **Medium-high.** Needed before implementing pack-ice-embedded drift. Do not implement thresholds from memory. |
| 7 | **ALTIBERG v4 / OSI SAF "Iceberg from Altimetry CDR/ICDR" (OSI-490, OSI-480)** — release status and download URL. | UNVERIFIED | **Medium.** Only candidate for a near-real-time public small-iceberg feed. ALTIBERG v3.1 stops at end-2021. |
| 8 | **Numeric operational stand-off distance** from any classification society, ice-navigator syllabus, or PWOM template. | Not found; appears genuinely operator-specific by design | **Low.** Handled by making it configurable — see d.2. |
| 9 | **`docs/DATASET.md` says BYU consolidated DB ends Aug 2023.** Live release is **v8.0 → 22 Apr 2025**. | Correction needed | **Low, but fix it** — ~20 extra months of trajectory training data. |
| 10 | Whether the **peer-reviewed JPO version** of WDE17 corrects the preprint's swapped $C_a$/$C_w$ text (erratum #1, b.4). | UNVERIFIED | Low — the code settles the correct values regardless. |

### Dead / blocked URLs encountered (recorded rather than silently skipped)

| URL | Result |
|---|---|
| `https://www.sciencedirect.com/science/article/abs/pii/S0165232X14001918` | **HTTP 403 Forbidden** |
| `https://www.seanoe.org/data/00279/39073/` | **HTTP 404** |
| `https://data-dataref.ifremer.fr/cersat/products/gridded/altiberg/` | **HTTP 404** (wrong path; correct path is under `/data/sea-ice/icebergs/altiberg/v3.1/`) |
| `ftp://eftp.ifremer.fr/cersat/products/gridded/altiberg/` | connection failed (wrong host/path) |
| `https://doi.org/10.17882/48388` | **HTTP 404** (guessed SEANOE DOI — not the right one; correct DOI is `10.12770/06770b5a-…`) |
| `https://www.ccg-gcc.gc.ca/publications/icebreaking-deglacage/ice-navigation-glaces/index-eng.html` | **HTTP 301** → `canada.ca/en/canadian-coast-guard.html`; the *Ice Navigation in Canadian Waters* manual was not located at its historical URL |

---

## 6. Actionable summary for the ML architecture

1. **Trajectory training data = BYU consolidated DB v8.0** (1978–Apr 2025, per-berg CSV tracks) **+ live USNIC CSV** for current state. Both no-auth, both verified live.
2. **Small-berg detection training data = ESSD/Zenodo shapefiles** (0.04 km² threshold, >0.90 F1 labels, CC-BY). **Not usable for trajectories — October snapshots only.**
3. **Implement WDE17 exactly as in b.5**, with $C_a=1.3$, $C_w=0.9$, $\Lambda$ built on $|f|$, the $\beta$ underflow clip, and the hemisphere sign flagged as an open question.
4. **Expect the physics core alone to be weak, and say so.** IDRIFTNET measured WDE17-only geodesic ADE at 147 km (A23A) / 127 km (B22A); the learned residual cuts that by 67–82 %. That is the justification for the hybrid design, from a primary source.
5. **For USNIC-size bergs the forecast is only as good as the ocean-current field** ($R<0.13$, wind contributes ~1 %). Invest there, not in drag tuning.
6. **Ship the output as a growing uncertainty region + configurable stand-off**, not a point forecast — matching IIP error circles, the CLS/AEZ pattern, and Polar Code 1.7.3, which requires a stand-off distance but deliberately fixes no number.
