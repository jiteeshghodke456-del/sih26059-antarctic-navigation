"""POLARIS Risk Index, computed honestly — as a band, never as a number.

This project deliberately does not publish a POLARIS RIO for MV Vasiliy
Golovnin, and that refusal is a finding rather than a gap. Her pre-1999 Russian
Register notation has no row in Table 1.3, no entry in any regulator's
equivalence schedule we could find, and the Polar Code makes equivalency a
per-ship, owner-initiated, flag-approved assessment with no lookup table BY
DESIGN. On a regime plausible for the Bharati approach the candidate rows span
**+19 (normal operation) to −21 (special consideration)** — so picking one row
is picking an answer, not computing it.

What this module does instead is compute the whole band across the plausible
rows and report where that band CROSSES A TIER BOUNDARY. Where it does not
cross, the class question does not matter and the officer can ignore it. Where
it does, the width of the band is the length of track that a Polar Ship
Certificate would settle. That is a stronger thing to show than a number.

The master prompt's own requirement (from the POLARIS section lost in the
compression and since reinstated) is the specification followed here: "display
its inputs, result, applicability, source, timestamp and operational
interpretation rather than presenting an unexplained generic risk score."

Two limitations are structural and are surfaced, not hidden:

*   RIO is indexed by WMO **stage of development**. This system has
    **concentration**. A stage must therefore be DECLARED by the officer; there
    is deliberately no default, because a default would be an invented
    observation. Until one is declared this module returns nothing.
*   Reducing the eleven-column table to one declared stage is the published
    single-stage form, and it is **not the IMO RIO**. Every response says so.

Table 1.4 (decayed ice) is not used: §1.1.3 restricts it to cases where decay is
confirmed by observation, which a forecast cannot do.
"""

from __future__ import annotations

# MSC.1/Circ.1519 Table 1.3, standard (non-decayed), verbatim.
STAGES = (
    "Ice-free", "New", "Grey", "Grey-White", "Thin FY 1st", "Thin FY 2nd",
    "Med FY <1 m", "Med FY", "Thick FY", "Second Year",
    "Light MY <2.5 m", "Heavy MY",
)

CLASSES = ("PC1", "PC2", "PC3", "PC4", "PC5", "PC6", "PC7",
           "IA Super", "IA", "IB", "IC", "Not ice strengthened")

_RIV_ROWS = {
    "PC1":      (3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1),
    "PC2":      (3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 0),
    "PC3":      (3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 0, -1),
    "PC4":      (3, 3, 3, 3, 2, 2, 2, 2, 1, 0, -1, -2),
    "PC5":      (3, 3, 3, 3, 2, 2, 1, 1, 0, -1, -2, -2),
    "PC6":      (3, 2, 2, 2, 2, 1, 1, 0, -1, -2, -3, -3),
    "PC7":      (3, 2, 2, 2, 1, 1, 0, -1, -2, -3, -3, -3),
    "IA Super": (3, 2, 2, 2, 2, 1, 0, -1, -2, -3, -4, -4),
    "IA":       (3, 2, 2, 2, 1, 0, -1, -2, -3, -4, -5, -5),
    "IB":       (3, 2, 2, 1, 0, -1, -2, -3, -4, -5, -6, -6),
    "IC":       (3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8),
    "Not ice strengthened": (3, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8, -8),
}

RIV = {cls: dict(zip(STAGES, row)) for cls, row in _RIV_ROWS.items()}

# The candidate rows this vessel might plausibly be assigned. Deliberately wide:
# narrowing it is the certificate's job, not ours.
DEFAULT_BAND = ("PC4", "IA")

NORMAL, ELEVATED, SPECIAL = "NORMAL", "ELEVATED", "SPECIAL"


def tier(rio: int, cls: str) -> str:
    """Table 1.1, whose two columns differ and whose bounds are half-open.

    Polar Classes have a middle band; a ship on a Finnish-Swedish equivalent or
    with no ice class does not — for those, every negative RIO is already
    'operation subject to special consideration'. Collapsing the two columns
    into one ladder is the commonest way to misread this table."""
    if rio >= 0:
        return NORMAL
    if cls.startswith("PC"):
        return ELEVATED if rio >= -10 else SPECIAL
    return SPECIAL


def speed_limit_kn(cls: str) -> int | None:
    """Table 1.2 speed limitation where operation is not normal."""
    if cls in ("PC3", "PC4", "PC5"):
        return 5
    if cls in ("PC6", "PC7", "IA Super", "IA", "IB", "IC",
               "Not ice strengthened"):
        return 3
    return None


def rio_exact(partials: dict[str, float], cls: str) -> int:
    """The real thing: RIO = sum(Ci x RIVi) over stages, concentrations in
    tenths. Used where an ice chart gives partial concentrations by stage."""
    return int(round(sum(c * RIV[cls][s] for s, c in partials.items())))


def rio_single_stage(sic: float, stage: str, cls: str) -> int:
    """The reduced form used on the chart: all ice taken as one declared stage,
    the rest open water.

        RIO = C x RIV[cls][stage] + (10 - C) x 3

    **This is not the IMO RIO.** It is the published single-stage reduction, and
    every caller is required to label it as such."""
    if stage not in RIV[cls]:
        raise ValueError(f"unknown stage {stage!r}")
    c = round(max(0.0, min(1.0, float(sic))) * 10)
    return int(c * RIV[cls][stage] + (10 - c) * RIV[cls]["Ice-free"])


def band(sic: float, stage: str, cls_lo: str = DEFAULT_BAND[1],
         cls_hi: str = DEFAULT_BAND[0]) -> dict:
    """The RIO band across the candidate rows, and whether it crosses a tier.

    `state` is the whole point:
      stable-normal     the class question does not matter here
      flips             the rows disagree about the tier - this is where a
                        certificate would change the answer
      stable-nonnormal  every candidate row says caution, whatever the class
    """
    lo_i, hi_i = CLASSES.index(cls_hi), CLASSES.index(cls_lo)
    rows = CLASSES[lo_i:hi_i + 1] if lo_i <= hi_i else CLASSES[hi_i:lo_i + 1]
    vals = {c: rio_single_stage(sic, stage, c) for c in rows}
    tiers = {c: tier(v, c) for c, v in vals.items()}
    uniq = set(tiers.values())
    if uniq == {NORMAL}:
        state = "stable-normal"
    elif len(uniq) == 1:
        state = "stable-nonnormal"
    else:
        state = "flips"
    speeds = [speed_limit_kn(c) for c, tr in tiers.items() if tr != NORMAL]
    speeds = [s for s in speeds if s]
    return {
        "rio_lo": min(vals.values()), "rio_hi": max(vals.values()),
        "tier_lo": tiers[min(vals, key=lambda c: vals[c])],
        "tier_hi": tiers[max(vals, key=lambda c: vals[c])],
        "state": state, "rows": rows,
        "speed_kn": [min(speeds), max(speeds)] if speeds else None,
    }


def along(legs: list[dict], stage: str, cls_lo: str = DEFAULT_BAND[1],
          cls_hi: str = DEFAULT_BAND[0]) -> dict:
    """Band per leg, plus where on the track the class question actually bites."""
    out = []
    for i, leg in enumerate(legs):
        b = band(float(leg.get("sic", 0.0)), stage, cls_lo, cls_hi)
        out.append({"i": i, "hours": leg.get("hours"),
                    "lat": leg.get("lat"), "lon": leg.get("lon"),
                    "sic": leg.get("sic"), **b})
    stable = sum(1 for r in out if r["state"] == "stable-normal")
    worst = min(out, key=lambda r: r["rio_lo"]) if out else None
    return {
        "table": "MSC.1/Circ.1519 Table 1.3",
        "issued": "2016-06-06",
        "form": "single-stage reduction — not the IMO RIO",
        "stage": stage,
        "classes": [cls_hi, cls_lo],
        "class_is_assumed": True,
        "legs": out,
        "stable_frac": round(stable / len(out), 3) if out else None,
        "worst": worst,
        "not_scored": ["compression", "ridging", "glacial ice"],
        "validation": "Antarctic: none published; IMO review overdue",
    }
