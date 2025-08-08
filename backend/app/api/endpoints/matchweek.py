from fastapi import APIRouter
from app.services.data_processing.data_loader import get_this_seasons_fixtures_data
from app.services.utils.matchweek import get_current_matchweek

router = APIRouter()

@router.get("/matchweek")
def get_matchweek():
    """
    Get current/most recent EPL matchweek.
    """
    fixtures = get_this_seasons_fixtures_data()
    current_matchweek = get_current_matchweek(fixtures)
    return {"current_matchweek": current_matchweek}
