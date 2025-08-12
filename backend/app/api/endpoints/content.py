from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
import traceback

from ...core.paths import CONTENT_DIR

router = APIRouter(
    prefix="/content",
    tags=["Content"],
)
logger = logging.getLogger(__name__)


@router.get("/model_explanation")
def get_model_explanation():
    try:
        with open(f"{CONTENT_DIR}/model_explanation.json", "r") as f:
            model_explanation = json.load(f)
        return model_explanation
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Model explanation file not found",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in model explanation file",
        )
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Failed to load model explanation: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))
