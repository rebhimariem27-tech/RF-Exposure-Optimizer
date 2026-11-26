from types import SimpleNamespace

import numpy as np
import pytest

from app.models.exposure import calculate_sar_profile_1d
from app.models.propagation import calculate_link_metrics, far_field_electric_field_rms
from app.models.simulation import simulate_network
from app.models.thermal import simulate_temperature_rise
from app.models.tissues import build_tissue_grid, default_head_layers


def test_tissue_grid_is_consistent():
    grid = build_tissue_grid(default_head_layers(), target_cell_size_m=1e-3)
    assert grid.size > 0
    assert len(grid.z_m) == len(grid.density_kg_m3)
    assert np.all(grid.dz_m > 0)


def test_sar_scales_with_square_of_incident_field():
    layers = default_head_layers()
    one = calculate_sar_profile_1d(1.0, 2.45e9, layers, 1e-3)
    two = calculate_sar_profile_1d(2.0, 2.45e9, layers, 1e-3)
    assert np.all(two.sar_profile_w_kg >= one.sar_profile_w_kg)
    assert two.max_local_sar_w_kg == pytest.approx(4 * one.max_local_sar_w_kg)


def test_thermal_rise_is_nonnegative_and_increases_with_sar():
    grid = build_tissue_grid(default_head_layers(), target_cell_size_m=1e-3)
    low = simulate_temperature_rise(grid, np.full(grid.size, 0.01), 10.0)
    high = simulate_temperature_rise(grid, np.full(grid.size, 0.02), 10.0)
    assert low.delta_t_max_k > 0
    assert high.delta_t_max_k >= low.delta_t_max_k


def test_link_bitrate_increases_with_transmit_power():
    common = dict(
        frequency_hz=2.5e9,
        distance_m=50.0,
        bandwidth_hz=100e6,
        tx_gain_dbi=8.0,
    )
    low = calculate_link_metrics(tx_power_w=1.0, **common)
    high = calculate_link_metrics(tx_power_w=2.0, **common)
    assert high["sinr_db"] > low["sinr_db"]
    assert high["bitrate_mbps"] >= low["bitrate_mbps"]


def test_free_space_field_is_finite():
    field = far_field_electric_field_rms(21.0, 8.0, 50.0)
    assert np.isfinite(field) and field > 0


def test_integrated_simulator_returns_metrics():
    design = SimpleNamespace(tx_power_w=21.0, n_antennas=8)
    scenario = SimpleNamespace(
        frequency_hz=2.5e9,
        distance_m=50.0,
        bandwidth_hz=100e6,
        operation_duration_s=60.0,
    )
    metrics = simulate_network(design, scenario)
    assert metrics.sar10g_w_kg >= 0
    assert metrics.delta_t_max_k >= 0
    assert metrics.delta_vm_abs_v >= 0
    assert metrics.energy_consumption_j > 0
    assert metrics.bitrate_mbps > 0
    assert metrics.infrastructure_cost > 0
    assert np.isfinite(metrics.sinr_db)
