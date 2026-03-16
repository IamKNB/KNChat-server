from fastapi import FastAPI

from core import configure_cors, get_settings, lifespan
from myapp.router import router

settings = get_settings()

app = FastAPI(
    lifespan=lifespan,
              )

configure_cors(app, settings)
app.include_router(router)
