from dataclasses import dataclass

from app.optimization.metrics import SimulationMetrics


@dataclass(frozen=True)
class ConstraintLimits:

    sar_limit_w_kg: float = 2.0

    delta_t_limit_k: float = 2.0

    minimum_bitrate_mbps: float = 100.0

    minimum_sinr_db: float = 5.0


@dataclass(frozen=True)
class PenaltyWeights:

    sar: float = 1000.0
    temperature: float = 1000.0
    bitrate: float = 100.0
    sinr: float = 100.0


def evaluate_constraints(
    metrics: SimulationMetrics,
    limits: ConstraintLimits
) -> dict:

    violations = {}

    # Normalized SAR violation
    violations["sar"] = max(
        0.0,
        metrics.sar10g_w_kg / limits.sar_limit_w_kg - 1.0
    )

    # Normalized thermal violation
    violations["temperature"] = max(
        0.0,
        metrics.delta_t_max_k / limits.delta_t_limit_k - 1.0
    )

    # Normalized bitrate violation
    violations["bitrate"] = max(
        0.0,
        (
            limits.minimum_bitrate_mbps
            - metrics.bitrate_mbps
        ) / limits.minimum_bitrate_mbps
    )

    # SINR violation in dB, with a stable normalization scale
    sinr_scale = max(abs(limits.minimum_sinr_db), 1.0)

    violations["sinr"] = max(
        0.0,
        (
            limits.minimum_sinr_db
            - metrics.sinr_db
        ) / sinr_scale
    )

    feasible = all(
        value <= 1e-12
        for value in violations.values()
    )

    return {
        "feasible": feasible,
        "violations": violations
    }


def compute_constraint_penalty(
    violations: dict,
    weights: PenaltyWeights
) -> float:

    penalty = (

        weights.sar * violations["sar"] ** 2

        + weights.temperature * violations["temperature"] ** 2

        + weights.bitrate * violations["bitrate"] ** 2

        + weights.sinr * violations["sinr"] ** 2
    )

    return float(penalty)