"""Teams router for Ted Lasso API."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.data import TEAMS
from app.models.teams import Team, TeamCreate, TeamUpdate, League

router = APIRouter(prefix="/teams", tags=["Teams"])

# In-memory storage (copy of seed data)
_teams_db: dict[str, dict] = dict(TEAMS)


def _generate_id(name: str) -> str:
    """Generate a URL-friendly ID from a name."""
    return name.lower().replace(" ", "-").replace("'", "")


@router.get(
    "",
    response_model=list[Team],
    summary="List all teams",
    description="Get a list of all teams with optional filtering by league or culture score.",
    responses={
        200: {
            "description": "List of teams",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "afc-richmond",
                            "name": "AFC Richmond",
                            "nickname": "The Greyhounds",
                            "league": "Premier League",
                            "stadium": "Nelson Road",
                            "founded_year": 1897,
                            "culture_score": 95,
                            "values": {
                                "primary_value": "Believe",
                                "secondary_values": ["Family", "Resilience"],
                                "team_motto": "Football is life!",
                            },
                            "rival_teams": ["west-ham"],
                        }
                    ]
                }
            },
        }
    },
)
async def list_teams(
    league: Optional[League] = Query(None, description="Filter by league"),
    min_culture_score: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum culture score"
    ),
) -> list[Team]:
    """List all teams with optional filters."""
    teams = list(_teams_db.values())

    if league:
        teams = [t for t in teams if t["league"] == league.value]

    if min_culture_score is not None:
        teams = [t for t in teams if t["culture_score"] >= min_culture_score]

    return [Team(**t) for t in teams]


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
