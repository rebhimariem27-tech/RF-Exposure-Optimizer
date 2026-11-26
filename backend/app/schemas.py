from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator
)


class SimulationConfig(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False
    )

    # ==========================================
    # 1. RADIO PARAMETERS
    # ==========================================

    frequency_ghz: float = Field(
        default=2.5,
        gt=0
    )

    tx_power_w: float = Field(
        default=21.0,
        gt=0
    )

    distance_m: float = Field(
        default=50.0,
        gt=0
    )

    bandwidth_mhz: float = Field(
        default=100.0,
        gt=0
    )

    # ==========================================
    # 2. ANTENNA PARAMETERS
    # ==========================================

    antenna_count: Literal[2, 4, 8, 16, 32] = 8

    element_gain_dbi: float = 8.0

    element_spacing_m: float | None = Field(
        default=None,
        gt=0
    )

    steering_angle_deg: float = Field(
        default=0.0,
        ge=-90,
        le=90
    )

    # Relative voltage excitation amplitudes
    amplitudes: list[float] | None = None

    # Additional phase corrections in degrees
    phase_offsets_deg: list[float] | None = None

    # ==========================================
    # 3. EXECUTION MODE
    # ==========================================

    mode: Literal[
        "simulation",
        "optimization"
    ] = "simulation"

    # ==========================================
    # 4. VALIDATION
    # ==========================================

    @model_validator(mode="after")
    def validate_antenna_parameters(self):

        if self.amplitudes is not None:

            if len(self.amplitudes) != self.antenna_count:
                raise ValueError(
                    "The number of amplitudes must match "
                    "the number of antenna elements."
                )

            if any(a < 0 for a in self.amplitudes):
                raise ValueError(
                    "Amplitudes must be non-negative."
                )

            if sum(a ** 2 for a in self.amplitudes) == 0:
                raise ValueError(
                    "At least one amplitude must be positive."
                )

        if self.phase_offsets_deg is not None:

            if len(self.phase_offsets_deg) != self.antenna_count:
                raise ValueError(
                    "The number of phase offsets must match "
                    "the number of antenna elements."
                )

        return self