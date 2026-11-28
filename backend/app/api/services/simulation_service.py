from dataclasses import asdict

from app.models.simulation import simulate_network
from app.optimization.problem import NetworkDesign, NetworkScenario


def run_simulation(request):
    design = NetworkDesign(**request.design.model_dump())
    scenario = NetworkScenario(**request.scenario.model_dump())
    scenario.validate()
    metrics = simulate_network(
        design=design,
        scenario=scenario,
        parameters=request.parameters.to_domain(),
    )
    return {
        "status": "success",
        "design": asdict(design),
        "scenario": asdict(scenario),
        "metrics": asdict(metrics),
        "model_scope": {
            "exposure_model": "1-D layered tissue model; SAR 10 g column proxy",
            "propagation_model": "far-field free-space approximation",
            "thermal_model": "1-D preliminary bioheat model",
            "membrane_model": "exploratory RC proxy; not a validated biological dosimetry model",
        },
    }
