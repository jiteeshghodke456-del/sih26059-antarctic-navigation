# True Claims — SIH 26059

**The rule for this file: if it is written here, we can put the evidence on
screen in under thirty seconds.** Anything we believe but cannot show lives in
§5 (Designed, not yet built) or nowhere at all.

Read this before the deck. It is the difference between answering a hard
question and absorbing it.

---

## 1. Claims we can prove on the spot

Each of these has a file in this repository that produces the number.

| # | Claim | Evidence |
|---|---|---|
| 1.1 | Our sea-ice model beats **persistence** — the baseline that actually matters — at every horizon from 1 to 7 days, by **+18.5% to +30.6%** | `isih/RESULTS.md` |
| 1.2 | The advantage **grows with lead time**: our error rises 2.1× from day 1 to day 7, persistence rises 2.5× | `isih/RESULTS.md` |
| 1.3 | The test set was scored **exactly once**, split by time, never randomly | `isih/RESULTS.md` |
| 1.4 | The satellite record reports suppressed coastal pixels as **0.0% ice — open water**. It fires on **100% of days**, ~118 cells/day | `isih/figures/ice_quality_audit.json` |
| 1.5 | In the **200 km approach to Bharati** this affects **43.2% of days** across 2018–2020 | same |
| 1.6 | Bharati's own cell was **closed to this vessel on 23 of 31** December 2019 days; the approach 100 km north was open **31 of 31** | `isih/figures/destination_window.json` |
| 1.7 | **Four of the eight** days Bharati appeared reachable were data artifacts reading exactly 0.0% | same |
| 1.8 | Masking those cells moves coastal ice **up** — 46.8% → 54.6% mean — i.e. the fix makes the router *more* cautious | `isih/RESULTS.md` §2 |
| 1.9 | Our iceberg drift model reproduces the published coefficient table and the paper's own 765 m critical length — **23/23 tests pass** | `models/iceberg/test_drift.py` |
| 1.10 | **33 icebergs** tracked live; **15 of them inside our routing corridor**, including D15A at 3,037 km² beside Bharati's approach | `models/iceberg/regime_report.json` |
| 1.11 | Route computed on real satellite ice with a real open-source router: **8.6 days steaming**, Cape Town → Bharati | `isih/RESULTS.md` |
| 1.12 | Built on **1,096 real daily satellite files, zero failures**. No synthetic data anywhere in the product | `isih/RESULTS.md` |

---

## 2. Where we are better than what exists today — and by how much

Each row states the gap, the source that establishes it, and what we do instead.
**None of these say "X is bad."** They say "X does not do this, and here is why
that matters at sea."

### 2.1 Uncertainty never reaches the routing decision

**What exists:** Operational ice services publish a concentration number.
Copernicus OSI SAF does ship per-pixel uncertainty — and its own producers state
that this uncertainty **excludes** melt-pond, thin-ice and weather-filter
effects (Lavergne et al. 2019). So what ships is a precision estimate, not a
total error budget.

**The measured scale of the problem:** across a 30-algorithm round robin,
published sea-ice algorithms disagree with each other by roughly **ten times
more at the ice edge** than in thick pack — standard deviations from 2.8% to
28.8% at low concentration (Ivanova et al. 2015). The ice edge is exactly where
a ship makes its decisions.

**What we do:** the route changes when the model is unsure. Model disagreement
becomes a calibrated safety margin that widens the corridor, rather than a
colour on a map.

> **Search result we could not disprove:** we found **no published study that
> propagates sea-ice forecast uncertainty into a routing decision.** Stated as
> our white space — and flagged in `docs/backlog.md` as medium confidence,
> because the search that established it was cut short.

### 2.2 The nearest Indian precedent is deterministic

**What exists:** an optimum-route study for the **Bharati–Maitri** leg (*Polar
Science*, 2021) — the same corridor we address — using deterministic ice and
wind resistance, with no uncertainty treatment.

**What we do:** the same corridor, probabilistically. This is a precedent that
proves the problem is recognised in the Indian programme, not a competitor we
are trying to displace. Say it that way.

### 2.3 Routers assume the ice holds still

**What exists:** PolarRoute, the open-source engine we reuse, builds one frozen
mesh. Verified by reading the installed source: the route planner has no time
dimension. A 17-day voyage is planned as though it will meet day-zero ice on
day seventeen.

**What we do:** a time-expanded graph — one ice layer per forecast day, so a
lead-time forecast can actually change the route. **A static router structurally
cannot consume a forecast**, which is why this matters more than it sounds.

### 2.4 Sea state costs nothing in the current engine

**What exists:** PolarRoute defines a wave-resistance function and **never calls
it**. Verified in the installed source. Waves act only as a binary cut-off. So
the Roaring Forties impose no speed or fuel penalty at all.

**What we do:** we name it as a known gap and treat our transit times as a
**lower bound** rather than quietly presenting them as predictions.

### 2.5 No one forecasts ice compression in the Antarctic

**What exists:** nothing. Russia's AARI forecasts gridded compression for the
Barents and Kara Seas only; Canada's system is Arctic-only; the Baltic services
publish none. **IMO POLARIS never uses the words pressure, compression, ridge or
drift** — verified across the full text.

Compression is the hazard that traps ships. From 1922 to 1990, **ten ships were
lost on the Northern Sea Route and nine of them to compression.**

**What we do:** we treat it as genuine white space *and* declare the two
constraints honestly — there is **no observational Antarctic ice-drift product
in the December–March season**, and ice strength is exponential in
concentration, so a 5-point concentration error becomes a **2.7× strength
error**. That is why we will not ship a compression number without an error bar.

### 2.6 Most tooling is Arctic-first

Antarctic retrievals are measurably worse than Arctic ones. Against ship
observations, one study reports **R² = 0.41** and the ice edge placed **38–102 km
too far south**. Our system is Antarctic-only, corridor-specific, and calibrated
to the vessel India actually charters.

---

## 3. The claims that make us credible — because they cost us something

Put these **on the slide**, not in your back pocket. An examiner who sees a team
disclose its own failures stops hunting for them.

- **Our own experiment came out against us.** We replaced the strawman
  straight-line route baseline with an honest one — the same router given older
  ice — and on the departure date we tested, planning on stale data cost
  **0.03 days**. Essentially nothing. One date is one sample; we report the null
  result and the multi-date sweep is queued.

- **We withdrew a headline number.** We previously reported a 17.4-day transit.
  It was computed with the ship at roughly **half its real speed** (beam and
  maximum speed were both wrong). Corrected to 8.6 days — and that is *steaming
  time only*.

- **We withdrew a figure caption.** An earlier route figure claimed it "bends
  around the thickest ice". Measurement showed the route crosses **more** average
  ice (19.6% vs 8.4%); only the maximum matters. Caption removed.

- **Our background is a reanalysis, not a live forecast.** This is the sharpest
  question we will be asked. Partial defence: if it contained the answer its own
  error would be near zero, not 0.163 — worse than persistence at every horizon.
  But we do not claim immunity. The clean test is written and not yet run.

- **One physics detail is inferred, not verified.** The reference code for our
  iceberg model deflects icebergs to the right of the wind at every latitude,
  because that paper's quantitative work is Arctic. We flip it left in the
  Southern Hemisphere from the Coriolis sign. It is marked inferred in the code
  and is nearly moot for the giant bergs we track.

---

## 4. What this system is **not**, and will never be

State these plainly. Every one of them is a question you will otherwise be asked.

| We do **not** | Why |
|---|---|
| Warn about **growlers or bergy bits** | A growler is ~5 m; the smallest iceberg tracked in the Antarctic is ~18.5 km. That is a **3.5 order-of-magnitude gap**, and nothing in orbit closes it. Radar and the lookout own this. |
| Steer the ship | We work at hours-to-days and tens of kilometres. Tactical steering stays on the bridge. The problem statement says *Decision Support*, and we mean it. |
| Replace the master's judgement | The system evaluates **the master's intended route first**, then offers alternatives as annotated deltas with reasons. A recommendation that gets rejected for good reasons is a success. |
| Quote a fuel figure | The engine's fuel polynomial is fitted to a different hull. We report fuel relatively or not at all. |
| See leads, ridges, or pressure | A 25 km concentration field cannot resolve a navigable lead, and no product anywhere forecasts Antarctic compression. |
| Claim a POLARIS-compliant limit yet | Our 80% ice threshold is a working stand-in. POLARIS is indexed by ice **type**, so compliance needs a thickness forecast — which is why one is on the roadmap. |
| Solve Southern Ocean traffic | The Indian Ocean sector sees single-digit vessels. We address fleet coordination for the Indian programme, nothing wider. |

---

## 5. Designed, not yet built — the honest roadmap

This is what "we know exactly what to build next" looks like. Sept 4 → December.

| Priority | Work | Status |
|---|---|---|
| 1 | **Time-expanded route graph** — one mesh layer per forecast day | Designed. The single change that makes a forecast usable by a router. |
| 2 | **Iceberg trajectories over time** — needs an ocean-current field; validation against the 1978–2025 observed-track archive | Physics done and tested. Both inputs free. |
| 3 | **Five-model ensemble + conformal calibration** | Specified with a pre-committed pass/fail gate. |
| 4 | **Thickness output channel** → POLARIS compliance | Forced by the regulation, not scope creep. |
| 5 | **Retrain with quality masking** and report error **by distance to coast** | Pooled error hides the cells that decide voyages. |
| 6 | **Bathymetry** — depth is currently constraining nothing | Free download, not yet done. |
| 7 | **Compression risk field** | White space. Blocked on a data decision: modelled drift, or our own feature tracking. |

---

## 6. How close is the architecture to "start building on 5 September"?

Honest assessment, component by component.

| Component | Settled? | What remains |
|---|---|---|
| Sea-ice correction model | ✅ **Settled** | Scale it up. Approach is proven and measured. |
| Data quality layer | ✅ **Settled** | Built this week; extend the same flags into training. |
| Iceberg drift physics | ✅ **Settled** | Implemented and tested. Needs a current field to step forward in time. |
| Routing engine choice | ✅ **Settled** | PolarRoute, reused under MIT. |
| Uncertainty method | ✅ **Settled** | Stratified conformal, with a written pass/fail gate. |
| Vessel calibration | 🟡 **Mostly** | Dimensions verified. Ice class found (ULA); its modern equivalent unsourced. Force limit still borrowed from another hull. |
| Time-expanded routing | 🟡 **Designed** | Known to be necessary; not yet built. |
| Two-phase seam (ocean → ice) | 🟡 **Designed** | Solve the ice leg backwards to a cost-to-go field, then route the ocean leg into it. Not yet an accepted decision record. |
| Compression / risk field | 🔴 **Open** | Genuine white space. Blocked on the drift-data decision. |

**Verdict: roughly 80% settled.** The three unsettled items are all *design*
decisions with known options, not unknowns. Nothing on this list requires a
research breakthrough — which is precisely what you want to be able to say on
4 September.

**What changed this week to get here:**
1. The baseline stopped being a strawman — straight line → same router, older ice.
2. We found the satellite data lies at the coast, and fixed it.
3. The vessel specification was wrong; corrected, and a headline number withdrawn.
4. The problem was reframed: **it is the last 100 km, not the ocean crossing**.
5. The iceberg pillar went from zero code to a tested implementation.
6. POLARIS replaced our invented ice threshold — and forces a thickness output.
7. Compression was identified as real white space *and* as a blocked one.

---

## 7. If an examiner asks

**"How is this different from what already exists?"**
Careful — do not attack a product we have not tested. Say: *"The data layer
every ice service is built on disagrees with itself by about ten times more at
the ice edge than in thick pack, and its producers state their published
uncertainty excludes three known error sources. We found no study that carries
that uncertainty into a routing decision. That is the gap."*

**"Is your 74% closure figure real, or a data artifact?"**
*"The closed days read 80–99% consistently across neighbouring cells and
consecutive days. It is the **open** days that are suspect — four of eight were
artifacts. If anything the true closure rate is higher."*

**"Your model saw a reanalysis, not a forecast. Isn't that leakage?"**
*"Partly defended: if it contained the answer its own error would be near zero,
not 0.163 — worse than persistence at every horizon. But we don't claim
immunity. The ablation that settles it is written and not yet run, and
production corrects a real forecast where the question cannot arise."*

**"Can it tell a captain about the ice that actually sinks ships?"**
*"No, and we say so on the slide. A growler is five metres; the smallest berg
anyone tracks in the Antarctic is eighteen kilometres. Nothing in orbit sees
them. That is radar and the lookout. What we do is stop you being somewhere you
cannot leave."*

**"What have you got that a team starting today hasn't?"**
*"Three years of real satellite data already audited, a bug found in the data
itself, a model that beats the right baseline, a tested implementation of a
published iceberg drift model including a correction to the paper's own
preprint — and a written list of everything we cannot do."*
