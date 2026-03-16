from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import get_settings, lifespan
from myapp.router import router

settings = get_settings()

def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


app = FastAPI(
    lifespan=lifespan,
              )

configured_origins = _parse_cors_origins(settings.cors_allow_origins)
env = settings.app_env.lower().strip()
if configured_origins:
    cors_origins = configured_origins
elif env in {"dev", "development", "local"}:
    cors_origins = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
    ]
else:
    cors_origins = [
        "tauri://localhost",
        "https://tauri.localhost",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)
