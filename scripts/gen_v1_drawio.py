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

Re-run after editing NODES/EDGES; do not hand-edit the XML.
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

# ---------------------------------------------------------------- page 1 ----
# id, style, label, x, y, w, h, extra
P1 = [
    ("legend", "band",
     "LEGEND&nbsp; &nbsp;solid = built and measured&nbsp; &#183;&nbsp; dashed = designed, not built"
     "&nbsp; &#183;&nbsp; dotted = white space, no product exists anywhere"
     "<br>orange = Jiteesh's original step&nbsp; &#183;&nbsp; blue = added this pass&nbsp; &#183;&nbsp; "
     "green = data source&nbsp; &#183;&nbsp; purple = external library we reuse",
     40, 20, 1560, 60, ""),

    # --- BAND A: two ways in --------------------------------------------
    ("start", "term", "Start", 700, 110, 180, 40, ""),
    ("marks", "proc", "Captain Marks Route in the Application", 620, 180, 340, 56, ""),
    ("nlogin", "note", "Captain Logs in application", 1000, 186, 250, 44, ""),
    ("aIn", "conn", "A", 556, 190, 36, 36, ""),
    ("trigger2", "new",
     "NEW: new pack, observation or ship-sensor update arrives"
     f"<br>{SM}the loop must also start without the captain asking &#8212; "
     f"an already cleared route may have closed up{E}",
     100, 174, 380, 68, DASH),
    ("backend", "proc", "Route is sent to the application's local processing", 620, 276, 340, 56, ""),
    ("nnav", "note", "Navigation Decision Processing start", 1000, 282, 250, 44, ""),
    ("nlocal", "new",
     "NEW: local = the bridge laptop"
     f"<br>{SM}no outbound network south of ~70&#176;S. Everything below reads the "
     f"voyage pack, not the internet &#8212; see page 2{E}",
     100, 270, 380, 68, ""),

    # --- BAND B: self-check and how loudly we fail -----------------------
    ("chk", "dec",
     "AI model checks yesterdays ice movement forecast correctness"
     f"<br>{SM}yesterday's 1-day forecast vs today's observation &#8212; free, honest, daily{E}",
     620, 370, 340, 120, DASH),
    ("keep", "proc", "Keep default Confidence in route suggestion", 180, 400, 300, 60, ""),
    ("lower", "proc", "Lower Confidence and increase number of safe routes", 1100, 400, 300, 60, ""),
    ("rung", "new",
     "NEW: declare which rung we are running on, and show it to the captain"
     f"<br>{SM}no do-overs at sea: the system must say how degraded it is "
     f"<b>before</b> the advice, not after{E}",
     600, 530, 380, 76, DASH),
    ("nrung", "note",
     "1&nbsp; corrected forecast + calibrated interval<br>"
     "2&nbsp; raw CMEMS forecast&nbsp;&nbsp;(our model failed verification)<br>"
     "3&nbsp; persistence from newest observation&nbsp;&nbsp;(feed lost)<br>"
     "4&nbsp; climatology for the date&nbsp;&nbsp;(no recent observation)",
     1030, 526, 370, 84, ""),

    # --- BAND C: what we read, seven streams ----------------------------
    ("cband", "band",
     "READ THE VOYAGE PACK &#8212; independent streams, in parallel."
     "&nbsp;&nbsp;Nothing below can be skipped: the router consumes all of it.",
     40, 650, 1560, 810, ""),

    # row 1 — ice observation
    ("r1a", "proc", "Read Latest &amp; historical ice concentration map", 70, 700, 300, 56, ""),
    ("r1n", "note", "Taken by NSIDC satellite with SSMIS sensor", 70, 762, 300, 36, ""),
    ("r1b", "proc",
     "Clean unreliable data/noise in satellite image"
     f"<br>{SM}isih/ice_quality.py &#183; fires every day, ~118 cells{E}", 410, 700, 300, 56, ""),
    ("r1c", "gap",
     "NEW: Polar Code &#167;11.3.4 wants prior-year statistics"
     f"<br>{SM}we hold 1,096 real daily files and use them only for training, "
     f"never as climatology the captain can see{E}", 750, 696, 300, 64, DASH),

    # row 2 — forecast
    ("r2a", "proc", "Fetch weather model's Sea-ice forecast", 70, 815, 300, 56, ""),
    ("r2n", "note", "CMEMS Sea-ice forecast", 70, 877, 300, 36, ""),
    ("r2b", "proc",
     "AI model corrects mistakes in the forecast"
     f"<br>{SM}residual U-Net &#183; corrected = clip(background + &#916;, 0, 1)"
     f"<br>zero-init head: a broken model degrades to CMEMS, not to zero{E}",
     410, 811, 300, 64, ""),
    ("r2c", "proc",
     "Add calibrated safety margin for vessel"
     f"<br>{SM}stratified conformal &#8594; SIC_upper, the number the router really uses{E}",
     750, 811, 300, 64, DASH),

    # row 3 — icebergs
    ("r3a", "proc", "Fetch current iceberg location near the course", 70, 930, 300, 56, ""),
    ("r3n", "note", "USNIC Current iceberg positions", 70, 992, 300, 36, ""),
    ("r3b", "proc",
     "Predict Iceberg trajectory"
     f"<br>{SM}Wagner closed form &#183; <b>physics, not machine learning</b> &#183; 23/23 tests"
     f"<br>&#8594; exclusion polygons{E}", 410, 926, 300, 64, ""),
    ("r3c", "gap",
     "USNIC tracks bergs &#8805; ~18.5 km"
     f"<br>{SM}a growler is ~5 m. That gap is 3.5 orders of magnitude and nothing in "
     f"orbit closes it &#8212; radar and the lookout own it{E}", 750, 926, 300, 64, ""),

    # row 4 — weather and seabed
    ("r4a", "proc", "Fetch Environment&nbsp; and Hazards lying ahead", 70, 1045, 300, 56, ""),
    ("r4n", "note", "ERA5/GFS wind + waves , GEBCO/IBCSO bathymetry", 70, 1107, 300, 36, ""),
    ("r4b", "proc",
     "Analyze weather forecast and hazards ahead"
     f"<br>{SM}wind sets the ice: free drift &#8776; 2% of wind speed, deflected "
     f"20&#8211;40&#176; <b>left</b> in the southern hemisphere{E}", 410, 1041, 300, 64, ""),
    ("r4c", "gap",
     "ERA5 under-reads the winds that beset ships"
     f"<br>{SM}bias &#8722;3.89 m/s above 20 m/s. Bias-correct with the ship's own "
     f"anemometer, or say so{E}", 750, 1041, 300, 64, DASH),

    # row 5 — protected areas  (NEW)
    ("r5a", "new", "NEW: Read protected and ecologically sensitive areas", 70, 1160, 300, 56, ""),
    ("r5n", "note", "CCAMLR MPAs, ASPA / ASMA, marine-mammal measures", 70, 1222, 300, 36, ""),
    ("r5b", "new",
     "Mark them as areas the route may not cross"
     f"<br>{SM}rides the same excluded_zones hook as the icebergs (ADR-010) &#8212; "
     f"the mechanism already exists{E}", 410, 1156, 300, 64, DASH),
    ("r5c", "gap",
     "Polar Code &#167;11.3.6&#8211;.8 requires this"
     f"<br>{SM}protected areas and marine-mammal measures are mandatory planning "
     f"factors. We currently consider neither{E}", 750, 1156, 300, 64, DASH),

    # row 6 — the ship itself  (NEW)
    ("r6a", "new", "NEW: Read the ship's own sensors", 70, 1275, 300, 56, ""),
    ("r6n", "note",
     "shaft power, speed log, X/S-band radar, AIS, met station, helicopter ice recon",
     70, 1337, 300, 44, ""),
    ("r6b", "new",
     "Correct our own models with what the ship actually measures"
     f"<br>{SM}shaft power is a <b>measured</b> ice resistance &#8212; the one number "
     f"our vessel config admits is borrowed from another hull{E}", 410, 1271, 300, 68, DASH),
    ("r6c", "gap",
     "Golovnin already flies ice reconnaissance"
     f"<br>{SM}she carries two helicopters used for ice air recon on the route. "
     f"That observation has no path into the system{E}", 750, 1271, 300, 68, DOT),

    # row 7 — pressure  (NEW, white space)
    ("r7a", "new", "NEW: Estimate ice pressure / compression risk", 70, 1390, 300, 56, DOT),
    ("r7n", "note", "modelled drift field &#8594; divergence &#8706;u/&#8706;x + &#8706;v/&#8706;y",
     70, 1452, 300, 36, ""),
    ("r7b", "new",
     "Flag convergence setting into the fast-ice edge"
     f"<br>{SM}the documented besetting geometry &#8212; and exactly where the ship sits "
     f"to offload at Bharati and Maitri{E}", 410, 1386, 300, 64, DOT),
    ("r7c", "gap",
     "No operational Antarctic pressure product exists, anywhere"
     f"<br>{SM}POLARIS never uses the words pressure, compression, ridge or drift. "
     f"This is white space, not an oversight{E}", 750, 1386, 300, 64, DOT),

    # --- BAND D: the routing engine -------------------------------------
    ("mesh", "proc", "build vessel modelled ice mesh", 500, 1520, 600, 56, ""),
    ("tmesh", "tag", "meshiphi", 1140, 1528, 130, 40, ""),
    ("nmesh", "note",
     "non-uniform: splits hardest where the ice is most variable. Calibrated to "
     "MV Vasiliy Golovnin &#8212; beam 22.4 m, 16.4 kn",
     190, 1516, 280, 64, ""),
    ("router", "proc", "Compute candidate routes", 500, 1616, 600, 56, ""),
    ("trouter", "tag", "PolarRoute", 1140, 1624, 130, 40, ""),
    ("ntime", "new",
     "NEW: one mesh layer per forecast day"
     f"<br>{SM}today the router plans a 17-day voyage on day-0 ice, as if the field "
     f"holds still. It does not{E}", 1300, 1608, 300, 72, DASH),

    # --- BAND E: safety screen ------------------------------------------
    ("polaris", "dec",
     "Is course's POLARIS ice concentration safe"
     f"<br>{SM}TODAY: a flat 80% cutoff. POLARIS is indexed by ice <b>type</b>, "
     f"so real compliance needs a thickness channel first{E}",
     620, 1720, 340, 130, ""),
    ("recarto", "proc", "Advise Captain to recartograph a new route", 1080, 1755, 300, 60, ""),
    ("aOut", "conn", "A", 1212, 1840, 36, 36, ""),
    ("hold", "new",
     "NEW: if no candidate ever passes &#8212; hold at the ice edge and wait"
     f"<br>{SM}the real answer at sea, and what Aurora Australis did at Mawson in 2014. "
     f"An endless redraw loop is not an outcome{E}", 100, 1745, 380, 80, DASH),
    ("annot", "new",
     "NEW: attach the hazards we cannot hard-gate on"
     f"<br>{SM}pressure risk &#183; protected-area proximity &#183; "
     f"<b>when the lookout will be blind</b>: sea state &gt; 4 ft hides growlers, "
     f"blizzard visibility &#8804; 100 m{E}", 590, 1890, 400, 80, DASH),

    # --- BAND F: the two modes ------------------------------------------
    ("mode", "dec",
     "NEW: is this the departure decision, or are we already underway?"
     f"<br>{SM}the captain's own instruction: argue once, then support{E}",
     620, 2015, 340, 130, DASH),

    ("tau", "dec",
     "Is new route better enough to suggest it?"
     f"<br>{SM}Cost(current) &#8722; Cost(alt) &gt; &#964;, where &#964; is our own "
     f"calibrated interval &#8212; not a hand-tuned number{E}",
     180, 2190, 340, 130, DASH),
    ("draw", "proc", "Draw recommended route and two backups for captain", 30, 2370, 300, 60, ""),
    ("keeporig", "proc", "Keep the captains original route", 380, 2370, 300, 60, ""),
    ("picks", "new",
     "NEW: the captain picks. His choice becomes THE route."
     f"<br>{SM}from here we never re-argue it{E}", 180, 2460, 340, 64, DASH),

    ("micro", "new",
     "NEW: do not re-open the strategic choice. Suggest micro changes, and the "
     "things he can miss."
     f"<br>{SM}a system that keeps arguing for a route the captain already rejected "
     f"is a system that gets switched off{E}", 1060, 2190, 380, 96, DASH),

    # --- BAND G: how it is said, and who to call ------------------------
    ("advisory", "new",
     "NEW: write it in ice-navigator language, and show the calculation"
     f"<br>{SM}9/10 close pack, thick first-year, ridged &#8212; not "
     f"&quot;lots of ice&quot;. WMO egg code: concentration, stage of development, "
     f"floe size{E}", 590, 2560, 400, 84, DASH),
    ("rescue", "new",
     "NEW: if trouble is foreseen &#8212; nearest icebreaker, station and MRCC for this sector"
     f"<br>{SM}Polar Code &#167;11.3.5 and &#167;11.3.9: places of refuge, and distance "
     f"from SAR. Static data, zero bandwidth{E}", 1060, 2556, 380, 92, DASH),
    ("end", "term", "End", 700, 2690, 180, 40, ""),
]

E_O = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;"
E_N = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=3 3;"
       "endArrow=none;strokeColor=#82b366;")
E_G = E_O + "dashed=1;dashPattern=3 3;strokeColor=#999999;endArrow=none;"

# source, target, label, extra
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
    ("rung", "r1a", "", ""),
    ("rung", "r2a", "", ""),
    ("rung", "r3a", "", ""),
    ("rung", "r4a", "", ""),
    ("rung", "r5a", "", ""),
    ("rung", "r6a", "", ""),
    ("rung", "r7a", "", ""),
    ("r1n", "r1a", "", E_N), ("r1a", "r1b", "", ""), ("r1c", "r1b", "", E_G),
    ("r2n", "r2a", "", E_N), ("r2a", "r2b", "", ""), ("r2b", "r2c", "", ""),
    ("r3n", "r3a", "", E_N), ("r3a", "r3b", "", ""), ("r3c", "r3b", "", E_G),
    ("r4n", "r4a", "", E_N), ("r4a", "r4b", "", ""), ("r4c", "r4b", "", E_G),
    ("r5n", "r5a", "", E_N), ("r5a", "r5b", "", ""), ("r5c", "r5b", "", E_G),
    ("r6n", "r6a", "", E_N), ("r6a", "r6b", "", ""), ("r6c", "r6b", "", E_G),
    ("r7n", "r7a", "", E_N), ("r7a", "r7b", "", ""), ("r7c", "r7b", "", E_G),
    ("r1b", "mesh", "", ""), ("r2c", "mesh", "", ""), ("r3b", "mesh", "", ""),
    ("r4b", "mesh", "", ""), ("r5b", "mesh", "", ""), ("r6b", "mesh", "", ""),
    ("r7b", "mesh", "", ""),
    ("nmesh", "mesh", "", E_N), ("tmesh", "mesh", "", E_N + "strokeColor=#9673a6;"),
    ("mesh", "router", "", ""),
    ("trouter", "router", "", E_N + "strokeColor=#9673a6;"),
    ("ntime", "router", "", E_N + "strokeColor=#6c8ebf;"),
    ("router", "polaris", "", ""),
    ("polaris", "recarto", "NO", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    ("recarto", "aOut", "", ""),
    ("recarto", "hold", "repeatedly", E_O + "dashed=1;strokeColor=#6c8ebf;"),
    ("polaris", "annot", "YES", "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    ("annot", "mode", "", ""),
    ("mode", "tau", "DEPARTURE&nbsp;&#8212; argue once",
     "exitX=0;exitY=0.5;entryX=0.5;entryY=0;"),
    ("mode", "micro", "UNDERWAY&nbsp;&#8212; support",
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

# ---------------------------------------------------------------- page 2 ----
P2 = [
    ("t2", "band",
     "WHERE EACH STEP RUNS. The split is not ours: the Canadian Coast Guard's ice "
     "navigation manual already separates a STRATEGIC phase ashore from a TACTICAL "
     "phase on the bridge, and leaves the routing recommendation with the shore ice "
     "desk while the bridge keeps real-time deviation authority.",
     40, 20, 1560, 66, ""),

    ("ashore", "band",
     "ASHORE &#8212; bandwidth, archives and GPUs live here",
     40, 110, 1560, 470, "fillColor=#F3F7FB;strokeColor=#6c8ebf;dashed=0;"),
    ("s1", "note", "NSIDC daily ice concentration", 70, 165, 235, 50, ""),
    ("s2", "note", "CMEMS sea-ice forecast", 320, 165, 235, 50, ""),
    ("s3", "note", "USNIC iceberg positions", 570, 165, 235, 50, ""),
    ("s4", "note", "ERA5 / GFS wind and waves", 820, 165, 235, 50, ""),
    ("s5", "note", "CCAMLR MPA + ASPA / ASMA<br>(static, ships once)", 1070, 165, 235, 50, ""),
    ("s6", "note", "IBCSO / GEBCO bathymetry<br>(static, ships once)", 1320, 165, 250, 50, ""),

    ("p1", "proc", "Quality control<br>isih/ice_quality.py", 70, 265, 285, 60, ""),
    ("p2", "proc", "Train the U-Net<br>(GPU &#8212; never at sea)", 385, 265, 285, 60, ""),
    ("p3", "proc", "Inference + conformal<br>&#8594; SIC_upper", 700, 265, 285, 60, DASH),
    ("p4", "proc", "Build the vessel mesh<br>meshiphi", 1015, 265, 285, 60, ""),
    ("p5", "new", "Fulfil imagery<br>requests from the ship", 1330, 265, 240, 60, DASH),

    ("pack", "new", "Build and sign the voyage pack", 500, 385, 600, 60, DASH),
    ("wts", "gap",
     "Model weights ~60 MB"
     f"<br>{SM}never over the satellite link &#8212; USB stick at port{E}",
     70, 385, 380, 60, ""),
    ("nharvest", "note", "the CMEMS harvest already runs daily on GitHub Actions",
     1150, 390, 420, 50, ""),

    ("link", "band",
     "ACROSS THE LINK &#8212; Iridium-class, ~704 kbps at best and usually far less. "
     "No geostationary VSAT reaches south of ~70&#176;S.",
     40, 615, 1560, 200, "fillColor=#FFF6E8;strokeColor=#d79b00;dashed=0;"),
    ("down", "proc",
     "&#8595;&nbsp; DOWN to the ship"
     f"<br>{SM}vessel-modelled mesh block <b>76 KB gzipped (measured)</b> &#183; "
     f"daily delta target 50 KB &#183; full corridor refresh 0.5&#8211;1 MB (extrapolated, "
     f"not yet measured){E}", 70, 670, 480, 76, ""),
    ("up", "new",
     "&#8593;&nbsp; UP from the ship"
     f"<br>{SM}route polyline <b>796 B</b> &#183; a request for tactical imagery is a few "
     f"bytes &#8212; the <i>image</i> is what we cannot afford &#183; sensor summary{E}",
     580, 670, 480, 76, DASH),
    ("never", "gap",
     "&#10007;&nbsp; NEVER crosses"
     f"<br>{SM}60 MB model weights &#183; raw NetCDF &#183; any live API call. "
     f"If a feature needs the internet at 70&#176;S, it is not a feature{E}",
     1090, 670, 480, 76, ""),

    ("aboard", "band",
     "ABOARD &#8212; everything that has to answer a question",
     40, 850, 1560, 320, "fillColor=#F4FAF4;strokeColor=#82b366;dashed=0;"),
    ("v1", "proc", "The voyage pack, on disk", 90, 905, 300, 56, ""),
    ("v2", "new", "The ship's own sensors<br>radar, AIS, shaft power, met, helicopter recon",
     430, 905, 320, 56, DASH),
    ("v3", "proc", "PolarRoute &#8212; routes are computed here, locally", 790, 905, 340, 56, ""),
    ("v4", "note", "so the master can re-plan with no link at all", 1170, 908, 350, 50, ""),
    ("v5", "proc", "The decision flow on page 1", 350, 1010, 400, 56, ""),
    ("v6", "term", "The Captain decides", 830, 1010, 300, 56, ""),
    ("v7", "gap",
     "why not send finished routes only?"
     f"<br>{SM}because then the master cannot re-plan when the ice disagrees with "
     f"the forecast &#8212; and it will{E}", 90, 1090, 500, 62, ""),
    ("v8", "gap",
     "why not run ingestion aboard?"
     f"<br>{SM}GB-scale downloads and a GPU. Neither exists at 70&#176;S{E}",
     640, 1090, 490, 62, ""),
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
    # the three rationale panels are commentary, so they attach with a plain
    # line and no arrowhead — but they do attach, so nothing floats
    ("pack", "never", "excluded from the pack", E_G),
    ("v7", "v3", "", E_G),
    ("v8", "v1", "", E_G),
    ("v6", "up", "his route, and what he asked for", E_O + "dashed=1;strokeColor=#6c8ebf;"),
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


x1, ids1 = page("Decision workflow", "navflow", P1, X1, 1680, 2800, "a")
x2, ids2 = page("Where it runs", "tiers", P2, X2, 1680, 1240, "b")

xml = '<mxfile host="app.diagrams.net" type="device">\n' + x1 + x2 + '</mxfile>\n'
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(xml)

print(f"wrote {OUT}")
print(f"  page 1: {len(P1)} shapes, {len(X1)} connectors")
print(f"  page 2: {len(P2)} shapes, {len(X2)} connectors")
print(f"  {len(xml)} bytes total")
