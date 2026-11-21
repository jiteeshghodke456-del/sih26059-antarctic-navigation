"""F2 checks: alias resolution, surface slicing, fill handling, and the
regridder accepting NEMO's curvilinear 2-D coordinates. Synthetic files in
the documented NEMO layout — the reader is marked untested on real output."""
import numpy as np
import pytest
import xarray as xr

from readers.nemo import NemoReader


def _nemo_files(tmp_path, style="classic"):
    y, x = 8, 10
    lon2d, lat2d = np.meshgrid(np.linspace(10, 30, x), np.linspace(-70, -60, y))
    coords = {"nav_lon": (("y", "x"), lon2d), "nav_lat": (("y", "x"), lat2d)}
    names = {"classic": ("ileadfra", "vozocrtx", "vomecrty", "votemper"),
             "cmip": ("siconc", "uo", "vo", "thetao")}[style]
    ice = np.random.default_rng(1).uniform(0, 1, (1, y, x))
    ice[0, 0, 0] = 1e20  # NEMO fill value on a land point
    t_file = tmp_path / "grid_T.nc"
    xr.Dataset({names[0]: (("time_counter", "y", "x"), ice),
                names[3]: (("time_counter", "deptht", "y", "x"),
                           np.full((1, 3, y, x), 271.5))},
               coords=coords).to_netcdf(t_file)
    u_file = tmp_path / "grid_U.nc"
    xr.Dataset({names[1]: (("time_counter", "depthu", "y", "x"),
                           np.full((1, 3, y, x), 0.1))},
               coords=coords).to_netcdf(u_file)
    v_file = tmp_path / "grid_V.nc"
    xr.Dataset({names[2]: (("time_counter", "depthv", "y", "x"),
                           np.full((1, 3, y, x), -0.05))},
               coords=coords).to_netcdf(v_file)
    return t_file, u_file, v_file


@pytest.mark.parametrize("style", ["classic", "cmip"])
def test_reads_both_naming_generations(tmp_path, style):
    r = NemoReader(*_nemo_files(tmp_path, style))
    assert r.lon.shape == (8, 10) and r.lat.shape == (8, 10)
    ice = r.field("ice_concentration")
    assert ice.shape == (8, 10)
    assert np.isnan(ice[0, 0])            # fill value -> NaN
    assert np.nanmax(ice) <= 1.0
    assert r.field("u_current").shape == (8, 10)   # top level of 3
    assert float(r.field("v_current")[3, 3]) == pytest.approx(-0.05)
    avail = r.available()
    assert avail["ice_concentration"] and not avail["ice_thickness"]


def test_unknown_layout_fails_loudly(tmp_path):
    p = tmp_path / "odd.nc"
    xr.Dataset({"mystery": (("y", "x"), np.zeros((2, 2)))},
               coords={"nav_lon": (("y", "x"), np.zeros((2, 2))),
                       "nav_lat": (("y", "x"), np.zeros((2, 2)))}).to_netcdf(p)
    r = NemoReader(p)
    with pytest.raises(KeyError, match="mystery"):
        r.field("ice_concentration")


def test_regridder_accepts_curvilinear_coords(tmp_path):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from grid import GlorysToNsidcRegridder

    r = NemoReader(*_nemo_files(tmp_path))
    nrt = sorted((Path(__file__).resolve().parent.parent.parent
                  / "data" / "nsidc_nrt").glob("*.nc"))
    if not nrt:
        pytest.skip("no NSIDC file on disk for the target grid")
    template = xr.open_dataset(nrt[0])
    rg = GlorysToNsidcRegridder(template, r.lat, r.lon)
    out = rg(r.field("u_current"))
    assert out.shape == (template.sizes["y"], template.sizes["x"])
    assert np.nanmax(np.abs(out)) <= 0.1 + 1e-6
