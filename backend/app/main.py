from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import predict, train, evaluate, fixtures, matchweek, superbru

app = FastAPI(
    title="EPL Predictor API",
    description="Predict outcomes of EPL matches using machine learning",
    version="1.0.0"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(train.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(evaluate.router, prefix="/api")
app.include_router(fixtures.router, prefix="/api")
app.include_router(matchweek.router, prefix="/api")
app.include_router(superbru.router, prefix="/api")


@app.get("/api/status")
def healthcheck():
    return {"status": "ok"}
