from fastapi import APIRouter, HTTPException

from app.api.services.simulation_service import run_simulation
from app.schemas import SimulationRunRequest

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run")
def simulation_run(request: SimulationRunRequest):
    try:
        return run_simulation(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
