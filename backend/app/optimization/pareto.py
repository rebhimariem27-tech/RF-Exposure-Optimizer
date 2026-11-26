import numpy as np


def pareto_front_indices(
    objective_matrix: np.ndarray,
    tolerance: float = 1e-12
) -> list[int]:

    values = np.asarray(
        objective_matrix,
        dtype=float
    )

    if values.ndim != 2:
        raise ValueError("Expected a 2D objective matrix.")

    if not np.all(np.isfinite(values)):
        raise ValueError("Objective values must be finite.")

    n = len(values)

    pareto_indices = []

    for i in range(n):

        dominated = False

        for j in range(n):

            if i == j:
                continue

            no_worse = np.all(
                values[j] <= values[i] + tolerance
            )

            strictly_better = np.any(
                values[j] < values[i] - tolerance
            )

            if no_worse and strictly_better:

                dominated = True
                break

        if not dominated:
            pareto_indices.append(i)

    return pareto_indices


def run_weight_sensitivity(
    component_matrix: np.ndarray,
    base_weights: list[float],
    samples: int = 200,
    concentration: float = 40.0,
    seed: int = 42
) -> dict:

    values = np.asarray(component_matrix, dtype=float)

    weights = np.asarray(base_weights, dtype=float)

    if values.ndim != 2 or values.shape[1] != 4:
        raise ValueError("Expected four objective components.")

    if weights.shape != (4,):
        raise ValueError("Expected four weights.")

    if np.any(weights <= 0):
        raise ValueError("Base weights must be positive.")

    if not np.isclose(np.sum(weights), 1.0):
        raise ValueError("Weights must sum to 1.")

    if samples < 1 or concentration <= 0:
        raise ValueError("Invalid sensitivity parameters.")

    rng = np.random.default_rng(seed)

    weight_samples = rng.dirichlet(
        weights * concentration,
        size=samples
    )

    selected_indices = []

    for sample in weight_samples:

        scores = values @ sample

        selected_indices.append(
            int(np.argmin(scores))
        )

    unique, counts = np.unique(
        selected_indices,
        return_counts=True
    )

    selection_frequency = {
        int(index): float(count / samples)
        for index, count in zip(unique, counts)
    }

    return {
        "weight_samples": weight_samples.tolist(),
        "selected_indices": selected_indices,
        "selection_frequency": selection_frequency
    }