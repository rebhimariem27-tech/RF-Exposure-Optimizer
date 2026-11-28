
import json

from app.models.simulation import (
    SimulationParameters,
    simulate_network
)

from app.optimization.problem import (
    NetworkDesign,
    NetworkScenario,
    optimize_network
)

from app.optimization.configuration import (
    PSOConfig,
    DesignBounds
)

from app.optimization.objective import (
    ObjectiveReferences,
    ObjectiveWeights
)

from app.optimization.constraints import (
    ConstraintLimits,
    PenaltyWeights
)


def main():

    # --------------------------------------------------
    # 1. Reference network scenario
    # --------------------------------------------------

    scenario = NetworkScenario(
        frequency_hz=2.5e9,
        distance_m=50.0,
        bandwidth_hz=100e6,
        operation_duration_s=360.0
    )

    simulation_parameters = SimulationParameters()

    # Wrapper to pass the physical model parameters.
    def simulator(design, scenario):
        return simulate_network(
            design=design,
            scenario=scenario,
            parameters=simulation_parameters
        )

    # --------------------------------------------------
    # 2. Initial reference configuration
    # --------------------------------------------------

    baseline_design = NetworkDesign(
        tx_power_w=21.0,
        n_antennas=8
    )

    baseline_metrics = simulator(
        baseline_design,
        scenario
    )

    # --------------------------------------------------
    # 3. Objective references
    # --------------------------------------------------

    references = ObjectiveReferences(
        sar_ref_w_kg=2.0,
        delta_t_ref_k=2.0,
        delta_vm_ref_v=0.01,
        energy_ref_j=baseline_metrics.energy_consumption_j,
        bitrate_target_mbps=100.0,
        cost_ref=baseline_metrics.infrastructure_cost
    )

    # Balanced AHP initialization:
    # all six criteria have equal importance.
    objective_weights = ObjectiveWeights(
        sar=1.0 / 6.0,
        temperature=1.0 / 6.0,
        membrane=1.0 / 6.0,
        energy=1.0 / 6.0,
        qos=1.0 / 6.0,
        cost=1.0 / 6.0
    )

    # --------------------------------------------------
    # 4. Network constraints
    # --------------------------------------------------

    constraint_limits = ConstraintLimits(
        sar_limit_w_kg=2.0,
        delta_t_limit_k=2.0,
        minimum_bitrate_mbps=100.0,
        minimum_sinr_db=5.0
    )

    penalty_weights = PenaltyWeights(
        sar=1000.0,
        temperature=1000.0,
        bitrate=100.0,
        sinr=100.0
    )

    # --------------------------------------------------
    # 5. PSO search space
    # --------------------------------------------------

    bounds = DesignBounds(
        lower=[1.0, 2.0],
        upper=[21.0, 16.0]
    )

    # Antenna count is a discrete design variable.
    allowed_antennas = [2, 4, 8, 16]

    config = PSOConfig(
        n_particles=12,
        n_iterations=20,
        inertia=0.7,
        cognitive=1.5,
        social=1.5,
        seed=42
    )

    # --------------------------------------------------
    # 6. Run optimization
    # --------------------------------------------------

    print("\nStarting RF network optimization...\n")

    result = optimize_network(
        simulator=simulator,
        scenario=scenario,
        references=references,
        objective_weights=objective_weights,
        constraint_limits=constraint_limits,
        penalty_weights=penalty_weights,
        bounds=bounds,
        config=config,
        allowed_antennas=allowed_antennas
    )

    # --------------------------------------------------
    # 7. Display results
    # --------------------------------------------------

    print("\n========== OPTIMIZATION RESULTS ==========\n")

    print(json.dumps(result, indent=4, ensure_ascii=False))

    print("\n========== FINAL VALIDATION ==========\n")

    if result["feasible"]:
        print("A feasible configuration was found.")
    else:
        print(
            "WARNING: The best candidate does not satisfy "
            "all constraints. Do not consider it an accepted solution."
        )

    print("\nBest transmit power:",
          result["best_design"]["tx_power_w"], "W")

    print("Best number of antennas:",
          result["best_design"]["n_antennas"])

    print("Objective value:",
          result["objective_value"])

    print("Constraint penalty:",
          result["constraint_penalty"])

    print("Total fitness:",
          result["total_fitness"])

    print("Feasible:",
          result["feasible"])


if __name__ == "__main__":
    main()
