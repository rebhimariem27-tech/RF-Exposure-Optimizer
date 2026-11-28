def convergence_payload(history: list[float]) -> dict:
    """Return a frontend-friendly representation of the PSO convergence history."""
    return {
        "x": list(range(1, len(history) + 1)),
        "y": [float(value) for value in history],
        "x_label": "Iteration",
        "y_label": "Best fitness",
    }
