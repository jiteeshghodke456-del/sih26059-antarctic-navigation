"""FastAPI service for the ISIH demo.

    .venv-demo/bin/uvicorn isih.demo.app:app --port 8000

Startup refuses to proceed if any day in the window has no satellite file on
disk, and warms every day into memory before serving — so anything that can
fail, fails before the examiner is in the room, not on slider tick 17.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import data

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    missing = data.preflight()
    if missing:
        raise RuntimeError(
            f"Refusing to start: no NOAA/NSIDC file on disk for {missing}. "
            f"Run isih/download_nsidc.py for those dates first.")
    t0 = time.time()
    for d in data.dates():
        data.day_field(d, True)
        data.day_field(d, False)
    data.route()
    data.cells()
    print(f"[demo] {len(data.dates())} days x 2 QA modes warmed in "
          f"{time.time() - t0:.1f}s — ready", flush=True)
    yield


app = FastAPI(title="SIH26059 — ISIH demo", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/summary")
def summary():
    return data.summary()


@app.get("/api/route")
def route():
    return data.route()


@app.get("/api/cells")
def cells():
    return {"source": data.SOURCE_ROUTE, "cells": data.cells()}


@app.get("/api/day/{d}")
def day(d: str, qa: str = "on"):
    if d not in data.dates():
        raise HTTPException(404, f"{d} is outside the demo window "
                                 f"{data.dates()[0]}..{data.dates()[-1]}")
    if qa not in ("on", "off"):
        raise HTTPException(400, "qa must be 'on' or 'off'")
    return data.day_field(d, qa == "on")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
