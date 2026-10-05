#!/usr/bin/env python3
"""Emit the decision-gate architecture as an importable .drawio file.

Stage 02 requires a draw.io-ready architecture for the decision layer. The
existing DECISION_FLOW diagram describes the operational flow; this one
describes the *mechanism* — which evidence feeds which gate, how nine gate
states collapse into one route-health state, and where a human sits.

The gate names, their questions and their blockers are IMPORTED from
isih/decision.py and isih/gates.py rather than retyped. A diagram that
restates the code in prose drifts from it within a week; this one cannot name
a gate the code does not have, because the generator would fail first.

Colour follows the UI, and for the same reason: UNKNOWN is grey, never red.
An unevaluable gate is an absence of measurement, not a hazard.

Run:  python scripts/gen_decision_gates_drawio.py
"""
from pathlib import Path
from xml.sax.saxutils import escape
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "isih"))

from decision import GATES, GATE_QUESTION      # noqa: E402
from gates import BLOCKED_ON                   # noqa: E402

OUT = str(ROOT / "docs" / "DECISION_GATES.drawio")

BASE = "rounded=0;whiteSpace=wrap;html=1;fontSize=11;verticalAlign=middle;"
S = {
    "src":     BASE + "fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#13385C;",
    "gate_ok": BASE + "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#254A20;",
    "gate_mar": BASE + "fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#5A4708;",
    # Grey and dashed: absence of evidence, deliberately not a hazard colour.
    "gate_unk": BASE + "fillColor=#f0f2f4;strokeColor=#9aa7b0;fontColor=#5C666E;"
                       "dashed=1;dashPattern=4 3;",
    "health":  "rounded=1;arcSize=30;whiteSpace=wrap;html=1;fontSize=13;fontStyle=1;"
               "fillColor=#f8cecc;strokeColor=#b85450;fontColor=#5C1F1D;"
               "verticalAlign=middle;",
    "human":   "rhombus;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;"
               "fillColor=#f5d9e8;strokeColor=#b8559a;fontColor=#5C2049;",
    "store":   "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;whiteSpace=wrap;"
               "html=1;fontSize=11;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#3B2A4A;",
    "note":    BASE + "fillColor=#ffffff;strokeColor=#b0bcc4;fontColor=#46545F;fontSize=10;"
                      "align=left;verticalAlign=top;",
    "title":   "text;html=1;strokeColor=none;fillColor=none;align=left;"
               "verticalAlign=middle;fontSize=13;fontStyle=1;fontColor=#0F1720;",
}

# Which gates we can actually evaluate today. Mirrors isih/gates.py: anything
# in BLOCKED_ON returns UNKNOWN, everything else is evaluated from real data.
STATE_NOW = {g: ("unk" if g in BLOCKED_ON else "ok") for g in GATES}
STATE_NOW["ice"] = "mar"          # 79% against an assumed 80% limit
_STYLE = {"ok": "gate_ok", "mar": "gate_mar", "unk": "gate_unk"}
_BADGE = {"ok": "PASS", "mar": "MARGINAL", "unk": "UNKNOWN"}

SOURCES = [
    ("s_ice",  "NOAA/NSIDC CDR<br>G02202 v6 · 25 km", ["ice"]),
    ("s_mesh", "meshiphi mesh<br>SIC · thickness · density", ["chart"]),
    ("s_win",  "destination window<br>vessel-performance mesh", ["logistics"]),
    ("s_alt",  "alternatives.json<br>PolarRoute corridors", ["contingency"]),
    ("s_ves",  "vessel config<br>isih/ice_meshes.py", ["capability"]),
    ("s_none", "NO SOURCE HELD<br>weather · traffic · comms · live sensors",
     ["weather", "traffic", "communications", "execution"]),
]

NODES, EDGES = [], []

NODES.append(("t1", "title", "Evidence", 40, 30, 220, 24))
NODES.append(("t2", "title", "Nine decision gates (§12)", 330, 30, 300, 24))
NODES.append(("t3", "title", "Derived state (§48A.13)", 700, 30, 260, 24))

y = 70
for cid, label, _ in SOURCES:
    h = 74 if cid == "s_none" else 54
    NODES.append((cid, "src", label, 40, y, 240, h))
    y += h + 16

for i, g in enumerate(GATES):
    st = STATE_NOW[g]
    label = f"<b>{g}</b> — {_BADGE[st]}<br><font style='font-size:9px'>{GATE_QUESTION[g]}</font>"
    NODES.append((f"g_{g}", _STYLE[st], label, 330, 70 + i * 62, 300, 50))

for cid, _, gs in SOURCES:
    for g in gs:
        dashed = ";dashed=1;dashPattern=4 3" if cid == "s_none" else ""
        EDGES.append((cid, f"g_{g}", "", dashed))

NODES.append(("health", "health",
              "ROUTE HEALTH<br>worst gate state wins<br>"
              "<font style='font-size:10px'>VALID · DEGRADED · CRITICAL · INVALID</font>",
              700, 250, 240, 90))
for g in GATES:
    EDGES.append((f"g_{g}", "health", "", ""))

NODES.append(("digest", "note",
              "<b>gate_digest()</b><br>Identical evidence yields an identical digest, "
              "so re-evaluating raises no transition. This is what separates "
              "“an assumption changed” from “new data arrived”.",
              700, 370, 240, 96))
EDGES.append(("health", "digest", "", ";dashed=1;dashPattern=3 3"))

NODES.append(("master", "human", "Master<br>approves?", 720, 500, 200, 90))
EDGES.append(("health", "master", "", ""))

NODES.append(("log", "store",
              "Decision log<br>versions · supersedes<br>who · when · why",
              700, 630, 240, 80))
EDGES.append(("master", "log", "named approval", ""))

NODES.append(("diverge", "note",
              "<b>Divergence</b><br>If the digest moves after approval, the master is told "
              "WHICH gate flipped — e.g. “logistics: PASS to FAIL”. "
              "An approved plan is never silently replaced (§4).",
              700, 730, 240, 104))
EDGES.append(("log", "diverge", "", ";dashed=1;dashPattern=3 3"))

NODES.append(("key", "note",
              "<b>Why six gates are grey</b><br>"
              "A gate we cannot evaluate is NOT a pass — it caps health at DEGRADED. "
              "Reporting VALID while blind to the chart, the weather and the traffic "
              "picture is a false negative, and §48A.12 makes that the expensive error "
              "here. Grey is absence of measurement, not a hazard: colouring it red "
              "would claim we looked.<br><br>"
              "Consequence: this prototype cannot certify any route as VALID, and says so.",
              40, 640, 560, 150))


def cell(cid, style, label, x, y, w, h):
    return (f'        <mxCell id="{cid}" value="{escape(label, {chr(34): "&quot;"})}" '
            f'style="{escape(style, {chr(34): "&quot;"})}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>\n')


def edge(eid, src, dst, label, style):
    return (f'        <mxCell id="{eid}" value="{escape(label)}" '
            f'style="{escape(style, {chr(34): "&quot;"})}" edge="1" parent="1" '
            f'source="{src}" target="{dst}">\n'
            f'          <mxGeometry relative="1" as="geometry" />\n'
            f'        </mxCell>\n')


E = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#7d8a93;"
     "endArrow=block;endFill=1;")

parts = [
    '<mxfile host="app.diagrams.net" type="device">\n',
    '  <diagram name="Decision Gates" id="decisiongates">\n',
    '    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="1654" '
    'math="0" shadow="0">\n',
    '      <root>\n',
    '        <mxCell id="0" />\n',
    '        <mxCell id="1" parent="0" />\n',
]

ids = set()
for cid, skey, label, x, y_, w, h in NODES:
    assert cid not in ids, f"duplicate node id {cid}"
    ids.add(cid)
    parts.append(cell(cid, S[skey], label, x, y_, w, h))

for i, (src, dst, label, extra) in enumerate(EDGES, 1):
    assert src in ids, f"edge {i}: unknown source {src}"
    assert dst in ids, f"edge {i}: unknown target {dst}"
    parts.append(edge(f"e{i}", src, dst, label, E + extra))

parts += ['      </root>\n', '    </mxGraphModel>\n', '  </diagram>\n', '</mxfile>\n']

xml = "".join(parts)
Path(OUT).write_text(xml, encoding="utf-8")

evaluable = sum(1 for g in GATES if STATE_NOW[g] != "unk")
print(f"wrote {OUT}")
print(f"  {len(NODES)} shapes, {len(EDGES)} connectors, {len(xml)} bytes")
print(f"  {evaluable} of {len(GATES)} gates evaluable — imported from isih/gates.py")
