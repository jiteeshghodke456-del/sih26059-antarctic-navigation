#!/usr/bin/env python3
"""Emit the corrected navigation decision flow as an importable .drawio file.

Written as a generator rather than hand-authored XML so the layout stays on a
grid: every box in a band shares a width, and edge endpoints are derived, not
eyeballed. Re-run it after editing NODES/EDGES to regenerate.
"""
from pathlib import Path
from xml.sax.saxutils import escape

# Derived from this file's location — see the note in gen_v1_drawio.py.
OUT = str(Path(__file__).resolve().parents[1] / "docs" / "DECISION_FLOW.drawio")

# draw.io style vocabulary, kept in the colour family of the original diagram
BASE = "rounded=0;whiteSpace=wrap;html=1;fontSize=12;verticalAlign=middle;"
S = {
    "proc":  BASE + "fillColor=#ffe6cc;strokeColor=#d79b00;fontColor=#5A3B08;",
    "dec":   "rhombus;whiteSpace=wrap;html=1;fontSize=11;fillColor=#f5d9e8;"
             "strokeColor=#b8559a;fontColor=#5C2049;",
    "note":  BASE + "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#254A20;fontSize=10;",
    "term":  "rounded=1;arcSize=40;whiteSpace=wrap;html=1;fontSize=13;fontStyle=1;"
             "fillColor=#f8cecc;strokeColor=#b85450;fontColor=#5C1F1D;",
    "new":   BASE + "fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#13385C;",
    "conn":  "ellipse;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;"
             "fillColor=#ffffff;strokeColor=#333333;",
}
DASH = "dashed=1;dashPattern=3 3;"

# id, style key, label (HTML, <br> for line breaks), x, y, w, h, extra style
NODES = [
    ("start",  "term", "Start", 490, 30, 140, 40, ""),
    ("marks",  "proc", "Captain Marks Route<br>in the Application", 400, 92, 320, 56, ""),
    ("nlogin", "note", "Captain Logs in application", 745, 100, 196, 40, ""),
    ("aIn",    "conn", "A", 335, 103, 34, 34, ""),
    ("backend", "proc", "Route is sent to the<br>applications backend", 400, 176, 320, 56, ""),
    ("nnav",   "note", "Navigation Decision<br>Processing start", 745, 184, 196, 40, ""),
    ("nlocal", "new",
     "<b>backend is LOCAL</b><br><font style='font-size:10px'>on the bridge laptop &#8212; "
     "no outbound network at 70&#176;S</font>", 120, 172, 256, 64, ""),

    ("chk", "dec",
     "AI model checks<br>yesterdays ice movement<br>forecast correctness"
     "<br><font style='font-size:9px;color:#C4500E'>NOT BUILT YET</font>",
     400, 260, 320, 114, DASH),
    ("keep", "proc", "Keep default Confidence<br>in route suggestion", 100, 289, 264, 56, ""),
    ("lower", "proc", "Lower Confidence and increase<br>number of safe routes", 756, 289, 274, 56, ""),

    # --- parallel band -------------------------------------------------
    ("band", "proc",
     "<b>READ THE VOYAGE PACK &#8212; three independent pulls, in parallel</b>",
     22, 452, 1076, 322,
     "fillColor=none;strokeColor=#B0B8C4;dashed=1;verticalAlign=top;align=left;"
     "spacingLeft=10;spacingTop=4;fontSize=11;fontColor=#7C8698;"),

    ("readIce", "proc", "Read Latest ice<br>concentration map", 30, 470, 330, 50, ""),
    ("nNsidc", "note", "Taken by NSIDC satellite with SSMIS sensor", 46, 524, 298, 32, ""),
    ("clean", "proc",
     "Clean unreliable data/noise<br>in satellite image"
     "<br><font style='font-size:9px'>isih/ice_quality.py &#183; the land-spillover filter "
     "writes 0.0 = open water</font>", 30, 578, 330, 76, ""),
    ("weather", "proc",
     "Analyze weather<br>forecast ahead"
     "<br><font style='font-size:9px'>ERA5 / GFS wind + waves &#8212; MOVED: an input, "
     "not a review</font>", 30, 676, 330, 74, ""),

    ("fetchFc", "proc", "Fetch weather model's<br>Sea-ice forecast", 395, 470, 330, 50, ""),
    ("nCmems", "note", "CMEMS Sea-ice forecast", 411, 524, 298, 32, ""),
    ("unet", "proc",
     "AI model corrects<br>mistakes in the forecast"
     "<br><font style='font-size:9px'>residual U-Net &#183; models/sic_correction/unet.py"
     "<br>corrected = clip(base + &#916;, 0, 1) &#183; 1 of 5 trained</font>",
     395, 578, 330, 76, ""),
    ("conformal", "new",
     "Add calibrated safety margin"
     "<br><font style='font-size:9px'>stratified conformal q&#770;(lead, regime)"
     "<br>&#8594; SIC_upper, the number the router really uses</font>",
     395, 676, 330, 74, DASH),

    ("fetchBerg", "proc", "Fetch current iceberg<br>location near the course", 760, 470, 330, 50, ""),
    ("nUsnic", "note", "USNIC Current iceberg positions", 776, 524, 298, 32, ""),
    ("drift", "proc",
     "Predict Iceberg trajectory"
     "<br><font style='font-size:9px'>Wagner closed form &#183; models/iceberg/drift.py"
     "<br><b>PHYSICS, not machine learning</b> &#183; 23/23 tests"
     "<br>&#8594; exclusion polygons, capped at 72 h</font>", 760, 578, 330, 94, ""),

    # --- routing engine -------------------------------------------------
    ("mesh", "new",
     "Build vessel-modelled ice mesh"
     "<br><font style='font-size:9px'>meshiphi &#8212; non-uniform, splits hardest in the "
     "marginal ice zone<br>calibrated to MV Vasiliy Golovnin: beam 22.4 m, 16.4 kn &#183; "
     "isih/ice_meshes.py</font>", 270, 816, 580, 76, ""),
    ("router", "new",
     "Compute candidate routes"
     "<br><font style='font-size:9px'>PolarRoute &#215; 12 sweep &#8594; dominance filter "
     "&#183; BAS engine, reused under MIT<br>this is where the routes come from</font>",
     270, 916, 580, 76, ""),

    ("polaris", "dec",
     "Is course's POLARIS ice<br>concentration safe"
     "<br><font style='font-size:9px;color:#C4500E'>TODAY: FLAT 80% CUTOFF</font>",
     394, 1016, 332, 124, ""),
    ("recarto", "proc", "Advise Captain to<br>recartograph a new route", 764, 1050, 290, 56, ""),
    ("aOut", "conn", "A", 892, 1129, 34, 34, ""),

    ("tau", "new",
     "Is the new route enough<br>better to suggest it?"
     "<br><font style='font-size:9px'>Cost(current) &#8722; Cost(alt) &gt; &#964;</font>",
     386, 1168, 348, 128, "rhombus;" + DASH),
    ("keepPlan", "new",
     "Keep the Captain's current plan"
     "<br><font style='font-size:9px'>no detour suggested &#8212; the change is smaller "
     "than our own error bar</font>", 60, 1200, 290, 64, ""),

    ("draw", "proc",
     "Draw recommended route and<br>two backups to captain"
     "<br><font style='font-size:9px'>each leg styled forecast-grade or climatology-grade "
     "by lead time</font>", 370, 1322, 380, 68, ""),
    ("end", "term", "End", 490, 1414, 140, 40, ""),
]

E_ORTH = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitDx=0;exitDy=0;"
E_NOTE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=3 3;"
          "endArrow=none;strokeColor=#82b366;")

# source, target, label, extra style
EDGES = [
    ("start", "marks", "", ""),
    ("aIn", "marks", "", ""),
    ("nlogin", "marks", "", E_NOTE),
    ("marks", "backend", "", ""),
    ("nnav", "backend", "", E_NOTE),
    ("nlocal", "backend", "", E_NOTE + "strokeColor=#6c8ebf;"),
    ("backend", "chk", "", ""),
    ("chk", "keep", "YES", "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"),
    ("chk", "lower", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("keep", "readIce", "", ""),
    ("keep", "fetchFc", "", ""),
    ("keep", "fetchBerg", "", ""),
    ("lower", "readIce", "", ""),
    ("lower", "fetchFc", "", ""),
    ("lower", "fetchBerg", "", ""),
    ("readIce", "nNsidc", "", ""),
    ("nNsidc", "clean", "", ""),
    ("clean", "weather", "", ""),
    ("fetchFc", "nCmems", "", ""),
    ("nCmems", "unet", "", ""),
    ("unet", "conformal", "", ""),
    ("fetchBerg", "nUsnic", "", ""),
    ("nUsnic", "drift", "", ""),
    ("weather", "mesh", "", ""),
    ("conformal", "mesh", "", ""),
    ("drift", "mesh", "", ""),
    ("mesh", "router", "", ""),
    ("router", "polaris", "", ""),
    ("polaris", "recarto", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("recarto", "aOut", "", ""),
    ("polaris", "tau", "YES", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("tau", "keepPlan", "NO", "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"),
    ("tau", "draw", "YES", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("draw", "end", "", ""),
    ("keepPlan", "end", "", "exitX=0.5;exitY=1;entryX=0;entryY=0.5;"),
]


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


parts = [
    '<mxfile host="app.diagrams.net" type="device">\n',
    '  <diagram name="Navigation Decision Flow" id="navflow">\n',
    '    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="1654" '
    'math="0" shadow="0">\n',
    '      <root>\n',
    '        <mxCell id="0" />\n',
    '        <mxCell id="1" parent="0" />\n',
]

ids = set()
for cid, skey, label, x, y, w, h, extra in NODES:
    assert cid not in ids, f"duplicate node id {cid}"
    ids.add(cid)
    parts.append(cell(cid, S[skey] + extra, label, x, y, w, h))

for i, (src, dst, label, extra) in enumerate(EDGES, 1):
    assert src in ids, f"edge {i}: unknown source {src}"
    assert dst in ids, f"edge {i}: unknown target {dst}"
    parts.append(edge(f"e{i}", src, dst, label, E_ORTH + extra if not extra.startswith("edgeStyle")
                      else extra))

parts += ['      </root>\n', '    </mxGraphModel>\n', '  </diagram>\n', '</mxfile>\n']

xml = "".join(parts)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(xml)

print(f"wrote {OUT}")
print(f"  {len(NODES)} shapes, {len(EDGES)} connectors, {len(xml)} bytes")
