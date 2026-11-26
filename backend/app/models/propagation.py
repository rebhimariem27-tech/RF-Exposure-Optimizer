from __future__ import annotations

import numpy as np


C0_M_S = 299_792_458.0
BOLTZMANN_J_K = 1.380649e-23


def db_to_linear(value_db: float) -> float:
    return float(10.0 ** (value_db / 10.0))


def wavelength_m(frequency_hz: float) -> float:
    if not np.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive and finite")
    return C0_M_S / frequency_hz


def ideal_array_gain_dbi(
    n_antennas: int,
    element_gain_dbi: float = 0.0,
    efficiency: float = 0.70,
) -> float:
    """Ideal broadside array-gain approximation at fixed total RF power.

    Assumes coherent phase alignment, equal power allocation, identical
    elements, and no mutual-coupling/scan/pattern losses beyond `efficiency`.
    It is not a substitute for the measured or simulated antenna pattern.
    """
    if isinstance(n_antennas, bool) or int(n_antennas) != n_antennas or n_antennas < 1:
        raise ValueError("n_antennas must be a positive integer")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError("efficiency must be in (0, 1]")
    return float(element_gain_dbi + 10.0 * np.log10(n_antennas * efficiency))


def fraunhofer_distance_m(
    frequency_hz: float,
    n_antennas: int,
    spacing_fraction_lambda: float = 0.5,
) -> float:
    """Approximate Fraunhofer distance for a uniform linear array aperture."""
    lam = wavelength_m(frequency_hz)
    if n_antennas < 1 or spacing_fraction_lambda <= 0:
        raise ValueError("Invalid array geometry")
    aperture_m = max((n_antennas - 1) * spacing_fraction_lambda * lam, lam / 2.0)
    return float(2.0 * aperture_m**2 / lam)


def far_field_electric_field_rms(
    tx_power_w: float,
    tx_gain_dbi: float,
    distance_m: float,
) -> float:
    """Free-space far-field RMS electric field in V/m.

    E_rms = sqrt(30 * EIRP) / r. This is not a near-field solver.
    """
    if not np.isfinite(tx_power_w) or tx_power_w <= 0:
        raise ValueError("tx_power_w must be positive and finite")
    if not np.isfinite(distance_m) or distance_m <= 0:
        raise ValueError("distance_m must be positive and finite")
    eirp_w = tx_power_w * db_to_linear(tx_gain_dbi)
    return float(np.sqrt(30.0 * eirp_w) / distance_m)


def friis_received_power_w(
    tx_power_w: float,
    frequency_hz: float,
    distance_m: float,
    tx_gain_dbi: float = 0.0,
    rx_gain_dbi: float = 0.0,
    system_loss_linear: float = 1.0,
) -> float:
    """Received power from the Friis free-space link equation."""
    if tx_power_w <= 0 or distance_m <= 0 or system_loss_linear <= 0:
        raise ValueError("Power, distance, and system loss must be positive")
    lam = wavelength_m(frequency_hz)
    path_factor = (lam / (4.0 * np.pi * distance_m)) ** 2
    power = tx_power_w * db_to_linear(tx_gain_dbi) * db_to_linear(rx_gain_dbi)
    return float(power * path_factor / system_loss_linear)


def calculate_link_metrics(
    tx_power_w: float,
    frequency_hz: float,
    distance_m: float,
    bandwidth_hz: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float = 0.0,
    noise_figure_db: float = 7.0,
    temperature_k: float = 290.0,
    interference_w: float = 0.0,
    scheduler_efficiency: float = 0.75,
    max_spectral_efficiency: float = 7.4,
) -> dict[str, float]:
    if bandwidth_hz <= 0 or temperature_k <= 0 or interference_w < 0:
        raise ValueError("Invalid bandwidth, temperature, or interference")
    if not (0 < scheduler_efficiency <= 1):
        raise ValueError("scheduler_efficiency must be in (0, 1]")
    if max_spectral_efficiency <= 0:
        raise ValueError("max_spectral_efficiency must be positive")

    rx_power_w = friis_received_power_w(
        tx_power_w=tx_power_w,
        frequency_hz=frequency_hz,
        distance_m=distance_m,
        tx_gain_dbi=tx_gain_dbi,
        rx_gain_dbi=rx_gain_dbi,
    )
    thermal_noise_w = BOLTZMANN_J_K * temperature_k * bandwidth_hz
    receiver_noise_w = thermal_noise_w * db_to_linear(noise_figure_db)
    denominator = receiver_noise_w + interference_w
    sinr_linear = rx_power_w / max(denominator, np.finfo(float).tiny)
    sinr_db = 10.0 * np.log10(max(sinr_linear, np.finfo(float).tiny))

    shannon_efficiency = np.log2(1.0 + sinr_linear)
    spectral_efficiency = min(float(shannon_efficiency), max_spectral_efficiency)
    bitrate_bps = bandwidth_hz * spectral_efficiency * scheduler_efficiency

    return {
        "received_power_w": float(rx_power_w),
        "noise_power_w": float(receiver_noise_w),
        "sinr_linear": float(sinr_linear),
        "sinr_db": float(sinr_db),
        "spectral_efficiency_bps_hz": float(spectral_efficiency),
        "bitrate_mbps": float(bitrate_bps / 1e6),
    }
