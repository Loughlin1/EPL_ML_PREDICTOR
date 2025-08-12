from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import (
    predict,
    train,
    evaluate,
    fixtures,
    matchweek,
    superbru,
    content,
)

from .core.config import settings

app = FastAPI(
    title="EPL Predictor API",
    description="Predict outcomes of EPL matches using machine learning",
    version="1.0.0",
    docs_url="/docs",
)
print(settings)
# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Superbru
app.include_router(superbru.router, prefix=settings.API_PREFIX)

# Content
app.include_router(content.router, prefix=settings.API_PREFIX)
