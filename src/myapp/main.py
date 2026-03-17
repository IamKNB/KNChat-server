from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core import configure_cors, get_settings, lifespan
from myapp.router import router

settings = get_settings()

app = FastAPI(
    lifespan=lifespan,
              )

configure_cors(app, settings)
app.mount("/updates", StaticFiles(directory=settings.updates_dir), name="updates")
app.include_router(router)
