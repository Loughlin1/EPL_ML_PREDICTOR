from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MatchInput(BaseModel):
    data: List[Dict[str, Any]]
    season: Optional[str] = None
