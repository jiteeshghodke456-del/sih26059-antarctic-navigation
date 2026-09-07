"""Tests for the protected-areas layer, against the real ATS register.

These assert facts, not plumbing. If the Treaty Secretariat republishes the
shapefile with a changed boundary, these tests are supposed to fail — that is
the point. A protected-area boundary moving silently under a cached route is
the failure mode this file exists to catch.

Requires the shapefile: `python isih/download_protected_areas.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

from protected_areas import (  # noqa: E402
    CORRIDOR,
    build_extract,
    load_areas,
    station_context,
)

pytest.importorskip("shapefile", reason="pyshp needed to read the ATS register")

if not any((ISIH / "data" / "protected_areas").glob("*.shp")):
    pytest.skip(
        "ATS shapefile absent — run isih/download_protected_areas.py",
        allow_module_level=True,
    )


@pytest.fixture(scope="module")
def corridor_areas():
    return load_areas(None, CORRIDOR)


@pytest.fixture(scope="module")
def all_areas():
    return load_areas(None, None)


def test_register_is_the_full_published_set(all_areas):
    """148 polygons: 142 ASPA + 6 ASMA, over 77 unique ASPAs and 6 ASMAs."""
    assert len(all_areas) == 148
    assert sum(1 for a in all_areas if a.kind == "ASPA") == 142
    assert sum(1 for a in all_areas if a.kind == "ASMA") == 6
    assert len({a.number for a in all_areas if a.kind == "ASPA"}) == 77
    assert len({a.number for a in all_areas if a.kind == "ASMA"}) == 6


def test_bharati_is_inside_asma_6(corridor_areas):
    """The load-bearing fact: India's station sits inside a managed area.

    A system that modelled ASMAs as no-go would refuse to route to Bharati.
    """
    ctx = station_context(corridor_areas)["Bharati"]
    inside = {(a["kind"], a["number"]) for a in ctx["inside"]}
    assert ("ASMA", "6") in inside

    asma6 = next(a for a in ctx["inside"] if a["number"] == "6")
    assert asma6["instrument"] == "M 2 (2007)"
    assert "India" in asma6["proponent"]


def test_aspa_and_asma_are_not_the_same_gate(corridor_areas):
    """Annex V Art. 3 vs Art. 4 — the distinction §48A.17 demands be kept."""
    aspa = next(a for a in corridor_areas if a.kind == "ASPA")
    asma = next(a for a in corridor_areas if a.kind == "ASMA")
    assert aspa.entry_regime == "permit_required"
    assert asma.entry_regime == "management_plan"
    assert aspa.entry_regime != asma.entry_regime


def test_no_corridor_area_restricts_transit(corridor_areas):
    """Zero marine areas here, so none binds the ship's track.

    If this ever fails, the corridor has gained a marine protected area and
    the routing mesh genuinely does need to know about it.
    """
    assert corridor_areas, "corridor extract is empty"
    assert not any(a.marine for a in corridor_areas)
    for a in corridor_areas:
        assert a.constraint_for_vessel()["applies_to"] == "shore_operations"


def test_marine_areas_would_bind_transit(all_areas):
    """The 8 marine areas elsewhere in Antarctica take the other branch.

    Guards against the classifier being accidentally correct here only
    because every corridor area happens to be terrestrial.
    """
    marine = [a for a in all_areas if a.marine]
    assert len(marine) == 8
    for a in marine:
        assert a.constraint_for_vessel()["applies_to"] == "transit_and_operations"


def test_stornes_is_the_nearest_area_to_bharati(corridor_areas):
    """ASPA 174 is ~2 km away — permit-gated, and closer than most think."""
    nearby = station_context(corridor_areas)["Bharati"]["nearby"]
    assert nearby, "expected neighbouring areas near Bharati"
    assert nearby[0]["number"] == "174"
    assert nearby[0]["distance_km"] < 5.0
    assert nearby[0]["entry_regime"] == "permit_required"


def test_maitri_is_outside_every_area_but_near_indias_own_aspa(corridor_areas):
    """Maitri is in no area; ASPA 163 Dakshin Gangotri — India's — is ~5 km."""
    ctx = station_context(corridor_areas)["Maitri"]
    assert ctx["inside"] == []
    nearest = ctx["nearby"][0]
    assert nearest["number"] == "163"
    assert nearest["proponent"] == "India"
    assert nearest["distance_km"] < 10.0


def test_extract_carries_its_own_provenance():
    """Every environmental object must state where it came from (§15)."""
    extract = build_extract()
    for key in ("source", "source_url", "legal_basis", "crs_source"):
        assert extract[key], f"{key} missing from the extract"
    assert "Annex V" in extract["legal_basis"]
    assert extract["counts"]["polygons"] == 33
    assert extract["counts"]["marine"] == 0
