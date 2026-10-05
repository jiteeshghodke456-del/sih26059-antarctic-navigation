# Viva Prep — Explain It, Then Defend It

Two halves. **Part 1** explains the whole system simply enough for anyone to
follow. **Part 2** is the hard questions, with honest answers.

Read Part 1 until you can say it without notes. Read Part 2 until nothing in it
surprises you.

---

# PART 1 — The Whole Thing, Simply

## The problem, in one breath

A ship sails to Antarctica once a year to resupply India's research stations.
The sea is full of ice that **moves**, and icebergs the size of cities that
**drift**. Pick the wrong path and you're stuck, burning fuel, or worse.

We're building the thing that says: *go this way.*

## Three questions, three answers

Everything we built answers exactly three questions:

| Question | Our answer |
|---|---|
| Where will the ice be? | A trained model that fixes a weather-service forecast |
| Where will icebergs drift? | Physics equations, not guesswork |
| So which way should the ship go? | A route-finder that treats risk as a real cost |

## Question 1: Where will the ice be?

**What "sea ice concentration" means.** Look down at a patch of ocean 25 km
across. If half of it is ice, that's 50%. That's the number. Not thickness, not
age — just how much of the surface is covered.

**How we see it.** Antarctica is dark for months and usually cloudy, so cameras
are useless. Instead, satellites *listen*. Everything warmer than absolute zero
gives off faint microwave radiation, and ice "sounds" different from water. So
we get a real ice map every single day, through darkness and cloud.

**The clever bit — we didn't build a forecaster.** A European service called
**CMEMS** already runs a giant physics simulation of the ocean and constantly
corrects it with real satellite data. Competing with that in eight days would be
foolish.

So instead of predicting the ice, **our model predicts how wrong CMEMS is.**

```
our answer = CMEMS forecast + our correction
```

Why this is smart, not lazy:
- If our correction is zero, we're exactly as good as CMEMS. **We can't be much
  worse.**
- Learning "where is this forecast off?" is far easier than learning all of
  ocean physics from scratch.
- It needs a small model — which is why it trains in about an hour on a free GPU.

**How it learns.** We show it thousands of real days: here's what the forecast
said, here's what the satellite actually saw. It learns the patterns in the gap.

## Question 2: Where will icebergs drift?

Here we deliberately used **no machine learning at all** for the core.

Picture an iceberg as a raft with ~90% of it hidden underwater. Three forces
move it:
- **Wind** pushes the small part above water
- **Ocean current** pushes the huge part below — usually the bigger effect
- **Coriolis**, the Earth's spin, curves the path sideways (same thing that
  spins hurricanes)

There's a published equation (**Wagner 2017**) that solves this directly. We use
it. It needs zero training data, can't produce a weird answer mid-demo, and it's
what the actual research literature uses as its foundation.

**Why not ML here?** Because we only have iceberg positions once a day or once a
week, for a few hundred big icebergs. That's tiny. Machine learning on tiny data
invents confident nonsense. Physics doesn't.

## Question 3: Which way should the ship go?

Chop the ocean into cells, like a chessboard. Each cell gets a **cost** — how
bad it is to sail through, based on ice, icebergs, and depth. Then find the
cheapest path across.

**Dijkstra's algorithm** does this: always explore the cheapest option you've
found so far, like water finding the easiest way downhill. It's guaranteed to
find the genuinely best path, not just a decent-looking one.

**We didn't write this either.** The **British Antarctic Survey** — the people
who actually run Antarctic ships — published **PolarRoute**, open source. We use
it, then extend it in two places where we found real gaps *by reading their
source code*:

1. **They throw away uncertainty.** Their code deletes the confidence
   information before routing. We keep it and route on "how bad could this
   realistically be," not just the average guess.
2. **They have no iceberg model.** But they left a hook for custom hazards, so
   we plug our drifting icebergs in without modifying their code at all.

## The part that makes it actually usable: it works offline

India's Antarctic ship uses **Iridium** satellite phones. Not broadband — slow,
expensive, sometimes just enough for a text message.

So a system that phones home for answers is **useless on the actual ship.**

Our design: the heavy work (gathering data, training, computing routes) happens
on land. Then everything the ship needs is squeezed into one small file — under
1 KB for a route — sent over the slow link, or carried aboard on a USB stick.

**The routing pipeline itself needs no network at all** — mesh, vessel model,
Dijkstra and smoothing run in about 9 seconds on a laptop CPU, a measured
benchmark of the reused PolarRoute engine.

We do not stage a live "unplug the network" demo: there is no on-demand
re-plan control wired into the app yet, so nothing would visibly happen if a
judge asked for it. What is true and demoable today is narrower and still
real — the running app makes no network call at all; every screen loads from
files already on disk. Wiring a captain-triggered re-plan onto that 9-second
pipeline is designed, not built.

## Prototype vs. Product — be precise about this

| | **ISIH prototype** (Sept 8) | **SIH product** (December) |
|---|---|---|
| Ice model input | 12 channels | 19 channels (adds weather, sea temperature) |
| Trained on | ~2 years | 1993–2024 |
| How many models | 1 | 5 (an "ensemble" — see below) |
| Uncertainty | not yet | measured, and it changes the route |
| Corrects | GLORYS12 (historical reanalysis) | live CMEMS forecast |

**The ensemble, simply:** train five models instead of one. If all five agree,
the situation is easy — be confident. If they disagree, it's genuinely
uncertain — be careful. That disagreement becomes a safety margin that pushes
the route away from risky water.

**Say this in the viva:** "The prototype proves the architecture. The product
adds the uncertainty layer that makes it safe."

---

# PART 2 — Sharp Questions, Honest Answers

## On the ice model

**Q: Why not just use CMEMS directly? Why do you exist?**
Fair, and we ask it ourselves in our own docs. Three reasons: we add a measured
uncertainty band that CMEMS doesn't publish in a routable form; our correction
runs *on the ship*, so a few KB of fresh observation re-corrects the whole
forecast without re-downloading it; and we cross-check multiple ice sources
instead of trusting one. Also — we ship raw CMEMS for any forecast day where we
can't prove we beat it. That's a rule in our code, not a promise.

**Q: How do you know your model isn't just memorising?**
We split by **time**, not randomly. Train on earlier days, test on later ones a
model has never seen. A random split would put Tuesday in training and Wednesday
in testing — and sea ice barely changes overnight, so that would look
spectacular and mean nothing. It's the most common way results in this field get
inflated.

**Q: Isn't yesterday's satellite image already a good forecast?**
**Yes — and this nearly caught us out.** We measured it: predicting today from
yesterday scores 0.0359 error, better than our first model's 0.1051. So we
changed the task: we forecast *days ahead*, where persistence stops being
competitive, and we score persistence at the same range so the comparison is
fair. We found this by testing it, before a judge could.

**Quote only the test-set numbers in the table in `ISIH_RESULTS.md`** — model
0.0968 against persistence 0.1395 at 7 days. There is a second, older set of
persistence figures (0.0359 at 1 day, 0.0610 at 3, 0.0893 at 7) measured over
**full-year 2020, all seasons**; it is in `isih/features.py`'s docstring and it
is not the held-out test slice. Reciting 0.0893 beside the model's 0.0968 makes
it look as though persistence wins at 7 days. It does not — the two numbers are
from different periods and must never be spoken in the same breath. The test
slice is the austral melt season, the last 15% of 2019–2020, where the ice is
moving fastest, persistence is weakest, and the operational question actually
lives.

**Q: Would a simple average correction do as well as your neural network?**
We test exactly that — a per-pixel average bias map and a constant offset, both
scored on the same held-out data. If they match the network, the network is
decoration and we'd say so. The test runs before training, so the bar is set
before we know our result.

**Q: 12 channels — what are they and why?**
The forecast being corrected; the last 7 days of real satellite observations;
the "innovation" (how wrong the forecast was against the newest real
observation); two seasonal signals; and a land mask. The innovation channel
matters most — it tells the model how wrong the forecast is *right now, at this
exact spot*.

## On icebergs

**Q: Why physics instead of AI here, when you used AI for ice?**
Because of the data. Ice: a full satellite map every day for decades — plenty to
learn from. Icebergs: positions maybe weekly, only for the biggest ones, a few
hundred of them. Machine learning on that is unreliable. Using the right tool
for each is the engineering, not a shortcut.

**Q: Your system only tracks huge icebergs. What about small ones?**
Correct, and we display this limitation in the interface rather than hiding it.
Tracking databases only cover icebergs above about 10 nautical miles. The small
"growlers" that actually hole a hull aren't tracked by anyone globally. We'd
rather state that than imply we've solved iceberg safety.

**Q: Why only project drift 72 hours?**
**Say first that we do not project drift at all yet.** `models/iceberg/drift.py`
computes an instantaneous drift *velocity* from the Wagner–Dell–Eisenman
equations — there is no time integrator, so no berg has been stepped forward an
hour, and no trajectory error has been measured. What we have run on the real
USNIC catalogue is a regime check (wind-dominated vs current-dominated) under a
declared sensitivity sweep, because we do not have wind and current at those
positions and did not invent them.

The 72-hour cap is the *design* limit for when projection is built: beyond it
the honest error bars grow large enough that the danger zone would block the
entire route — technically correct, practically useless. Note our own stated
reason for that number has been corrected too: the cap is not supported by a
measured 127–147 km error figure, because the paper that number comes from
never states the rollout length behind it. The defensible reason is simpler —
**no Antarctic tabular-berg error curve exists in the literature at any lead**,
so 72 hours is where the evidence stops, not where a measured curve stops.

Today the map shows last known positions, labelled as observations. That is
honest and it is also one third of PS-26059 still on the roadmap. Do not let
the question pass as though the capability exists.

## On routing

**Q: You used someone else's routing library. What did you actually build?**
We built the ice forecast, the iceberg drift layer, the uncertainty that changes
the route, the offline system, and the interface. For routing specifically, we
found the domain's own tool and extended it in two places we identified by
reading its source. Reimplementing Dijkstra to look impressive would have been
worse engineering and the first thing a knowledgeable judge would question.

**Q: What if your forecast is wrong and the ship gets stuck?**
Layered: we route on a cautious upper bound, not the average. Beyond our proven
skill range we mark the route as planning-grade with a wide band, not a precise
line. And it's decision *support* — it doesn't replace the captain or official
navigation charts, and it says so on screen.

## On honesty and limits

**Q: What's the weakest part of your system?**
The uncertainty calibration for the December model. Our safety margin only means
something if it's genuinely right the percentage of time it claims. We've
written down a numeric pass/fail test in advance, and what we'll do if it fails
— including publicly demoting our own headline claim. It's in
`ML_ARCHITECTURE.md` §1.6.

**Q: Is any of your data or output fake?**
No. Every input traces to a named live source we verified by fetching real files
— we can show you the download logs. No placeholder data anywhere.

**Q: What can't your system do?**
Predict small growlers. Give calibrated absolute fuel numbers (we show relative
comparisons and label the absolutes uncalibrated, because the underlying fuel
curve is fitted to a different ship). Replace official navigation charts. And
much of Antarctic seafloor depth is satellite-estimated, not surveyed — so we
apply a bigger safety margin where the data is predicted rather than measured.

**Q: What would you do with three more months?**
The five-model ensemble with calibrated uncertainty, sea-ice radar imagery for
sharper ice edges, and validation against NCPOR's own station measurements.
They're already scheduled — not aspirations.

---

## When the system is wrong — which way, and why it matters

**Q: What happens when your system is wrong? Which error is worse?**

They are not symmetric, and we designed around the asymmetry rather than around
accuracy.

A **false negative** is calling an impassable cell passable — we route the ship
into ice it cannot handle. In the Southern Ocean the consequence is besetting or
hull damage, with no port of refuge, no nearby salvage and a search-and-rescue
response measured in days. The nearest comparable case on a voyage serving the
Indian programme, MV *Magdalena Oldendorff* in 2002, was beset near
Novolazarevskaya for roughly five and a half months.

A **false positive** is calling a passable cell impassable — the ship takes a
detour it did not need. The cost is hours of steaming, fuel, and charter time
that is expensive but recoverable.

So the errors differ by orders of magnitude in consequence, and a system tuned
for accuracy would trade them one-for-one. We deliberately do not.

**The proof that this is a design principle and not a slogan is in our own
numbers.** When we found the CDR was reporting suppressed coastal pixels as
0.0 % ice and masked them, the coast got *heavier*: 46.8 % → 54.6 % on 1 Dec
2019, 62.5 % → 65.4 % on 10 Dec (`docs/ISIH_RESULTS.md` §2). The fix moved the
system toward more false positives and fewer false negatives, and it made our
own headline result worse — four of the eight days Bharati looked reachable
turned out to be that artifact. We shipped the more cautious reading anyway.
That is the direction a safety system must fail in.

**What we do not have, and will say so:** we have not measured a false-positive
or false-negative *rate* against ground truth. The 80 % ice limit those errors
are defined against is a working stand-in — it comes from no ice class and no
POLARIS row, and `isih/ice_meshes.py` labels it as such in the code. Measuring
the rates needs a passability ground truth we do not have; the honest interim
is to be transparently conservative and to say which number is invented.

---

## Selling it, deploying it, and who pays

**Q: How would this actually be deployed and sold?**

**Deployment** is split by where the resources are, not by preference. The GPU
work — training, ensemble inference, pack building — runs ashore at NCPOR. The
ship carries a CPU-only laptop. Model weights, about 60 MB, never cross the
satellite link; they load from a USB stick at Cape Town before departure, which
is a supported path rather than a degraded one for a vessel that sails once a
season. What crosses the link is a nightly voyage pack of changed cells only,
targeted under 1 MB (ADR-023). Full detail in `docs/PPT_CONTENT.md` §6.

**The pilot path** is NCPOR and the charter operator on the *Golovnin*, because
that is where the credibility already is: the corridor, the vessel and the
season are the ones we built against. From there the same product serves other
national Antarctic programmes running similar-class hulls into similar coastal
approaches — the problem is shared, the ship class is shared, and COMNAP is a
small, well-connected buyer community.

**What is actually sold** is a per-voyage decision pack subscription, not a
box on the bridge. The system does not replace ECDIS and is not a navigation
product; it sits beside it as decision support. That distinction is also what
keeps the regulatory burden proportionate.

**Say the hard part out loud:** this is a small, slow, relationship-driven
institutional market with very few buyers, and if NCPOR declines there is no
substitute customer for the second stage. It is in our backlog as the plan's
single biggest point of failure, with no answer yet.

---

## The 30-second version

> Antarctic ships need to know where ice will be and where icebergs will drift.
> We take Europe's operational ocean forecast and train a model to fix its
> mistakes. We predict iceberg drift with real physics instead of guessing. We
> feed both into the British Antarctic Survey's own routing engine, which we
> extended to actually use uncertainty — something their version throws away.
> And because the ship has almost no internet, the design keeps heavy compute
> ashore and runs the router locally — a 9-second offline benchmark today,
> with the on-demand control for a captain to trigger it still to be built.

## If you remember three things

1. **We correct an existing forecast instead of replacing it** — so we can't be
   much worse, and we're often better.
2. **We chose the right tool per problem** — deep learning for ice (lots of
   data), physics for icebergs (little data). Not "AI everywhere."
3. **We test ourselves harder than the judges will** — we found and fixed our
   own worst flaw (persistence beating our model) before anyone else could.
