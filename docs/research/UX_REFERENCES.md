# UX references, and the OpenCPN reuse determination

§2.1 names five references and asks for a specific decision:

> "Investigate OpenCPN… Determine whether its GUI, map rendering approach,
> route display methods, or related open-source implementation patterns can be
> used as inspiration or **reused where legally/technically appropriate** for
> this Antarctic application."

That determination had never been made. It is made here.

---

## 1. OpenCPN — the reuse determination

**Licence, from the source rather than the badge.** GitHub auto-detects
"GPL-2.0", which is imprecise. OpenCPN's own `LICENSING` file states the code
is "distributed using a GPLv2+ license", and the machine-readable
`data/copyright` manifest gives `License: GPL-2+` for the catch-all `Files: *`
entry. **GPL-2-or-later**, not GPL-2-only — and that matters, because the
"or-later" is what lets OpenCPN's core combine legally with the GPL-3+ and
LGPL-3+ components it also bundles, alongside BSD, MIT, zlib, Apache-2.0 and
ODbL-licensed OpenStreetMap basemap shapefiles.

**No plugin escape hatch.** OpenCPN's developer manual is unambiguous:
*"Plugins must be distributed under the license terms of GPL V2 or later."*
There is no linking exception of the kind some GPL projects offer.

**What each route would cost us:**

| Route | Obligation |
|---|---|
| Design inspiration — layout, the idea of a status strip | **None.** Copyright protects the expression, not the functional arrangement |
| Copying source into our tree | The combined work becomes GPL-2-or-later on distribution; source must be offered to recipients |
| Via the plugin API | Same — explicitly, per their manual |
| Reimplementing a documented behaviour from scratch | **None.** This is the legitimate route |

**Technically it is moot anyway.** OpenCPN is a monolithic C++/wxWidgets
desktop application targeting installed binaries. There is no browser target
and no WebAssembly build. None of its rendering code could run in our
Python/FastAPI + vanilla-JS stack, so the technical fit rules out code reuse
before the licence even arrives.

> **Verdict: design inspiration only. Do not reuse OpenCPN code.**
> Licence and technical fit reach the same conclusion independently, which is
> what makes this a clean call rather than a close one.

**The legitimate path to the same familiarity is the standards themselves:**

- **GDAL is MIT-licensed** and is the mainstream, licence-clean way to read
  S-57 today, entirely independent of OpenCPN. (OpenCPN's own S-57 handling
  descends from GDAL/OGR.)
- **AIS (ITU-R M.1371)** — ITU-R Recommendations are freely downloadable.
- **NMEA 0183** — the document is sold, but the wire sentences have been
  public for decades with a large legal open-source parsing ecosystem.
- **IHO publications are copyrighted.** Implementing S-52/S-57 is normal and
  common; reproducing IHO's text is not.
- **S-63 is categorically different** — an encryption scheme and RENC
  *membership* relationship for distributing licensed ENC data, not a format.
  Do not conflate it with S-57/S-52.

### What we took

- **OpenCPN's chart-confidence / data-quality bar.** It sits bottom-left
  beside the scale bar and tells the operator how far to trust what they are
  looking at. That maps directly onto our own documented sea-ice retrieval
  error sources — coastal contamination, thin-ice under-read — and is the
  single most transferable idea of the five references.
- **Its minimal-toolbar philosophy**: *"Those and only those toolbar buttons
  really needed for daily operation."*
- **Polarstern MapViewer's habit** of bundling coastline, maritime boundaries
  and bathymetry as *default* reference layers rather than optional extras —
  which is precisely what our chart was missing.
- **Its treatment of the Antarctic Circle** as its own labelled line rather
  than one graticule parallel among many. Implemented.
- **Degrees-and-minutes coordinates**, which both Polarstern's and Nuyina's
  own screenshots use rather than decimal degrees. Implemented.

### What we deliberately did not take

- **Laura Bassi's rainbow/"jet" ice ramp** (verified from the legend PNG its
  dashboard serves): perceptually non-uniform, implies false hard bands, not
  colourblind-safe. Our sequential blue ramp is the better choice and stays.
- **OpenCPN's symbol density** — soundings scattered across every water area
  is right for a professional ECDIS operator on a bridge monitor, wrong for a
  glanceable decision-support display.
- **Nuyina's blank background.** The published screenshot showing a flat sea
  with no coastline is a *mid-ocean turning-circle test off West Africa at
  ~29°S* — nowhere near ice or coast. Generalising it would have reproduced
  the exact "no coastline, no landmass" problem §2.2 asks us to fix.

---

## 2. The five references, honestly characterised

| Reference | What it is | Transferable decision |
|---|---|---|
| **Polarstern MapViewer** (AWI) | Browser tool aboard RV Polarstern. Many *independently selectable* layers — MODIS, Sentinel-1 SAR, onboard Sigma S6 ice radar, AMSR2, 9-day drift forecast — over OSM coastlines, Marine Regions boundaries and AWI bathymetry. Supports WGS84, EPSG:3995 and **EPSG:3031** | Layer independence; reference layers by default; ice drift as small hook glyphs at grid points, not animated particles |
| **R/V Laura Bassi** (OGS) | Public near-real-time dashboard. **Hybrid regional coastline**: NGA for Antarctica, LINZ for New Zealand, OSM elsewhere | The hybrid sourcing pattern — which is exactly what we adopted |
| **RSV Nuyina** (AAD) | Onboard system "D.i.R.T."; the public pages are static dated log entries, **not** a live map (verified by inspecting the page source — no map library, no map container) | Degrees-minutes-seconds edge labels. Little else; see above |
| **IcySea** (Drift+Noise) | AWI spin-off, ~7 staff, co-developed with the Norwegian Met Institute. Iridium-tested, near-real-time within ~1 h of satellite recording, offline browser cache, click-a-point-to-forecast-drift | The click-to-forecast interaction; stating data age prominently |
| **OpenCPN** | Community ECDIS-style chart plotter, C++/wxWidgets | See §1 |

**Two caveats worth recording rather than hiding:**

1. **Polarstern and Nuyina are both IcySea customers.** Three of the five
   references are therefore not independent, and "look at Polarstern" and
   "look at IcySea" are partly the same instruction.
2. §2.1 cites IcySea specifically for **iceberg movement visualisation**, and
   no source could be found describing its iceberg symbology as distinct from
   its general ice-drift symbology. The one thing the reference was named for
   could not be verified.

---

## 3. What changed in the chart

§2.2 asks for "very accurate maps". Before this, the chart had no coastline,
no land, no graticule — it read as a scatter plot of ice cells — and its
geometry was wrong.

| Change | Detail |
|---|---|
| **Projection** | Was a linear lat/lon stretch, which draws every latitude at the same horizontal scale: measured, a degree of longitude came out **2.92× too wide at Bharati (69.4°S)**, and Bharati was drawn at the same scale as Cape Town though a degree there is 0.42× the length. Now **Mercator** — conformal, and a rhumb line is straight, which is the habit passage planning is built on |
| **Frame** | The container was hardcoded to 3:2 against a 1.625:1 extent, squashing the picture a second time. The aspect is now **derived from the projection** (0.9565) and cannot disagree with it |
| **Coastline** | Natural Earth 1:50m, **public domain**, clipped to the corridor and RDP-simplified to a **21 KB committed extract** — the same build-time pattern as `protected_areas.py`, so the running app still has zero geospatial dependencies |
| **Graticule** | Every 10°, with the **Antarctic Circle** drawn and named separately |
| **Sea** | The ramp's zero stop is the sea colour exactly, so a cell measuring 0% ice reads as open water instead of tiling the ocean with pale squares. Nothing is hidden — 0% *is* open water |
| **Ice cells** | Sized from the projection, with a nominal 1.35× factor because the CDR grid is polar stereographic and its samples are not a regular lat/lon lattice; drawn true-size they leave gaps that read as missing data |

**Filed, not done:** the BAS **Antarctic Digital Database** (CC BY 4.0, native
EPSG:3031) separates ice-coastline, rock-coastline, grounding-line and
ice-shelf-front — distinctions that are operationally real at Bharati and that
Natural Earth does not carry. And a **polar-stereographic chart mode** for the
southern leg: the corridor spans 30°S to 70°S, two cartographic regimes, and no
single projection is correct for both ends. Real voyage planning already
separates an ocean passage chart from an ice chart; so should this.
