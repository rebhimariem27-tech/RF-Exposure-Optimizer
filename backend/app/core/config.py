import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "RF Exposure Optimizer")
    app_version: str = os.getenv("APP_VERSION", "0.2.0")
    frontend_origins: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if item.strip()
    )


settings = Settings()
