from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.optimization import router as optimization_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(simulation_router)
api_router.include_router(optimization_router)
