from __future__ import annotations

from dataclasses import dataclass
import warnings

import numpy as np


REFERENCE_DIELECTRIC_FREQUENCY_HZ = 2.45e9


@dataclass(frozen=True)
class TissueLayer:
    """One homogeneous layer in a 1-D head phantom."""

    name: str
    thickness_m: float
    epsilon_r: float
    conductivity_s_m: float
    density_kg_m3: float
    specific_heat_j_kg_k: float
    thermal_conductivity_w_m_k: float
    perfusion_s_inv: float = 0.0

    def validate(self) -> None:
        positive_fields = {
            "thickness_m": self.thickness_m,
            "epsilon_r": self.epsilon_r,
            "density_kg_m3": self.density_kg_m3,
            "specific_heat_j_kg_k": self.specific_heat_j_kg_k,
            "thermal_conductivity_w_m_k": self.thermal_conductivity_w_m_k,
        }
        for name, value in positive_fields.items():
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{self.name}.{name} must be positive and finite")

        if not np.isfinite(self.conductivity_s_m) or self.conductivity_s_m < 0:
            raise ValueError(f"{self.name}.conductivity_s_m must be finite and non-negative")
        if not np.isfinite(self.perfusion_s_inv) or self.perfusion_s_inv < 0:
            raise ValueError(f"{self.name}.perfusion_s_inv must be finite and non-negative")


@dataclass(frozen=True)
class TissueGrid:
    """Cell-centred discretisation of a stack of tissue layers."""

    z_m: np.ndarray
    dz_m: np.ndarray
    layer_index: np.ndarray
    layer_names: tuple[str, ...]
    epsilon_r: np.ndarray
    conductivity_s_m: np.ndarray
    density_kg_m3: np.ndarray
    specific_heat_j_kg_k: np.ndarray
    thermal_conductivity_w_m_k: np.ndarray
    perfusion_s_inv: np.ndarray

    @property
    def size(self) -> int:
        return int(self.z_m.size)


def default_head_layers() -> list[TissueLayer]:
    """Return an illustrative 1-D head stack for approximately 2.45-2.50 GHz.

    Dielectric constants/conductivities are based on published 2.45 GHz tissue
    data. Thicknesses follow the project's simplified head-layer assumptions.
    Thermal properties and perfusion are initial modelling values and must be
    calibrated for the chosen anatomical phantom.
    """
    return [
        TissueLayer(
            name="skin", thickness_m=0.002,
            epsilon_r=37.952, conductivity_s_m=1.4876,
            density_kg_m3=1100.0, specific_heat_j_kg_k=3391.0,
            thermal_conductivity_w_m_k=0.37, perfusion_s_inv=0.0,
        ),
        TissueLayer(
            name="fat", thickness_m=0.003,
            epsilon_r=5.2749, conductivity_s_m=0.10672,
            density_kg_m3=920.0, specific_heat_j_kg_k=2348.0,
            thermal_conductivity_w_m_k=0.21, perfusion_s_inv=0.0,
        ),
        TissueLayer(
            name="cortical_bone", thickness_m=0.006,
            epsilon_r=11.352, conductivity_s_m=0.40411,
            density_kg_m3=1850.0, specific_heat_j_kg_k=1590.0,
            thermal_conductivity_w_m_k=1.16, perfusion_s_inv=0.0,
        ),
        TissueLayer(
            name="csf", thickness_m=0.002,
            epsilon_r=66.168, conductivity_s_m=3.5041,
            density_kg_m3=1007.0, specific_heat_j_kg_k=4000.0,
            thermal_conductivity_w_m_k=0.60, perfusion_s_inv=0.0,
        ),
        TissueLayer(
            name="brain_gray_matter", thickness_m=0.020,
            epsilon_r=48.83, conductivity_s_m=1.843,
            density_kg_m3=1045.0, specific_heat_j_kg_k=3630.0,
            thermal_conductivity_w_m_k=0.51, perfusion_s_inv=0.0,
        ),
    ]


def validate_frequency_for_default_tissues(frequency_hz: float) -> None:
    if not np.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive and finite")

    relative_difference = abs(frequency_hz - REFERENCE_DIELECTRIC_FREQUENCY_HZ) / REFERENCE_DIELECTRIC_FREQUENCY_HZ
    if relative_difference > 0.05:
        warnings.warn(
            "Default tissue dielectric properties are referenced to 2.45 GHz. "
            "For this frequency, replace them with frequency-specific tissue data.",
            UserWarning,
            stacklevel=2,
        )


def build_tissue_grid(
    layers: list[TissueLayer],
    target_cell_size_m: float = 5e-4,
) -> TissueGrid:
    if not layers:
        raise ValueError("At least one tissue layer is required")
    if not np.isfinite(target_cell_size_m) or target_cell_size_m <= 0:
        raise ValueError("target_cell_size_m must be positive and finite")

    for layer in layers:
        layer.validate()

    z_parts: list[np.ndarray] = []
    dz_parts: list[np.ndarray] = []
    index_parts: list[np.ndarray] = []
    eps_parts: list[np.ndarray] = []
    sigma_parts: list[np.ndarray] = []
    rho_parts: list[np.ndarray] = []
    cp_parts: list[np.ndarray] = []
    k_parts: list[np.ndarray] = []
    perfusion_parts: list[np.ndarray] = []

    z_start = 0.0
    for idx, layer in enumerate(layers):
        n_cells = max(1, int(np.ceil(layer.thickness_m / target_cell_size_m)))
        cell_size = layer.thickness_m / n_cells
        dz = np.full(n_cells, cell_size, dtype=float)
        centers = z_start + (np.arange(n_cells, dtype=float) + 0.5) * cell_size

        z_parts.append(centers)
        dz_parts.append(dz)
        index_parts.append(np.full(n_cells, idx, dtype=int))
        eps_parts.append(np.full(n_cells, layer.epsilon_r, dtype=float))
        sigma_parts.append(np.full(n_cells, layer.conductivity_s_m, dtype=float))
        rho_parts.append(np.full(n_cells, layer.density_kg_m3, dtype=float))
        cp_parts.append(np.full(n_cells, layer.specific_heat_j_kg_k, dtype=float))
        k_parts.append(np.full(n_cells, layer.thermal_conductivity_w_m_k, dtype=float))
        perfusion_parts.append(np.full(n_cells, layer.perfusion_s_inv, dtype=float))
        z_start += layer.thickness_m

    return TissueGrid(
        z_m=np.concatenate(z_parts),
        dz_m=np.concatenate(dz_parts),
        layer_index=np.concatenate(index_parts),
        layer_names=tuple(layer.name for layer in layers),
        epsilon_r=np.concatenate(eps_parts),
        conductivity_s_m=np.concatenate(sigma_parts),
        density_kg_m3=np.concatenate(rho_parts),
        specific_heat_j_kg_k=np.concatenate(cp_parts),
        thermal_conductivity_w_m_k=np.concatenate(k_parts),
        perfusion_s_inv=np.concatenate(perfusion_parts),
    )
