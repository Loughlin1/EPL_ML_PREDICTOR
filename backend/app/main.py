import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.endpoints import (
    content,
    evaluate,
    fixtures,
    matchweek,
    predict,
    seasons,
    superbru,
    train,
)
from .core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EPL Predictor API",
    description="Predict outcomes of EPL matches using machine learning",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.get("/api/status")
def healthcheck():
    return {"status": "ok"}


# Routers
## Model
app.include_router(train.router, prefix=settings.API_PREFIX)
app.include_router(predict.router, prefix=settings.API_PREFIX)
app.include_router(evaluate.router, prefix=settings.API_PREFIX)

## Fixtures
app.include_router(fixtures.router, prefix=settings.API_PREFIX)
app.include_router(matchweek.router, prefix=settings.API_PREFIX)
app.include_router(seasons.router, prefix=settings.API_PREFIX)

# Superbru
app.include_router(superbru.router, prefix=settings.API_PREFIX)

# Content
app.include_router(content.router, prefix=settings.API_PREFIX)
