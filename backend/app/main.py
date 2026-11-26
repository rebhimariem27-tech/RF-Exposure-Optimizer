from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import SimulationConfig
from app.models.antenna import analyze_ula
from fastapi import HTTPException

# Initialisation de l'application
app = FastAPI(
    title="RF Exposure Optimizer API",
    description="5G/6G electromagnetic exposure simulation and optimization",
    version="0.1.0"
)


# Autoriser les échanges avec notre frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Vérifier que le serveur fonctionne
@app.get("/health")
def health_check():

    return {
        "status": "running",
        "application": "RF Exposure Optimizer"
    }

@app.get("/")
def home():

    return {
        "message": "Welcome to RF Exposure Optimizer",
        "status": "Application is running",
        "documentation": "/docs"
    }
# Obtenir la configuration par défaut
@app.get("/config/default")
def get_default_config():

    config = SimulationConfig()

    return config.model_dump()


# Vérifier une configuration envoyée par l'utilisateur
@app.post("/config/validate")
def validate_config(config: SimulationConfig):

    return {
        "valid": True,
        "message": "Configuration validated successfully",
        "configuration": config.model_dump()
    }
# ==========================================
# ANTENNA ANALYSIS
# ==========================================

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
            phase_offsets_deg=config.phase_offsets_deg
        )

        return {
            "status": "success",

            "message": "ULA antenna analysis completed",

            "input_parameters": {
                "frequency_ghz": config.frequency_ghz,
                "antenna_count": config.antenna_count,
                "element_gain_dbi": config.element_gain_dbi,
                "steering_angle_deg": config.steering_angle_deg
            },

            "antenna_results": result,

            "assumptions": [
                "Uniform Linear Array (ULA)",
                "Ideal identical antenna elements",
                "No mutual coupling",
                "Fixed total excitation power",
                "Isotropic-element approximation for array directivity"
            ]
        }

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )