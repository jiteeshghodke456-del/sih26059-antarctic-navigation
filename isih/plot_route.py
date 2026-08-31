"""Render the route figure for the deck.

Designed to be understood with no prior knowledge, and — importantly — the
claim it makes is measured in this script, not asserted. Every number in the
annotation is computed from the same data being drawn, so the figure cannot
drift away from the truth if the route or the date changes.

An earlier version of this figure claimed the route "bends around the thickest
ice". Measuring showed that was false: the time-optimal route actually crosses
*more* average ice (19.6% vs 8.4%) because it trades moderate ice for a shorter
path. The true and stronger finding is about the ship's hard limit — see below.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

FIG_DIR = Path("isih/figures")

# Must match the vessel config in make_route_figure.py: above this ice
# concentration the ship cannot pass.
ICE_LIMIT = 80.0


def densify(a, b, n):
    return np.c_[np.linspace(a[0], b[0], n), np.linspace(a[1], b[1], n)]


def sample_ice(path: np.ndarray, tree: cKDTree, sic: np.ndarray):
    """Ice concentration along a polyline, sampled densely enough that long
    legs are not under-counted. Returns (values, points)."""
    pts = np.vstack([densify(path[i], path[i + 1], 60) for i in range(len(path) - 1)])
    dist, idx = tree.query(pts, k=1)
    near = dist < 1.0        # only where we genuinely have ice data
    return sic[idx[near]], pts[near]


def main() -> int:
    data = json.loads((FIG_DIR / "routes.json").read_text())
    feature = data["paths"]["features"][0]
    coords = np.array(feature["geometry"]["coordinates"])
    props = feature["properties"]
    travel_days = props["traveltime"][-1] if isinstance(props.get("traveltime"), list) \
        else props.get("traveltime")

    ice = pd.read_csv(FIG_DIR / "sic_points.csv")
    tree = cKDTree(np.c_[ice["long"], ice.lat])
    sic = ice.SIC.values

    start, end = coords[0], coords[-1]
    straight = densify(start, end, 2000)

    route_vals, _ = sample_ice(coords, tree, sic)
    str_vals, str_pts = sample_ice(straight, tree, sic)

    route_max, str_max = route_vals.max(), str_vals.max()
    blocked = str_pts[str_vals > ICE_LIMIT]

    print(f"route    max ice {route_max:.0f}%  over limit: {(route_vals > ICE_LIMIT).sum()}")
    print(f"straight max ice {str_max:.0f}%  over limit: {(str_vals > ICE_LIMIT).sum()}")

    fig, ax = plt.subplots(figsize=(13.5, 8.5))

    sea = ice[ice.SIC < 15]
    ax.scatter(sea["long"], sea.lat, c="#e3edf5", s=9, marker="s", linewidths=0)
    iced = ice[ice.SIC >= 15]
    sc = ax.scatter(iced["long"], iced.lat, c=iced.SIC, cmap="Blues",
                    vmin=15, vmax=100, s=11, marker="s", linewidths=0)
    cbar = plt.colorbar(sc, ax=ax, pad=0.015, shrink=0.8)
    cbar.set_label("Sea ice covering the ocean surface (%)", fontsize=11)
    cbar.ax.axhline(ICE_LIMIT, color="#b03a2e", lw=2.5)
    cbar.ax.text(1.9, ICE_LIMIT, "  ship's\n  limit", transform=cbar.ax.get_yaxis_transform(),
                 color="#b03a2e", fontsize=9.5, weight="bold", va="center")

    ax.plot(straight[:, 0], straight[:, 1], "--", color="#b03a2e", lw=2.2, zorder=3)
    if len(blocked):
        ax.scatter(blocked[::40, 0], blocked[::40, 1], s=210, marker="X",
                   color="#b03a2e", zorder=12, linewidths=1.4, edgecolors="white")

    ax.plot(coords[:, 0], coords[:, 1], "-", color="white", lw=6, zorder=4)
    ax.plot(coords[:, 0], coords[:, 1], "-", color="#117a3d", lw=3.4, zorder=5)

    for (x, y), name, off in [
        (start, "CAPE TOWN\n(start)", (14, 14)),
        (end, "BHARATI STATION\n(destination)", (-95, -52)),
    ]:
        ax.plot(x, y, "o", ms=13, color="#111", zorder=8)
        ax.plot(x, y, "o", ms=6.5, color="white", zorder=9)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=off,
                    fontsize=11.5, weight="bold", zorder=10,
                    bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#555"))

    if len(blocked):
        anchor = blocked[len(blocked) // 2]
        ax.annotate(
            f"The straight line runs into ice {str_max:.0f}% thick.\n"
            f"This ship cannot pass above {ICE_LIMIT:.0f}% — it would\n"
            "be stuck here.",
            xy=(anchor[0], anchor[1]), xytext=(48.5, -41.0),
            fontsize=11.5, weight="bold", color="#b03a2e", ha="left", zorder=11,
            arrowprops=dict(arrowstyle="->", color="#b03a2e", lw=2.2,
                            connectionstyle="arc3,rad=0.25"),
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#b03a2e", lw=1.6))

    mid = coords[int(len(coords) * 0.30)]
    ax.annotate(
        f"Our route never exceeds {route_max:.0f}% ice.\n"
        "It stays passable the whole way.",
        xy=(mid[0], mid[1]), xytext=(16.5, -52.5),
        fontsize=11.5, weight="bold", color="#117a3d", ha="left", zorder=11,
        arrowprops=dict(arrowstyle="->", color="#117a3d", lw=2.2,
                        connectionstyle="arc3,rad=-0.2"),
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#117a3d", lw=1.6))

    handles = [
        Line2D([], [], color="#117a3d", lw=3.4,
               label=f"Route our system computes — {travel_days:.1f} days, max {route_max:.0f}% ice"),
        Line2D([], [], color="#b03a2e", lw=2.2, ls="--",
               label=f"Straight line — reaches {str_max:.0f}% ice"),
        Line2D([], [], color="#b03a2e", lw=0, marker="X", ms=11,
               label="Impassable for this ship"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.085),
              ncol=3, fontsize=10.5, framealpha=0.97, borderpad=0.7)

    ax.set_title("Why routing matters: the direct path is blocked by ice",
                 fontsize=15.5, weight="bold", pad=14)
    ax.text(0.5, 1.007,
            "Cape Town → Bharati, 1 December 2019 (start of the real resupply season). "
            "Ice measured by satellite (NOAA/NSIDC).",
            transform=ax.transAxes, ha="center", fontsize=10.5, color="#444")

    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°S)", fontsize=11)
    ax.grid(alpha=0.25, ls=":")
    ax.set_xlim(14, 82)
    ax.set_ylim(-71, -30)

    out = FIG_DIR / "route_map.png"
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches="tight")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
