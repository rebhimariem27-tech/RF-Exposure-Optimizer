
import numpy as np

from app.optimization.pso import ParticleSwarmOptimizer
from app.optimization.configuration import PSOConfig, DesignBounds
from app.optimization.optimizer import optimize_configuration


def sphere_function(x):
    """
    Fonction mathématique de test.
    Son minimum global est 0, atteint en (0, 0).
    """
    return np.sum(x ** 2)


def test_pso_basic():

    pso = ParticleSwarmOptimizer(
        objective_function=sphere_function,
        lower_bounds=[-10, -10],
        upper_bounds=[10, 10],
        n_particles=30,
        n_iterations=100,
        seed=42
    )

    result = pso.optimize()

    assert np.isfinite(result["best_score"])
    assert result["best_score"] >= 0
    assert len(result["best_position"]) == 2
    assert len(result["history"]) == 100


def test_pso_discrete_variable():

    pso = ParticleSwarmOptimizer(
        objective_function=sphere_function,
        lower_bounds=[-10, 2],
        upper_bounds=[10, 32],
        n_particles=20,
        n_iterations=50,
        seed=42,
        discrete_values={1: [2, 4, 8, 16, 32]}
    )

    result = pso.optimize()

    assert result["best_position"][1] in [2, 4, 8, 16, 32]


def test_optimizer_interface():

    bounds = DesignBounds(
        lower=[-10, -10],
        upper=[10, 10]
    )

    config = PSOConfig(
        n_particles=20,
        n_iterations=50,
        seed=42
    )

    result = optimize_configuration(
        objective_function=sphere_function,
        bounds=bounds,
        config=config
    )

    assert "best_position" in result
    assert "best_score" in result
    assert np.isfinite(result["best_score"])
