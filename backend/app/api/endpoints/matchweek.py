from fastapi import APIRouter
from app.services.utils.fixtures import get_fixtures_data
from app.services.utils.matchweek import get_current_matchweek

router = APIRouter(
    prefix="/matchweek",
    tags=["Matchweek"],
)

@router.get("/")
def get_matchweek():
    """
    Get current/most recent EPL matchweek.
    """
    fixtures = get_fixtures_data()
    current_matchweek = get_current_matchweek(fixtures)
    return {"current_matchweek": current_matchweek}
