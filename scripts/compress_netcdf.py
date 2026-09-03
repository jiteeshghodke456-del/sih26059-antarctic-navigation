#!/usr/bin/env python3
"""Shrink a harvested CMEMS forecast file before it goes into git.

Why this exists
---------------
`copernicusmarine subset` writes NetCDF with **no compression at all** --
verified on a real harvest file: `zlib=False, complevel=0, shuffle=False,
contiguous`. Four variables of raw float32 over a 10 x 277 x 961 grid is
42.6 MB per day, every day, committed permanently to git history.

At that rate the archive reaches roughly 4.3 GB by December, which is past the
point where clones become painful and GitHub starts asking questions. The data
itself is not the problem -- the storage format is.

Measured on the 2026-08-31 harvest file:

    as downloaded (no compression)   42.62 MB
    float32 + deflate + shuffle      12.86 MB   3.3x   fully lossless
    int16   + deflate + shuffle       4.99 MB   8.5x   error <= 1.7e-5

We default to int16 packing. What that costs, stated precisely:

    siconc   max error 1.7e-05   (concentration is used at ~1e-2)
    sithick  max error 3.3e-04 m (0.33 mm)
    usi/vsi  max error 5.0e-05 m/s (drift speeds are ~1e-1 m/s)

Every one of those is about three orders of magnitude below the precision any
downstream step actually uses, and the NaN/land mask is preserved exactly. If
you would rather keep bit-exact floats, pass --lossless: you still get 3.3x,
which is enough to keep the archive near 1 GB by December.

This is a *precision* trade, not a data-fabrication one. Nothing is invented,
nothing is filled in, and the land mask is untouched.

    python scripts/compress_netcdf.py FILE [--lossless] [--keep-original]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import xarray as xr

# Full-scale ranges with generous headroom over what the fields actually
# contain, so the quantisation step stays far below useful precision.
# int16 spans +/-32767; we use 30000 to leave room at the ends.
PACK_RANGE = {
    "siconc": 1.0,     # concentration, 0..1
    "sithick": 20.0,   # metres; observed max in a real file was 4.1
    "usi": 3.0,        # m/s; observed |max| was 0.69
    "vsi": 3.0,
}
INT16_SPAN = 30000.0
FILL = -32767


def encoding_for(ds: xr.Dataset, lossless: bool) -> dict:
    enc = {}
    for name, var in ds.data_vars.items():
        if not np.issubdtype(var.dtype, np.floating):
            continue
        spec = {"zlib": True, "complevel": 5, "shuffle": True}
        if not lossless and name in PACK_RANGE:
            spec.update({
                "dtype": "int16",
                "scale_factor": PACK_RANGE[name] / INT16_SPAN,
                "add_offset": 0.0,
                "_FillValue": FILL,
            })
        enc[name] = spec
    return enc


def compress(path: Path, lossless: bool = False,
             keep_original: bool = False) -> tuple[float, float]:
    """Rewrite `path` compressed in place. Returns (before_mb, after_mb)."""
    before = os.path.getsize(path) / 1e6
    tmp = path.with_suffix(".compressing.nc")

    with xr.open_dataset(path) as ds:
        ds.load()                       # detach before overwriting the source
        ds.to_netcdf(tmp, encoding=encoding_for(ds, lossless))

    after = os.path.getsize(tmp) / 1e6
    if after >= before:
        # Already compressed, or compression did not help. Leave it alone
        # rather than churn the file for nothing.
        tmp.unlink(missing_ok=True)
        return before, before

    if keep_original:
        path.rename(path.with_suffix(".orig.nc"))
    tmp.replace(path)
    return before, after


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--lossless", action="store_true",
                    help="keep float32; 3.3x instead of 8.5x")
    ap.add_argument("--keep-original", action="store_true",
                    help="retain the uncompressed file alongside, as .orig.nc")
    args = ap.parse_args()

    if not args.file.exists():
        print(f"no such file: {args.file}", file=sys.stderr)
        return 1

    before, after = compress(args.file, args.lossless, args.keep_original)
    if after == before:
        print(f"{args.file.name}: already compact at {before:.2f} MB, left as is")
    else:
        print(f"{args.file.name}: {before:.2f} MB -> {after:.2f} MB "
              f"({before / after:.1f}x smaller, "
              f"{'lossless' if args.lossless else 'int16 packed'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
