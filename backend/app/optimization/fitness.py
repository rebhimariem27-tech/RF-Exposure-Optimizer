from app.optimization.metrics import SimulationMetrics
from app.optimization.objective import (
    ObjectiveReferences,
    ObjectiveWeights,
    compute_objective
)
from app.optimization.constraints import (
    ConstraintLimits,
    PenaltyWeights,
    evaluate_constraints,
    compute_constraint_penalty
)


def evaluate_candidate(
    metrics: SimulationMetrics,
    references: ObjectiveReferences,
    objective_weights: ObjectiveWeights,
    constraint_limits: ConstraintLimits,
    penalty_weights: PenaltyWeights
) -> dict:

    # 1. Calculate the six-objective function
    objective = compute_objective(
        metrics,
        objective_weights,
        references
    )

    # 2. Evaluate constraints
    constraint_result = evaluate_constraints(
        metrics,
        constraint_limits
    )

    # 3. Calculate constraint penalty
    penalty = compute_constraint_penalty(
        constraint_result["violations"],
        penalty_weights
    )

    # 4. Total fitness for PSO
    total_fitness = (
        objective["objective_value"] + penalty
    )

    return {
        "objective_value": objective["objective_value"],
        "constraint_penalty": penalty,
        "total_fitness": total_fitness,
        "feasible": constraint_result["feasible"],
        "objective_components": objective["components"],
        "constraint_violations": constraint_result["violations"]
    }