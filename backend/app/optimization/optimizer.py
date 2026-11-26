
from app.optimization.pso import ParticleSwarmOptimizer
from app.optimization.configuration import PSOConfig, DesignBounds


def optimize_configuration(
    objective_function,
    bounds: DesignBounds,
    config: PSOConfig,
    discrete_values=None
):

    bounds.validate()

    optimizer = ParticleSwarmOptimizer(
        objective_function=objective_function,
        lower_bounds=bounds.lower,
        upper_bounds=bounds.upper,
        n_particles=config.n_particles,
        n_iterations=config.n_iterations,
        inertia=config.inertia,
        cognitive=config.cognitive,
        social=config.social,
        seed=config.seed,
        discrete_values=discrete_values
    )

    result = optimizer.optimize()

    return result
