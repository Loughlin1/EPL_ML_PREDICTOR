from fastapi import APIRouter, HTTPException
from app.services.models.train import train_model

router = APIRouter()

@router.post("/train")
def run_training():
    try:
        result = train_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
