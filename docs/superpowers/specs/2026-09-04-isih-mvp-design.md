# ISIH MVP — design (4 September 2026)

Approved in chat on 4 Sep: "make something nice and real enough for a small
MVP, not ambitious, must not fail in front of judges, three hours."

## What it is

A local web app an examiner can click, built **only** from real files already
on disk. It makes three already-measured findings interactive:

1. **The route on the ice.** The real PolarRoute path (Cape Town → Bharati,
   1 Dec 2019, `isih/figures/routes.json`) drawn over the real NOAA/NSIDC
   satellite ice field for that day.
2. **The destination window.** A slider over 1–31 December 2019. The ice
   field updates from the real daily files; Bharati's status flips open/closed
   from `isih/figures/destination_window.json` — the measured **23/31 days
   closed** while the approach 100 km north is open **31/31**.
3. **The data-quality finding.** A "raw satellite / quality-checked" toggle.
   Raw shows the CDR's land-spillover cells as 0.0 % (looks like open water);
   quality-checked shows them as *unknown*. At Bharati on 1 Dec 2019 that is
   0.0 % versus 30.7 %.

Every panel carries its source and date. Nothing is computed that was not
already computed and published in `docs/ISIH_RESULTS.md`; the app reads those
outputs, so it cannot contradict them.

## What it is not

- No live re-routing (needs a Python 3.11 env + PolarRoute; iteration 2).
- No model inference: the trained checkpoint is on Kaggle, not on disk.
  The measured skill numbers are shown as text with their caveats, nothing
  more, until the checkpoint is fetched (iteration 3).
- No fuel figure, no voyage-duration claim (`ISIH_RESULTS.md` §6 forbids both).

## Shape

```
isih/demo/
  data.py          pure loaders over isih/figures/*.json and isih/data/nsidc_sic/*.nc
  app.py           FastAPI: /, /api/summary, /api/route, /api/cells, /api/day/{date}
  static/          index.html, app.js, style.css — canvas ice raster + SVG vectors
  test_data.py     pytest against the real files (no fixtures, no synthetic data)
  requirements.txt pinned
```

**Why no Leaflet / tiles / CDN.** Basemap tiles need internet; the pitch is
"works with no internet". A canvas + SVG lat/lon projection has zero external
dependencies and cannot fail from a missing network. It is also the same view
as the figure the team has already been showing.

**Why FastAPI stays.** An examiner can open `/api/day/2019-12-10` and see the
JSON. That is the difference between a system and an HTML file, and it is the
December stack.

## Data flow

```
NSIDC .nc (real, on disk) ──load_sic(apply_qa)──▶ day_field(date, qa)  ──▶ /api/day
destination_window.json  ───────────────────────▶ window()             ──▶ /api/summary
routes.json (paths, cellboxes) ─────────────────▶ route(), cells()     ──▶ /api/route, /api/cells
```

Station open/closed status comes from `destination_window.json` (mesh-derived,
as published), **never** recomputed from the raw raster — recomputing would
risk a different number on screen than in the results document.

## Failure behaviour

- A missing daily file is caught **at startup**: the app refuses to start and
  names the date. A slider that dies on day 17 in front of a judge is the one
  thing this must never do.
- Any other read error returns a plain HTTP 500 with the file name, not a
  blank map.

## Verification

- `pytest isih/demo` against the real files: the published numbers (23/31,
  0/31, 8.58 days, 0.0 vs 30.7) must fall out of the loaders unchanged.
- Server started, every endpoint fetched, JSON shape and values checked.
- Page loaded headlessly (node, no browser here); real-browser check is the
  user opening it on their laptop.

## Runs on the laptop

```
uv venv .venv-demo --python 3.12
uv pip install --python .venv-demo/bin/python -r isih/demo/requirements.txt
.venv-demo/bin/uvicorn isih.demo.app:app --port 8000
```
