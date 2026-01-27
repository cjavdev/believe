"""Ted Lasso API - Believe in the power of positivity.

A comprehensive API celebrating the wisdom, humor, and heart of Ted Lasso.
Perfect for SDK demos showcasing REST API features.
"""

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import verify_api_key
from app.middleware.versioning import (
    DEFAULT_VERSION,
    SUPPORTED_VERSIONS,
    APIVersionMiddleware,
    get_api_version,
)
from app.routers import (
    characters_router,
    episodes_router,
    interactive_router,
    matches_router,
    quotes_router,
    streaming_router,
    team_members_router,
    teams_router,
    websocket_router,
)

# Create the FastAPI application
# Note: Auth dependency is applied per-router to allow WebSocket endpoints to work
# (HTTPBearer doesn't support WebSocket connections)
app = FastAPI(
    title="Ted Lasso API",
    description="""
## Believe in the Power of Positivity!

A comprehensive API celebrating the wisdom, humor, and heart of Ted Lasso.
Perfect for SDK demos showcasing various REST API features.

### Features

- **CRUD Operations**: Full Create, Read, Update, Delete for all resources
- **Rich Data Models**: Characters, Teams, Matches, Episodes, and Quotes
- **Union Types (oneOf)**: Team Members demonstrate discriminated unions
- **Interactive Endpoints**: Believe Engine, Conflict Resolution, and more
- **SSE Streaming**: Real-time pep talks and match commentary
- **Custom Easter Eggs**: Special HTTP status codes for fun

### Core Resources

- **Characters**: Ted, Roy Kent, Rebecca, Jamie, and the whole gang
- **Teams**: AFC Richmond, Manchester City, West Ham, and more
- **Matches**: Historic matches with turning points and lessons learned
- **Episodes**: Full episode guide with Ted's wisdom
- **Quotes**: Searchable collection of memorable quotes

### Interactive Endpoints

- **POST /believe**: The Believe Engine - get motivational guidance
- **POST /conflicts/resolve**: Diamond Dogs-style conflict resolution
- **POST /reframe**: Transform negative thoughts positively
- **POST /press**: Press conference simulator
- **GET /coaching/principles**: Ted's coaching philosophy
- **GET /biscuits**: Biscuits as a Service!

### Streaming (Server-Sent Events)

- **GET /pep-talk**: Pep talk from Ted (add `?stream=true` for SSE)
- **POST /matches/{id}/commentary/stream**: Live match commentary

### WebSocket (Real-time)

- **WS /matches/live**: Live match simulation with real-time events (goals, fouls, cards, etc.)
- **WS /ws/test**: Simple WebSocket echo test endpoint

### Data Types Coverage

All common API data types are integrated across our models:
- **Characters**: date (birth), float (height), decimal (salary), email, URL (profile image)
- **Teams**: float (attendance, win %), decimal (budget), URL (website), email, GeoLocation (lat/long)
- **Episodes**: date (air date), float (viewer rating, viewers in millions)
- **Matches**: datetime, float (possession, temperature), decimal (revenue)
- **Quotes**: float (popularity score), int (shares)
- **File uploads**: POST /teams/{id}/logo for image uploads

### Easter Eggs

- **429**: "Too Much Negativity" - when you need to be more positive
- **403**: "Judgment Without Curiosity" - be curious, not judgmental
- **418**: "I'm a Believer!" - when you believe too much (is that possible?)

### API Versioning

This API supports header-based versioning using date format (YYYY-MM-DD).
Include one of these headers in your request:

- `X-API-Version: 2026-01-20` (preferred)
- `API-Version: 2026-01-20`

Response headers will include:
- `X-API-Version`: The version used for the request
- `X-API-Supported-Versions`: List of all supported versions

If no version header is provided, the API defaults to the latest stable version.

*"Be curious, not judgmental."* - Ted Lasso
    """,
    version="2026-01-20",
    contact={
        "name": "AFC Richmond Technical Team",
        "email": "believe@afcrichmond.com",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
    servers=[
        {"url": "https://believe.cjav.dev", "description": "Production"},
    ],
    openapi_tags=[
        {
            "name": "Characters",
            "description": "Operations related to Ted Lasso characters",
        },
        {
            "name": "Teams",
            "description": "Operations related to football teams",
        },
        {
            "name": "Matches",
            "description": "Operations related to football matches",
        },
        {
            "name": "Episodes",
            "description": "Operations related to TV episodes",
        },
        {
            "name": "Quotes",
            "description": "Memorable quotes from the show",
        },
        {
            "name": "Interactive",
            "description": "Interactive endpoints for motivation and guidance",
        },
        {
            "name": "Streaming",
            "description": "Server-Sent Events (SSE) streaming endpoints",
        },
        {
            "name": "WebSocket",
            "description": "WebSocket endpoints for real-time bidirectional communication - Live match simulation",
        },
        {
            "name": "Team Members",
            "description": "Team members with union types (oneOf) - Players, Coaches, Medical Staff, Equipment Managers",
        },
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API versioning middleware
app.add_middleware(APIVersionMiddleware)

# Include routers
app.include_router(characters_router)
app.include_router(teams_router)
app.include_router(matches_router)
app.include_router(episodes_router)
app.include_router(quotes_router)
app.include_router(interactive_router)
app.include_router(streaming_router)
app.include_router(websocket_router)
app.include_router(team_members_router)


# Root endpoint
@app.get(
    "/",
    summary="Welcome to the Ted Lasso API",
    dependencies=[Depends(verify_api_key)],
    description="Get a warm welcome and overview of available endpoints.",
    tags=["Root"],
    responses={
        200: {
            "description": "Welcome message and API overview",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to the Ted Lasso API! Believe!",
                        "version": "1.0.0",
                        "ted_says": "Hey there, friend! You've made it to the Ted Lasso API. Now that's what I call a good decision!",
                        "endpoints": {
                            "characters": "/characters",
                            "teams": "/teams",
                            "matches": "/matches",
                            "episodes": "/episodes",
                            "quotes": "/quotes",
                            "believe_engine": "/believe",
                            "conflict_resolution": "/conflicts/resolve",
                            "reframe": "/reframe",
                            "press_conference": "/press",
                            "coaching_principles": "/coaching/principles",
                            "biscuits": "/biscuits",
                            "pep_talk": "/pep-talk",
                            "live_match_websocket": "ws://localhost:8000/matches/live",
                            "documentation": "/docs",
                        },
                        "tip": "Try GET /quotes/random for some instant wisdom!",
                    }
                }
            },
        }
    },
)
async def root(request: Request):
    """Welcome endpoint with API overview."""
    current_version = get_api_version(request)
    return {
        "message": "Welcome to the Ted Lasso API! Believe!",
        "version": current_version,
        "supported_versions": SUPPORTED_VERSIONS,
        "default_version": DEFAULT_VERSION,
        "ted_says": "Hey there, friend! You've made it to the Ted Lasso API. "
        "Now that's what I call a good decision!",
        "endpoints": {
            "characters": "/characters",
            "teams": "/teams",
            "team_members": "/team-members",
            "matches": "/matches",
            "episodes": "/episodes",
            "quotes": "/quotes",
            "believe_engine": "/believe",
            "conflict_resolution": "/conflicts/resolve",
            "reframe": "/reframe",
            "press_conference": "/press",
            "coaching_principles": "/coaching/principles",
            "biscuits": "/biscuits",
            "pep_talk": "/pep-talk",
            "live_match_websocket": "ws://{host}/matches/live",
            "documentation": "/docs",
        },
        "tip": "Try GET /quotes/random for some instant wisdom, or connect to /matches/live via WebSocket for a live match!",
    }


# Health check endpoint
@app.get(
    "/health",
    summary="Health Check",
    dependencies=[Depends(verify_api_key)],
    description="Check if the API is running and healthy.",
    tags=["Root"],
    responses={
        200: {
            "description": "API health status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "message": "The API is running smoother than Ted's mustache!",
                        "believe_level": "maximum",
                    }
                }
            },
        }
    },
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "The API is running smoother than Ted's mustache!",
        "believe_level": "maximum",
    }


# Version endpoint
@app.get(
    "/version",
    summary="API Version Information",
    dependencies=[Depends(verify_api_key)],
    description="Get detailed information about API versioning.",
    tags=["Root"],
)
async def version_info(request: Request):
    """Get API version information."""
    current_version = get_api_version(request)
    return {
        "current_version": current_version,
        "default_version": DEFAULT_VERSION,
        "supported_versions": SUPPORTED_VERSIONS,
        "versioning": {
            "header": "X-API-Version",
            "alternative_header": "API-Version",
            "format": "YYYY-MM-DD (e.g., 2026-01-20)",
        },
        "ted_says": "Versions are like growth, friend. "
        "We keep getting better, but we never forget where we came from!",
    }


# Custom exception handler for 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler with Ted Lasso flair."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "Hmm, couldn't find what you're looking for. "
            "But hey, sometimes the best discoveries happen when we get a little lost!",
            "ted_advice": "Keep exploring, friend. The journey is the destination.",
            "path": str(request.url.path),
        },
    )


# Custom exception handler for 500
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler with Ted Lasso flair."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Well, that's not ideal. But you know what? "
            "Every setback is a setup for a comeback!",
            "ted_advice": "Take a breath, be a goldfish, and try again.",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
