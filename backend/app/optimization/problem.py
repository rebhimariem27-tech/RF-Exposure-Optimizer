
from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np

from app.optimization.metrics import SimulationMetrics
from app.optimization.fitness import evaluate_candidate
from app.optimization.configuration import PSOConfig, DesignBounds
from app.optimization.optimizer import optimize_configuration


@dataclass(frozen=True)
class NetworkScenario:
    """Paramètres fixes du scénario radio simulé."""

    frequency_hz: float
    distance_m: float
    bandwidth_hz: float
    operation_duration_s: float

    def validate(self):
        values = asdict(self)

        for name, value in values.items():
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite.")


@dataclass(frozen=True)
class NetworkDesign:
    """Variables de décision du PSO."""

    tx_power_w: float
    n_antennas: int


def optimize_network(
    simulator: Callable,
    scenario: NetworkScenario,
    references,
    objective_weights,
    constraint_limits,
    penalty_weights,
    bounds: DesignBounds,
    config: PSOConfig,
    allowed_antennas=None
) -> dict:
    """
    Connecte le PSO au simulateur physique et à la fonction fitness.

    simulator(design, scenario) doit retourner un SimulationMetrics.
    """

    scenario.validate()
    bounds.validate()

    if len(bounds.lower) != 2:
        raise ValueError(
            "The initial PSO problem requires exactly 2 variables: "
            "transmit power and number of antennas."
        )

    if bounds.lower[0] <= 0:
        raise ValueError("Transmit power lower bound must be positive.")

    if bounds.lower[1] < 1:
        raise ValueError("The number of antennas must be positive.")

    if allowed_antennas is None:
        allowed_antennas = [2, 4, 8, 16, 32]

    allowed_antennas = sorted(set(allowed_antennas))

    if not allowed_antennas:
        raise ValueError("At least one antenna count is required.")

    if any(
        value < bounds.lower[1] or value > bounds.upper[1]
        for value in allowed_antennas
    ):
        raise ValueError("Allowed antenna counts must lie inside the bounds.")

    def evaluate_position(position):

        design = NetworkDesign(
            tx_power_w=float(position[0]),
            n_antennas=int(round(position[1]))
        )

        metrics = simulator(design, scenario)

        if not isinstance(metrics, SimulationMetrics):
            raise TypeError(
                "The simulator must return a SimulationMetrics object."
            )

        evaluation = evaluate_candidate(
            metrics=metrics,
            references=references,
            objective_weights=objective_weights,
            constraint_limits=constraint_limits,
            penalty_weights=penalty_weights
        )

        return float(evaluation["total_fitness"])

    # The second variable is discrete: number of antennas.
    result = optimize_configuration(
        objective_function=evaluate_position,
        bounds=bounds,
        config=config,
        discrete_values={1: allowed_antennas}
    )

    if not np.isfinite(result["best_score"]):
        raise RuntimeError(
            "PSO did not find a candidate with a finite fitness."
        )

    # Reconstruct and evaluate the best configuration.
    best_position = result["best_position"]

    best_design = NetworkDesign(
        tx_power_w=float(best_position[0]),
        n_antennas=int(round(best_position[1]))
    )

    best_metrics = simulator(best_design, scenario)

    best_evaluation = evaluate_candidate(
        metrics=best_metrics,
        references=references,
        objective_weights=objective_weights,
        constraint_limits=constraint_limits,
        penalty_weights=penalty_weights
    )

    return {
        "best_design": asdict(best_design),
        "scenario": asdict(scenario),
        "metrics": {
            key: float(value)
            for key, value in asdict(best_metrics).items()
        },
        "objective_value": float(
            best_evaluation["objective_value"]
        ),
        "constraint_penalty": float(
            best_evaluation["constraint_penalty"]
        ),
        "total_fitness": float(
            best_evaluation["total_fitness"]
        ),
        "feasible": bool(best_evaluation["feasible"]),
        "objective_components": {
            key: float(value)
            for key, value in
            best_evaluation["objective_components"].items()
        },
        "constraint_violations": {
            key: float(value)
            for key, value in
            best_evaluation["constraint_violations"].items()
        },
        "pso": {
            "best_score": float(result["best_score"]),
            "history": [
                float(value) for value in result["history"]
            ],
            "iterations": int(result["iterations"])
        }
    }
