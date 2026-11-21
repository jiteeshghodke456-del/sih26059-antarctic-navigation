"""F4 checks: the melt terms behave the way the cited papers say they must."""
import numpy as np

from melt import (basal_melt_m_per_day, buoyant_convection_m_per_day,
                  freshwater_m3_per_day, wave_erosion_m_per_day)


def test_no_melt_in_freezing_still_water():
    assert basal_melt_m_per_day(0.0, -1.92, 30_000) == 0.0
    assert buoyant_convection_m_per_day(-1.92) == 0.0


def test_warmer_faster_rougher_melts_more():
    assert basal_melt_m_per_day(0.5, 2.0, 30_000) > basal_melt_m_per_day(0.5, 0.0, 30_000)
    assert basal_melt_m_per_day(1.0, 2.0, 30_000) > basal_melt_m_per_day(0.2, 2.0, 30_000)
    assert wave_erosion_m_per_day(4.0, 0.0) > wave_erosion_m_per_day(1.0, 0.0)


def test_magnitudes_are_literature_scale():
    # ~0 °C water, 0.2 m/s relative flow, 2 m seas: each term should sit in
    # the centimetres-to-decimetres per day range the papers report.
    mb = basal_melt_m_per_day(0.2, 0.5, 30_000)
    me = wave_erosion_m_per_day(2.0, 0.5)
    assert 0.0005 < mb < 0.5
    assert 0.01 < me < 2.0


def test_freshwater_positive_and_scales_with_size():
    small = freshwater_m3_per_day(5_000, 3_000, 0.2, 0.5, 2.0)
    big = freshwater_m3_per_day(50_000, 30_000, 0.2, 0.5, 2.0)
    assert 0 < small < big
