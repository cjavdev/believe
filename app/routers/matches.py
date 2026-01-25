"""Matches router for Ted Lasso API."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.data import MATCHES
from app.models.matches import Match, MatchCreate, MatchUpdate, MatchResult, MatchType
from app.pagination import PaginationParams, PaginatedResponse, paginate

router = APIRouter(prefix="/matches", tags=["Matches"])

# In-memory storage (copy of seed data)
_matches_db: dict[str, dict] = dict(MATCHES)

# Counter for generating IDs
_match_counter = len(_matches_db) + 1


@router.get(
    "",
    response_model=PaginatedResponse[Match],
    summary="List all matches",
    description="Get a paginated list of all matches with optional filtering.",
    responses={
        200: {
            "description": "Paginated list of matches",
        }
    },
)
async def list_matches(
    pagination: PaginationParams = Depends(),
    team_id: Optional[str] = Query(None, description="Filter by team (home or away)"),
    result: Optional[MatchResult] = Query(None, description="Filter by result"),
    match_type: Optional[MatchType] = Query(None, description="Filter by match type"),
) -> PaginatedResponse[Match]:
    """List all matches with optional filters and pagination."""
    matches = list(_matches_db.values())

    if team_id:
        matches = [
            m
            for m in matches
            if m["home_team_id"] == team_id or m["away_team_id"] == team_id
        ]

    if result:
        matches = [m for m in matches if m["result"] == result.value]

    if match_type:
        matches = [m for m in matches if m["match_type"] == match_type.value]

    paginated, total = paginate(matches, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Match(**m) for m in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{match_id}",
    response_model=Match,
    summary="Get a match by ID",
    description="Retrieve detailed information about a specific match.",
    responses={
        200: {"description": "Match details"},
        404: {"description": "Match not found"},
    },
)
async def get_match(match_id: str) -> Match:
    """Get a specific match by ID."""
    if match_id not in _matches_db:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found. Must have been played in an alternate universe!",
        )
    return Match(**_matches_db[match_id])


@router.post(
    "",
    response_model=Match,
    status_code=201,
    summary="Create a new match",
    description="Schedule a new match.",
    responses={
        201: {"description": "Match created successfully"},
    },
)
async def create_match(match: MatchCreate) -> Match:
    """Create a new match."""
    global _match_counter

    match_id = f"match-{_match_counter:03d}"
    _match_counter += 1

    match_data = {"id": match_id, **match.model_dump()}

    # Convert datetime to ISO string for storage
    if isinstance(match_data["date"], datetime):
        match_data["date"] = match_data["date"].isoformat()

    _matches_db[match_id] = match_data

    return Match(**match_data)


@router.patch(
    "/{match_id}",
    response_model=Match,
    summary="Update a match",
    description="Update specific fields of an existing match (e.g., update score).",
    responses={
        200: {"description": "Match updated successfully"},
        404: {"description": "Match not found"},
    },
)
async def update_match(match_id: str, updates: MatchUpdate) -> Match:
    """Update an existing match."""
    if match_id not in _matches_db:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found.",
        )

    match_data = _matches_db[match_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            if key == "date" and isinstance(value, datetime):
                match_data[key] = value.isoformat()
            elif isinstance(value, list):
                # For lists like turning_points, convert to dicts
                match_data[key] = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in value
                ]
            else:
                match_data[key] = value

    return Match(**match_data)


@router.delete(
    "/{match_id}",
    status_code=204,
    summary="Delete a match",
    description="Remove a match from the database.",
    responses={
        204: {"description": "Match deleted successfully"},
        404: {"description": "Match not found"},
    },
)
async def delete_match(match_id: str) -> None:
    """Delete a match."""
    if match_id not in _matches_db:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found.",
        )

    del _matches_db[match_id]


@router.get(
    "/{match_id}/turning-points",
    summary="Get match turning points",
    description="Get all turning points from a specific match.",
)
async def get_turning_points(match_id: str) -> list[dict]:
    """Get a match's turning points."""
    if match_id not in _matches_db:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found.",
        )

    return _matches_db[match_id].get("turning_points", [])


@router.get(
    "/{match_id}/lesson",
    summary="Get match lesson",
    description="Get the life lesson learned from a specific match.",
)
async def get_match_lesson(match_id: str) -> dict:
    """Get the lesson learned from a match."""
    if match_id not in _matches_db:
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found.",
        )

    match = _matches_db[match_id]
    return {
        "match_id": match_id,
        "result": match.get("result"),
        "lesson_learned": match.get(
            "lesson_learned",
            "Every match teaches us something, even if we haven't figured out what yet.",
        ),
        "ted_halftime_speech": match.get("ted_halftime_speech"),
    }
