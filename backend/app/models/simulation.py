from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.exposure import calculate_sar_profile_1d
from app.models.membrane import MembraneRCProxyParameters, estimate_delta_vm_rc_proxy
from app.models.propagation import (
    calculate_link_metrics,
    far_field_electric_field_rms,
    fraunhofer_distance_m,
    ideal_array_gain_dbi,
)
from app.models.thermal import simulate_temperature_rise
from app.models.tissues import (
    TissueLayer,
    default_head_layers,
    validate_frequency_for_default_tissues,
)
from app.optimization.metrics import SimulationMetrics


@dataclass(frozen=True)
class SimulationParameters:
    """Configurable assumptions for the initial network simulation."""

    element_gain_dbi: float = 0.0
    array_efficiency: float = 0.70
    receiver_gain_dbi: float = 0.0
    noise_figure_db: float = 7.0
    receiver_temperature_k: float = 290.0
    interference_w: float = 0.0
    scheduler_efficiency: float = 0.75
    max_spectral_efficiency: float = 7.4

    pa_efficiency: float = 0.35
    rf_chain_power_w: float = 0.5
    baseband_power_w: float = 5.0
    n_rf_chains: int | None = None

    fixed_infrastructure_cost: float = 10000.0
    antenna_element_cost: float = 250.0
    rf_chain_cost: float = 500.0

    tissue_cell_size_m: float = 5e-4
    surface_heat_transfer_w_m2_k: float = 8.0
    membrane_proxy: MembraneRCProxyParameters = MembraneRCProxyParameters()


def simulate_network(
    design,
    scenario,
    parameters: SimulationParameters | None = None,
    tissue_layers: list[TissueLayer] | None = None,
) -> SimulationMetrics:
    """Run the current 1-D prototype for one candidate network design.

    `design` must expose tx_power_w and n_antennas.
    `scenario` must expose frequency_hz, distance_m, bandwidth_hz,
    and operation_duration_s. This matches the NetworkDesign and
    NetworkScenario dataclasses in app.optimization.problem.
    """
    params = parameters or SimulationParameters()

    tx_power_w = float(design.tx_power_w)
    n_antennas = int(design.n_antennas)
    frequency_hz = float(scenario.frequency_hz)
    distance_m = float(scenario.distance_m)
    bandwidth_hz = float(scenario.bandwidth_hz)
    duration_s = float(scenario.operation_duration_s)

    if not np.isfinite(tx_power_w) or tx_power_w <= 0:
        raise ValueError("Transmit power must be positive and finite")
    if n_antennas < 1:
        raise ValueError("At least one antenna is required")
    if not (100e6 <= frequency_hz <= 6e9):
        raise ValueError(
            "This prototype uses a SAR-based exposure model intended for "
            "100 MHz to 6 GHz. Above 6 GHz, an absorbed-power-density model is needed."
        )
    if distance_m <= 0 or bandwidth_hz <= 0 or duration_s <= 0:
        raise ValueError("Distance, bandwidth, and operation duration must be positive")
    if not (0 < params.pa_efficiency <= 1):
        raise ValueError("PA efficiency must be in (0, 1]")

    validate_frequency_for_default_tissues(frequency_hz)
    layers = tissue_layers if tissue_layers is not None else default_head_layers()

    tx_array_gain_dbi = ideal_array_gain_dbi(
        n_antennas=n_antennas,
        element_gain_dbi=params.element_gain_dbi,
        efficiency=params.array_efficiency,
    )

    # Far-field approximation: the caller should ensure distance >= Fraunhofer distance.
    # We return no fabricated near-field correction.
    required_far_field_distance_m = fraunhofer_distance_m(frequency_hz, n_antennas)
    if distance_m < required_far_field_distance_m:
        raise ValueError(
            f"The selected distance ({distance_m:.3g} m) is below the estimated "
            f"Fraunhofer distance ({required_far_field_distance_m:.3g} m). "
            "Use a near-field EM model or change the geometry."
        )

    incident_field = far_field_electric_field_rms(
        tx_power_w=tx_power_w,
        tx_gain_dbi=tx_array_gain_dbi,
        distance_m=distance_m,
    )

    exposure = calculate_sar_profile_1d(
        incident_field_rms_v_m=incident_field,
        frequency_hz=frequency_hz,
        layers=layers,
        target_cell_size_m=params.tissue_cell_size_m,
    )

    thermal = simulate_temperature_rise(
        grid=exposure.grid,
        sar_profile_w_kg=exposure.sar_profile_w_kg,
        duration_s=duration_s,
        surface_heat_transfer_w_m2_k=params.surface_heat_transfer_w_m2_k,
    )

    link = calculate_link_metrics(
        tx_power_w=tx_power_w,
        frequency_hz=frequency_hz,
        distance_m=distance_m,
        bandwidth_hz=bandwidth_hz,
        tx_gain_dbi=tx_array_gain_dbi,
        rx_gain_dbi=params.receiver_gain_dbi,
        noise_figure_db=params.noise_figure_db,
        temperature_k=params.receiver_temperature_k,
        interference_w=params.interference_w,
        scheduler_efficiency=params.scheduler_efficiency,
        max_spectral_efficiency=params.max_spectral_efficiency,
    )

    n_rf_chains = params.n_rf_chains if params.n_rf_chains is not None else n_antennas
    if n_rf_chains < 1 or n_rf_chains > n_antennas:
        raise ValueError("n_rf_chains must be between 1 and n_antennas")

    dc_power_w = (
        tx_power_w / params.pa_efficiency
        + n_rf_chains * params.rf_chain_power_w
        + params.baseband_power_w
    )
    energy_j = dc_power_w * duration_s

    infrastructure_cost = (
        params.fixed_infrastructure_cost
        + n_antennas * params.antenna_element_cost
        + n_rf_chains * params.rf_chain_cost
    )

    delta_vm_proxy = estimate_delta_vm_rc_proxy(
        incident_field_rms_v_m=incident_field,
        frequency_hz=frequency_hz,
        parameters=params.membrane_proxy,
    )

    return SimulationMetrics(
        sar10g_w_kg=exposure.sar10g_column_proxy_w_kg,
        delta_t_max_k=thermal.delta_t_max_k,
        delta_vm_abs_v=delta_vm_proxy,
        energy_consumption_j=energy_j,
        bitrate_mbps=link["bitrate_mbps"],
        infrastructure_cost=infrastructure_cost,
        sinr_db=link["sinr_db"],
    )
