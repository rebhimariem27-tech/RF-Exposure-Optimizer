from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MembraneRCProxyParameters:
    """Exploratory lumped-RC proxy parameters; not validated for GHz dosimetry."""

    effective_length_m: float = 10e-6
    time_constant_s: float = 10e-9


def estimate_delta_vm_rc_proxy(
    incident_field_rms_v_m: float,
    frequency_hz: float,
    parameters: MembraneRCProxyParameters | None = None,
) -> float:
    """Return a simple low-pass membrane-voltage proxy in volts.

    V_quasi = E * effective_length; |H(jw)| = 1/sqrt(1 + (w*tau)^2).
    This is retained only as an exploratory sixth-objective indicator. It is
    not a validated biological membrane-polarization model at 2.5 GHz.
    """
    if incident_field_rms_v_m < 0 or not np.isfinite(incident_field_rms_v_m):
        raise ValueError("incident_field_rms_v_m must be finite and non-negative")
    if frequency_hz <= 0 or not np.isfinite(frequency_hz):
        raise ValueError("frequency_hz must be positive and finite")

    params = parameters or MembraneRCProxyParameters()
    if params.effective_length_m <= 0 or params.time_constant_s <= 0:
        raise ValueError("Membrane proxy parameters must be positive")

    omega_tau = 2.0 * np.pi * frequency_hz * params.time_constant_s
    low_pass_gain = 1.0 / np.sqrt(1.0 + omega_tau**2)
    return float(incident_field_rms_v_m * params.effective_length_m * low_pass_gain)
