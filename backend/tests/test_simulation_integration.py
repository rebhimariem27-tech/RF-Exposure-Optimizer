
from types import SimpleNamespace
import numpy as np

from app.models.simulation import simulate_network
from app.optimization.metrics import SimulationMetrics


def test_reference_network_simulation():

    design = SimpleNamespace(
        tx_power_w=21.0,
        n_antennas=8
    )

    scenario = SimpleNamespace(
        frequency_hz=2.5e9,
        distance_m=50.0,
        bandwidth_hz=100e6,
        operation_duration_s=360.0
    )

    metrics = simulate_network(design, scenario)

    assert isinstance(metrics, SimulationMetrics)

    values = [
        metrics.sar10g_w_kg,
        metrics.delta_t_max_k,
        metrics.delta_vm_abs_v,
        metrics.energy_consumption_j,
        metrics.bitrate_mbps,
        metrics.infrastructure_cost,
        metrics.sinr_db
    ]

    assert all(np.isfinite(value) for value in values)

    assert metrics.sar10g_w_kg >= 0
    assert metrics.delta_t_max_k >= 0
    assert metrics.delta_vm_abs_v >= 0
    assert metrics.energy_consumption_j > 0
    assert metrics.bitrate_mbps > 0
    assert metrics.infrastructure_cost > 0
