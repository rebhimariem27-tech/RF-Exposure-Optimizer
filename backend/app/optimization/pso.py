
import numpy as np


class ParticleSwarmOptimizer:

    def __init__(
        self,
        objective_function,
        lower_bounds,
        upper_bounds,
        n_particles=30,
        n_iterations=100,
        inertia=0.7,
        cognitive=1.5,
        social=1.5,
        seed=42,
        discrete_values=None
    ):

        self.objective_function = objective_function

        self.lower = np.asarray(lower_bounds, dtype=float)
        self.upper = np.asarray(upper_bounds, dtype=float)

        if self.lower.ndim != 1 or self.upper.ndim != 1:
            raise ValueError("Bounds must be one-dimensional.")

        if self.lower.shape != self.upper.shape:
            raise ValueError("Bounds must have the same dimensions.")

        if np.any(self.lower >= self.upper):
            raise ValueError("Each lower bound must be smaller than upper bound.")

        if n_particles < 2 or n_iterations < 1:
            raise ValueError("At least 2 particles and 1 iteration are required.")

        self.n_particles = n_particles
        self.n_iterations = n_iterations

        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social

        self.rng = np.random.default_rng(seed)

        # Optional discrete values for selected variables.
        # Example: {1: [2, 4, 8, 16, 32]}
        self.discrete_values = discrete_values or {}

        self.dimension = len(self.lower)

    def project_position(self, position):

        position = np.clip(position, self.lower, self.upper)

        for index, allowed_values in self.discrete_values.items():

            values = np.asarray(allowed_values, dtype=float)

            if len(values) == 0:
                raise ValueError("Discrete values cannot be empty.")

            position[index] = values[
                np.argmin(np.abs(values - position[index]))
            ]

        return position

    def evaluate(self, position):

        try:
            value = float(self.objective_function(position.copy()))

            if not np.isfinite(value):
                return float("inf")

            return value

        except (ValueError, FloatingPointError):
            return float("inf")

    def optimize(self):

        # Initialize particle positions and velocities.
        positions = self.rng.uniform(
            self.lower,
            self.upper,
            size=(self.n_particles, self.dimension)
        )

        for i in range(self.n_particles):
            positions[i] = self.project_position(positions[i])

        velocities = np.zeros_like(positions)

        # Evaluate initial particles.
        scores = np.array([
            self.evaluate(position)
            for position in positions
        ])

        personal_best_positions = positions.copy()
        personal_best_scores = scores.copy()

        best_index = np.argmin(scores)

        global_best_position = positions[best_index].copy()
        global_best_score = scores[best_index]

        history = []

        # Main PSO loop.
        for iteration in range(self.n_iterations):

            r1 = self.rng.random(positions.shape)
            r2 = self.rng.random(positions.shape)

            velocities = (
                self.inertia * velocities
                + self.cognitive * r1 *
                (personal_best_positions - positions)
                + self.social * r2 *
                (global_best_position - positions)
            )

            positions = positions + velocities

            # Keep particles inside the search space.
            for i in range(self.n_particles):
                positions[i] = self.project_position(positions[i])

            scores = np.array([
                self.evaluate(position)
                for position in positions
            ])

            # Update personal best positions.
            improved = scores < personal_best_scores

            personal_best_positions[improved] = positions[improved]
            personal_best_scores[improved] = scores[improved]

            # Update global best.
            best_index = np.argmin(personal_best_scores)

            if personal_best_scores[best_index] < global_best_score:

                global_best_score = personal_best_scores[best_index]

                global_best_position = (
                    personal_best_positions[best_index].copy()
                )

            history.append(global_best_score)

        return {
            "best_position": global_best_position,
            "best_score": float(global_best_score),
            "history": history,
            "iterations": self.n_iterations
        }
