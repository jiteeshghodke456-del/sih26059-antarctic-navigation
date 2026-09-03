#!/usr/bin/env python3
"""Regenerate docs/v1.drawio — the navigation decision workflow.

Page 1 is Jiteesh's own flowchart, corrected and extended. Every label he wrote
is preserved verbatim; anything this script adds is prefixed "NEW:" so the
original wording stays legible and attribution is obvious. Two structural fixes
carry over from review: the data band now precedes the mesh and router (a router
cannot run before its inputs exist), and every edge attaches to a shape id
rather than a bare coordinate — the hand-drawn file had 13 arrows terminating at
floating points, which look connected until a box is moved.

Page 2 is the half the flowchart cannot show: which side of the satellite link
each step runs on. That split is not our invention — the Canadian Coast Guard's
ice navigation manual already separates a strategic phase ashore from a tactical
phase on the bridge, and puts the routing recommendation with the shore ice desk
while the bridge keeps real-time deviation authority.

Border style encodes build status, which is the honest part:
    solid   built and measured
    dashed  designed, not built
    dotted  white space — no product exists anywhere

The seven-stream data band is emitted from ROWS rather than hand-placed, because
the first cut hard-coded 300px columns and 26 labels overflowed their boxes.
Geometry belongs in one place. Re-run after editing; do not hand-edit the XML.
"""
from xml.sax.saxutils import escape

OUT = ('/home/jiteesh/sih/SIH26059-antarctic-navigation/.claude/worktrees/'
       'foamy-seeking-allen/docs/v1.drawio')

# Jiteesh's original palette, kept so the file still looks like his diagram.
BASE = "rounded=0;whiteSpace=wrap;html=1;fontSize=12;verticalAlign=middle;align=center;"
S = {
    "proc": BASE + "fillColor=#ffe6cc;strokeColor=#d79b00;fontColor=#5A3B08;",
    "dec":  "rhombus;whiteSpace=wrap;html=1;fontSize=11;align=center;"
            "fillColor=#f5d9e8;strokeColor=#b8559a;fontColor=#5C2049;",
    "note": BASE + "fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#254A20;fontSize=10;",
    "term": "rounded=1;arcSize=40;whiteSpace=wrap;html=1;fontSize=13;fontStyle=1;"
            "align=center;fillColor=#f8cecc;strokeColor=#b85450;fontColor=#5C1F1D;",
    "new":  BASE + "fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#13385C;",
    "gap":  BASE + "fillColor=#f5f5f5;strokeColor=#999999;fontColor=#333333;",
    "conn": "ellipse;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;align=center;"
            "fillColor=#ffffff;strokeColor=#333333;",
    "tag":  BASE + "fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#3F2A50;fontSize=11;",
    "band": "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#B0B8C4;"
            "dashed=1;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;"
            "fontSize=12;fontColor=#7C8698;fontStyle=1;",
}
DASH = "dashed=1;dashPattern=8 4;"          # designed, not built
DOT = "dashed=1;dashPattern=2 4;"           # white space

SM = "<font style='font-size:9px'>"         # small print inside a box
E = "</font>"

MID = 840                                   # canvas centre line


def c(w):
    """x that centres a box of width w."""
    return MID - w // 2


# ---------------------------------------------------------------- page 1 ----
# id, style, label, x, y, w, h, extra
P1 = [
    ("legend", "band",
     "LEGEND&nbsp; &nbsp;solid = built and measured&nbsp; &#183;&nbsp; dashed = designed, not built"
     "&nbsp; &#183;&nbsp; dotted = white space, no product exists anywhere"
     "<br>orange = Jiteesh's original step&nbsp; &#183;&nbsp; blue = added this pass&nbsp; &#183;&nbsp; "
     "green = data source&nbsp; &#183;&nbsp; grey = a gap, stated plainly&nbsp; &#183;&nbsp; "
     "purple = external library we reuse",
     40, 20, 1600, 62, ""),

    # --- BAND A: two ways in --------------------------------------------
    ("start", "term", "Start", c(180), 110, 180, 40, ""),
    ("marks", "proc", "Captain Marks Route in the Application", c(340), 180, 340, 56, ""),
    ("nlogin", "note", "Captain Logs in application", 1060, 186, 260, 44, ""),
    ("aIn", "conn", "A", 606, 190, 36, 36, ""),
    ("trigger2", "new",
     "NEW: new pack, observation or ship-sensor update arrives"
     f"<br>{SM}the loop must also start without the captain asking &#8212; "
     f"an already cleared route may have closed up{E}",
     90, 168, 420, 80, DASH),
    ("backend", "proc", "Route is sent to the application's local processing", c(340), 280, 340, 56, ""),
    ("nnav", "note", "Navigation Decision Processing start", 1060, 286, 260, 44, ""),
    ("nlocal", "new",
     "NEW: local = the bridge laptop"
     f"<br>{SM}no outbound network south of ~70&#176;S. Everything below reads the "
     f"voyage pack, not the internet &#8212; see page 2{E}",
     90, 268, 420, 80, ""),

    # --- BAND B: self-check and how loudly we fail -----------------------
    ("chk", "dec",
     "AI model checks yesterdays ice movement forecast correctness"
     f"<br>{SM}yesterday's 1-day forecast vs today's observation{E}",
     c(360), 380, 360, 130, DASH),
    ("keep", "proc", "Keep default Confidence in route suggestion", 150, 415, 330, 60, ""),
    ("lower", "proc", "Lower Confidence and increase number of safe routes", 1200, 415, 330, 60, ""),
    ("rung", "new",
     "NEW: declare which rung we are running on, and show it to the captain"
     f"<br>{SM}no do-overs at sea &#8212; the system must say how degraded it is "
     f"<b>before</b> the advice, not after{E}",
     c(420), 550, 420, 96, DASH),
    ("nrung", "note",
     "1&nbsp; corrected forecast + calibrated interval<br>"
     "2&nbsp; raw CMEMS forecast (our model failed verification)<br>"
     "3&nbsp; persistence from newest observation (feed lost)<br>"
     "4&nbsp; climatology for the date (no recent observation)",
     1120, 546, 410, 92, ""),
]

# --- BAND C: the seven streams we read, generated on a grid --------------
COLS = [(70, 400), (500, 400), (930, 400)]   # (x, width) for source / step / note-on-gap
BAND_TOP = 720
PITCH = 152
BOX_H = 88
NOTE_H = 46
GAP_Y = 6                                    # nudge so the gap panel optically centres

# key, source style+label, green note, middle step (style, label, extra),
# right-hand gap panel (style, label, extra)
ROWS = [
    ("r1",
     ("proc", "Read Latest &amp; historical ice concentration map", ""),
     "Taken by NSIDC satellite with SSMIS sensor",
     ("proc", "Clean unreliable data/noise in satellite image"
      f"<br>{SM}isih/ice_quality.py &#183; fires every single day, ~118 cells{E}", ""),
     ("gap", "NEW: Polar Code &#167;11.3.4 wants prior-year statistics"
      f"<br>{SM}we hold 1,096 real daily files and use them only for training, never as "
      f"climatology the captain can actually see{E}", DASH)),

    ("r2",
     ("proc", "Fetch weather model's Sea-ice forecast", ""),
     "CMEMS Sea-ice forecast",
     ("proc", "AI model corrects mistakes in the forecast"
      f"<br>{SM}residual U-Net &#183; corrected = clip(background + &#916;, 0, 1)"
      f"<br>zero-init head, so a broken model degrades to CMEMS, not to zero{E}", ""),
     ("proc", "Add calibrated safety margin for vessel"
      f"<br>{SM}stratified conformal &#8594; SIC_upper, the number the router really uses{E}",
      DASH)),

    ("r3",
     ("proc", "Fetch current iceberg location near the course", ""),
     "USNIC Current iceberg positions",
     ("proc", "Predict Iceberg trajectory"
      f"<br>{SM}Wagner closed form &#183; <b>physics, not machine learning</b> &#183; "
      f"23/23 tests pass &#183; &#8594; exclusion polygons{E}", ""),
     ("gap", "USNIC tracks bergs &#8805; ~18.5 km"
      f"<br>{SM}a growler is ~5 m. That gap is 3.5 orders of magnitude and nothing in orbit "
      f"closes it &#8212; radar and the lookout own it{E}", "")),

    ("r4",
     ("proc", "Fetch Environment&nbsp; and Hazards lying ahead", ""),
     "ERA5/GFS wind + waves , GEBCO/IBCSO bathymetry",
     ("proc", "Analyze weather forecast and hazards ahead"
      f"<br>{SM}wind sets the ice: free drift &#8776; 2% of wind speed, deflected "
      f"20&#8211;40&#176; <b>left</b> in the southern hemisphere{E}", ""),
     ("gap", "ERA5 under-reads the winds that beset ships"
      f"<br>{SM}bias &#8722;3.89 m/s above 20 m/s. Bias-correct it with the ship's own "
      f"anemometer, or say so out loud{E}", DASH)),

    ("r5",
     ("new", "NEW: Read protected and ecologically sensitive areas", ""),
     "CCAMLR MPAs, ASPA / ASMA, marine-mammal measures",
     ("new", "Mark them as areas the route may not cross"
      f"<br>{SM}rides the same excluded_zones hook as the icebergs (ADR-010) &#8212; "
      f"the mechanism already exists, only the polygons are missing{E}", DASH),
     ("gap", "Polar Code &#167;11.3.6&#8211;.8 requires this"
      f"<br>{SM}protected areas and marine-mammal measures are mandatory planning "
      f"factors. We currently consider neither{E}", DASH)),

    ("r6",
     ("new", "NEW: Read the ship's own sensors", ""),
     "shaft power, speed log, X/S-band radar, AIS, met station, helicopter ice recon",
     ("new", "Correct our own models with what the ship actually measures"
      f"<br>{SM}shaft power is a <b>measured</b> ice resistance &#8212; the one number our "
      f"vessel config admits is borrowed from another hull{E}", DASH),
     ("gap", "Golovnin already flies ice reconnaissance"
      f"<br>{SM}she carries two helicopters used for ice air recon on the route. That "
      f"observation has no path into the system{E}", DOT)),

    ("r7",
     ("new", "NEW: Estimate ice pressure / compression risk", DOT),
     "modelled drift field &#8594; divergence &#8706;u/&#8706;x + &#8706;v/&#8706;y",
     ("new", "Flag convergence setting into the fast-ice edge"
      f"<br>{SM}the documented besetting geometry &#8212; and exactly where the ship sits "
      f"to offload at Bharati and Maitri{E}", DOT),
     ("gap", "No operational Antarctic pressure product exists, anywhere"
      f"<br>{SM}POLARIS never uses the words pressure, compression, ridge or drift. "
      f"This is white space, not an oversight{E}", DOT)),
]

for i, (key, (sst, slab, sx), note, (pst, plab, px), (gst, glab, gx)) in enumerate(ROWS):
    y = BAND_TOP + i * PITCH
    P1.append((f"{key}a", sst, slab, COLS[0][0], y, COLS[0][1], BOX_H, sx))
    P1.append((f"{key}n", "note", note, COLS[0][0], y + BOX_H + 6, COLS[0][1], NOTE_H, ""))
    P1.append((f"{key}b", pst, plab, COLS[1][0], y, COLS[1][1], BOX_H, px))
    P1.append((f"{key}c", gst, glab, COLS[2][0], y + GAP_Y, COLS[2][1], BOX_H, gx))

BAND_BOT = BAND_TOP + (len(ROWS) - 1) * PITCH + BOX_H + 6 + NOTE_H
P1.append(("cband", "band",
           "READ THE VOYAGE PACK &#8212; independent streams, in parallel."
           "&nbsp;&nbsp;Nothing here is optional: the router consumes all of it.",
           40, BAND_TOP - 56, 1600, (BAND_BOT - BAND_TOP) + 80, ""))

y = BAND_BOT + 70
P1 += [
    # --- BAND D: the routing engine -------------------------------------
    ("mesh", "proc", "build vessel modelled ice mesh", c(620), y, 620, 60, ""),
    ("tmesh", "tag", "meshiphi", 1200, y + 10, 140, 40, ""),
    ("nmesh", "note",
     "non-uniform &#8212; splits hardest where the ice is most variable. "
     "Calibrated to MV Vasiliy Golovnin: beam 22.4 m, 16.4 kn",
     170, y - 6, 320, 72, ""),
    ("router", "proc", "Compute candidate routes", c(620), y + 100, 620, 60, ""),
    ("trouter", "tag", "PolarRoute", 1200, y + 110, 140, 40, ""),
    ("ntime", "new",
     "NEW: one mesh layer per forecast day"
     f"<br>{SM}today the router plans a 17-day voyage on day-0 ice, as if the field holds "
     f"still. It does not{E}", 90, y + 92, 400, 76, DASH),

    # --- BAND E: safety screen ------------------------------------------
    ("polaris", "dec",
     "Is course's POLARIS ice concentration safe"
     f"<br>{SM}TODAY: a flat 80% cutoff. POLARIS is indexed by ice <b>type</b>, so real "
     f"compliance needs a thickness channel first{E}",
     c(400), y + 215, 400, 140, ""),
    ("recarto", "proc", "Advise Captain to recartograph a new route", 1140, y + 255, 330, 60, ""),
    ("aOut", "conn", "A", 1287, y + 340, 36, 36, ""),
    ("hold", "new",
     "NEW: if no candidate ever passes &#8212; hold at the ice edge and wait"
     f"<br>{SM}the real answer at sea, and what Aurora Australis did at Mawson in 2014. "
     f"An endless redraw loop is not an outcome{E}", 90, y + 241, 420, 96, DASH),
    ("annot", "new",
     "NEW: attach the hazards we cannot hard-gate on"
     f"<br>{SM}pressure risk &#183; protected-area proximity &#183; <b>when the lookout will "
     f"be blind</b>: sea state &gt; 4 ft hides growlers, blizzard visibility &#8804; 100 m{E}",
     c(460), y + 400, 460, 88, DASH),

    # --- BAND F: the two modes ------------------------------------------
    ("mode", "dec",
     "NEW: is this the departure decision, or are we already underway?"
     f"<br>{SM}the captain's own instruction: argue once, then support{E}",
     c(400), y + 530, 400, 140, DASH),
    ("tau", "dec",
     "Is new route better enough to suggest it?"
     f"<br>{SM}Cost(current) &#8722; Cost(alt) &gt; &#964;, where &#964; comes from our own "
     f"calibrated interval &#8212; not a hand-tuned number{E}",
     170, y + 720, 400, 140, DASH),
    ("draw", "proc", "Draw recommended route and two backups for captain", 70, y + 905, 320, 64, ""),
    ("keeporig", "proc", "Keep the captains original route", 420, y + 905, 320, 64, ""),
    ("picks", "new",
     "NEW: the captain picks. His choice becomes THE route."
     f"<br>{SM}from here we never re-argue it{E}", 190, y + 1005, 400, 64, DASH),
    ("micro", "new",
     "NEW: do not re-open the strategic choice. Suggest micro changes, and the things "
     "he can miss."
     f"<br>{SM}a system that keeps arguing for a route the captain already rejected is a "
     f"system that gets switched off{E}", 1080, y + 745, 420, 96, DASH),

    # --- BAND G: how it is said, and who to call ------------------------
    ("advisory", "new",
     "NEW: write it in ice-navigator language, and show the calculation"
     f"<br>{SM}&quot;9/10 close pack, thick first-year, ridged&quot; &#8212; not &quot;lots "
     f"of ice&quot;. WMO egg code: concentration, stage of development, floe size{E}",
     c(460), y + 1120, 460, 92, DASH),
    ("rescue", "new",
     "NEW: if trouble is foreseen &#8212; nearest icebreaker, station and MRCC for this sector"
     f"<br>{SM}Polar Code &#167;11.3.5 and &#167;11.3.9: places of refuge, and distance from "
     f"SAR. Static data, zero bandwidth{E}", 1080, y + 1116, 420, 100, DASH),
    ("end", "term", "End", c(180), y + 1260, 180, 40, ""),
]
P1_H = y + 1400

E_O = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;"
E_N = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=3 3;"
       "endArrow=none;strokeColor=#82b366;")
E_G = E_O + "dashed=1;dashPattern=3 3;strokeColor=#999999;endArrow=none;"

X1 = [
    ("start", "marks", "", ""),
    ("aIn", "marks", "", ""),
    ("nlogin", "marks", "", E_N),
    ("marks", "backend", "", ""),
    ("nnav", "backend", "", E_N),
    ("nlocal", "backend", "", E_N + "strokeColor=#6c8ebf;"),
    ("trigger2", "backend", "", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    ("backend", "chk", "", ""),
    ("chk", "keep", "YES", "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"),
    ("chk", "lower", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("keep", "rung", "", ""),
    ("lower", "rung", "", ""),
    ("nrung", "rung", "", E_N),
    ("mesh", "router", "", ""),
    ("nmesh", "mesh", "", E_N),
    ("tmesh", "mesh", "", E_N + "strokeColor=#9673a6;"),
    ("trouter", "router", "", E_N + "strokeColor=#9673a6;"),
    ("ntime", "router", "", E_N + "strokeColor=#6c8ebf;"),
    ("router", "polaris", "", ""),
    ("polaris", "recarto", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("recarto", "aOut", "", ""),
    ("recarto", "hold", "repeatedly", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    ("polaris", "annot", "YES", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("annot", "mode", "", ""),
    ("mode", "tau", "DEPARTURE &#8212; argue once",
     "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("mode", "micro", "UNDERWAY &#8212; support",
     "exitX=1;exitY=0.5;entryX=0.5;entryY=0;"),
    ("tau", "draw", "YES", "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("tau", "keeporig", "NO", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("draw", "picks", "", ""),
    ("keeporig", "picks", "", ""),
    ("picks", "advisory", "", ""),
    ("micro", "advisory", "", ""),
    ("advisory", "rescue", "risk rising", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    ("advisory", "end", "", ""),
    ("rescue", "end", "", ""),
]
# every stream is fed by the confidence decision and feeds the mesh
for key, *_ in ROWS:
    X1 += [("rung", f"{key}a", "", ""),
           (f"{key}n", f"{key}a", "", E_N),
           (f"{key}a", f"{key}b", "", ""),
           (f"{key}c", f"{key}b", "", E_G),
           (f"{key}b", "mesh", "", "")]

# ---------------------------------------------------------------- page 2 ----
P2 = [
    ("t2", "band",
     "WHERE EACH STEP RUNS. The split is not ours: the Canadian Coast Guard's ice "
     "navigation manual already separates a STRATEGIC phase ashore from a TACTICAL phase "
     "on the bridge, and leaves the routing recommendation with the shore ice desk while "
     "the bridge keeps real-time deviation authority.",
     40, 20, 1600, 66, ""),

    ("ashore", "band", "ASHORE &#8212; bandwidth, archives and GPUs live here",
     40, 110, 1600, 470, "fillColor=#F3F7FB;strokeColor=#6c8ebf;dashed=0;"),
    ("s1", "note", "NSIDC daily ice concentration", 70, 165, 245, 54, ""),
    ("s2", "note", "CMEMS sea-ice forecast", 330, 165, 245, 54, ""),
    ("s3", "note", "USNIC iceberg positions", 590, 165, 245, 54, ""),
    ("s4", "note", "ERA5 / GFS wind and waves", 850, 165, 245, 54, ""),
    ("s5", "note", "CCAMLR MPA + ASPA / ASMA<br>(static, ships once)", 1110, 165, 245, 54, ""),
    ("s6", "note", "IBCSO / GEBCO bathymetry<br>(static, ships once)", 1370, 165, 245, 54, ""),

    ("p1", "proc", "Quality control<br>isih/ice_quality.py", 70, 270, 290, 64, ""),
    ("p2", "proc", "Train the U-Net<br>(GPU &#8212; never at sea)", 390, 270, 290, 64, ""),
    ("p3", "proc", "Inference + conformal<br>&#8594; SIC_upper", 710, 270, 290, 64, DASH),
    ("p4", "proc", "Build the vessel mesh<br>meshiphi", 1030, 270, 290, 64, ""),
    ("p5", "new", "Fulfil imagery requests<br>from the ship", 1350, 270, 265, 64, DASH),

    ("wts", "gap", "Model weights ~60 MB"
     f"<br>{SM}never over the satellite link &#8212; USB stick at port{E}",
     70, 390, 420, 64, ""),
    ("pack", "new", "Build and sign the voyage pack", 540, 390, 520, 64, DASH),
    ("nharvest", "note", "the CMEMS harvest already runs daily on GitHub Actions",
     1110, 392, 505, 60, ""),

    ("link", "band",
     "ACROSS THE LINK &#8212; Iridium-class, ~704 kbps at best and usually far less. "
     "No geostationary VSAT reaches south of ~70&#176;S.",
     40, 615, 1600, 210, "fillColor=#FFF6E8;strokeColor=#d79b00;dashed=0;"),
    ("down", "proc", "&#8595;&nbsp; DOWN to the ship"
     f"<br>{SM}vessel-modelled mesh block <b>76 KB gzipped (measured)</b> &#183; daily delta "
     f"target 50 KB &#183; full corridor refresh 0.5&#8211;1 MB (extrapolated, not measured){E}",
     70, 680, 500, 88, ""),
    ("up", "new", "&#8593;&nbsp; UP from the ship"
     f"<br>{SM}route polyline <b>796 B</b> &#183; a request for tactical imagery is a few bytes "
     f"&#8212; the <i>image</i> is what we cannot afford &#183; sensor summary{E}",
     600, 680, 500, 88, DASH),
    ("never", "gap", "&#10007;&nbsp; NEVER crosses"
     f"<br>{SM}60 MB model weights &#183; raw NetCDF &#183; any live API call. If a feature "
     f"needs the internet at 70&#176;S, it is not a feature{E}",
     1130, 680, 485, 88, ""),

    ("aboard", "band", "ABOARD &#8212; everything that has to answer a question",
     40, 860, 1600, 330, "fillColor=#F4FAF4;strokeColor=#82b366;dashed=0;"),
    ("v1", "proc", "The voyage pack, on disk", 90, 915, 320, 60, ""),
    ("v2", "new", "The ship's own sensors"
     f"<br>{SM}radar, AIS, shaft power, met, helicopter recon{E}", 450, 915, 340, 60, DASH),
    ("v3", "proc", "PolarRoute &#8212; routes are computed here, locally", 830, 915, 340, 60, ""),
    ("v4", "note", "so the master can re-plan with no link at all", 1210, 918, 400, 54, ""),
    ("v5", "proc", "The decision flow on page 1", 380, 1020, 400, 60, ""),
    ("v6", "term", "The Captain decides", 850, 1020, 320, 60, ""),
    ("v7", "gap", "why not send finished routes only?"
     f"<br>{SM}because then the master cannot re-plan when the ice disagrees with the "
     f"forecast &#8212; and it will{E}", 90, 1105, 520, 70, ""),
    ("v8", "gap", "why not run ingestion aboard?"
     f"<br>{SM}GB-scale downloads and a GPU. Neither exists at 70&#176;S{E}",
     650, 1105, 520, 70, ""),
]

X2 = [
    ("s1", "p1", "", E_O), ("s2", "p3", "", E_O), ("s3", "p4", "", E_O),
    ("s4", "p4", "", E_O), ("s5", "p4", "", E_O), ("s6", "p4", "", E_O),
    ("p1", "p2", "", E_O), ("p2", "p3", "", E_O), ("p3", "p4", "", E_O),
    ("p4", "pack", "", E_O), ("p5", "pack", "", E_O),
    ("nharvest", "p1", "", E_N),
    ("pack", "down", "", E_O),
    ("wts", "v1", "USB at port", E_O + "dashed=1;strokeColor=#999999;"),
    ("down", "v1", "", E_O),
    ("up", "p5", "", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    ("v1", "v5", "", E_O), ("v2", "v5", "", E_O), ("v3", "v5", "", E_O),
    ("v4", "v3", "", E_N),
    ("v5", "v6", "", E_O),
    ("v6", "up", "his route, and what he asked for", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    # the rationale panels are commentary, so they attach with a plain line and
    # no arrowhead — but they do attach, so nothing floats
    ("pack", "never", "excluded from the pack", E_G),
    ("v7", "v3", "", E_G),
    ("v8", "v1", "", E_G),
]


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


def page(name, pid, nodes, edges, w, h, prefix):
    ids = set()
    out = [f'  <diagram name="{name}" id="{pid}">\n',
           f'    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" '
           f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
           f'pageWidth="{w}" pageHeight="{h}" math="0" shadow="0">\n',
           '      <root>\n',
           '        <mxCell id="0" />\n',
           '        <mxCell id="1" parent="0" />\n']
    for cid, skey, label, x, y, cw, ch, extra in nodes:
        assert cid not in ids, f"{name}: duplicate id {cid}"
        ids.add(cid)
        out.append(cell(cid, S[skey] + extra, label, x, y, cw, ch))
    for i, (src, dst, label, extra) in enumerate(edges, 1):
        assert src in ids, f"{name}: edge {i} unknown source {src}"
        assert dst in ids, f"{name}: edge {i} unknown target {dst}"
        style = extra if extra.startswith("edgeStyle") else E_O + extra
        out.append(edge(f"{prefix}{i}", src, dst, label, style))
    out += ['      </root>\n', '    </mxGraphModel>\n', '  </diagram>\n']
    return "".join(out), ids


x1, _ = page("Decision workflow", "navflow", P1, X1, 1680, P1_H, "a")
x2, _ = page("Where it runs", "tiers", P2, X2, 1680, 1260, "b")

xml = '<mxfile host="app.diagrams.net" type="device">\n' + x1 + x2 + '</mxfile>\n'
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(xml)

print(f"wrote {OUT}")
print(f"  page 1: {len(P1)} shapes, {len(X1)} connectors, canvas 1680x{P1_H}")
print(f"  page 2: {len(P2)} shapes, {len(X2)} connectors")
print(f"  {len(xml)} bytes total")
