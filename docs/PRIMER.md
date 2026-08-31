# SIH26059 Primer — What the Team Actually Needs to Understand

This is not a link list. It teaches the ideas behind every major decision in
`ARCHITECTURE.md` and `ML_ARCHITECTURE.md`, in plain language, so anyone on
the team can read a chapter and actually understand what we built and why —
not just recognize the vocabulary. Real technical terms are used and defined
the first time they appear (look for **bolded terms** — that's your cue a
definition follows). Sources are at the end of each chapter, and now that
you'll understand the concept first, they'll actually make sense when you
open them.

Read the chapter for your role first (see `TEAM_GUIDE.md` for who owns
what), then skim the rest — every part of this system touches every other
part.

---

## Chapter 1 — Forecasting Sea Ice: What It Is, and How We Predict It

### What "sea ice concentration" actually means

When we say "40% sea ice concentration" in a map cell, we mean: if you could
look down at that patch of ocean (say, 25 km × 25 km), 40% of its surface is
covered in ice and 60% is open water. That's it. It says nothing about how
*thick* the ice is, or how old it is — just how much of the surface it
covers. This one number is the single most important thing for a ship,
because it roughly tells you "can I sail through here at all."

### How satellites actually see this, at night, through cloud

You can't just point a camera at Antarctica in winter — it's dark for
months, and often cloudy. Instead, satellites carry **passive microwave
radiometers** — instruments that don't shine any light down, they just
*listen* for the natural microwave radiation every surface constantly gives
off (everything above absolute zero radiates some energy; microwaves are
one band of that). Ice and open water emit microwaves differently, so a
satellite can tell them apart from the pattern of radiation alone, day or
night, cloud or clear sky. That's why this kind of data (not ordinary
photos) is the backbone of sea-ice monitoring.

### The forecasting problem, in one sentence

Given today's ice map, plus a forecast of wind/current/temperature for the
next several days, predict tomorrow's ice map — and the map for each of the
next 10 days. This has to be done for every grid cell at once: it's not one
number to predict, it's a whole map, every day.

### The "obvious" approach, and why we didn't build it

The obvious idea: train a neural network that looks at recent ice maps and
weather, and directly predicts the future ice map from scratch. This is what
most competing teams will build (see `COMPETITIVE_ANALYSIS.md`).

Here's the problem: an organization called **CMEMS** (Copernicus Marine
Service — a real European operational forecasting service) already runs a
full physics simulation of the ocean and ice — a system that solves the
actual equations of fluid motion for water and ice, continuously corrected
against real satellite observations (a process called **data assimilation**
— think of it as constantly nudging the simulation back toward reality every
time new real data comes in, so it never drifts too far off). This CMEMS
forecast is *already good*. Building a from-scratch model and hoping to beat
a system like that, on a hackathon timeline, is a losing bet — and worse,
our own research (`COMPETITIVE_ANALYSIS.md`) explicitly says CMEMS is "the
bar to beat." A first version of our design tried to beat it head-on and an
adversarial review caught that it wasn't going to work (see
`WEAKNESS_ANALYSIS.md`).

### What we actually built: a correction model, not a forecaster

Instead, our model's only job is: **look at CMEMS's forecast, and predict
how wrong it probably is, and in which direction.** This "leftover error" is
called a **residual**. Formally: `corrected forecast = CMEMS's forecast +
our predicted correction`.

Why this is a smarter design, not a smaller one:
- If our correction model predicts zero, we're exactly as good as CMEMS —
  we can never be *worse* by much, because we're not replacing the hard
  part (the physics), only refining it.
- The task is genuinely easier: instead of "predict the whole ice map,"
  it's "predict how far off is *this specific* forecast, given what we can
  see right now" — a smaller, more learnable problem.
- It needs a much smaller neural network (roughly 3 million adjustable
  numbers, called **parameters**, instead of the 8–15 million a from-scratch
  forecaster would need) — which trains faster and fits inside a free-tier
  GPU budget (see `ML_ARCHITECTURE.md` §1.3 for the actual math).

### What a U-Net is, and why we use one

A **U-Net** is a type of neural network built specifically for image-shaped
data — a grid of numbers, like a photo, or in our case, a grid of ice
percentages. Picture it as an hourglass shape:

1. The first half repeatedly shrinks the image down, layer by layer. Each
   shrinking step forces the network to summarize a wider area into fewer
   numbers, so early layers see fine detail and later layers see the big
   picture ("there's a large ice mass here," "this whole region is under
   storm influence").
2. The second half expands it back up, step by step, turning that
   big-picture understanding back into a full-resolution answer — one
   number per grid cell again.
3. Crucially, there are **skip connections**: shortcuts that carry the fine
   detail directly from the shrinking half to the matching expanding step,
   so that detail isn't lost just because the middle of the network was
   busy thinking about the big picture.

Why this shape matters for us specifically: the single most important line
on the map is the **ice edge** — the boundary between ice and open water.
U-Nets were originally invented for finding precise boundaries in microscope
images (where's the exact edge of this cell), and that's exactly the skill
we need here: not just "roughly where's the ice," but "exactly where does
it start."

### Why five copies of the model (an ensemble), and what that buys us

We train **five separate copies** of this correction model — same design,
different random starting points, and each one sees a slightly different
version of the training data (a technique called **input perturbation** —
deliberately jittering the inputs a little, like feeding one copy slightly
noisier wind data than another, so the five copies don't just memorize the
exact same patterns).

Here's why that's useful: if all five copies agree closely, that's a sign
this is an "easy" case — we can be confident. If the five copies give quite
different answers, that disagreement itself is a signal: this is a hard,
uncertain case, and we should be more careful here. This collection of five
opinions is called an **ensemble**, and the spread between them is our first
raw signal of uncertainty.

### Turning "the models disagree" into an honest safety margin

Here's the part that actually matters for a ship's safety: it's not enough
to say "the models disagree a bit here." We need a *number* — something
like "we are 90% confident the true ice concentration is below X%" — that a
routing algorithm can actually use as a rule.

The naive way to do this (used in the first draft of this design, and caught
as a weakness — see `WEAKNESS_ANALYSIS.md` §8) is to assume the errors form
a bell curve (a **Gaussian** — the familiar symmetric hump shape) and just
add "a bit more than one standard deviation" as a margin. The problem: real
ice-edge errors are *not* symmetric bell curves — they're lopsided, and
concentration can't go below 0% or above 100%, so a symmetric-bell-curve
assumption produces margins that are sometimes too tight and sometimes
nonsensical (predicting more than 100% ice, for example).

What we actually use is called **conformal prediction**. Here's the idea in
plain terms, no formula needed:

1. Take real historical data the model has *never trained on* (this matters
   — testing on data the model already learned from would just tell us how
   good its memory is, not how good its predictions are).
2. For each held-out day, check: was the true ice concentration actually
   below our proposed "upper bound"? Keep score.
3. Adjust the bound until it's actually right the target fraction of the
   time — say, 90% — *as measured*, not assumed.

The result: when the system says "90% confident," it's because on real
data it has never seen, it was actually right about 90% of the time. That's
a measured, honest number, not a statistical guess dressed up as one.

We go one step further and split this check by **regime** — separately for
open water, the messy **marginal ice zone (MIZ)** (the transition band
between open water and solid pack ice, where conditions are most chaotic and
predictions are hardest), and solid pack ice — because a model's confidence
should behave differently in a calm, predictable area versus a churning,
unpredictable one, and one single number for the whole ocean would hide
that.

### Why this actually changes the route, not just the display

The uncertainty margin isn't just a number shown on screen — it's fed
directly into the routing engine (Chapter 3) as an extra layer: "confidently
safe ice %" instead of "average predicted ice %." A cell that looks
borderline-fine on average, but has wide uncertainty, gets treated as riskier
than a cell with the same average but tight, confident uncertainty. Moving
the risk-tolerance slider in the interface literally changes this margin and
visibly moves the route — that's the whole point of doing this work.

### Sources to go deeper

- Ronneberger, Fischer & Brox (2015), *U-Net: Convolutional Networks for
  Biomedical Image Segmentation*, arXiv:1505.04597 — the original U-Net
  paper. Read this once you understand the hourglass shape above; the paper
  will make immediate sense.
- Angelopoulos & Bates (2021), *A Gentle Introduction to Conformal
  Prediction and Distribution-Free Uncertainty Quantification*,
  arXiv:2107.07511 — despite the intimidating title, this is written to be
  approachable, and it's the exact method we use.
- Copernicus Marine Service product docs for
  `GLOBAL_ANALYSISFORECAST_PHY_001_024` at data.marine.copernicus.eu — this
  is the actual forecast we correct.
- NOAA/NSIDC Sea Ice Concentration CDR docs at nsidc.org/data/g02202 — the
  real satellite product we train on.

---

## Chapter 2 — Icebergs: Physics First, a Learned Correction Second

### What we're actually predicting

Given a large iceberg's current position, its size, and the wind and ocean
current at that spot right now, predict where it will be tomorrow, in three
days, and in a week.

### The physics, in plain terms

Picture an iceberg as a huge raft, mostly hidden underwater — for tabular
(flat-topped, table-shaped) Antarctic icebergs, often *around 90% of the
mass sits below the surface*. Two things push on it:

- **Wind drag**, pushing on the small part sticking up above the water.
- **Ocean current drag**, pushing on the enormous part submerged below —
  and because that part is so much bigger, ocean currents often matter more
  than wind for these giant bergs.

There's a third effect: because the Earth is rotating, anything moving
across its surface gets deflected sideways — the same **Coriolis effect**
that makes hurricanes spin. It doesn't push the iceberg forward or backward,
it bends its path to one side.

The **Wagner, Dell & Eisenman (2017)** model adds these forces together
properly — correctly weighted for the iceberg's actual size and how deep it
sits — and gives a direct formula for velocity. It doesn't need to simulate
the motion second-by-second; it solves for the answer directly (mathematicians
call this a **closed-form solution**). That means: no risk of the calculation
going numerically unstable mid-demo, and it needs zero training data — just
real wind, real current, and the iceberg's real measured size.

### Why we don't use the old "2% of wind speed" shortcut

There's a well-known rule of thumb that icebergs drift at roughly 2% of the
wind speed. It's a reasonable approximation for smaller bergs in strong
wind — but it breaks down for the giant tabular icebergs that dominate the
Southern Ocean, because those are dragged mainly by *current*, not wind. A
team that uses the simple rule here is using a shortcut that's specifically
wrong for the exact icebergs this problem is about.

### The learned correction, and why it's *not* a neural network

Physics gets us close, but real icebergs aren't perfect rectangles, and
currents aren't known with perfect precision everywhere — so there's
leftover error. We fit a second, much simpler model to predict that leftover
error, using real tracked-iceberg position data (from the BYU/USNIC
databases — real satellite-tracked iceberg positions going back decades).

This second model is **gradient boosting** — not a neural network. Here's
the idea: build a simple decision tree that makes a rough guess, look at
where it was wrong, then build another small tree whose whole job is to fix
*those specific mistakes*, then another, and another — a chain of trees,
each one correcting the ones before it.

Why not a neural network here, when we used one in Chapter 1? Because
neural networks need a lot of data to learn reliably, and iceberg tracking
data is *sparse* — position updates maybe once a day or once a week, for a
few hundred trackable icebergs total. That's a small, tabular (spreadsheet-
shaped) dataset, and gradient boosting is the right tool for that kind of
data — it's the same logic that led the researchers behind **IDRIFTNET**
(a 2025 paper using a similar physics-plus-learned-correction pattern) to
avoid a pure neural-network approach too.

A nice bonus: gradient boosting can tell you which input mattered most for
each correction (called **feature importance**). We checked this, and it
lines up with real physics — wind matters more for small bergs, current
matters more for large ones — which is a genuine sanity check that the model
learned something real, not a statistical fluke.

### Why the danger zone around a berg only extends 72 hours, not 7 days

Physics-only iceberg predictions get less accurate the further out you
project — small early errors compound over time. If we drew a "stay away"
zone using a full week's worth of accumulated uncertainty, it would be so
large (roughly 100+ km radius, per our own measurements) that it would
blockade huge chunks of open ocean that are almost certainly fine. So we cap
the projection at 72 hours — far enough to matter for a ship actually
executing that leg of the voyage, short enough to still mean something. This
is a real, deliberate honesty tradeoff: a wider zone would look more
"thorough" but would actually be useless.

### Sources to go deeper

- Wagner, Dell & Eisenman (2017), *An Analytical Model of Iceberg Drift*,
  arXiv:1610.06403 — the exact physics model we implement. Reference code:
  tillwagner.me/wde17.
- IDRIFTNET (2025), arXiv:2507.00036 — the paper that validated the
  physics-plus-learned-correction pattern for icebergs.
- BYU/NIC Iceberg Tracking Database, scp.byu.edu/data/iceberg — the real
  dataset our correction model trains on.

---

## Chapter 3 — Getting the Ship There: Meshes, Graphs, and Real Routing

### The problem, stated simply

Given a map of how risky each part of the ocean is (from Chapters 1 and 2),
plus a start point and an end point, find a good path between them —
"good" meaning some balance of fast, fuel-efficient, and safe.

### Turning a map into something a computer can search

First, the map gets chopped into cells — imagine a grid, like a chessboard
laid over the ocean. Our tool (**meshiphi**, from the same team as the
routing engine) uses a *smarter* grid: cells shrink smaller in complicated
areas (like near the ice edge, where conditions change quickly from one spot
to the next) and stay large in open, uneventful ocean. This saves computing
effort without losing important detail — called an **adaptive mesh**.

Each cell becomes a **node**, connected to its neighboring cells, and each
connection has a **cost** — how much time, fuel, or risk it takes to cross
from one cell into the next, based on the ice/iceberg/wave conditions there.

### Dijkstra's algorithm, in plain terms

**Dijkstra's algorithm** is a systematic way of finding the cheapest total
path across this network of connected cells. The intuition: always expand
outward from whichever reachable cell currently has the *cheapest known
total cost so far* — like water finding the path of least resistance,
spreading out fastest where it's easiest. Because it always expands the
cheapest option first, it's mathematically guaranteed to find the actual
best path, not just a decent-looking one — as long as the costs on each
connection are set correctly.

### Why we use PolarRoute instead of building our own

We didn't write a routing algorithm from scratch. **PolarRoute** is real,
existing, open-source software built by the British Antarctic Survey (BAS)
— the same organization that operates real Antarctic research ships. It
already knows how to turn real ship specifications (how fast can *this*
particular ship go through ice of *this* thickness, at *this* wave height)
into proper routing costs — a genuinely hard problem we didn't need to
re-solve.

We checked, hands-on, that it actually works for our case: installed it,
ran it, and timed it (see `ML_ARCHITECTURE.md` §0) — a full route
computation takes about 9 seconds on an ordinary laptop, no GPU needed. That
matters a lot: it means the *entire decision engine* can run on the ship's
bridge with no internet connection at all (see Chapter 5).

### The two real gaps we found in PolarRoute, and how we fixed them

We read PolarRoute's actual source code (not just its documentation) and
found two genuine limitations:

1. **It throws away uncertainty.** Its existing forecast-loading code
   literally deletes the confidence/spread information before routing,
   using only the average prediction. We feed it our "confidently safe ice
   %" number from Chapter 1 instead of the plain average — so it's
   automatically more cautious exactly where our forecast is least certain.
2. **It has no built-in iceberg model.** But it does have a general-purpose
   "avoid this area" mechanism (called `excluded_zones`) originally meant
   for other kinds of hazards. We use that same mechanism to inject our
   iceberg danger zones from Chapter 2 — no need to modify PolarRoute's own
   code at all.

### Why we show several routes, not just one "the best" answer

Fastest, cheapest-fuel, and safest routes usually aren't the same route.
Rather than picking one and hiding that tradeoff, we run the routing engine
several times under different priorities and show the ship's crew a small
set of genuinely different good options — called a **Pareto set** (a
standard idea from optimization: none of the options is strictly worse than
another on every measure at once, so which one is "best" depends on which
the crew cares about most right now). This mirrors how real commercial
ship-routing services like StormGeo actually work — they keep a human
making the final call, because full automation isn't trusted at the edge
cases, and neither should we pretend it is.

### Sources to go deeper

- PolarRoute, github.com/antarctica/PolarRoute — the real tool, MIT
  licensed, read the code once you understand the mesh + Dijkstra idea
  above.
- Fox-Kemper / Coles et al., *Long-Range Route-planning for Autonomous
  Vehicles in the Polar Oceans*, arXiv:2111.00293 — the paper explaining
  PolarRoute's actual method.
- GEBCO gridded bathymetry (seafloor depth data), gebco.net — one of the
  real inputs the routing engine needs to avoid shallow water.

---

## Chapter 4 — Real Data: Satellites, Ocean Models, Weather, and Why None of It Can Be Fake

### The non-negotiable rule

Nothing in this system runs on made-up numbers. Every input — every ice map,
every wind field, every ocean current — traces back to a real satellite, a
real weather model, or a real ocean simulation that a real scientific
organization operates today. `DATASET.md` records exactly which ones, with
the live web addresses and access requirements, hand-verified by actually
fetching real data from each one during this project's research phase.

### The three kinds of data this system actually needs

- **Satellite data**: sea ice concentration (Chapter 1) from passive
  microwave sensors, and iceberg positions (Chapter 2) tracked by a mix of
  radar and infrared imagery.
- **Oceanographic data**: current speed/direction and sea surface
  temperature — mostly from CMEMS's ocean simulation (Chapter 1), which is
  itself constantly corrected against real buoy and satellite measurements.
- **Meteorological data**: wind, air pressure, and wave height — from
  **ERA5** (a huge historical weather record used for training) and **GFS**
  (a live daily weather forecast used for actual operations).

### What these files actually look like

Most of this data arrives as **NetCDF** files — think of it as a labeled
spreadsheet with more than two dimensions: latitude × longitude × time,
where every single cell holds one number (like "38% ice concentration at
this location, on this date"). A normal spreadsheet only has rows and
columns; this kind of data needs a third (and sometimes fourth) dimension,
which is exactly what NetCDF is designed for. The Python tool **xarray**
is what makes working with data shaped like this manageable — it lets you
ask questions like "give me every ice value for this one small box of ocean,
across the last 30 days" without writing complicated indexing code by hand.

### Why every source was verified live, not just found in a search

A data source that turns out to be broken, defunct, or paywalled — discovered
*during* the actual build, not before — is one of the most common ways an
ambitious project quietly runs out of runway. So before any architecture
decision was made, every single required data source was actually fetched
from, live, from inside this project's own environment, and the results
recorded in `DATASET.md`. If a source needed a free account, that's noted;
if a source turned out not to exist at all (like a ready-made "safe shipping
lane" dataset — it doesn't exist anywhere, because computing that *is* this
project's job), that's also stated plainly rather than glossed over.

### Data quality control (QC), and why it matters more than it sounds

Satellites sometimes report **false ice** — a sensor artifact near
coastlines can look like ice where there's actually open water, because land
interferes with the microwave signal the same way ice does. Bad weather can
also *block* the signal entirely for a patch of ocean, leaving a data gap.
If these glitches aren't caught, the system might mistake a sensor error for
a real disagreement between data sources (see Chapter 1's fusion idea) and
route the ship around a hazard that was never actually there. So before any
data gets used, it passes through a **QC pass**: known glitch patterns get
flagged (not silently fixed or hidden — flagged, so downstream steps know to
treat that spot with extra caution).

### Sources to go deeper

- xarray docs, docs.xarray.dev — the actual tool, with a genuinely good
  beginner tutorial.
- NASA Earthdata, urs.earthdata.nasa.gov — where the real satellite sea-ice
  data comes from.
- Copernicus Climate Data Store, cds.climate.copernicus.eu — where ERA5
  weather history comes from.

---

## Chapter 5 — The Backend: One Program, Two Places It Runs

### The core idea, in one sentence

The exact same program runs in two different modes: a **shore mode** (needs
internet and real computing power, does all the heavy lifting) and a
**vessel mode** (needs no internet at all, runs on an ordinary laptop on the
ship's bridge, and does the actual day-to-day route planning).

### Why this split exists at all

India's actual Antarctic resupply ship doesn't have reliable internet for
months at a time — real polar shipping communication (**Iridium**, a
satellite phone network) is slow and expensive, nowhere close to normal
broadband. A system that assumes the ship can just call a server whenever it
wants is assuming infrastructure the ship genuinely doesn't have. So instead:
everything that needs a lot of bandwidth or computing power (gathering
satellite data, training the models) happens ashore, where that's available
— and everything the ship actually needs *to make a decision* runs entirely
on board, offline.

### What FastAPI actually is

**FastAPI** is a way of writing a small web server in Python. It's what lets
the map you see in the browser (Chapter 6) ask the backend questions like
"what's the current route?" or "what's today's ice forecast?" and get an
answer back. It's the same underlying program whether it's running ashore or
on the ship — just switched into a different mode by one setting.

### The "voyage pack" — how data actually gets from shore to ship

Instead of the ship needing a live connection, the shore side bundles
everything the ship needs — the latest ice forecast, iceberg positions,
candidate routes — into one small, compressed file once a day, called a
**voyage pack**. The ship downloads just that one small file whenever it
gets a chance to — could be a slow satellite link, could genuinely be
someone plugging in a USB stick the next time the ship is in port. We
actually measured how small this file can be (see `ARCHITECTURE.md` §1.2):
a full day's worth of route information compresses to well under 1 kilobyte
— small enough to fit even through the slowest, most limited version of the
ship's satellite messaging.

### "Signed and versioned" — why that matters

The pack is cryptographically **signed**, like a wax seal on a letter: the
ship's software can check "this really came from our own shore system, and
nobody tampered with it in transit." It's also **versioned** — the ship
keeps the last several packs, so if a new one ever looks wrong or arrives
corrupted, it can simply fall back to yesterday's instead of trusting broken
data.

### Sources to go deeper

- FastAPI docs, fastapi.tiangolo.com — genuinely one of the more readable
  framework docs out there, worth just reading start to finish once.
- `cryptography` Python library docs, cryptography.io — for how the signing
  actually works (Ed25519, a standard modern signature scheme).

---

## Chapter 6 — The Screen the Captain Actually Looks At

### The real design problem

It's easy to draw a confident-looking line on a map. It's much harder to
honestly show *uncertainty* — "the ice edge is probably here, but could
plausibly be anywhere in this band" — without the interface looking broken
or making the whole tool seem untrustworthy. Getting this right is where all
the honest engineering from Chapters 1–5 either reaches the person actually
making decisions, or gets lost.

### Why we borrow real nautical chart color conventions

Anyone who has actually navigated a ship already knows to read amber and red
as "caution" and "danger" on a real navigation chart. Reusing that exact
color language — instead of inventing a new one — means the interface is
instantly readable to someone with real maritime experience, rather than
something they have to learn from scratch.

### MapLibre and PMTiles, briefly

**MapLibre GL JS** is the library that actually draws the interactive,
pannable, zoomable map in the browser. **PMTiles** is a clever single-file
format for map data that doesn't need its own separate server running to
work — the map data can just be a file sitting on disk, which matters a lot
given the ship's offline reality: once a pack has arrived, the map keeps
working with zero internet, indefinitely.

### The staleness banner

Every screen in the interface permanently shows *how old* the current
information is — not hidden in a tooltip somewhere, but always visible. The
reasoning: a four-day-old ice forecast might still be useful, but only if
the person looking at it knows it's four days old. Hiding that fact would
make the tool *look* more confident while actually being less trustworthy —
exactly the kind of dishonesty this whole project is designed to avoid (see
`DIFFERENTIATION.md` D6).

### Sources to go deeper

- MapLibre GL JS docs, maplibre.org/maplibre-gl-js/docs
- PMTiles spec, github.com/protomaps/PMTiles

---

## How these six chapters fit together

Data (Ch. 4) feeds the ice forecast (Ch. 1) and the iceberg tracker (Ch. 2).
Both feed the routing engine (Ch. 3), which runs inside the backend (Ch. 5),
which the ship reaches with zero internet required. The interface (Ch. 6) is
where a real captain has to trust — or rightly distrust — everything that
happened in the five chapters before it. If any one chapter is weak, the
whole chain is weak at that link. That's why every chapter above has both a
"what we chose" and a "why not the simpler/fancier alternative" — read both
halves, not just the conclusion.
