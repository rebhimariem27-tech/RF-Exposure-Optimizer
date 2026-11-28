from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.constants import APP_NAME, APP_VERSION
from app.core.config import settings
from app.models.antenna import analyze_ula
from app.schemas import SimulationConfig

app = FastAPI(
    title=APP_NAME,
    description="Simulation and optimization prototype for RF exposure and 5G/6G network trade-offs.",
    version=APP_VERSION,
)

origins = list(settings.frontend_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)


# Compatibility endpoints retained from the initial API.
@app.get("/")
def home():
    return {"message": f"Welcome to {APP_NAME}", "status": "Application is running", "documentation": "/docs"}


@app.get("/health", include_in_schema=False)
def legacy_health():
    return {"status": "running", "application": APP_NAME}


@app.get("/config/default")
def get_default_config():
    return SimulationConfig().model_dump()


@app.post("/config/validate")
def validate_config(config: SimulationConfig):
    return {"valid": True, "message": "Configuration validated successfully", "configuration": config.model_dump()}


@app.post("/antenna/analyze")
def antenna_analysis(config: SimulationConfig):
    try:
        result = analyze_ula(
            frequency_ghz=config.frequency_ghz,
            antenna_count=config.antenna_count,
            element_gain_dbi=config.element_gain_dbi,
            element_spacing_m=config.element_spacing_m,
            steering_angle_deg=config.steering_angle_deg,
            amplitudes=config.amplitudes,
            phase_offsets_deg=config.phase_offsets_deg,
        )
        return {
            "status": "success",
            "message": "ULA antenna analysis completed",
            "input_parameters": {
                "frequency_ghz": config.frequency_ghz,
                "antenna_count": config.antenna_count,
                "element_gain_dbi": config.element_gain_dbi,
                "steering_angle_deg": config.steering_angle_deg,
            },
            "antenna_results": result,
            "assumptions": [
                "Uniform Linear Array (ULA)",
                "Ideal identical antenna elements",
                "No mutual coupling",
                "Fixed total excitation power",
                "Isotropic-element approximation for array directivity",
            ],
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
