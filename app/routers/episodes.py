"""Episodes router for Ted Lasso API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.auth import verify_api_key
from app.data import EPISODES
from app.models.episodes import Episode, EpisodeCreate, EpisodeUpdate
from app.pagination import PaginationParams, PaginatedResponse, paginate

router = APIRouter(
    prefix="/episodes",
    tags=["Episodes"],
    dependencies=[Depends(verify_api_key)],
)

# In-memory storage (copy of seed data)
_episodes_db: dict[str, dict] = dict(EPISODES)


def _generate_id(season: int, episode_number: int) -> str:
    """Generate an episode ID from season and episode number."""
    return f"s{season:02d}e{episode_number:02d}"


@router.get(
    "",
    response_model=PaginatedResponse[Episode],
    summary="List all episodes",
    description="Get a paginated list of all Ted Lasso episodes with optional filtering by season.",
    responses={
        200: {
            "description": "Paginated list of episodes",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "s01e01",
                                "season": 1,
                                "episode_number": 1,
                                "title": "Pilot",
                                "director": "Tom Marshall",
                                "writer": "Jason Sudeikis, Bill Lawrence, Brendan Hunt, Joe Kelly",
                                "air_date": "2020-08-14",
                                "runtime_minutes": 32,
                                "synopsis": "American football coach Ted Lasso is hired to manage AFC Richmond, a struggling English Premier League team.",
                                "main_theme": "Taking chances and believing in yourself",
                                "ted_wisdom": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                                "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time.",
                                "character_focus": ["ted-lasso", "rebecca-welton", "coach-beard"],
                                "memorable_moments": [
                                    "Ted's first press conference",
                                    "The BELIEVE sign goes up",
                                ],
                            }
                        ],
                        "total": 34,
                        "skip": 0,
                        "limit": 20,
                        "has_more": True,
                        "page": 1,
                        "pages": 2,
                    }
                }
            },
        }
    },
)
async def list_episodes(
    pagination: PaginationParams = Depends(),
    season: Optional[int] = Query(None, ge=1, le=3, description="Filter by season"),
    character_focus: Optional[str] = Query(
        None, description="Filter by character focus (character ID)"
    ),
) -> PaginatedResponse[Episode]:
    """List all episodes with optional filters and pagination."""
    episodes = list(_episodes_db.values())

    if season:
        episodes = [e for e in episodes if e["season"] == season]

    if character_focus:
        episodes = [
            e for e in episodes if character_focus in e.get("character_focus", [])
        ]

    # Sort by season and episode number
    episodes.sort(key=lambda e: (e["season"], e["episode_number"]))

    paginated, total = paginate(episodes, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Episode(**e) for e in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{episode_id}",
    response_model=Episode,
    summary="Get an episode by ID",
    description="Retrieve detailed information about a specific episode.",
    responses={
        200: {
            "description": "Episode details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "s01e01",
                        "season": 1,
                        "episode_number": 1,
                        "title": "Pilot",
                        "director": "Tom Marshall",
                        "writer": "Jason Sudeikis, Bill Lawrence, Brendan Hunt, Joe Kelly",
                        "air_date": "2020-08-14",
                        "runtime_minutes": 32,
                        "synopsis": "American football coach Ted Lasso is hired to manage AFC Richmond, a struggling English Premier League team.",
                        "main_theme": "Taking chances and believing in yourself",
                        "ted_wisdom": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                        "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time.",
                        "character_focus": ["ted-lasso", "rebecca-welton", "coach-beard"],
                        "memorable_moments": [
                            "Ted's first press conference",
                            "The BELIEVE sign goes up",
                            "Ted tastes his first 'garbage water' (English tea)",
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Episode not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Episode 's04e01' not found. Maybe it's in the blooper reel!"
                    }
                }
            },
        },
    },
)
async def get_episode(episode_id: str) -> Episode:
    """Get a specific episode by ID."""
    if episode_id not in _episodes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Episode '{episode_id}' not found. Maybe it's in the blooper reel!",
        )
    return Episode(**_episodes_db[episode_id])


@router.post(
    "",
    response_model=Episode,
    status_code=201,
    summary="Create a new episode",
    description="Add a new episode to the series.",
    responses={
        201: {
            "description": "Episode created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "s04e01",
                        "season": 4,
                        "episode_number": 1,
                        "title": "New Beginnings",
                        "director": "MJ Delaney",
                        "writer": "Jason Sudeikis",
                        "air_date": "2025-06-01",
                        "runtime_minutes": 45,
                        "synopsis": "A new chapter begins for AFC Richmond as they face their biggest challenge yet.",
                        "main_theme": "Fresh starts and second chances",
                        "ted_wisdom": "Every ending is just a new beginning wearing a different hat.",
                        "biscuits_with_boss_moment": None,
                        "character_focus": ["ted-lasso", "roy-kent"],
                        "memorable_moments": [],
                    }
                }
            },
        },
        409: {
            "description": "Episode already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Episode 's01e01' already exists. No retcons allowed!"
                    }
                }
            },
        },
    },
)
async def create_episode(episode: EpisodeCreate) -> Episode:
    """Create a new episode."""
    episode_id = _generate_id(episode.season, episode.episode_number)

    if episode_id in _episodes_db:
        raise HTTPException(
            status_code=409,
            detail=f"Episode '{episode_id}' already exists. No retcons allowed!",
        )

    episode_data = {"id": episode_id, **episode.model_dump()}
    _episodes_db[episode_id] = episode_data

    return Episode(**episode_data)


@router.patch(
    "/{episode_id}",
    response_model=Episode,
    summary="Update an episode",
    description="Update specific fields of an existing episode.",
    responses={
        200: {
            "description": "Episode updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "s01e01",
                        "season": 1,
                        "episode_number": 1,
                        "title": "Pilot",
                        "director": "Tom Marshall",
                        "writer": "Jason Sudeikis, Bill Lawrence, Brendan Hunt, Joe Kelly",
                        "air_date": "2020-08-14",
                        "runtime_minutes": 32,
                        "synopsis": "American football coach Ted Lasso is hired to manage AFC Richmond, a struggling English Premier League team.",
                        "main_theme": "Taking chances and believing in yourself",
                        "ted_wisdom": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                        "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time, beginning their bonding ritual.",
                        "character_focus": ["ted-lasso", "rebecca-welton", "coach-beard"],
                        "memorable_moments": [
                            "Ted's first press conference",
                            "The BELIEVE sign goes up",
                            "Ted tastes his first 'garbage water' (English tea)",
                            "Ted meets Nate for the first time",
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Episode not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Episode 's04e01' not found."}
                }
            },
        },
    },
)
async def update_episode(episode_id: str, updates: EpisodeUpdate) -> Episode:
    """Update an existing episode."""
    if episode_id not in _episodes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Episode '{episode_id}' not found.",
        )

    episode_data = _episodes_db[episode_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            episode_data[key] = value

    # Regenerate ID if season or episode number changed
    if "season" in update_data or "episode_number" in update_data:
        new_id = _generate_id(
            episode_data["season"], episode_data["episode_number"]
        )
        if new_id != episode_id:
            episode_data["id"] = new_id
            _episodes_db[new_id] = episode_data
            del _episodes_db[episode_id]

    return Episode(**episode_data)


@router.delete(
    "/{episode_id}",
    status_code=204,
    summary="Delete an episode",
    description="Remove an episode from the database.",
    responses={
        204: {"description": "Episode deleted successfully"},
        404: {
            "description": "Episode not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Episode 's04e01' not found."}
                }
            },
        },
    },
)
async def delete_episode(episode_id: str) -> None:
    """Delete an episode."""
    if episode_id not in _episodes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Episode '{episode_id}' not found.",
        )

    del _episodes_db[episode_id]


@router.get(
    "/{episode_id}/wisdom",
    summary="Get episode wisdom",
    description="Get Ted's wisdom and memorable moments from a specific episode.",
    responses={
        200: {
            "description": "Episode wisdom details",
            "content": {
                "application/json": {
                    "example": {
                        "episode_id": "s01e01",
                        "title": "Pilot",
                        "main_theme": "Taking chances and believing in yourself",
                        "ted_wisdom": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                        "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time.",
                        "memorable_moments": [
                            "Ted's first press conference",
                            "The BELIEVE sign goes up",
                            "Ted tastes his first 'garbage water' (English tea)",
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Episode not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Episode 's04e01' not found."}
                }
            },
        },
    },
)
async def get_episode_wisdom(episode_id: str) -> dict:
    """Get the wisdom from an episode."""
    if episode_id not in _episodes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Episode '{episode_id}' not found.",
        )

    episode = _episodes_db[episode_id]
    return {
        "episode_id": episode_id,
        "title": episode["title"],
        "main_theme": episode["main_theme"],
        "ted_wisdom": episode["ted_wisdom"],
        "biscuits_with_boss_moment": episode.get("biscuits_with_boss_moment"),
        "memorable_moments": episode.get("memorable_moments", []),
    }


@router.get(
    "/seasons/{season_number}",
    response_model=PaginatedResponse[Episode],
    summary="Get all episodes from a season",
    description="Get a paginated list of episodes from a specific season.",
    responses={
        200: {
            "description": "Paginated list of episodes from the season",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "s01e01",
                                "season": 1,
                                "episode_number": 1,
                                "title": "Pilot",
                                "director": "Tom Marshall",
                                "writer": "Jason Sudeikis, Bill Lawrence, Brendan Hunt, Joe Kelly",
                                "air_date": "2020-08-14",
                                "runtime_minutes": 32,
                                "synopsis": "American football coach Ted Lasso is hired to manage AFC Richmond.",
                                "main_theme": "Taking chances and believing in yourself",
                                "ted_wisdom": "Taking on a challenge is a lot like riding a horse.",
                                "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time.",
                                "character_focus": ["ted-lasso", "rebecca-welton"],
                                "memorable_moments": ["Ted's first press conference"],
                            }
                        ],
                        "total": 10,
                        "skip": 0,
                        "limit": 20,
                        "has_more": False,
                        "page": 1,
                        "pages": 1,
                    }
                }
            },
        },
        404: {
            "description": "Season not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Season 4 doesn't exist. Ted Lasso has 3 seasons!"
                    }
                }
            },
        },
    },
)
async def get_season_episodes(
    season_number: int,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[Episode]:
    """Get all episodes from a season with pagination."""
    if season_number < 1 or season_number > 3:
        raise HTTPException(
            status_code=404,
            detail=f"Season {season_number} doesn't exist. Ted Lasso has 3 seasons!",
        )

    episodes = [e for e in _episodes_db.values() if e["season"] == season_number]
    episodes.sort(key=lambda e: e["episode_number"])

    paginated, total = paginate(episodes, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Episode(**e) for e in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )
