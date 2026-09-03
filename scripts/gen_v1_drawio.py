#!/usr/bin/env python3
"""Emit docs/v1.drawio — a faithful transcription of Jiteesh's hand-drawn flow.

This is deliberately NOT an improved version. Every box, every word and every
connection is his; the generator exists only so the geometry sits on a grid and
so every edge attaches to a shape id rather than to a bare coordinate, which is
what the hand-drawn file did in thirteen places (draw.io renders those as if
connected right up until a box is moved).

Wording is verbatim, including "callibrated", "ERA/GFS" and "recartograph".
Do not correct them here — the file is meant to match what he drew.

The shore/vessel tier diagram that used to live on page 2 now has its own file,
docs/v1_tiers.drawio, so that v1.drawio is one page like the original.

Re-run after editing NODES/EDGES; do not hand-edit the XML.
"""
from xml.sax.saxutils import escape

BASE_DIR = ('/home/jiteesh/sih/SIH26059-antarctic-navigation/.claude/worktrees/'
            'foamy-seeking-allen/docs/')
OUT = BASE_DIR + 'v1.drawio'
OUT_TIERS = BASE_DIR + 'v1_tiers.drawio'

BASE = "rounded=0;whiteSpace=wrap;html=1;fontSize=12;verticalAlign=middle;align=center;"
S = {
    "proc": BASE + "fillColor=#ffe6cc;strokeColor=#d79b00;fontColor=#5A3B08;",
    "dec":  "rhombus;whiteSpace=wrap;html=1;fontSize=12;align=center;"
            "fillColor=#e8b5d8;strokeColor=#a34e8c;fontColor=#4A1B3D;",
    "note": BASE + "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#254A20;fontSize=11;",
    "term": "rounded=1;arcSize=40;whiteSpace=wrap;html=1;fontSize=13;fontStyle=1;"
            "align=center;fillColor=#f8cecc;strokeColor=#b85450;fontColor=#5C1F1D;",
    "blue": BASE + "fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#13385C;",
    "conn": "ellipse;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;align=center;"
            "fillColor=#ffffff;strokeColor=#333333;",
    "band": "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#B0B8C4;"
            "dashed=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;"
            "fontSize=12;fontColor=#7C8698;fontStyle=1;",
    "gap":  BASE + "fillColor=#f5f5f5;strokeColor=#999999;fontColor=#333333;",
}

# ---------------------------------------------------------------- page 1 ----
# id, style, label, x, y, w, h
NODES = [
    # entry
    ("aIn",     "conn", "A", 5, 118, 40, 40),
    ("start",   "term", "Start", 175, 30, 150, 44),
    ("marks",   "proc", "Captain Marks Route in the Application", 60, 100, 290, 66),
    ("nlogin",  "note", "Captain Logs in application", 380, 108, 210, 50),
    ("backend", "proc", "Route is sent to the application's local processing "
                        "and data is fetched as voyage pack", 60, 210, 290, 90),
    ("nnav",    "note", "Navigation Decision Processing start", 380, 226, 210, 58),

    # self-check
    ("chk",     "dec",  "AI model checks yesterdays ice movement forecast correctness",
     640, 60, 300, 190),
    ("keep",    "proc", "Keep default Confidence in route suggestion", 990, 78, 270, 70),
    ("lower",   "proc", "Lower Confidence and increase number of safe routes", 990, 178, 270, 70),
    ("notify",  "blue", "Notify system's degradation state to the captain", 640, 300, 300, 76),
    ("nqual",   "note", "Check data quality and state before further processing.",
     990, 306, 270, 64),

    # routing engine
    ("tmesh",   "blue", "meshiphi", 1330, 60, 130, 38),
    ("mesh",    "blue", "build vessel modelled ice mesh", 1310, 110, 170, 150),
    ("trouter", "blue", "PolarRoute", 1530, 60, 130, 38),
    ("router",  "blue", "Compute candidate routes", 1510, 110, 170, 150),

    # decision chain
    ("polaris", "dec",  "Is course's POLARIS ice concentration safe", 1330, 310, 240, 170),
    ("recarto", "proc", "Advise Captain to recartograph a new route", 1250, 530, 240, 80),
    ("aOut",    "conn", "A", 1350, 645, 40, 40),
    ("hazards", "blue", "Include additional hazards in suggested routes", 1620, 400, 230, 88),
    ("mode",    "dec",  "Is this departure decision or have we already left port",
     1610, 540, 250, 180),
    ("tau",     "dec",  "Is new route better enough to suggest it?", 1360, 770, 230, 175),
    ("keeporig", "proc", "Keep the captains original route", 1240, 1000, 230, 76),
    ("drawrec", "proc", "Draw recommended route and two backups for captain",
     1510, 1000, 240, 76),
    ("finalize", "blue", "The Captain finalizes the sail route", 1370, 1120, 250, 80),
    ("micro",   "proc", "Suggest microchanges along the route being followed, warn captain "
                        "about weather states hidden dangers by low visibility and halt calls "
                        "to take if situation calls", 1910, 700, 280, 200),
    ("insights", "blue", "Give captain insights in navigational language along with calculations",
     1830, 970, 250, 100),
    ("trouble", "proc", "If trouble is foreseen suggest contacting nearest icebreaker, "
                        "station and MRCC", 2120, 970, 250, 110),
    ("end",     "term", "End", 1880, 1140, 160, 46),
]

# the five data streams, in his order: note above the source box
ROWS = [
    ("r1", "Taken by NSIDC satellite with SSMIS sensor",
     "Read Latest &amp; historical ice concentration map",
     "Clean unreliable data/noise in satellite image", None),
    ("r2", "CMEMS Sea-ice forecast",
     "Fetch weather model's Sea-ice forecast",
     "AI model corrects mistakes in the forecast",
     "Add callibrated safety margin for vessel"),
    ("r3", "USNIC Current iceberg positions",
     "Fetch current iceberg location near the course",
     "Predict Iceberg trajectory", None),
    ("r4", "ERA/GFS wind + waves , GEBCO bathymetry",
     "Fetch Environment&nbsp; and Hazards lying ahead",
     "Analyze weather forecast and hazards ahead", None),
    ("r5", "modelled drift field",
     "Estimate ice pressure / compression risk",
     "Flag dangerous ice-pressure convergence conditions", None),
]

BAND_TOP, PITCH = 430, 145
COL = [(60, 290), (390, 290), (720, 290)]

for i, (key, note, src, step2, step3) in enumerate(ROWS):
    y = BAND_TOP + i * PITCH
    NODES.append((f"{key}n", "note", note, COL[0][0], y, COL[0][1], 50))
    NODES.append((f"{key}a", "proc", src, COL[0][0], y + 56, COL[0][1], 76))
    NODES.append((f"{key}b", "proc", step2, COL[1][0], y + 56, COL[1][1], 76))
    if step3:
        NODES.append((f"{key}c", "proc", step3, COL[2][0], y + 56, COL[2][1], 76))

E_O = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;"
E_N = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=3 3;"
       "endArrow=none;strokeColor=#82b366;")
E_T = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=3 3;"
       "endArrow=none;strokeColor=#6c8ebf;")

EDGES = [
    ("start", "marks", ""), ("aIn", "marks", ""),
    ("nlogin", "marks", "", E_N),
    ("marks", "backend", ""),
    ("nnav", "backend", "", E_N),
    ("marks", "chk", ""),
    ("chk", "keep", "YES", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("chk", "lower", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("keep", "notify", ""), ("lower", "notify", ""),
    ("nqual", "notify", "", E_N),
    ("notify", "mesh", ""),
    ("tmesh", "mesh", "", E_T), ("trouter", "router", "", E_T),
    ("mesh", "router", ""),
    ("router", "polaris", ""),
    ("polaris", "recarto", "NO", "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("recarto", "aOut", ""),
    ("polaris", "hazards", "YES", "exitX=1;exitY=0.5;entryX=0.5;entryY=0;"),
    ("hazards", "mode", ""),
    ("mode", "tau", "Departure", "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("mode", "micro", "", "exitX=1;exitY=0.5;entryX=0.5;entryY=0;"),
    ("tau", "keeporig", "NO", "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("tau", "drawrec", "YES", "exitX=1;exitY=0.5;entryX=0.5;entryY=0;"),
    ("keeporig", "finalize", ""), ("drawrec", "finalize", ""),
    ("micro", "insights", ""), ("trouble", "insights", ""),
    ("insights", "end", ""),
]
for key, _n, _s, _b, step3 in ROWS:
    EDGES.append(("backend", f"{key}a", ""))
    EDGES.append((f"{key}n", f"{key}a", "", E_N))
    EDGES.append((f"{key}a", f"{key}b", ""))
    if step3:
        EDGES.append((f"{key}b", f"{key}c", ""))
        EDGES.append((f"{key}c", "mesh", ""))
    else:
        EDGES.append((f"{key}b", "mesh", ""))

# ---------------------------------------------------------- tiers file ----
SM, E = "<font style='font-size:9px'>", "</font>"
TIERS = [
    ("t2", "band",
     "WHERE EACH STEP RUNS. The split is not ours: the Canadian Coast Guard's ice navigation "
     "manual already separates a STRATEGIC phase ashore from a TACTICAL phase on the bridge, "
     "and leaves the routing recommendation with the shore ice desk while the bridge keeps "
     "real-time deviation authority.", 40, 20, 1600, 66),
    ("ashore", "band", "ASHORE &#8212; bandwidth, archives and GPUs live here", 40, 110, 1600, 470),
    ("s1", "note", "NSIDC daily ice concentration", 70, 165, 245, 54),
    ("s2", "note", "CMEMS sea-ice forecast", 330, 165, 245, 54),
    ("s3", "note", "USNIC iceberg positions", 590, 165, 245, 54),
    ("s4", "note", "ERA5 / GFS wind and waves", 850, 165, 245, 54),
    ("s5", "note", "ASPA / ASMA protected areas<br>(static, ships once)", 1110, 165, 245, 54),
    ("s6", "note", "IBCSO / GEBCO bathymetry<br>(static, ships once)", 1370, 165, 245, 54),
    ("p1", "proc", "Quality control<br>isih/ice_quality.py", 70, 270, 290, 64),
    ("p2", "proc", "Train the U-Net<br>(GPU &#8212; never at sea)", 390, 270, 290, 64),
    ("p3", "proc", "Inference + conformal<br>&#8594; SIC_upper", 710, 270, 290, 64),
    ("p4", "proc", "Build the vessel mesh<br>meshiphi", 1030, 270, 290, 64),
    ("p5", "blue", "Fulfil imagery requests<br>from the ship", 1350, 270, 265, 64),
    ("wts", "gap", "Model weights ~60 MB"
     f"<br>{SM}never over the satellite link &#8212; USB stick at port{E}", 70, 390, 420, 64),
    ("pack", "blue", "Build and sign the voyage pack", 540, 390, 520, 64),
    ("nharvest", "note", "the CMEMS harvest already runs daily on GitHub Actions",
     1110, 392, 505, 60),
    ("link", "band",
     "ACROSS THE LINK &#8212; Iridium-class, ~704 kbps at best and usually far less. "
     "No geostationary VSAT reaches south of ~70&#176;S.", 40, 615, 1600, 210),
    ("down", "proc", "&#8595;&nbsp; DOWN to the ship"
     f"<br>{SM}vessel-modelled mesh block <b>76 KB gzipped (measured)</b> &#183; daily delta "
     f"target 50 KB &#183; full corridor refresh 0.5&#8211;1 MB (extrapolated){E}",
     70, 680, 500, 88),
    ("up", "blue", "&#8593;&nbsp; UP from the ship"
     f"<br>{SM}route polyline <b>796 B</b> &#183; a request for tactical imagery is a few bytes "
     f"&#8212; the <i>image</i> is what we cannot afford{E}", 600, 680, 500, 88),
    ("never", "gap", "&#10007;&nbsp; NEVER crosses"
     f"<br>{SM}60 MB model weights &#183; raw NetCDF &#183; any live API call. If a feature "
     f"needs the internet at 70&#176;S, it is not a feature{E}", 1130, 680, 485, 88),
    ("aboard", "band", "ABOARD &#8212; everything that has to answer a question", 40, 860, 1600, 330),
    ("v1", "proc", "The voyage pack, on disk", 90, 915, 320, 60),
    ("v2", "blue", "The ship's own sensors"
     f"<br>{SM}radar, AIS, shaft power, met, helicopter recon{E}", 450, 915, 340, 60),
    ("v3", "proc", "PolarRoute &#8212; routes are computed here, locally", 830, 915, 340, 60),
    ("v4", "note", "so the master can re-plan with no link at all", 1210, 918, 400, 54),
    ("v5", "proc", "The decision flow in v1.drawio", 380, 1020, 400, 60),
    ("v6", "term", "The Captain decides", 850, 1020, 320, 60),
    ("v7", "gap", "why not send finished routes only?"
     f"<br>{SM}because then the master cannot re-plan when the ice disagrees with the "
     f"forecast &#8212; and it will{E}", 90, 1105, 520, 70),
    ("v8", "gap", "why not run ingestion aboard?"
     f"<br>{SM}GB-scale downloads and a GPU. Neither exists at 70&#176;S{E}", 650, 1105, 520, 70),
]
E_G = E_O + "dashed=1;dashPattern=3 3;strokeColor=#999999;endArrow=none;"
TIER_EDGES = [
    ("s1", "p1", ""), ("s2", "p3", ""), ("s3", "p4", ""), ("s4", "p4", ""),
    ("s5", "p4", ""), ("s6", "p4", ""),
    ("p1", "p2", ""), ("p2", "p3", ""), ("p3", "p4", ""), ("p4", "pack", ""), ("p5", "pack", ""),
    ("nharvest", "p1", "", E_N),
    ("pack", "down", ""), ("wts", "v1", "USB at port", E_G),
    ("down", "v1", ""), ("up", "p5", "", E_T),
    ("v1", "v5", ""), ("v2", "v5", ""), ("v3", "v5", ""), ("v4", "v3", "", E_N),
    ("v5", "v6", ""), ("v6", "up", "his route, and what he asked for", E_T),
    ("pack", "never", "excluded from the pack", E_G), ("v7", "v3", "", E_G), ("v8", "v1", "", E_G),
]
TIER_BANDS = {"ashore": "fillColor=#F3F7FB;strokeColor=#6c8ebf;dashed=0;",
              "link": "fillColor=#FFF6E8;strokeColor=#d79b00;dashed=0;",
              "aboard": "fillColor=#F4FAF4;strokeColor=#82b366;dashed=0;"}


def cell(cid, style, label, x, y, w, h):
    return (f'        <mxCell id="{cid}" value="{escape(label, {chr(34): "&quot;"})}" '
            f'style="{escape(style, {chr(34): "&quot;"})}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
            f'        </mxCell>\n')


def edge(eid, src, dst, label, style):
    return (f'        <mxCell id="{eid}" value="{escape(label, {chr(34): "&quot;"})}" '
            f'style="{escape(style, {chr(34): "&quot;"})}" edge="1" parent="1" '
            f'source="{src}" target="{dst}">\n'
            f'          <mxGeometry relative="1" as="geometry" />\n'
            f'        </mxCell>\n')


def build(name, pid, nodes, edges, w, h, prefix, extra_style=None):
    ids = set()
    out = [f'<mxfile host="app.diagrams.net" type="device">\n',
           f'  <diagram name="{name}" id="{pid}">\n',
           f'    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
           f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" '
           f'pageHeight="{h}" math="0" shadow="0">\n',
           '      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n']
    for cid, skey, label, x, y, cw, ch in nodes:
        assert cid not in ids, f"duplicate id {cid}"
        ids.add(cid)
        style = S[skey] + ((extra_style or {}).get(cid, ""))
        out.append(cell(cid, style, label, x, y, cw, ch))
    for i, e in enumerate(edges, 1):
        src, dst, label = e[0], e[1], e[2]
        st = e[3] if len(e) > 3 else ""
        assert src in ids, f"{name}: edge {i} unknown source {src}"
        assert dst in ids, f"{name}: edge {i} unknown target {dst}"
        out.append(edge(f"{prefix}{i}", src, dst, label,
                        st if st.startswith("edgeStyle") else E_O + st))
    out += ['      </root>\n', '    </mxGraphModel>\n', '  </diagram>\n', '</mxfile>\n']
    return "".join(out), ids


xml, ids = build("Decision workflow", "navflow", NODES, EDGES, 2420, 1280, "a")
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(xml)
print(f"wrote {OUT}\n  {len(NODES)} shapes, {len(EDGES)} connectors, 1 page, {len(xml)} bytes")

xml2, _ = build("Where it runs", "tiers", TIERS, TIER_EDGES, 1680, 1260, "b", TIER_BANDS)
with open(OUT_TIERS, "w", encoding="utf-8") as fh:
    fh.write(xml2)
print(f"wrote {OUT_TIERS}\n  {len(TIERS)} shapes, {len(TIER_EDGES)} connectors")
