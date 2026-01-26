"""API Routers for Ted Lasso API."""

from app.routers.characters import router as characters_router
from app.routers.episodes import router as episodes_router
from app.routers.interactive import router as interactive_router
from app.routers.matches import router as matches_router
from app.routers.quotes import router as quotes_router
from app.routers.streaming import router as streaming_router
from app.routers.team_members import router as team_members_router
from app.routers.teams import router as teams_router
from app.routers.websocket import router as websocket_router

__all__ = [
    "characters_router",
    "teams_router",
    "matches_router",
    "episodes_router",
    "quotes_router",
    "interactive_router",
    "streaming_router",
    "team_members_router",
    "websocket_router",
]
