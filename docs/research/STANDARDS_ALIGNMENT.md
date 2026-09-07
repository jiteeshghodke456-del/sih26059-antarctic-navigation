# Standards alignment — the professional navigation stack

§31 names a digital navigation stack this system should align with. Before this
document, `S-101`, `S-111`, `S-124`, `A.893`, `SOLAS`, `WMO Manual 558` and
`squat` had **zero occurrences anywhere in the repository** — and unlike every
other documented gap, none of them even had a backlog line.

Everything below was obtained by fetching IHO's and IMO's own PDFs directly.
Where a primary source could not be read, the item says `UNVERIFIED` and names
what would settle it. That discipline matters here more than usual: a
confidently wrong standards claim in front of a maritime audience is worse than
an admitted gap.

---

## 1. The correction that matters most

**Our own source brief states that IHO S-101 "is the operational ENC product
specification from 1 January 2026". That is not what IHO says**, and it would
be a specific, checkable error in front of anyone who follows this.

IHO's *Roadmap for the S-100 Implementation Decade*, v5.0, October 2025, keeps
four facts apart that the claim collapses into one:

| Fact | What it actually is |
|---|---|
| **1 January 2026** | The date S-100 **ECDIS** *may be used voluntarily*. Verbatim: *"S-100 ECDIS can be used voluntary from 1 January 2026 and will be mandated in new installations from 1 January 2029."* An equipment permission — not a chart-production cutover, not a mandate |
| **2025 → 2026** | Member States asked to begin regular **native S-101 production**, coverage "gradually growing in the course of 2026" — **in parallel with** continued S-57 production |
| **1 January 2029** | S-100 ECDIS mandatory for **new installations only**. Not a fleet retrofit, and it does not retire S-57 |
| **S-57's sunset** | **There is none.** Verbatim: *"If the results indicate that there will be widespread and substantial residual dependence on S-57 ENCs, limited provisions will be made to extend the period to ensure an orderly transition."* |

This is the **"dual fuel"** model: new ECDIS from 2025 must process S-57 and
S-101 in parallel with identical presentation.

**The sentence that is safe to say:**

> S-101 native production is ramping through 2025–2026 under a dual-fuel model
> alongside S-57, with no fixed S-57 retirement date; S-100 ECDIS carriage
> becomes mandatory for new installations only from 1 January 2029.

---

## 2. The S-100 family, and the one we are not using

| Spec | What it is | Relevance here |
|---|---|---|
| **S-100** | The IHO Universal Hydrographic Data Model — a framework built on ISO 19100, not a chart | Vocabulary, not implementation |
| **S-101** | Electronic navigational chart | The base layer we do not have |
| **S-102** | Gridded **bathymetric surface** | Directly the "no bathymetry in the routing mesh" gap. Designed to interoperate with S-101 and S-104 |
| **S-104** | Water level / tidal information | Turns a static charted depth into a predicted depth at a time |
| **S-111** | Surface currents | Set and drift |
| **S-124** | Navigational warnings, structured | Digital successor to free-text NAVTEX/NAVAREA |
| **S-129** | Under-keel clearance management | The *output* product a tool like this should eventually speak |
| **S-98** | "Data Product Interoperability in S-100 Navigational Systems" | How several S-100 datasets combine on one display rather than as silos |

**And the find worth acting on: S-411 Sea Ice.** The IHO Roadmap states that a
regular **S-411 sea-ice data service is already operational** through the JCOMM
Ice Logistics Portal, for world regions including **"Southern (Antarctica)"**.
That is a live, standards-based, Antarctic-specific ice data source, in the
professional format, that this project is not using and had not heard of.
Filed.

---

## 3. IMO instruments

### 3.1 A.893(21) — Guidelines for Voyage Planning
Adopted 25 November 1999. The four stages, quoted from §1.3:

> "Voyage and passage planning includes **appraisal**… detailed **planning** of
> the whole voyage or passage from berth to berth… **execution** of the plan;
> and the **monitoring** of the progress of the vessel in the implementation of
> the plan."

Our §4 workflow maps onto this cleanly, which is worth saying: command centre
and voyage/mission definition are *appraisal*; route creation, waypoints and
review are *planning*; approval and active navigation are *execution*; and the
day slider with route health and divergence detection is *monitoring*.

Two clauses to lift verbatim, because they name things we had treated as our
own inventions:

- **§3.2.2** — *"allowance for the increase of draught due to **squat and heel
  effect** when turning"*. Squat is named in the IMO guideline itself.
- **§3.2.3** — *"minimum clearance required under the keel in critical areas
  with restricted water depth"*. The textual hook for a UKC feature.

### 3.2 How a non-binding guideline becomes practically mandatory
**SOLAS V/34 §1**, verbatim (via MSC.99(73), in force 1 July 2002):

> "Prior to proceeding to sea, the master shall ensure that the intended voyage
> has been planned using the appropriate nautical charts and nautical
> publications for the area concerned, **taking into account the guidelines and
> recommendations developed by the Organization**."

That is the mechanism. A.893(21) is a non-binding Assembly resolution; SOLAS
V/34 is a binding Convention regulation requiring plans to take it into
account. §34 also carries the master's-discretion clause — owners "shall not
prevent or restrict the master… from taking or executing any decision which, in
the master's professional judgement, is necessary for safe navigation" — which
is the treaty-level statement of the same principle our global rule 12 encodes.

### 3.3 Other SOLAS Chapter V regulations that bear on this
- **Reg 19** — carriage: charts and publications, *"an ECDIS may be accepted as
  meeting the chart carriage requirements"*, GNSS, echo sounder, 9 GHz radar,
  AIS (≥300 GT), gyrocompass (≥500 GT).
- **Reg 27** — charts and publications *"shall be adequate and up to date"*.

**ECDIS is two instruments, not one**, and citing them together is a tell:
- **MSC.232(82)** (2006) — Revised Performance Standards for ECDIS. What the
  equipment must do.
- **MSC.282(86)** (2009) — inserted the carriage schedule at SOLAS V/19.2.10.
  Who must carry it and by when.

### 3.4 Polar Code Part I-A Chapter 11 — what it adds
Via MSC.385(94). It does **not** restructure appraisal/planning/execution/
monitoring; it adds a mandatory polar hazard layer inside them. The two clauses
that are load-bearing for this project, verbatim:

- **§11.3.2** — *"any limitations of the hydrographic information and aids to
  navigation available"*. **This is IMO instructing the master to treat charted
  confidence as non-uniform in polar waters** — which is precisely the argument
  our chart gate makes when it returns UNKNOWN because the mesh carries no
  bathymetry. We were not being pedantic; we were being compliant.
- **§11.3.9** — *"operation in areas remote from SAR capabilities"*. The
  standards hook for GMDSS-coverage awareness. Most of the Antarctic operating
  area is **Sea Area A4**.

---

## 4. Sensors and the data-exchange layer

| Item | Standard | Free? | What integration would actually take |
|---|---|---|---|
| **AIS** | **ITU-R M.1371-6** (Feb 2026); carriage SOLAS V/19.2.4 | **Yes — ITU states "Free Download"** | Cheapest live-traffic feed. Prototypable today via a shore/satellite aggregator, no hardware |
| **Radar / ARPA** | **MSC.192(79)** (2004) — unifies the former separate radar and ARPA standards | Target data usually proprietary | Most expensive here, and **the sensor that matters most for ice**: growlers and bergy bits do not transmit AIS |
| **GNSS** | MSC.112(73) (2000), GPS-specific; a multi-constellation successor exists — number `UNVERIFIED` | — | Cheapest sensor; universal NMEA output |
| **Gyro** | Commonly cited as A.424(XI) — `UNVERIFIED` | — | Mandatory ≥500 GT under V/19.2.5 |
| **Echo sounder** | A.224(VII), updated by MSC.74(69) Annex 4 | — | **The live cross-check against a static bathymetric model** — it catches the case where the chart is wrong, which §11.3.2 says is the normal case here |
| **GMDSS** | SOLAS Chapter IV | — | For us this means *modelling sea areas A1–A4*, not radio hardware |
| **IEC 61162 / NMEA 0183, 2000** | Paywalled | Specs paid; parsers thoroughly open-sourced | The substrate under all of the above |

---

## 5. Chart quality, under-keel clearance, and squat

**CATZOC** — Category of Zone of Confidence, an S-57 attribute encoding
position accuracy, depth accuracy and seafloor coverage in bands (A1 best,
through A2/B/C/D to U unassessed), keyed to survey categories in **IHO S-44**.
Exact band definitions and S-101's replacement mechanism are `UNVERIFIED`;
settle against the S-101 Feature Catalogue and **IHO S-67**, the *Mariner's
Guide to Accuracy of Depth Information in ENCs*.

**Squat** — sinkage and trim increase in shallow or confined water because
accelerated flow between hull and seabed lowers pressure; the effect scales
with the **square of speed** and grows sharply as depth-to-draught ratio falls.
Barrass's method is the commonly named formulation, with separate open-water
and confined-channel forms. **The coefficients are `UNVERIFIED` and must not be
used in a margin calculation until checked** against Barrass & Derrett or
PIANC's *Harbour Approach Channels Design Guidelines* (2014). What *is* safely
citable is that A.893(21) §3.2.2 names squat as a voyage-planning factor — that
is the standards-level reason to model it, independent of which formula.

**Why "a depth value is not equally reliable everywhere" is the standards' own
posture, not ours:** IHO's chart-quality model is built on survey coverage
varying by area and requires that variability to be *encoded and displayed*
rather than smoothed; and Polar Code §11.3.2 independently requires the master
to weigh the limitations of the hydrographic information available. A tool
carrying one global "trust the seabed" assumption is less standards-aligned
than one carrying per-cell confidence — which describes most of the Antarctic
coast, and is why our chart gate is UNKNOWN rather than PASS.

---

## 6. WMO — and an unresolved citation

A.893(21) itself cites *"Volume D of WMO Publication No. 9"* for weather-routeing
services, which confirms IMO anchors to numbered WMO documents.

**`WMO Manual 558` could not be verified**, and no evidence was found that it is
a sea-ice document at all. WMO's e-Library renders client-side and could not be
read this session. The sea-ice terminology reference is **most likely
WMO-No. 259, *WMO Sea-Ice Nomenclature*** — but that is prior knowledge, not
confirmed against a primary source, and is marked `UNVERIFIED`.

If WMO-No. 259 is correct, it sits *above* our existing citations rather than
beside them: **MANICE and the WMO egg code are operational implementations of
that nomenclature in one ice service's charting practice, not substitutes for
citing the underlying international standard.** Check at library.wmo.int before
either number reaches a slide.

---

## 7. The honest roadmap to a real bridge

In dependency order, each tied to an instrument above. This is what §31
alignment would actually cost, and it is written as a roadmap a mariner would
recognise rather than as an apology.

0. **Data-exchange layer** (IEC 61162 / NMEA). Not a sensor — the substrate.
   Skipping it makes every later sensor a bespoke integration.
1. **ENC** (S-57 today, dual-fuel S-101 from 2025–26). The only thing SOLAS
   V/19 and V/27 actually mandate. Antarctic coverage is sparse, which is
   exactly why step 2 matters as much.
2. **S-102 bathymetric surface into the routing mesh.** Closes the chart gate
   and makes the vessel's currently inert `min_depth` constraint real.
3. **GNSS position + gyro heading.** Makes the route live rather than static —
   the prerequisite for A.893(21)'s *monitoring* stage to mean anything.
4. **AIS** — cheapest, spec is free, prototypable with no hardware.
5. **Radar / ARPA** — buys detection of everything that does not transmit,
   which in these waters is the ice.
6. **Echo sounder** — the live cross-check that catches a wrong chart.
7. **S-104 / S-111** — the dynamic correction that turns a bathymetric grid
   into a real under-keel clearance at a time.
8. **S-124 warnings and the operational S-411 Sea Ice service** — the most
   Antarctic-relevant, already-available, currently-unused source on this list.
9. **GMDSS coverage awareness** (sea areas A1–A4) — not radio hardware, a
   coverage model, so the tool can flag what Polar Code §11.3.9 requires.

---

## 7A. MARPOL and the Antarctic Special Area

Reinstated here because **MARPOL was named in the master prompt and lost when it
was compressed** (`docs/MASTER_AUDIT.md` §A.4). Worth stating precisely: the
requirement went missing from the *prompt*, not from the project — the heavy
fuel oil ban was already researched and recorded in `docs/backlog.md` and
`docs/ppt_source/research.md`. What was missing was its place in the standards
stack, which is what this section fixes.

### 7A.1 Annex I Regulation 43 — the heavy fuel oil ban

Carriage **and** use of heavy fuel oil is prohibited south of 60°S. Mandatory
since 1 August 2011; the only exemption is for vessels engaged in securing the
safety of a ship or in a search-and-rescue operation.

Consequences for this project, in order of how much they change the software:

1. **The entire modelled route south of 60°S is inside the ban.** The vessel runs
   MGO/MDO, not HFO. Any fuel-consumption figure that assumes a residual fuel
   price or density is wrong for this corridor.
2. It is **a single latitude test**, not a polygon — cheaper than the protected
   areas layer already implemented.
3. Do **not** conflate it with Regulation 43A, which is the *Arctic* ban
   (MEPC.329(76), in force 1 July 2024 with waivers to 2029). Different
   instrument, different geography, different dates.

### 7A.2 Annexes IV and V — sewage and garbage

The Antarctic area is a **Special Area** under Annexes I, II and V. Garbage
discharge is prohibited; sewage discharge is restricted by distance from ice
shelves and fast ice, not merely from land. For a decision-support tool the
operational consequence is that **discharge planning is a voyage constraint with
a geographic component**, in the same family as the ASPA/ASMA layer already
built — it is a candidate layer, not a compliance engine, and this project does
not implement it.

### 7A.3 Why it belongs in a navigation tool at all

It does not change where the ship can safely go; it changes what the ship must
carry and what it may release along the way. The honest scope statement is that
MARPOL constrains **voyage preparation and waste handling**, and this system
touches it at exactly one point: the fuel assumption behind any energy or cost
figure. That point is now recorded rather than assumed.

---

## 8. Everything left UNVERIFIED

WMO-No. 558 and No. 574 identities; WMO-No. 259 as the sea-ice nomenclature;
exact CATZOC band definitions and S-101's quality-of-bathymetric-data
mechanism; Barrass squat coefficients (both forms); the gyro performance
standard number; the multi-constellation GNSS successor to MSC.112(73);
whether SOLAS V/34's master's-discretion clause was later renumbered as
"34-1"; current S-101/S-102 edition numbers; and the full text of the Roadmap's
Annex 4 dual-fuel concept, whose title and role are confirmed but whose content
was not machine-readable.
