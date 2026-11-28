from fastapi import APIRouter, HTTPException

from app.api.services.optimization_service import run_optimization
from app.schemas import OptimizationRunRequest

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.post("/run")
def optimization_run(request: OptimizationRunRequest):
    try:
        return run_optimization(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
