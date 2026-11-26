from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.models.tissues import TissueGrid


@dataclass(frozen=True)
class ThermalResult:
    delta_t_profile_k: np.ndarray
    delta_t_max_k: float
    time_step_s: float
    n_steps: int


def simulate_temperature_rise(
    grid: TissueGrid,
    sar_profile_w_kg: np.ndarray,
    duration_s: float,
    surface_heat_transfer_w_m2_k: float = 8.0,
    blood_density_kg_m3: float = 1060.0,
    blood_specific_heat_j_kg_k: float = 3617.0,
    requested_time_step_s: float | None = None,
) -> ThermalResult:
    """Solve a 1-D transient Pennes-style temperature-rise equation.

    Uses an explicit finite-volume scheme, convective skin boundary, and a
    fixed-temperature deep boundary. Perfusion is read from TissueGrid; the
    default phantom currently sets it to zero until tissue-specific values are
    supplied. The result is a preliminary model, not a medical/standards test.
    """
    sar = np.asarray(sar_profile_w_kg, dtype=float)
    if sar.shape != (grid.size,):
        raise ValueError("SAR profile size must match the tissue grid")
    if np.any(~np.isfinite(sar)) or np.any(sar < 0):
        raise ValueError("SAR values must be finite and non-negative")
    if not np.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("duration_s must be positive and finite")
    if surface_heat_transfer_w_m2_k < 0:
        raise ValueError("Surface heat transfer coefficient cannot be negative")

    rho = grid.density_kg_m3
    cp = grid.specific_heat_j_kg_k
    conductivity = grid.thermal_conductivity_w_m_k
    dz = grid.dz_m
    capacity_per_volume = rho * cp
    diffusivity = conductivity / capacity_per_volume

    alpha_max = float(np.max(diffusivity))
    min_dx = float(np.min(dz))
    stable_dt = 0.4 * min_dx**2 / (2.0 * alpha_max)

    if requested_time_step_s is not None:
        if not np.isfinite(requested_time_step_s) or requested_time_step_s <= 0:
            raise ValueError("requested_time_step_s must be positive")
        stable_dt = min(stable_dt, requested_time_step_s)

    n_steps = max(1, int(np.ceil(duration_s / stable_dt)))
    dt = duration_s / n_steps

    delta_t = np.zeros(grid.size, dtype=float)
    max_temperature_rise = 0.0
    source_w_m3 = rho * sar
    perfusion_sink = blood_density_kg_m3 * blood_specific_heat_j_kg_k * grid.perfusion_s_inv

    # Harmonic-mean thermal conductivity at each interface.
    k_face = 2.0 * conductivity[:-1] * conductivity[1:] / (
        conductivity[:-1] + conductivity[1:]
    )
    center_distance = 0.5 * (dz[:-1] + dz[1:])

    for _ in range(n_steps):
        flux_right = np.zeros(grid.size, dtype=float)
        flux_left = np.zeros(grid.size, dtype=float)

        if grid.size > 1:
            interface_flux = k_face * (delta_t[1:] - delta_t[:-1]) / center_distance
            flux_right[:-1] = interface_flux
            flux_left[1:] = interface_flux

        # Positive outward heat flux at the skin surface.
        flux_left[0] = surface_heat_transfer_w_m2_k * delta_t[0]
        conduction_w_m3 = (flux_right - flux_left) / dz

        rate_k_s = (
            conduction_w_m3 + source_w_m3 - perfusion_sink * delta_t
        ) / capacity_per_volume

        delta_t = delta_t + dt * rate_k_s

        # Approximate the deep brain boundary as a large core-temperature reservoir.
        delta_t[-1] = 0.0
        delta_t = np.maximum(delta_t, 0.0)
        max_temperature_rise = max(max_temperature_rise, float(np.max(delta_t)))

    return ThermalResult(
        delta_t_profile_k=delta_t,
        delta_t_max_k=max_temperature_rise,
        time_step_s=float(dt),
        n_steps=n_steps,
    )
