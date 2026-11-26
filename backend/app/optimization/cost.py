from dataclasses import dataclass


@dataclass(frozen=True)
class InfrastructureCostModel:

    fixed_cost: float
    element_cost: float
    rf_chain_cost: float
    installation_cost: float = 0.0

    def estimate(
        self,
        antenna_count: int,
        rf_chain_count: int
    ) -> float:

        if antenna_count < 1:
            raise ValueError("Invalid antenna count.")

        if not 1 <= rf_chain_count <= antenna_count:
            raise ValueError("Invalid RF chain count.")

        values = [
            self.fixed_cost,
            self.element_cost,
            self.rf_chain_cost,
            self.installation_cost
        ]

        if any(value < 0 for value in values):
            raise ValueError("Costs must be non-negative.")

        return (
            self.fixed_cost
            + antenna_count * self.element_cost
            + rf_chain_count * self.rf_chain_cost
            + self.installation_cost
        )