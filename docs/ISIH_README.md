# `isih/` — ISIH Prototype (Sept 8 demo)

**Everything in this folder belongs to the internal-SIH prototype demo, not the
December SIH final product.** Kept separate deliberately so the two are never
confused — in the repo, in the checkpoints, or in the numbers we quote to
judges.

## The separation rule

| | ISIH prototype (Sept 8) | SIH final (December) |
|---|---|---|
| Lives in | `isih/` | repo root (`models/`, `api/`, `web/`, …) |
| Model | small, single member, short training window | 5-member ensemble, 1993–2024 |
| Input channels | reduced set (see `config.py`) | full 19 channels (`ML_ARCHITECTURE.md` §1.2) |
| Base field | GLORYS12 reanalysis | real CMEMS forecast archive (Stage B) |
| Calibration | none — prototype reports raw output | stratified conformal (`ML_ARCHITECTURE.md` §1.6) |
| Trained on | free Kaggle GPU | Kaggle / local RTX 5060 |

**The one thing shared: the U-Net architecture** (`models/sic_correction/unet.py`).
Deliberately not duplicated — it is verified once and used by both, so the
prototype genuinely demonstrates the production architecture at smaller scale
rather than being a different thing wearing the same name. Everything else
here is prototype-only.

## What the prototype model actually is

Same *shape* as the production model — a **bias-correction residual U-Net** —
just smaller and fed less:

```
corrected SIC = clip( background SIC + model's predicted correction , 0, 1 )
```

- **Background** (what we correct): GLORYS12 ocean reanalysis sea-ice
  concentration — a real physics model's output.
- **Truth** (what we correct *toward*): NOAA/NSIDC CDR passive-microwave
  observations — what the satellite actually measured.
- The model learns where the physics model disagrees with reality.

This is a real trained model on real data. It is *not* the December model, and
we say so plainly to judges: "this prototype corrects a reanalysis background;
the production version corrects the live operational forecast and adds
calibrated uncertainty."

## Data sources (both verified reachable, 2026-08-31)

| Source | What | Auth | Verified |
|---|---|---|---|
| NOAA/NSIDC CDR `G02202_V6` | truth: observed SIC, 25 km south polar stereographic, **332×316** | **none** | ✅ downloaded a real file |
| CMEMS `cmems_mod_glo_phy_my_0.083deg_P1D-m` | background: GLORYS12 `siconc` | CMEMS account | ✅ catalog confirmed |

Note the NSIDC grid is **332×316**, which independently confirms the dimension
`ML_ARCHITECTURE.md` §1.3 had only assumed — that backlog item is now closed.

NSIDC files also carry `cdr_seaice_conc_qa_flag` and `cdr_seaice_conc_stdev`,
which feed the QC layer (`ML_ARCHITECTURE.md` §4.1) for free.

## Files

- `download_nsidc.py` — fetch observed SIC (no auth needed)
- further scripts land as each increment is verified

## Troubleshooting: Kaggle CLI dependency conflicts

The Kaggle CLI can fail to install with dependency-resolution errors. Pinning
the versions below resolved it (verified on Windows, 2026-08-31):

```
py -m pip install --upgrade pip==25.3
py -m pip install kaggle==2.2.4 kagglesdk==0.1.37 jupytext==1.19.5 \
    markdown-it-py==4.2.0 mdit-py-plugins==0.6.1 python-dotenv==1.2.3 \
    python-slugify==8.0.4 text-unidecode==1.3
py -c "import kaggle, kagglesdk, jupytext, dotenv, slugify; print('ok')"
py -m kaggle --version
```

Only needed for the CLI (uploading notebooks, pulling results). Running the
notebook in the Kaggle web UI needs none of this.

## Running order

1. `python isih/download_nsidc.py` — truth data
2. *(next increment)* GLORYS12 background + regridding to the NSIDC grid
3. *(next increment)* train on Kaggle
