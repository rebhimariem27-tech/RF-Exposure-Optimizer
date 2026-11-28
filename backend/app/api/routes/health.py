from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "running", "application": "RF Exposure Optimizer", "api_version": "0.2.0"}
