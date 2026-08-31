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

**The ship then re-plans routes entirely offline, in about 9 seconds.**

In the demo: unplug the network, keep planning. That's not a trick — that's how
it's designed to work at sea.

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
changed the task. Persistence decays fast — 0.0359 at 1 day, 0.0610 at 3, 0.0893
at 7 — so we forecast *days ahead*, where it stops being competitive, and we
score persistence at the same range so the comparison is fair. We found this by
testing it, before a judge could.

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
Because beyond that, honest error bars get so large (100+ km) the danger zone
would block the entire route — technically correct, practically useless. We cap
it at 72 hours and refresh daily from new observations. Past that we show last
known positions, labelled as observations, not predictions.

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

## The 30-second version

> Antarctic ships need to know where ice will be and where icebergs will drift.
> We take Europe's operational ocean forecast and train a model to fix its
> mistakes. We predict iceberg drift with real physics instead of guessing. We
> feed both into the British Antarctic Survey's own routing engine, which we
> extended to actually use uncertainty — something their version throws away.
> And because the ship has almost no internet, everything runs offline on a
> laptop on the bridge. Unplug the network and it still works.

## If you remember three things

1. **We correct an existing forecast instead of replacing it** — so we can't be
   much worse, and we're often better.
2. **We chose the right tool per problem** — deep learning for ice (lots of
   data), physics for icebergs (little data). Not "AI everywhere."
3. **We test ourselves harder than the judges will** — we found and fixed our
   own worst flaw (persistence beating our model) before anyone else could.
