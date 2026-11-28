def validate_finite_positive(value: float, name: str) -> float:
    """Small reusable guard for numeric values used outside Pydantic."""
    import math

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value
