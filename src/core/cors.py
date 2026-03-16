from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings, get_settings


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _build_prod_origins(settings: Settings) -> list[str]:
    configured = _parse_cors_origins(settings.cors_prod_origins)
    if configured:
        return configured
    scheme = settings.tauri_app_scheme.strip() or "tauri"
    https_prefix = "https" if settings.tauri_use_https_scheme else "http"
    return [
        f"{scheme}://localhost",
        f"{https_prefix}://{scheme}.localhost",
    ]


def _build_dev_origins(settings: Settings) -> list[str]:
    configured = _parse_cors_origins(settings.cors_dev_origins)
    if configured:
        return configured
    defaults = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
    ]
    if settings.tauri_dev_host:
        host = settings.tauri_dev_host.strip()
        if host:
            defaults.append(f"http://{host}:{settings.tauri_dev_port}")
    return defaults


def _resolve_cors_origins(settings: Settings) -> list[str]:
    configured_origins = _parse_cors_origins(settings.cors_allow_origins)
    env = settings.app_env.lower().strip()
    if configured_origins:
        return configured_origins
    if env in {"dev", "development", "local"}:
        return _dedupe(_build_dev_origins(settings) + _build_prod_origins(settings))
    return _build_prod_origins(settings)


def configure_cors(app: FastAPI, settings: Settings | None = None) -> None:
    resolved_settings = settings or get_settings()
    cors_origins = _resolve_cors_origins(resolved_settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=resolved_settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
