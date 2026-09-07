# Foundation-model reuse decision matrix

**Question this document answers:** nine open foundation models were named for
evaluation as reusable building blocks for PS-26059. Which should we use,
adapt, benchmark, or reject — and why?

**Method.** Every model card and file listing below was read directly from the
live Hugging Face Hub on **2026-09-07** via the Hub API, not from search
results or recollection. Where a fact could not be established from the card
itself it is marked `UNVERIFIED` with the source that would settle it. The
governing instruction was explicit: *"Do NOT conclude that any of these models
is suitable simply because it appears on Hugging Face."*

**A caveat about citing this document.** Model cards change. Before any of
these facts goes on a slide, pin the repository revision hash — today's
verification is only reproducible against a commit.

**Headline: no model earns USE.** Not one of the nine forecasts sea-ice
concentration, and not one was trained on the passive-microwave data that
observes it. Two earn ADAPT or BENCHMARK-ONLY for roles adjacent to our
problem. Six are rejected.

---

## 1. The matrix

Format as required: SOURCE → CAPABILITY → EVIDENCE → LIMITATIONS → LICENSE →
COST → DATA REQUIREMENTS → ANTARCTIC RELEVANCE → RECOMMENDATION.

### 1.1 `ibm-nasa-geospatial/Prithvi-WxC-1.0-2300M` — REJECT

| Field | Finding |
|---|---|
| **Source** | IBM + NASA, arXiv 2409.13598, `terratorch` |
| **Capability** | 2.3 B-parameter weather/climate foundation model; two timestamps in, one (possibly future) timestamp out |
| **Evidence** | Card: trained on **160 variables from MERRA-2**; pretrained on forecasting *and* masked reconstruction; input delta ∈ [−3,−6,−9,−12] h, lead ∈ [0,6,12,24] h |
| **Limitations** | The card itself steers this variant away from forecasting: *"We recommend using `prithvi.wxc.2300m.v1` for generic use cases that do not focus on forecasting."* Emulates MERRA-2 at ≈0.5°×0.625° (~55 km) — **coarser than our 25 km target**. Whether sea-ice fraction is among the 160 variables is `UNVERIFIED` (settle via the variable table in arXiv 2409.13598) |
| **License** | CDLA-Permissive-2.0 — commercially usable; **not** the binding constraint |
| **Cost** | 2.3 B parameters rules out fine-tuning on a 16 GB T4 |
| **Data requirements** | MERRA-2 fields across several collections |
| **Antarctic relevance** | Low. In MERRA-2, sea ice is a prescribed boundary, not a prognostic variable — there is nothing for the model to have learned to forecast |
| **Recommendation** | **REJECT.** Wrong variant for forecasting by its own card, coarser than our target, and superseded by §1.2 for any role it could play |

### 1.2 `ibm-nasa-geospatial/Prithvi-WxC-1.0-2300M-rollout` — REJECT (dominated)

| Field | Finding |
|---|---|
| **Capability** | The forecasting variant: further trained for autoregressive rollout, input delta and lead both fixed at 6 h |
| **Evidence** | Card: *"We recommend using `prithvi.wxc.rollout.2300m.v1` for forecasting applications"* |
| **Limitations** | For the one role it could play — supplying forecast forcing — Aurora dominates on size, input resolution, initialisation simplicity and published skill evidence |
| **License** | **apache-2.0 — note this differs from the base model's CDLA-Permissive-2.0.** The prompt's supplied evidence described only the base licence; the two variants are not licensed alike |
| **Recommendation** | **REJECT as dominated**, not as unusable. Reopen only if Aurora fails the T4 fit test |

### 1.3 / 1.4 `Prithvi-EO-2.0-300M` and `-600M` — REJECT

| Field | Finding |
|---|---|
| **Capability** | ViT masked-autoencoder EO backbone with 3D patch/positional embeddings; optional geolocation and day-of-year embeddings |
| **Evidence** | Card: pretrained on NASA **HLS V2 at 30 m**, 4.2 M samples, six **optical** bands (Blue, Green, Red, Narrow NIR, SWIR 1, SWIR 2). Benchmarked on GEO-bench across 0.1–15 m tasks |
| **Limitations** | **Optical only.** Blind through polar night — months of darkness at 69–70°S — and through the Southern Ocean's near-permanent cloud. This is precisely why operational sea-ice monitoring uses passive microwave and SAR. No temporal-forecast objective |
| **License** | apache-2.0 (both) — not the constraint |
| **Antarctic relevance** | Very low, on modality grounds alone |
| **Recommendation** | **REJECT.** Parameters do not fix physics: 600 M fails for the same reason 300 M does |

### 1.5 `ibm-esa-geospatial/TerraMind-1.0-small` — ADAPT (scope decision, not a model decision)

| Field | Finding |
|---|---|
| **Source** | IBM + ESA + Jülich, arXiv 2504.11171 |
| **Capability** | Multimodal any-to-any generative EO model. Raw input modalities: **S2L2A, S2L1C, S1GRD, S1RTC, DEM, RGB** |
| **Evidence** | Card: 500 B tokens, 9 M samples, TerraMesh dataset; PANGAEA benchmark |
| **Why it stands out** | The only candidate with a **physically relevant modality: Sentinel-1 SAR**, which is all-weather, day/night, and the operational standard for ice-edge and iceberg detection |
| **Limitations** | Benchmarks are land tasks (land-use segmentation, water-body mapping, vegetation). Domain shift from TerraMesh's S1 distribution (likely IW VV/VH over land — `UNVERIFIED`) to polar EW HH/HV acquisitions is unquantified |
| **License** | apache-2.0 |
| **Data requirements** | We would need to **start harvesting Sentinel-1** — we currently do not — plus a labelled polar SAR set. AI4Arctic/AutoICE is the candidate and is **Arctic**, not Antarctic (`UNVERIFIED`) |
| **Antarctic relevance** | Moderate, for *nowcasting* the ice edge and icebergs — **not** for SIC forecasting |
| **Recommendation** | **ADAPT**, if and only if we take on SAR. `small` is the variant that fine-tunes on a T4. This is a scope decision about whether to add a data modality, not a judgement that the model is unsuitable |

### 1.6 `ibm-esa-geospatial/TerraMind-1.0-base` — BENCHMARK-ONLY

| Field | Finding |
|---|---|
| **Role** | Frozen-encoder comparison against a fine-tuned `small` on the same SAR task |
| **Limitations** | Full fine-tune of `base` on 16 GB is `UNVERIFIED`. **Never use any-to-any generation operationally**: the card warns its generations *"are not reconstructions but 'mental images'"* — a generated ice edge is a hallucinated navigation hazard |
| **Recommendation** | **BENCHMARK-ONLY**, with generation explicitly excluded from any operational path |

### 1.7 `microsoft/aurora` — BENCHMARK-ONLY

| Field | Finding |
|---|---|
| **Source** | Microsoft; Bodnar et al., *Nature* 2025, doi 10.1038/s41586-025-09005-y |
| **Capability** | Earth-system foundation model. **Verified by file listing**, the repository contains exactly these checkpoints: `aurora-0.1-finetuned`, `aurora-0.25-pretrained`, `-12h-pretrained`, `-finetuned`, `-small-pretrained`, `-v1.5`, `-v1.5-ensemble`, **`aurora-0.25-wave`**, **`aurora-0.4-air-pollution`** |
| **Evidence** | **There is no sea-ice checkpoint in the repository.** Tags cover atmospheric dynamics, atmospheric chemistry, ocean waves, tropical-cyclone tracking |
| **Why it is interesting** | Its documented job — causal 6-hourly rollouts of surface wind and temperature — is precisely what our U-Net lacks, and it runs without fine-tuning |
| **Limitations** | Polar-region skill not separately evidenced (`UNVERIFIED`). Parameter count and ERA5 training window, specifically whether 2020 is inside it, `UNVERIFIED` (settle in the paper) — this matters because our test slice would then be in its training data. 16 GB Turing has no native bf16; fp16/fp32 tolerance `UNVERIFIED` |
| **License** | MIT — the cleanest of the nine |
| **Antarctic relevance** | Indirect but real: forcing supplier, and `aurora-0.25-wave` is relevant to the Cape Town crossing, the roughest ocean on Earth |
| **Recommendation** | **BENCHMARK-ONLY.** Benchmark as a forcing supplier **against free operational NWP**, and adopt only on evidence. See §2 — this is the decision that matters |

### 1.8 `OneScience-Group/Pangu_Weather` — REJECT

| Field | Finding |
|---|---|
| **Evidence** | README states verbatim: *"This repository is a reproduction of the original Pangu-Weather paper."* **17 downloads total.** Original is Huawei Cloud, *Nature* 2023 |
| **Limitations** | Unverifiable weights. A third-party reproduction gives no auditable skill claim |
| **Supply chain** | Install instructions pull from `http://mirrors.onescience.ai:3141` with `--trusted-host` — **plain HTTP**. For a deployment aimed at a government research programme this is on its own a sufficient objection |
| **License** | apache-2.0 *on the reproduction*. If the original weights are non-commercial (`UNVERIFIED` — check Huawei's licence), an Apache-2.0 label here is either a relicensing they cannot perform or a from-scratch retrain of unknown quality. Either reading argues against use |
| **Recommendation** | **REJECT.** A citable Pangu means the original, at which point licence may bind — and Aurora already fills the role under MIT |

### 1.9 `OneScience-Group/SatMAE` — REJECT

| Field | Finding |
|---|---|
| **Evidence** | README states verbatim: *"The weight files will be uploaded soon and are expected to be completed in the near future."* **16 downloads.** Pretrained on fMoW (functional map of the world — buildings and land use) and fMoW-Sentinel |
| **Limitations** | **There is nothing to run.** You cannot reuse weights that do not exist |
| **License** | **cc-by-nc-4.0 — non-commercial.** This alone forecloses the startup path in §39 |
| **Antarctic relevance** | None |
| **Recommendation** | **REJECT.** It fails on every axis: no weights, wrong domain, wrong modality, prohibitive licence. It is a placeholder repository, not a candidate |

---

## 2. The decision that actually matters

The interesting question is **not** "should a foundation model replace our
U-Net". It clearly should not — see §3. The question is whether one should
supply the **wind and temperature forcing our U-Net demonstrably lacks**:
`docs/ISIH_RESULTS.md` names ERA5 wind and temperature as the top
unimplemented improvement, and the model currently has 12 channels containing
neither.

That reframe survives scrutiny only after being split in two.

**(i) The architecture is right.** The SIC model should receive *forecast*
atmospheric forcing over [t, t+lead], and be trained on forcing of the quality
it will actually see in deployment. This is defensible and non-obvious.

**(ii) The instrument choice is not automatic.** A free operational NWP feed
supplies the same variables with skill a 1.3 B-parameter model on a T4 will
not beat. Presented as *"we integrated Aurora"*, this is bolt-on, and the
first expert question — *"why not ECMWF open data?"* — has no good answer.
Presented as *"forcing is a pluggable service; we benchmarked foundation model
against NWP against persisted analysis and chose on evidence"*, it is
engineering.

### 2.1 The leakage trap — and a correction to our own roadmap

Define the leak precisely: **an input channel valid at t+lead whose generation
used observations from the interval (t, t+lead]**.

- **Reanalysis valid at t+lead is a leak.** This is our known GLORYS12 issue.
- **It would be a *worse* leak for temperature.** In ERA5 and MERRA-2, sea ice
  is not forecast — it is **prescribed from satellite SIC as the lower boundary
  condition** (`UNVERIFIED`, being checked against ECMWF and NASA GMAO
  documentation). Two-metre temperature over the marginal ice zone is
  therefore close to a deterministic function of the *observed* ice at that
  date, given the large ice/water thermal contrast.
- **Therefore: adding "ERA5 wind and temperature at t+lead", exactly as
  `docs/ISIH_RESULTS.md` currently recommends, would add a second leak and
  make our results less defensible, not more.** Corrected below.
- **A forecast rollout is categorically different.** Output at t+lead
  initialised from analyses at t−6 h and t is a deterministic function of
  information available at t — the same information set as our persistence
  channel. Training such a model on reanalysis is *not* a leak: every AI
  weather model is trained on ERA5 and evaluated causally. That is the
  accepted protocol.

### 2.2 The cheapest decisive experiment

Gates in order, each cheap enough to abandon:

- **Gate 0 (≈1 day, no foundation model).** Add ERA5 10 m U/V **valid at t**
  as two channels; retrain all four horizons, same seed. If this does not help
  even at 1-day lead, forcing does not help this architecture and the branch
  closes.
- **Gate 1 (≈1 hour).** Does `aurora-0.25-pretrained` forward-pass fit 16 GB?
  If not, fall back to `aurora-0.25-small-pretrained`.
- **The four-arm test.** Score the test slice with forcing from (a) ERA5 at
  t+lead [leaky upper bound], (b) ERA5 at t persisted [causal, free],
  (c) Aurora rollout [causal, foundation model], (d) archived GFS forecast
  [causal, NWP]. **Adopt Aurora only if (c) beats (d) by more than the
  seed-to-seed spread** — which requires ≥3 seeds, since one seed cannot
  resolve a few percent.

### 2.3 The physics upgrade worth more than any foundation model

Do not feed raw wind — feed the **wind-advected first guess**. Free-drift ice
moves at roughly 2% of the 10 m wind speed, deflected left of the wind in the
Southern Hemisphere (Nansen rule; coefficient and turning angle `UNVERIFIED`
pending Thorndike & Colony). Semi-Lagrangian advection of SIC(t) by that
drift over [t, t+lead] is simultaneously **a stronger baseline our model must
beat**, a better input channel than raw wind because it encodes physics the
CNN would otherwise infer from ~1,000 days, and the way ice navigators
actually reason.

---

## 3. Why no foundation model forecasts Antarctic sea ice

**The claim we can defend, stated bounded:** *"None of the nine open
checkpoints we adjudicated forecasts sea-ice concentration or was trained on
polar passive-microwave data. The reanalyses the weather models emulate treat
sea ice as a prescribed observational boundary rather than a prognostic
variable, so there is nothing for such a model to have learned to forecast."*

**Do not** claim the unbounded negative "no foundation model forecasts
Antarctic sea ice". It is unverifiable and one counterexample from a judge
sinks it.

Why the absence is structurally unsurprising:

1. **Variable set.** Atmospheric models inherit their reanalysis's prognostic
   set, in which SIC is an input. No target, no model.
2. **Modality.** The only continuous, all-weather, multi-decade SIC record is
   passive microwave at 25 km — a modality none of the EO models pretrained
   on.
3. **Physics.** SIC is a bounded, heavily censored field (mostly exact 0 or 1)
   of a thin fractured solid with plastic rheology. Antarctic specifics:
   unconfined to the north, largely seasonal first-year ice, a wide
   wave-affected marginal ice zone, extent swinging roughly 3→18 million km²
   annually.
4. **Scale — the strongest argument.** The entire 1979-present daily SIC
   record is on the order of 17,000 frames of ~10⁵ pixels. That is *tiny* by
   foundation-model standards. The premise that scale unlocks transfer does
   not apply, and a ~2 M-parameter CNN saturates the available information.
   **This is an information-theoretic argument, not a compute-budget one** —
   and it is the argument to make.
5. **Benchmarks.** No sea-ice task in the major EO or weather benchmarks
   (`UNVERIFIED` for WeatherBench2's exact list), so no incentive.

**Prior art we must cite, currently `UNVERIFIED` and being checked:**
**IceNet** (Andersson et al., *Nature Communications* 2021, British Antarctic
Survey) — reported as a U-Net at 25 km. If confirmed, this is the strongest
possible support for our architecture: the field's own choice for this target
was a small purpose-built U-Net, not a foundation model. Also to check:
SICNet, SIPN South (Antarctic community forecast exercise), AI4Arctic/AutoICE.

---

## 4. The answer to "why didn't you just use a foundation model?"

> We adjudicated nine open Earth-observation and weather foundation models
> against one question: does the checkpoint forecast sea-ice concentration, or
> was it trained on the passive-microwave data that observes it? None was. The
> weather models emulate reanalyses in which sea ice is a prescribed boundary,
> not a forecast variable; the EO models are pretrained on optical or
> land-focused imagery, whereas the only continuous all-weather record of
> Antarctic sea ice is 25 km passive microwave. That target is a bounded field
> with three years of daily data — small enough that a 1.9-million-parameter
> U-Net trained on a free T4 beats persistence by 18–31% at one- to seven-day
> leads on a held-out melt season, under a protocol whose upper-bound nature we
> disclose. Where a foundation model does fit — Aurora for forecast wind
> forcing, TerraMind for SAR iceberg detection — it is on our roadmap as a
> benchmarked component, not a replacement.

---

## 5. What this changes

| Change | Where | Status |
|---|---|---|
| ERA5 wind/temp **at t+lead** removed as a recommendation — it adds a leak | `docs/ISIH_RESULTS.md` | to fix |
| Leak-free ablation (channel 0 = `background[t]`) is now the highest-value single experiment | `docs/backlog.md` | to file |
| "We couldn't afford a foundation model" replaced by "the target is too small to need one" | pitch materials | to fix |
| Stronger baseline needed: persistence + climatological tendency | `docs/backlog.md` | to file |
| ≥3 seeds required before comparing arms that differ by a few percent | `docs/backlog.md` | to file |
| Licence must not appear as a reason in the Prithvi or Aurora verdicts | this document | done |

**Open verifications** are tracked in §2.1, §2.3 and §3 above, each marked
`UNVERIFIED` with the source that settles it. None may reach a slide until
checked.
