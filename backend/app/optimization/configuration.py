
from dataclasses import dataclass


@dataclass
class PSOConfig:
    n_particles: int = 30
    n_iterations: int = 100

    inertia: float = 0.7
    cognitive: float = 1.5
    social: float = 1.5

    seed: int | None = 42


@dataclass
class DesignBounds:
    """
    Bornes des variables de décision.
    Chaque variable possède une borne minimale et maximale.
    """

    lower: list[float]
    upper: list[float]

    def validate(self):
        if len(self.lower) != len(self.upper):
            raise ValueError("Lower and upper bounds must have the same size.")

        if not self.lower:
            raise ValueError("At least one design variable is required.")

        for low, high in zip(self.lower, self.upper):
            if low >= high:
                raise ValueError("Each lower bound must be smaller than upper bound.")
