
import pytest

from app.optimization.metrics import SimulationMetrics

from app.optimization.objective import (
    ObjectiveReferences,
    ObjectiveWeights,
    compute_objective,
)

from app.optimization.constraints import (
    ConstraintLimits,
    PenaltyWeights,
    evaluate_constraints,
    compute_constraint_penalty,
)

from app.optimization.fitness import evaluate_candidate

from app.optimization.weights import (
    balanced_pairwise_matrix,
    compute_ahp_weights,
)


# -----------------------------------------
# 1. Donnees de test
# -----------------------------------------

def create_metrics(
    sar=1.0,
    temperature=1.0,
    membrane=0.001,
    energy=1000.0,
    bitrate=120.0,
    cost=5000.0,
    sinr=10.0
):

    return SimulationMetrics(
        sar10g_w_kg=sar,
        delta_t_max_k=temperature,
        delta_vm_abs_v=membrane,
        energy_consumption_j=energy,
        bitrate_mbps=bitrate,
        infrastructure_cost=cost,
        sinr_db=sinr,
    )


def create_references():

    return ObjectiveReferences(
        sar_ref_w_kg=2.0,
        delta_t_ref_k=2.0,
        delta_vm_ref_v=0.01,
        energy_ref_j=2000.0,
        bitrate_target_mbps=100.0,
        cost_ref=10000.0,
    )


def create_weights():

    return ObjectiveWeights(
        sar=1/6,
        temperature=1/6,
        membrane=1/6,
        energy=1/6,
        qos=1/6,
        cost=1/6,
    )


# -----------------------------------------
# 2. Test AHP
# -----------------------------------------

def test_ahp_balanced_weights():

    matrix = balanced_pairwise_matrix()

    result = compute_ahp_weights(matrix)

    weights = result["weights"]

    assert len(weights) == 6

    assert sum(weights.values()) == pytest.approx(1.0)

    for weight in weights.values():
        assert weight == pytest.approx(1/6)

    assert result["consistent"] is True


# -----------------------------------------
# 3. Test fonction objectif
# -----------------------------------------

def test_objective_calculation():

    metrics = create_metrics()

    result = compute_objective(
        metrics,
        create_weights(),
        create_references()
    )

    # Components:
    # SAR         = 1 / 2 = 0.5
    # Temperature = 1 / 2 = 0.5
    # Membrane    = 0.001 / 0.01 = 0.1
    # Energy      = 1000 / 2000 = 0.5
    # QoS         = 0 because bitrate >= target
    # Cost        = 5000 / 10000 = 0.5

    expected = (0.5 + 0.5 + 0.1 + 0.5 + 0 + 0.5) / 6

    assert result["objective_value"] == pytest.approx(expected)


# -----------------------------------------
# 4. Test contraintes respectees
# -----------------------------------------

def test_feasible_configuration():

    metrics = create_metrics()

    result = evaluate_constraints(
        metrics,
        ConstraintLimits()
    )

    assert result["feasible"] is True

    assert all(
        value == 0
        for value in result["violations"].values()
    )


# -----------------------------------------
# 5. Test contraintes violees
# -----------------------------------------

def test_violated_constraints():

    metrics = create_metrics(
        sar=3.0,
        temperature=3.0,
        bitrate=80.0,
        sinr=0.0
    )

    result = evaluate_constraints(
        metrics,
        ConstraintLimits()
    )

    assert result["feasible"] is False

    assert result["violations"]["sar"] > 0

    assert result["violations"]["temperature"] > 0

    assert result["violations"]["bitrate"] > 0

    assert result["violations"]["sinr"] > 0


# -----------------------------------------
# 6. Test penalite
# -----------------------------------------

def test_constraint_penalty():

    violations = {
        "sar": 0.5,
        "temperature": 0.5,
        "bitrate": 0.2,
        "sinr": 1.0
    }

    weights = PenaltyWeights()

    penalty = compute_constraint_penalty(
        violations,
        weights
    )

    expected = (
        1000 * 0.5**2
        + 1000 * 0.5**2
        + 100 * 0.2**2
        + 100 * 1.0**2
    )

    assert penalty == pytest.approx(expected)


# -----------------------------------------
# 7. Test evaluation complete
# -----------------------------------------

def test_complete_fitness():

    metrics = create_metrics()

    result = evaluate_candidate(
        metrics=metrics,
        references=create_references(),
        objective_weights=create_weights(),
        constraint_limits=ConstraintLimits(),
        penalty_weights=PenaltyWeights()
    )

    assert result["feasible"] is True

    assert result["constraint_penalty"] == 0

    assert result["total_fitness"] == pytest.approx(
        result["objective_value"]
    )


def test_infeasible_candidate_has_penalty():

    metrics = create_metrics(sar=3.0)

    result = evaluate_candidate(
        metrics=metrics,
        references=create_references(),
        objective_weights=create_weights(),
        constraint_limits=ConstraintLimits(),
        penalty_weights=PenaltyWeights()
    )

    assert result["feasible"] is False

    assert result["constraint_penalty"] > 0

    assert result["total_fitness"] > result["objective_value"]
