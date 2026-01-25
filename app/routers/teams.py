"""Teams router for Ted Lasso API."""

import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.data import TEAMS
from app.models.teams import Team, TeamCreate, TeamUpdate, League
from app.pagination import PaginationParams, PaginatedResponse, paginate


class FileUploadResponse(BaseModel):
    """Response model for file uploads."""

    file_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
    uploaded_at: datetime

router = APIRouter(prefix="/teams", tags=["Teams"])

# In-memory storage (copy of seed data)
_teams_db: dict[str, dict] = dict(TEAMS)

# File storage for team logos
_team_files: dict[str, dict[UUID, tuple[bytes, str, str]]] = {}  # team_id -> {file_id -> (content, filename, content_type)}


def _generate_id(name: str) -> str:
    """Generate a URL-friendly ID from a name."""
    return name.lower().replace(" ", "-").replace("'", "")


@router.get(
    "",
    response_model=PaginatedResponse[Team],
    summary="List all teams",
    description="Get a paginated list of all teams with optional filtering by league or culture score.",
    responses={
        200: {
            "description": "Paginated list of teams",
        }
    },
)
async def list_teams(
    pagination: PaginationParams = Depends(),
    league: Optional[League] = Query(None, description="Filter by league"),
    min_culture_score: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum culture score"
    ),
) -> PaginatedResponse[Team]:
    """List all teams with optional filters and pagination."""
    teams = list(_teams_db.values())

    if league:
        teams = [t for t in teams if t["league"] == league.value]

    if min_culture_score is not None:
        teams = [t for t in teams if t["culture_score"] >= min_culture_score]

    paginated, total = paginate(teams, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Team(**t) for t in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{team_id}",
    response_model=Team,
    summary="Get a team by ID",
    description="Retrieve detailed information about a specific team.",
    responses={
        200: {"description": "Team details"},
        404: {"description": "Team not found"},
    },
)
async def get_team(team_id: str) -> Team:
    """Get a specific team by ID."""
    if team_id not in _teams_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team '{team_id}' not found. Maybe they got relegated to obscurity!",
        )
    return Team(**_teams_db[team_id])


@router.post(
    "",
    response_model=Team,
    status_code=201,
    summary="Create a new team",
    description="Add a new team to the league.",
    responses={
        201: {"description": "Team created successfully"},
        409: {"description": "Team already exists"},
    },
)
async def create_team(team: TeamCreate) -> Team:
    """Create a new team."""
    team_id = _generate_id(team.name)

    if team_id in _teams_db:
        raise HTTPException(
            status_code=409,
            detail=f"Team with ID '{team_id}' already exists. There's only room for one!",
        )

    team_data = {"id": team_id, **team.model_dump()}
    _teams_db[team_id] = team_data

    return Team(**team_data)


@router.patch(
    "/{team_id}",
    response_model=Team,
    summary="Update a team",
    description="Update specific fields of an existing team.",
    responses={
        200: {"description": "Team updated successfully"},
        404: {"description": "Team not found"},
    },
)
async def update_team(team_id: str, updates: TeamUpdate) -> Team:
    """Update an existing team."""
    if team_id not in _teams_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team '{team_id}' not found. Can't improve what doesn't exist!",
        )

    team_data = _teams_db[team_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            if isinstance(value, dict) and key in team_data:
                team_data[key].update(value)
            else:
                team_data[key] = value

    return Team(**team_data)


@router.delete(
    "/{team_id}",
    status_code=204,
    summary="Delete a team",
    description="Remove a team from the database (relegation to oblivion).",
    responses={
        204: {"description": "Team deleted successfully"},
        404: {"description": "Team not found"},
    },
)
async def delete_team(team_id: str) -> None:
    """Delete a team."""
    if team_id not in _teams_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team '{team_id}' not found. Already relegated!",
        )

    del _teams_db[team_id]


@router.get(
    "/{team_id}/rivals",
    response_model=list[Team],
    summary="Get team's rivals",
    description="Get all rival teams for a specific team.",
)
async def get_team_rivals(team_id: str) -> list[Team]:
    """Get a team's rivals."""
    if team_id not in _teams_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team '{team_id}' not found.",
        )

    rival_ids = _teams_db[team_id].get("rival_teams", [])
    rivals = [Team(**_teams_db[rid]) for rid in rival_ids if rid in _teams_db]

    return rivals


@router.get(
    "/{team_id}/culture",
    summary="Get team culture details",
    description="Get detailed culture and values information for a team.",
)
async def get_team_culture(team_id: str) -> dict:
    """Get detailed team culture information."""
    if team_id not in _teams_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team '{team_id}' not found.",
        )

    team = _teams_db[team_id]
    return {
        "team_name": team["name"],
        "culture_score": team["culture_score"],
        "values": team["values"],
        "culture_assessment": _assess_culture(team["culture_score"]),
    }


def _assess_culture(score: int) -> str:
    """Generate a culture assessment based on score."""
    if score >= 90:
        return "This team has embraced the BELIEVE philosophy. They're playing for each other, not just themselves."
    elif score >= 70:
        return "Good culture foundation. Keep working on vulnerability and trust."
    elif score >= 50:
        return "Room for improvement. Time for some Diamond Dogs sessions."
    else:
        return "Culture crisis. Needs immediate biscuits-with-the-boss intervention."


# =============================================================================
# FILE UPLOAD/DOWNLOAD ENDPOINTS (Logo, images, etc.)
# =============================================================================


@router.post(
    "/{team_id}/logo",
    response_model=FileUploadResponse,
    status_code=201,
    summary="Upload team logo",
    description="Upload a logo image for a team. Accepts image files (jpg, png, gif, webp).",
    responses={
        201: {"description": "Logo uploaded successfully"},
        404: {"description": "Team not found"},
        415: {"description": "Unsupported file type"},
    },
)
async def upload_team_logo(
    team_id: str,
    file: UploadFile = File(..., description="Logo image file"),
) -> FileUploadResponse:
    """Upload a team logo."""
    if team_id not in _teams_db:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    content_type = file.content_type or "application/octet-stream"
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Allowed: {', '.join(allowed_types)}",
        )

    # Read file content
    content = await file.read()
    file_id = uuid4()
    checksum = hashlib.sha256(content).hexdigest()

    # Store file
    if team_id not in _team_files:
        _team_files[team_id] = {}
    _team_files[team_id][file_id] = (content, file.filename or "logo", content_type)

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename or "logo",
        content_type=content_type,
        size_bytes=len(content),
        checksum_sha256=checksum,
        uploaded_at=datetime.now(timezone.utc),
    )


@router.get(
    "/{team_id}/logo/{file_id}",
    summary="Download team logo",
    description="Download a team's logo by file ID.",
    responses={
        200: {
            "description": "Logo file content",
            "content": {"image/*": {}},
        },
        404: {"description": "Team or file not found"},
    },
)
async def download_team_logo(team_id: str, file_id: UUID) -> Response:
    """Download a team's logo."""
    if team_id not in _teams_db:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")

    if team_id not in _team_files or file_id not in _team_files[team_id]:
        raise HTTPException(status_code=404, detail="Logo not found.")

    content, filename, content_type = _team_files[team_id][file_id]

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@router.delete(
    "/{team_id}/logo/{file_id}",
    status_code=204,
    summary="Delete team logo",
    description="Delete a team's logo.",
    responses={
        204: {"description": "Logo deleted"},
        404: {"description": "Team or file not found"},
    },
)
async def delete_team_logo(team_id: str, file_id: UUID) -> None:
    """Delete a team's logo."""
    if team_id not in _teams_db:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")

    if team_id not in _team_files or file_id not in _team_files[team_id]:
        raise HTTPException(status_code=404, detail="Logo not found.")

    del _team_files[team_id][file_id]


@router.get(
    "/{team_id}/logos",
    response_model=list[FileUploadResponse],
    summary="List team logos",
    description="List all uploaded logos for a team.",
)
async def list_team_logos(team_id: str) -> list[FileUploadResponse]:
    """List all logos for a team."""
    if team_id not in _teams_db:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")

    if team_id not in _team_files:
        return []

    logos = []
    for file_id, (content, filename, content_type) in _team_files[team_id].items():
        logos.append(
            FileUploadResponse(
                file_id=file_id,
                filename=filename,
                content_type=content_type,
                size_bytes=len(content),
                checksum_sha256=hashlib.sha256(content).hexdigest(),
                uploaded_at=datetime.now(timezone.utc),  # Simplified for demo
            )
        )

    return logos
