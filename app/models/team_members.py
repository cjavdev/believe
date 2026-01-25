"""Team member models demonstrating union types (oneOf) in OpenAPI.

This module shows how to use discriminated unions in Pydantic/FastAPI
to generate oneOf schemas in OpenAPI documentation.
"""

from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class MemberType(str, Enum):
    """Types of team members - used as discriminator."""

    PLAYER = "player"
    COACH = "coach"
    MEDICAL_STAFF = "medical_staff"
    EQUIPMENT_MANAGER = "equipment_manager"


class Position(str, Enum):
    """Football positions for players."""

    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"


class CoachSpecialty(str, Enum):
    """Coaching specialties."""

    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    GOALKEEPING_COACH = "goalkeeping_coach"
    FITNESS_COACH = "fitness_coach"
    TACTICAL_ANALYST = "tactical_analyst"


class MedicalSpecialty(str, Enum):
    """Medical staff specialties."""

    TEAM_DOCTOR = "team_doctor"
    PHYSIOTHERAPIST = "physiotherapist"
    SPORTS_PSYCHOLOGIST = "sports_psychologist"
    NUTRITIONIST = "nutritionist"
    MASSAGE_THERAPIST = "massage_therapist"


# === Base fields shared by all member types ===


class TeamMemberBase(BaseModel):
    """Base fields shared by all team member types."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Full name of the team member",
        json_schema_extra={"example": "Jamie Tartt"},
    )
    team_id: str = Field(
        description="ID of the team they belong to",
        json_schema_extra={"example": "afc-richmond"},
    )
    years_with_team: int = Field(
        ge=0,
        le=50,
        description="Number of years with the current team",
        json_schema_extra={"example": 3},
    )
    bio: Optional[str] = Field(
        default=None,
        description="Short biography",
        json_schema_extra={"example": "A talented but initially arrogant striker who grows throughout the series."},
    )


# === Specific member type models ===


class PlayerBase(TeamMemberBase):
    """A football player on the team."""

    member_type: Literal[MemberType.PLAYER] = Field(
        default=MemberType.PLAYER,
        description="Discriminator field indicating this is a player",
    )
    position: Position = Field(
        description="Playing position on the field",
        json_schema_extra={"example": "forward"},
    )
    jersey_number: int = Field(
        ge=1,
        le=99,
        description="Jersey/shirt number",
        json_schema_extra={"example": 9},
    )
    goals_scored: int = Field(
        ge=0,
        default=0,
        description="Total goals scored for the team",
        json_schema_extra={"example": 47},
    )
    assists: int = Field(
        ge=0,
        default=0,
        description="Total assists for the team",
        json_schema_extra={"example": 23},
    )
    is_captain: bool = Field(
        default=False,
        description="Whether this player is team captain",
        json_schema_extra={"example": False},
    )
    preferred_foot: str = Field(
        default="right",
        description="Preferred foot (left/right/both)",
        json_schema_extra={"example": "right"},
    )


class CoachBase(TeamMemberBase):
    """A coach or coaching staff member."""

    member_type: Literal[MemberType.COACH] = Field(
        default=MemberType.COACH,
        description="Discriminator field indicating this is a coach",
    )
    specialty: CoachSpecialty = Field(
        description="Coaching specialty/role",
        json_schema_extra={"example": "head_coach"},
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Coaching certifications and licenses",
        json_schema_extra={"example": ["UEFA Pro License", "FA Level 4"]},
    )
    previous_teams: list[str] = Field(
        default_factory=list,
        description="Previous teams coached",
        json_schema_extra={"example": ["Wichita State Shockers"]},
    )
    win_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Career win rate (0.0 to 1.0)",
        json_schema_extra={"example": 0.65},
    )
    philosophy: Optional[str] = Field(
        default=None,
        description="Coaching philosophy",
        json_schema_extra={"example": "Believe in your players, and they'll believe in themselves."},
    )


class MedicalStaffBase(TeamMemberBase):
    """Medical and wellness staff member."""

    member_type: Literal[MemberType.MEDICAL_STAFF] = Field(
        default=MemberType.MEDICAL_STAFF,
        description="Discriminator field indicating this is medical staff",
    )
    specialty: MedicalSpecialty = Field(
        description="Medical specialty",
        json_schema_extra={"example": "sports_psychologist"},
    )
    qualifications: list[str] = Field(
        default_factory=list,
        description="Medical qualifications and degrees",
        json_schema_extra={"example": ["PhD Clinical Psychology", "Sports Psychology Certification"]},
    )
    license_number: Optional[str] = Field(
        default=None,
        description="Professional license number",
        json_schema_extra={"example": "PSY-12345"},
    )
    patients_treated: int = Field(
        ge=0,
        default=0,
        description="Number of team members treated/supported",
        json_schema_extra={"example": 25},
    )


class EquipmentManagerBase(TeamMemberBase):
    """Equipment and kit management staff."""

    member_type: Literal[MemberType.EQUIPMENT_MANAGER] = Field(
        default=MemberType.EQUIPMENT_MANAGER,
        description="Discriminator field indicating this is an equipment manager",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="List of responsibilities",
        json_schema_extra={"example": ["Kit preparation", "Equipment maintenance", "Travel logistics"]},
    )
    inventory_count: int = Field(
        ge=0,
        default=0,
        description="Number of items in inventory",
        json_schema_extra={"example": 500},
    )
    is_head_kitman: bool = Field(
        default=False,
        description="Whether this is the head equipment manager",
        json_schema_extra={"example": True},
    )
    match_day_role: Optional[str] = Field(
        default=None,
        description="Specific role on match days",
        json_schema_extra={"example": "First team kit preparation and pitch-side equipment"},
    )


# === Full models with ID ===


class Player(PlayerBase):
    """Full player model with ID."""

    id: str = Field(
        description="Unique identifier",
        json_schema_extra={"example": "jamie-tartt"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "jamie-tartt",
                "member_type": "player",
                "name": "Jamie Tartt",
                "team_id": "afc-richmond",
                "years_with_team": 3,
                "bio": "A talented striker who evolved from arrogant to team-first player.",
                "position": "forward",
                "jersey_number": 9,
                "goals_scored": 47,
                "assists": 23,
                "is_captain": False,
                "preferred_foot": "right",
            }
        }
    }


class Coach(CoachBase):
    """Full coach model with ID."""

    id: str = Field(
        description="Unique identifier",
        json_schema_extra={"example": "ted-lasso-coach"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ted-lasso-coach",
                "member_type": "coach",
                "name": "Ted Lasso",
                "team_id": "afc-richmond",
                "years_with_team": 2,
                "bio": "American football coach turned English football manager.",
                "specialty": "head_coach",
                "certifications": ["NCAA Division II"],
                "previous_teams": ["Wichita State Shockers"],
                "win_rate": 0.55,
                "philosophy": "Believe in believe.",
            }
        }
    }


class MedicalStaff(MedicalStaffBase):
    """Full medical staff model with ID."""

    id: str = Field(
        description="Unique identifier",
        json_schema_extra={"example": "dr-sharon-fieldstone"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "dr-sharon-fieldstone",
                "member_type": "medical_staff",
                "name": "Dr. Sharon Fieldstone",
                "team_id": "afc-richmond",
                "years_with_team": 1,
                "bio": "Team sports psychologist who helps players with mental health.",
                "specialty": "sports_psychologist",
                "qualifications": ["PhD Clinical Psychology", "Sports Psychology Certification"],
                "license_number": "PSY-12345",
                "patients_treated": 25,
            }
        }
    }


class EquipmentManager(EquipmentManagerBase):
    """Full equipment manager model with ID."""

    id: str = Field(
        description="Unique identifier",
        json_schema_extra={"example": "nathan-shelley-kitman"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "nathan-shelley-kitman",
                "member_type": "equipment_manager",
                "name": "Nathan Shelley",
                "team_id": "afc-richmond",
                "years_with_team": 5,
                "bio": "Former kit man who showed tactical genius.",
                "responsibilities": ["Kit preparation", "Equipment maintenance"],
                "inventory_count": 500,
                "is_head_kitman": True,
                "match_day_role": "First team kit preparation",
            }
        }
    }


# === Union Type (oneOf) - The main attraction! ===


# This creates a discriminated union using Pydantic's Annotated + Field(discriminator=...)
# In OpenAPI/JSON Schema, this generates a "oneOf" with a discriminator mapping
TeamMember = Annotated[
    Union[Player, Coach, MedicalStaff, EquipmentManager],
    Field(discriminator="member_type"),
]

# For create operations (without ID)
TeamMemberCreate = Annotated[
    Union[PlayerBase, CoachBase, MedicalStaffBase, EquipmentManagerBase],
    Field(discriminator="member_type"),
]


# === Update models (all fields optional) ===


class PlayerUpdate(BaseModel):
    """Update model for players."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    team_id: Optional[str] = None
    years_with_team: Optional[int] = Field(default=None, ge=0, le=50)
    bio: Optional[str] = None
    position: Optional[Position] = None
    jersey_number: Optional[int] = Field(default=None, ge=1, le=99)
    goals_scored: Optional[int] = Field(default=None, ge=0)
    assists: Optional[int] = Field(default=None, ge=0)
    is_captain: Optional[bool] = None
    preferred_foot: Optional[str] = None


class CoachUpdate(BaseModel):
    """Update model for coaches."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    team_id: Optional[str] = None
    years_with_team: Optional[int] = Field(default=None, ge=0, le=50)
    bio: Optional[str] = None
    specialty: Optional[CoachSpecialty] = None
    certifications: Optional[list[str]] = None
    previous_teams: Optional[list[str]] = None
    win_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    philosophy: Optional[str] = None


class MedicalStaffUpdate(BaseModel):
    """Update model for medical staff."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    team_id: Optional[str] = None
    years_with_team: Optional[int] = Field(default=None, ge=0, le=50)
    bio: Optional[str] = None
    specialty: Optional[MedicalSpecialty] = None
    qualifications: Optional[list[str]] = None
    license_number: Optional[str] = None
    patients_treated: Optional[int] = Field(default=None, ge=0)


class EquipmentManagerUpdate(BaseModel):
    """Update model for equipment managers."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    team_id: Optional[str] = None
    years_with_team: Optional[int] = Field(default=None, ge=0, le=50)
    bio: Optional[str] = None
    responsibilities: Optional[list[str]] = None
    inventory_count: Optional[int] = Field(default=None, ge=0)
    is_head_kitman: Optional[bool] = None
    match_day_role: Optional[str] = None


# Union for updates - also demonstrates oneOf
TeamMemberUpdate = Annotated[
    Union[PlayerUpdate, CoachUpdate, MedicalStaffUpdate, EquipmentManagerUpdate],
    Field(description="Update data for a team member - type determines which fields are valid"),
]
