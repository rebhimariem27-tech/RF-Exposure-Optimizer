import numpy as np


CRITERIA = [
    "sar",
    "temperature",
    "membrane",
    "energy",
    "qos",
    "cost"
]


def balanced_pairwise_matrix():

    n = len(CRITERIA)

    return np.ones((n, n), dtype=float)


def compute_ahp_weights(
    pairwise_matrix: np.ndarray
) -> dict:

    matrix = np.asarray(
        pairwise_matrix,
        dtype=float
    )

    n = len(CRITERIA)

    if matrix.shape != (n, n):
        raise ValueError(
            "The AHP matrix must be 6x6."
        )

    if not np.all(np.isfinite(matrix)) or np.any(matrix <= 0):
        raise ValueError("Invalid AHP matrix values.")

    if not np.allclose(np.diag(matrix), 1.0):
        raise ValueError("Diagonal must equal 1.")

    if not np.allclose(matrix * matrix.T, 1.0):
        raise ValueError("The matrix must be reciprocal.")

    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    index = np.argmax(eigenvalues.real)

    lambda_max = eigenvalues[index].real

    vector = np.abs(
        eigenvectors[:, index].real
    )

    weights = vector / np.sum(vector)

    consistency_index = (
        (lambda_max - n) / (n - 1)
    )

    random_index = {
        1: 0.0,
        2: 0.0,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }

    ri = random_index[n]

    consistency_ratio = (
        consistency_index / ri
        if ri > 0 else 0.0
    )

    return {
        "weights": dict(
            zip(CRITERIA, weights.tolist())
        ),
        "consistency_index": float(consistency_index),
        "consistency_ratio": float(consistency_ratio),
        "consistent": bool(consistency_ratio <= 0.10)
    }