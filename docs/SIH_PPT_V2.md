# SIH 2026 · PS-26059 — corrected six-slide deck

Replaces the submitted deck, which contradicts this repository in eight places
(`docs/MASTER_AUDIT.md` §D.4, corrections 1–8). **Every claim below is traceable
to a file in this repo.** Tags: **[M]** measured here · **[S]** sourced ·
**[D]** derived · **[T]** target, not achieved.

AICTE format: six slides. Do not add a seventh.

---

## Slide 1 — Title
Unchanged. PS-26059 · AI-Enabled Antarctic Sea-Ice, Iceberg Trajectory and
Navigation Decision Support System · Theme: Smart Automation · Software.

---

## Slide 2 — The problem is the last 100 km

> **The ocean crossing is not the problem. The station door is.**

- Bharati's own cell was **closed 23 of 31 days**; the approach 100 km north was
  **open 31 of 31**. The 5,800 km crossing averages **6 % ice**. **[M]**
- The charter is **day rate × 100 days**, so **one held day ≈ 1 % of the
  season's hire**. **[D from S: NCPOR tender]**
- The tender already anticipates ice stopping the discharge — and has **no
  clause for when the fallback is also blocked**. **[S]**
- At the ship's real 8.6 kn the transit is ~15.2 days against a **D+9** forecast
  ceiling: **41 % of the voyage is beyond any forecast at departure**. **[D]**

**Who decides:** the master owns navigation; **the expedition leader owns the
one field that flips route health on 23 of 31 days** — station required, or
approach acceptable. Nothing today computes that consequence for them.

---

## Slide 3 — What the system does

**Nine decision gates. Six of them are grey.**

> **A gate we cannot evaluate is never a pass.** UNKNOWN caps route health at
> DEGRADED, and each grey gate names the dataset that would settle it.

Enforced in code, not in a caption: an empty gate list is DEGRADED, not VALID,
and a test asserts a gate with no data can never read as a pass. **[M]**

**The thirty seconds that matter:** approve a route → advance the clock →
health goes INVALID and the console **names the gate that broke** → step back
and it says nothing, because nothing changed. A plan should degrade when an
assumption breaks, not every time new data arrives. **[M]**

Also built: time-aware routing (each cell costed with the conditions valid when
the ship would arrive), iceberg CPA against the ship's **future** track,
P1/P2/P3 alerting with all nine mandated fields, A/B/C corridors, versioned
attributed approvals.

---

## Slide 4 — Impact

| What changed | Figure | Tag |
|---|---|---|
| Data defect found in the incumbent satellite product | land-spillover writes **0.0 % ice** on **100 % of days**, ~118 cells/day; **43.2 %** of days inside the Bharati box | **[M]** |
| Corrected in the safe direction | coastal mean ice **46.8 → 54.6 %** — masking makes the coast look *heavier*, not lighter | **[M]** |
| Reachability rests on an assumption, and we show where it breaks | reachable at ≥ 50 %, **no route at all at ≤ 45 %** | **[M]** |
| Forecast correction vs the baseline that matters | RMSE **+18.5 %** at 1 day, **+30.6 %** at 7 — **upper bound on skill, not a measurement of it** (leak caveat) | **[M]** |
| Daily pack over Iridium | **7.8 KB gzipped**, 0.09 s at Certus 704 kbps | **[M]** |
| Ship-days saved | **not proven.** Measured regret 0.03 d on one departure; daily re-planning measured *slower* | **[M]** |

**We report our own null result.** Planning on stale ice did not cost this
voyage time. That is a finding about the crossing, not a claim about the season.

---

## Slide 5 — Architecture, proof and feasibility

**Two tiers.** Heavy processing ashore; **the whole router runs aboard**, because
south of ~70°S the link is Iridium or nothing. **[S]**

- Full route search **~2 s** live, PolarRoute pipeline **~9 s** — **on a bridge
  laptop, no GPU**. **[M]**
- **Zero external network calls**, enforced by a test that fails if any
  `http(s)://` appears in the page. **[M]**
- **1,096** real daily NOAA/NSIDC files, 0 failures (one-time archive). The
  separate daily CMEMS cron has 7 files and **failed once**. Two pipelines, two
  statements. **[M]**
- NetCDF compression **42.6 MB → 5.1–5.2 MB (8.2–8.3×)** in production logs. **[M]**
- Routing engine is **BAS's own PolarRoute + meshiphi (MIT)** — reused, with
  three limitations verified in its source. **[M]**
- **₹0 infrastructure spend to date.** Free GPU, free CI, free data, open engine. **[M]**
- 133 tests.

---

## Slide 6 — Research, business and honest limits

**Research that changed the design, not decoration:**
- **POLARIS applicability.** We publish **no RIO for this vessel**, and the
  reason is the result: POLARIS is indexed by ice *type*, no row exists for this
  hull, the Polar Code makes equivalency a per-ship flag-approved assessment, and
  guessing spans **40 RIO points**. **[S]** *(This corrects the submitted deck,
  which claimed POLARIS replaced our 80 % threshold. It did not.)*
- **Iceberg drift** — Wagner–Dell–Eisenman (2017) implemented with three
  numerical traps in the published form found and fixed. **Trajectory error has
  never been measured.** **[M]**
- **Protected areas** — 33 in corridor, **zero marine**, so none restricts
  transit. Modelling them as no-go geometry would have **refused to route to
  India's own station**. **[M]**
- **Standards** — corrected our own brief: 1 Jan 2026 is *voluntary* S-100 ECDIS
  use, 2029 is new installations only, and **S-57 has no sunset date**. **[S]**

**Business.** Per-season programme service contract with NCPOR, priced in the
customer's own units (`N × their charter day rate`), with the post-season
verification report as a contracted deliverable. Procurement via GeM, where a
DPIIT startup is **exempt from turnover, experience and EMD requirements**. **[S]**
Honest ceiling: an **8–12 person specialist company**, not a venture outcome.

**What we have not proven:** a saved ship-day · an iceberg trajectory error ·
one navigator's opinion of the screen.

---

## References
[1] IMO MSC.1/Circ.1519 (POLARIS) · [2] Wagner, Dell & Eisenman 2017,
*J. Phys. Oceanogr.* 47(7) · [3] Ivanova et al. 2015, *The Cryosphere* 9 ·
[4] Lavergne et al. 2019, *The Cryosphere* 13 · [5] USNIC Antarctic Iceberg
Dataset · [6] BAS PolarRoute / meshiphi (MIT) · [7] NOAA/NSIDC CDR G02202 v6 ·
[8] IMO Polar Code Part I-A Ch.11 · [9] MARPOL Annex I Reg. 43
