from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


# -----------------------------------------------------------------------------
# Existing antenna-analysis request (kept for backward compatibility)
# -----------------------------------------------------------------------------
class SimulationConfig(StrictModel):
    frequency_ghz: float = Field(default=2.5, gt=0)
    tx_power_w: float = Field(default=21.0, gt=0)
    distance_m: float = Field(default=50.0, gt=0)
    bandwidth_mhz: float = Field(default=100.0, gt=0)
    antenna_count: Literal[2, 4, 8, 16, 32] = 8
    element_gain_dbi: float = 8.0
    element_spacing_m: float | None = Field(default=None, gt=0)
    steering_angle_deg: float = Field(default=0.0, ge=-90, le=90)
    amplitudes: list[float] | None = None
    phase_offsets_deg: list[float] | None = None
    mode: Literal["simulation", "optimization"] = "simulation"

    @model_validator(mode="after")
    def validate_antenna_parameters(self):
        if self.amplitudes is not None:
            if len(self.amplitudes) != self.antenna_count:
                raise ValueError("The number of amplitudes must match antenna_count.")
            if any(a < 0 for a in self.amplitudes):
                raise ValueError("Amplitudes must be non-negative.")
            if sum(a ** 2 for a in self.amplitudes) == 0:
                raise ValueError("At least one amplitude must be positive.")
        if self.phase_offsets_deg is not None and len(self.phase_offsets_deg) != self.antenna_count:
            raise ValueError("The number of phase offsets must match antenna_count.")
        return self


# -----------------------------------------------------------------------------
# Complete network simulation and optimization requests
# -----------------------------------------------------------------------------
class NetworkScenarioInput(StrictModel):
    frequency_hz: float = Field(default=2.5e9, ge=100e6, le=6e9)
    distance_m: float = Field(default=50.0, gt=0)
    bandwidth_hz: float = Field(default=100e6, gt=0)
    operation_duration_s: float = Field(default=360.0, gt=0)


class NetworkDesignInput(StrictModel):
    tx_power_w: float = Field(default=21.0, gt=0, le=1000)
    n_antennas: Literal[2, 4, 8, 16] = 8


class SimulationParametersInput(StrictModel):
    element_gain_dbi: float = Field(default=0.0, ge=-20, le=30)
    array_efficiency: float = Field(default=0.70, gt=0, le=1)
    receiver_gain_dbi: float = Field(default=0.0, ge=-20, le=30)
    noise_figure_db: float = Field(default=7.0, ge=0, le=30)
    receiver_temperature_k: float = Field(default=290.0, gt=0)
    interference_w: float = Field(default=0.0, ge=0)
    scheduler_efficiency: float = Field(default=0.75, gt=0, le=1)
    max_spectral_efficiency: float = Field(default=7.4, gt=0)
    pa_efficiency: float = Field(default=0.35, gt=0, le=1)
    rf_chain_power_w: float = Field(default=0.5, ge=0)
    baseband_power_w: float = Field(default=5.0, ge=0)
    n_rf_chains: int | None = Field(default=None, ge=1)
    fixed_infrastructure_cost: float = Field(default=10000.0, ge=0)
    antenna_element_cost: float = Field(default=250.0, ge=0)
    rf_chain_cost: float = Field(default=500.0, ge=0)
    tissue_cell_size_m: float = Field(default=5e-4, gt=0)
    surface_heat_transfer_w_m2_k: float = Field(default=8.0, ge=0)

    def to_domain(self):
        from app.models.simulation import SimulationParameters
        return SimulationParameters(**self.model_dump())


class SimulationRunRequest(StrictModel):
    design: NetworkDesignInput = Field(default_factory=NetworkDesignInput)
    scenario: NetworkScenarioInput = Field(default_factory=NetworkScenarioInput)
    parameters: SimulationParametersInput = Field(default_factory=SimulationParametersInput)


class PSOConfigInput(StrictModel):
    n_particles: int = Field(default=12, ge=2, le=200)
    n_iterations: int = Field(default=20, ge=1, le=1000)
    inertia: float = Field(default=0.7, ge=0, le=2)
    cognitive: float = Field(default=1.5, ge=0)
    social: float = Field(default=1.5, ge=0)
    seed: int | None = 42


class DesignBoundsInput(StrictModel):
    min_tx_power_w: float = Field(default=1.0, gt=0)
    max_tx_power_w: float = Field(default=21.0, gt=0)
    min_antennas: int = Field(default=2, ge=2)
    max_antennas: int = Field(default=16, ge=2)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_tx_power_w >= self.max_tx_power_w:
            raise ValueError("min_tx_power_w must be smaller than max_tx_power_w")
        if self.min_antennas >= self.max_antennas:
            raise ValueError("min_antennas must be smaller than max_antennas")
        return self


class ObjectiveWeightsInput(StrictModel):
    sar: float = Field(default=1 / 6, ge=0)
    temperature: float = Field(default=1 / 6, ge=0)
    membrane: float = Field(default=1 / 6, ge=0)
    energy: float = Field(default=1 / 6, ge=0)
    qos: float = Field(default=1 / 6, ge=0)
    cost: float = Field(default=1 / 6, ge=0)

    @model_validator(mode="after")
    def validate_sum(self):
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError("The six objective weights must sum to 1.")
        return self


class ObjectiveReferencesInput(StrictModel):
    sar_ref_w_kg: float = Field(default=2.0, gt=0)
    delta_t_ref_k: float = Field(default=2.0, gt=0)
    delta_vm_ref_v: float = Field(default=0.01, gt=0)
    energy_ref_j: float | None = Field(default=None, gt=0)
    bitrate_target_mbps: float = Field(default=100.0, gt=0)
    cost_ref: float | None = Field(default=None, gt=0)


class ConstraintLimitsInput(StrictModel):
    sar_limit_w_kg: float = Field(default=2.0, gt=0)
    delta_t_limit_k: float = Field(default=2.0, gt=0)
    minimum_bitrate_mbps: float = Field(default=100.0, gt=0)
    minimum_sinr_db: float = Field(default=5.0)


class PenaltyWeightsInput(StrictModel):
    sar: float = Field(default=1000.0, ge=0)
    temperature: float = Field(default=1000.0, ge=0)
    bitrate: float = Field(default=100.0, ge=0)
    sinr: float = Field(default=100.0, ge=0)


class OptimizationRunRequest(StrictModel):
    scenario: NetworkScenarioInput = Field(default_factory=NetworkScenarioInput)
    baseline_design: NetworkDesignInput = Field(default_factory=NetworkDesignInput)
    parameters: SimulationParametersInput = Field(default_factory=SimulationParametersInput)
    pso: PSOConfigInput = Field(default_factory=PSOConfigInput)
    bounds: DesignBoundsInput = Field(default_factory=DesignBoundsInput)
    allowed_antennas: list[Literal[2, 4, 8, 16]] = Field(default_factory=lambda: [2, 4, 8, 16])
    weights: ObjectiveWeightsInput = Field(default_factory=ObjectiveWeightsInput)
    references: ObjectiveReferencesInput = Field(default_factory=ObjectiveReferencesInput)
    constraints: ConstraintLimitsInput = Field(default_factory=ConstraintLimitsInput)
    penalties: PenaltyWeightsInput = Field(default_factory=PenaltyWeightsInput)

    @model_validator(mode="after")
    def validate_optimization_domain(self):
        if not self.allowed_antennas:
            raise ValueError("allowed_antennas cannot be empty")
        if len(set(self.allowed_antennas)) != len(self.allowed_antennas):
            raise ValueError("allowed_antennas cannot contain duplicates")
        if any(n < self.bounds.min_antennas or n > self.bounds.max_antennas for n in self.allowed_antennas):
            raise ValueError("Every allowed antenna count must lie inside the antenna bounds")
        if self.baseline_design.tx_power_w < self.bounds.min_tx_power_w or self.baseline_design.tx_power_w > self.bounds.max_tx_power_w:
            raise ValueError("baseline_design.tx_power_w must lie inside the power bounds")
        if self.baseline_design.n_antennas not in self.allowed_antennas:
            raise ValueError("baseline_design.n_antennas must be one of allowed_antennas")
        return self
