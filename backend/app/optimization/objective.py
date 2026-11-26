from dataclasses import dataclass
import math

from app.optimization.metrics import SimulationMetrics


@dataclass(frozen=True)
class ObjectiveReferences:

    sar_ref_w_kg: float
    delta_t_ref_k: float
    delta_vm_ref_v: float
    energy_ref_j: float
    bitrate_target_mbps: float
    cost_ref: float

    def validate(self):

        values = [
            self.sar_ref_w_kg,
            self.delta_t_ref_k,
            self.delta_vm_ref_v,
            self.energy_ref_j,
            self.bitrate_target_mbps,
            self.cost_ref
        ]

        if any(
            not math.isfinite(value) or value <= 0
            for value in values
        ):
            raise ValueError(
                "All reference values must be finite and positive."
            )


@dataclass(frozen=True)
class ObjectiveWeights:

    sar: float
    temperature: float
    membrane: float
    energy: float
    qos: float
    cost: float

    def validate(self):

        values = [
            self.sar,
            self.temperature,
            self.membrane,
            self.energy,
            self.qos,
            self.cost
        ]

        if any(
            not math.isfinite(value) or value < 0
            for value in values
        ):
            raise ValueError(
                "Weights must be finite and non-negative."
            )

        if not math.isclose(
            sum(values), 1.0, abs_tol=1e-6
        ):
            raise ValueError(
                "The six weights must sum to 1."
            )


def compute_objective_components(
    metrics: SimulationMetrics,
    references: ObjectiveReferences
) -> dict:

    references.validate()

    values = [
        metrics.sar10g_w_kg,
        metrics.delta_t_max_k,
        metrics.delta_vm_abs_v,
        metrics.energy_consumption_j,
        metrics.bitrate_mbps,
        metrics.infrastructure_cost
    ]

    if any(
        not math.isfinite(value) or value < 0
        for value in values
    ):
        raise ValueError(
            "All physical metrics must be finite and non-negative."
        )

    return {

        "sar": (
            metrics.sar10g_w_kg
            / references.sar_ref_w_kg
        ),

        "temperature": (
            metrics.delta_t_max_k
            / references.delta_t_ref_k
        ),

        "membrane": (
            metrics.delta_vm_abs_v
            / references.delta_vm_ref_v
        ),

        "energy": (
            metrics.energy_consumption_j
            / references.energy_ref_j
        ),

        "qos": (
            1.0 - min(
                metrics.bitrate_mbps
                / references.bitrate_target_mbps,
                1.0
            )
        ),

        "cost": (
            metrics.infrastructure_cost
            / references.cost_ref
        )
    }


def compute_objective(
    metrics: SimulationMetrics,
    weights: ObjectiveWeights,
    references: ObjectiveReferences
) -> dict:

    weights.validate()

    components = compute_objective_components(
        metrics,
        references
    )

    objective_value = (

        weights.sar * components["sar"]

        + weights.temperature * components["temperature"]

        + weights.membrane * components["membrane"]

        + weights.energy * components["energy"]

        + weights.qos * components["qos"]

        + weights.cost * components["cost"]
    )

    return {
        "objective_value": float(objective_value),
        "components": components
    }