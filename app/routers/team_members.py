"""Team Members router demonstrating union types (oneOf) in OpenAPI.

This router shows how discriminated unions work with FastAPI/Pydantic,
generating proper oneOf schemas in the OpenAPI documentation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.data import TEAM_MEMBERS
from app.models.team_members import (
    TeamMember,
    TeamMemberCreate,
    Player,
    PlayerBase,
    PlayerUpdate,
    Coach,
    CoachBase,
    CoachUpdate,
    MedicalStaff,
    MedicalStaffBase,
    MedicalStaffUpdate,
    EquipmentManager,
    EquipmentManagerBase,
    EquipmentManagerUpdate,
    MemberType,
    Position,
    CoachSpecialty,
    MedicalSpecialty,
)
from app.pagination import PaginationParams, PaginatedResponse, paginate

router = APIRouter(prefix="/team-members", tags=["Team Members"])

# In-memory storage (copy of seed data)
_members_db: dict[str, dict] = dict(TEAM_MEMBERS)


def _generate_id(name: str) -> str:
    """Generate a URL-friendly ID from a name."""
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def _dict_to_model(data: dict) -> TeamMember:
    """Convert a dictionary to the appropriate TeamMember subtype."""
    member_type = data.get("member_type")
    if member_type == MemberType.PLAYER or member_type == "player":
        return Player(**data)
    elif member_type == MemberType.COACH or member_type == "coach":
        return Coach(**data)
    elif member_type == MemberType.MEDICAL_STAFF or member_type == "medical_staff":
        return MedicalStaff(**data)
    elif member_type == MemberType.EQUIPMENT_MANAGER or member_type == "equipment_manager":
        return EquipmentManager(**data)
    else:
        raise ValueError(f"Unknown member type: {member_type}")


@router.get(
    "",
    response_model=PaginatedResponse[TeamMember],
    summary="List all team members",
    description="""Get a paginated list of all team members.

This endpoint demonstrates **union types (oneOf)** in the response.
Each team member can be one of: Player, Coach, MedicalStaff, or EquipmentManager.
The `member_type` field acts as a discriminator to determine the shape of each object.
""",
    responses={
        200: {
            "description": "Paginated list of team members (oneOf: Player, Coach, MedicalStaff, EquipmentManager)",
        }
    },
)
async def list_team_members(
    pagination: PaginationParams = Depends(),
    member_type: Optional[MemberType] = Query(None, description="Filter by member type"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
) -> PaginatedResponse[TeamMember]:
    """List all team members with optional filters and pagination."""
    members = list(_members_db.values())

    if member_type:
        members = [m for m in members if m["member_type"] == member_type.value]

    if team_id:
        members = [m for m in members if m.get("team_id") == team_id]

    paginated, total = paginate(members, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[_dict_to_model(m) for m in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{member_id}",
    response_model=TeamMember,
    summary="Get a team member by ID",
    description="""Retrieve detailed information about a specific team member.

The response is a **union type (oneOf)** - the actual shape depends on the member's type:
- **player**: Includes position, jersey_number, goals, assists
- **coach**: Includes specialty, certifications, win_rate
- **medical_staff**: Includes medical specialty, qualifications
- **equipment_manager**: Includes responsibilities, inventory
""",
    responses={
        200: {"description": "Team member details (oneOf based on member_type)"},
        404: {"description": "Team member not found"},
    },
)
async def get_team_member(member_id: str) -> TeamMember:
    """Get a specific team member by ID."""
    if member_id not in _members_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team member '{member_id}' not found. Everyone matters on this team!",
        )
    return _dict_to_model(_members_db[member_id])


@router.post(
    "",
    response_model=TeamMember,
    status_code=201,
    summary="Create a new team member",
    description="""Add a new team member to a team.

The request body is a **union type (oneOf)** - you must include the `member_type` discriminator field:
- `"member_type": "player"` - Creates a player (requires position, jersey_number, etc.)
- `"member_type": "coach"` - Creates a coach (requires specialty, etc.)
- `"member_type": "medical_staff"` - Creates medical staff (requires medical specialty, etc.)
- `"member_type": "equipment_manager"` - Creates equipment manager (requires responsibilities, etc.)

**Example for creating a player:**
```json
{
  "member_type": "player",
  "name": "Sam Obisanya",
  "team_id": "afc-richmond",
  "years_with_team": 2,
  "position": "midfielder",
  "jersey_number": 24,
  "goals_scored": 12,
  "assists": 15
}
```
""",
    responses={
        201: {"description": "Team member created successfully"},
        409: {"description": "Team member already exists"},
    },
)
async def create_team_member(member: TeamMemberCreate) -> TeamMember:
    """Create a new team member."""
    member_id = _generate_id(member.name)

    if member_id in _members_db:
        raise HTTPException(
            status_code=409,
            detail=f"Team member with ID '{member_id}' already exists. We're all unique here!",
        )

    member_data = {"id": member_id, **member.model_dump()}
    _members_db[member_id] = member_data

    return _dict_to_model(member_data)


@router.patch(
    "/{member_id}",
    response_model=TeamMember,
    summary="Update a team member",
    description="Update specific fields of an existing team member. Fields vary by member type.",
    responses={
        200: {"description": "Team member updated successfully"},
        404: {"description": "Team member not found"},
    },
)
async def update_team_member(
    member_id: str,
    updates: PlayerUpdate | CoachUpdate | MedicalStaffUpdate | EquipmentManagerUpdate,
) -> TeamMember:
    """Update an existing team member."""
    if member_id not in _members_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team member '{member_id}' not found. Can't update someone not on the roster!",
        )

    member_data = _members_db[member_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            member_data[key] = value

    return _dict_to_model(member_data)


@router.delete(
    "/{member_id}",
    status_code=204,
    summary="Delete a team member",
    description="Remove a team member from the roster.",
    responses={
        204: {"description": "Team member removed successfully"},
        404: {"description": "Team member not found"},
    },
)
async def delete_team_member(member_id: str) -> None:
    """Delete a team member."""
    if member_id not in _members_db:
        raise HTTPException(
            status_code=404,
            detail=f"Team member '{member_id}' not found.",
        )

    del _members_db[member_id]


# === Additional endpoints showcasing filtered union returns ===


@router.get(
    "/players/",
    response_model=PaginatedResponse[Player],
    summary="List all players",
    description="Get only players (filtered subset of team members).",
)
async def list_players(
    pagination: PaginationParams = Depends(),
    position: Optional[Position] = Query(None, description="Filter by position"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
) -> PaginatedResponse[Player]:
    """List all players with optional filters."""
    players = [m for m in _members_db.values() if m["member_type"] == "player"]

    if position:
        players = [p for p in players if p.get("position") == position.value]

    if team_id:
        players = [p for p in players if p.get("team_id") == team_id]

    paginated, total = paginate(players, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Player(**p) for p in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/coaches/",
    response_model=PaginatedResponse[Coach],
    summary="List all coaches",
    description="Get only coaches (filtered subset of team members).",
)
async def list_coaches(
    pagination: PaginationParams = Depends(),
    specialty: Optional[CoachSpecialty] = Query(None, description="Filter by specialty"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
) -> PaginatedResponse[Coach]:
    """List all coaches with optional filters."""
    coaches = [m for m in _members_db.values() if m["member_type"] == "coach"]

    if specialty:
        coaches = [c for c in coaches if c.get("specialty") == specialty.value]

    if team_id:
        coaches = [c for c in coaches if c.get("team_id") == team_id]

    paginated, total = paginate(coaches, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Coach(**c) for c in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/staff/",
    response_model=PaginatedResponse[MedicalStaff | EquipmentManager],
    summary="List all staff (non-player, non-coach)",
    description="""Get all staff members (medical staff and equipment managers).

This demonstrates a **narrower union type** - the response is oneOf MedicalStaff or EquipmentManager.
""",
)
async def list_staff(
    pagination: PaginationParams = Depends(),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
) -> PaginatedResponse[MedicalStaff | EquipmentManager]:
    """List all staff (medical and equipment)."""
    staff = [
        m for m in _members_db.values()
        if m["member_type"] in ["medical_staff", "equipment_manager"]
    ]

    if team_id:
        staff = [s for s in staff if s.get("team_id") == team_id]

    paginated, total = paginate(staff, pagination.skip, pagination.limit)
    result = []
    for s in paginated:
        if s["member_type"] == "medical_staff":
            result.append(MedicalStaff(**s))
        else:
            result.append(EquipmentManager(**s))

    return PaginatedResponse(
        data=result,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )
