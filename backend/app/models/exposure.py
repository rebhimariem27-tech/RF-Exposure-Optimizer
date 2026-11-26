from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.tissues import TissueGrid, TissueLayer, build_tissue_grid


EPSILON_0_F_M = 8.8541878128e-12
MU_0_H_M = 1.25663706212e-6
ETA_0_OHM = float(np.sqrt(MU_0_H_M / EPSILON_0_F_M))


@dataclass(frozen=True)
class ExposureResult:
    z_m: np.ndarray
    field_rms_v_m: np.ndarray
    sar_profile_w_kg: np.ndarray
    sar10g_column_proxy_w_kg: float
    max_local_sar_w_kg: float
    grid: TissueGrid


def _layer_intrinsic_impedance_and_attenuation(
    frequency_hz: float,
    layer: TissueLayer,
) -> tuple[complex, float]:
    omega = 2.0 * np.pi * frequency_hz
    eps_complex = layer.epsilon_r - 1j * layer.conductivity_s_m / (omega * EPSILON_0_F_M)
    refractive_index = np.sqrt(eps_complex)
    eta = ETA_0_OHM / refractive_index
    propagation_constant = 1j * omega * np.sqrt(MU_0_H_M * EPSILON_0_F_M * eps_complex)
    alpha_np_m = max(float(np.real(propagation_constant)), 0.0)
    return complex(eta), alpha_np_m


def _single_pass_10g_column_average(
    sar_profile_w_kg: np.ndarray,
    grid: TissueGrid,
    target_mass_kg: float = 0.010,
) -> float:
    """Return a 10-g mass-weighted 1-D column proxy, not a compliance SAR10g.

    The assumed cross-section equals the base of a 10-g cube of 1000 kg/m^3.
    A 1-D model cannot perform the required 3-D cubic spatial averaging.
    """
    reference_density = 1000.0
    cube_side_m = (target_mass_kg / reference_density) ** (1.0 / 3.0)
    cross_section_m2 = cube_side_m**2
    cell_masses = grid.density_kg_m3 * grid.dz_m * cross_section_m2

    best_average = None
    n_cells = len(sar_profile_w_kg)
    for start in range(n_cells):
        remaining = target_mass_kg
        absorbed_power_w = 0.0
        collected_mass_kg = 0.0

        for idx in range(start, n_cells):
            mass_to_take = min(remaining, cell_masses[idx])
            absorbed_power_w += sar_profile_w_kg[idx] * mass_to_take
            collected_mass_kg += mass_to_take
            remaining -= mass_to_take
            if remaining <= 1e-12:
                break

        if collected_mass_kg >= target_mass_kg - 1e-12:
            average = absorbed_power_w / target_mass_kg
            best_average = average if best_average is None else max(best_average, average)

    if best_average is None:
        raise ValueError(
            "The tissue column is too small to contain the selected 10-g mass. "
            "Increase the modeled tissue depth or revise the phantom geometry."
        )
    return float(best_average)


def calculate_sar_profile_1d(
    incident_field_rms_v_m: float,
    frequency_hz: float,
    layers: list[TissueLayer],
    target_cell_size_m: float = 5e-4,
) -> ExposureResult:
    """Estimate a normal-incidence, single-pass 1-D SAR profile.

    Interface transmission is included, but multiple internal reflections,
    oblique incidence, 3-D anatomy, antenna near fields, and transverse field
    variations are not. E is RMS, so SAR = sigma * E_rms^2 / density.
    """
    if not np.isfinite(incident_field_rms_v_m) or incident_field_rms_v_m < 0:
        raise ValueError("incident_field_rms_v_m must be finite and non-negative")
    if not np.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive and finite")
    if not layers:
        raise ValueError("At least one tissue layer is required")

    grid = build_tissue_grid(layers, target_cell_size_m)
    field = np.zeros(grid.size, dtype=float)

    current_field = complex(incident_field_rms_v_m, 0.0)
    previous_impedance = complex(ETA_0_OHM, 0.0)
    z_start = 0.0

    for layer_idx, layer in enumerate(layers):
        eta_layer, alpha = _layer_intrinsic_impedance_and_attenuation(frequency_hz, layer)
        transmission_e = 2.0 * eta_layer / (previous_impedance + eta_layer)
        field_entering_layer = current_field * transmission_e

        cell_ids = np.flatnonzero(grid.layer_index == layer_idx)
        local_depth = grid.z_m[cell_ids] - z_start
        field[cell_ids] = np.abs(field_entering_layer) * np.exp(-alpha * local_depth)

        current_field = field_entering_layer * np.exp(-alpha * layer.thickness_m)
        previous_impedance = eta_layer
        z_start += layer.thickness_m

    sar = grid.conductivity_s_m * field**2 / grid.density_kg_m3
    sar = np.maximum(sar, 0.0)
    sar_proxy = _single_pass_10g_column_average(sar, grid)

    return ExposureResult(
        z_m=grid.z_m.copy(),
        field_rms_v_m=field,
        sar_profile_w_kg=sar,
        sar10g_column_proxy_w_kg=sar_proxy,
        max_local_sar_w_kg=float(np.max(sar)),
        grid=grid,
    )
