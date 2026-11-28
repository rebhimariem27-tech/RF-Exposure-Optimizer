from dataclasses import asdict

from app.models.simulation import simulate_network
from app.optimization.configuration import DesignBounds, PSOConfig
from app.optimization.constraints import ConstraintLimits, PenaltyWeights
from app.optimization.objective import ObjectiveReferences, ObjectiveWeights
from app.optimization.problem import NetworkDesign, NetworkScenario, optimize_network


def run_optimization(request):
    scenario = NetworkScenario(**request.scenario.model_dump())
    scenario.validate()
    parameters = request.parameters.to_domain()
    baseline_design = NetworkDesign(**request.baseline_design.model_dump())

    def simulator(design, selected_scenario):
        return simulate_network(
            design=design,
            scenario=selected_scenario,
            parameters=parameters,
        )

    baseline_metrics = simulator(baseline_design, scenario)

    refs_input = request.references
    references = ObjectiveReferences(
        sar_ref_w_kg=refs_input.sar_ref_w_kg,
        delta_t_ref_k=refs_input.delta_t_ref_k,
        delta_vm_ref_v=refs_input.delta_vm_ref_v,
        energy_ref_j=refs_input.energy_ref_j or baseline_metrics.energy_consumption_j,
        bitrate_target_mbps=refs_input.bitrate_target_mbps,
        cost_ref=refs_input.cost_ref or baseline_metrics.infrastructure_cost,
    )
    objective_weights = ObjectiveWeights(**request.weights.model_dump())
    constraints = ConstraintLimits(**request.constraints.model_dump())
    penalties = PenaltyWeights(**request.penalties.model_dump())
    pso_config = PSOConfig(**request.pso.model_dump())
    bounds = DesignBounds(
        lower=[request.bounds.min_tx_power_w, float(request.bounds.min_antennas)],
        upper=[request.bounds.max_tx_power_w, float(request.bounds.max_antennas)],
    )

    result = optimize_network(
        simulator=simulator,
        scenario=scenario,
        references=references,
        objective_weights=objective_weights,
        constraint_limits=constraints,
        penalty_weights=penalties,
        bounds=bounds,
        config=pso_config,
        allowed_antennas=request.allowed_antennas,
    )

    return {
        "status": "success",
        "baseline": {
            "design": asdict(baseline_design),
            "metrics": asdict(baseline_metrics),
        },
        "optimization": result,
        "comparison": _build_comparison(asdict(baseline_metrics), result["metrics"]),
        "model_scope": {
            "note": "Optimization is valid only within the assumptions and limitations of the current prototype models.",
            "sar": "The reported 10 g value is a 1-D column proxy, not a regulatory 3-D SAR 10 g compliance result.",
            "membrane": "The membrane voltage is an exploratory RC proxy.",
        },
    }


def _build_comparison(baseline: dict, optimized: dict) -> dict:
    comparison = {}
    for key, before in baseline.items():
        after = optimized[key]
        difference = after - before
        comparison[key] = {
            "baseline": before,
            "optimized": after,
            "absolute_change": difference,
            "relative_change_percent": (difference / before * 100.0) if before != 0 else None,
        }
    return comparison
