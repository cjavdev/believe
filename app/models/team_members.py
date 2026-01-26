"""Team member models demonstrating union types (oneOf) in OpenAPI.

This module shows how to use discriminated unions in Pydantic/FastAPI
to generate oneOf schemas in OpenAPI documentation.

TeamMember references a Character by ID - character details (name, bio, etc.)
come from the Character model. TeamMember only stores role-specific data.
"""

from enum import Enum
from typing import Annotated, Literal

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
    """Base fields shared by all team member types.

    References a Character by ID rather than duplicating character data.
    """

    character_id: str = Field(
        description="ID of the character (references /characters/{id})",
        json_schema_extra={"example": "jamie-tartt"},
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
    win_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Career win rate (0.0 to 1.0)",
        json_schema_extra={"example": 0.65},
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
        json_schema_extra={
            "example": ["PhD Clinical Psychology", "Sports Psychology Certification"]
        },
    )
    license_number: str | None = Field(
        default=None,
        description="Professional license number",
        json_schema_extra={"example": "PSY-12345"},
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
        json_schema_extra={"example": ["Kit preparation", "Equipment maintenance"]},
    )
    is_head_kitman: bool = Field(
        default=False,
        description="Whether this is the head equipment manager",
        json_schema_extra={"example": True},
    )


# === Full models with ID ===


class Player(PlayerBase):
    """Full player model with ID."""

    id: str = Field(
        description="Unique identifier for this team membership",
        json_schema_extra={"example": "jamie-tartt-richmond"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "jamie-tartt-richmond",
                "member_type": "player",
                "character_id": "jamie-tartt",
                "team_id": "afc-richmond",
                "years_with_team": 3,
                "position": "forward",
                "jersey_number": 9,
                "goals_scored": 47,
                "assists": 23,
                "is_captain": False,
            }
        }
    }


class Coach(CoachBase):
    """Full coach model with ID."""

    id: str = Field(
        description="Unique identifier for this team membership",
        json_schema_extra={"example": "ted-lasso-richmond"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ted-lasso-richmond",
                "member_type": "coach",
                "character_id": "ted-lasso",
                "team_id": "afc-richmond",
                "years_with_team": 2,
                "specialty": "head_coach",
                "certifications": ["NCAA Division II"],
                "win_rate": 0.55,
            }
        }
    }


class MedicalStaff(MedicalStaffBase):
    """Full medical staff model with ID."""

    id: str = Field(
        description="Unique identifier for this team membership",
        json_schema_extra={"example": "sharon-fieldstone-richmond"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "sharon-fieldstone-richmond",
                "member_type": "medical_staff",
                "character_id": "dr-sharon",
                "team_id": "afc-richmond",
                "years_with_team": 1,
                "specialty": "sports_psychologist",
                "qualifications": ["PhD Clinical Psychology"],
                "license_number": "PSY-12345",
            }
        }
    }


class EquipmentManager(EquipmentManagerBase):
    """Full equipment manager model with ID."""

    id: str = Field(
        description="Unique identifier for this team membership",
        json_schema_extra={"example": "nate-kitman-richmond"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "nate-kitman-richmond",
                "member_type": "equipment_manager",
                "character_id": "nathan-shelley",
                "team_id": "afc-richmond",
                "years_with_team": 5,
                "responsibilities": ["Kit preparation", "Equipment maintenance"],
                "is_head_kitman": True,
            }
        }
    }


# === Union Type (oneOf) - The main attraction! ===


# This creates a discriminated union using Pydantic's Annotated + Field(discriminator=...)
# In OpenAPI/JSON Schema, this generates a "oneOf" with a discriminator mapping
TeamMember = Annotated[
    Player | Coach | MedicalStaff | EquipmentManager,
    Field(discriminator="member_type"),
]

# For create operations (without ID)
TeamMemberCreate = Annotated[
    PlayerBase | CoachBase | MedicalStaffBase | EquipmentManagerBase,
    Field(discriminator="member_type"),
]


# === Update models (all fields optional) ===


class PlayerUpdate(BaseModel):
    """Update model for players."""

    team_id: str | None = None
    years_with_team: int | None = Field(default=None, ge=0, le=50)
    position: Position | None = None
    jersey_number: int | None = Field(default=None, ge=1, le=99)
    goals_scored: int | None = Field(default=None, ge=0)
    assists: int | None = Field(default=None, ge=0)
    is_captain: bool | None = None


class CoachUpdate(BaseModel):
    """Update model for coaches."""

    team_id: str | None = None
    years_with_team: int | None = Field(default=None, ge=0, le=50)
    specialty: CoachSpecialty | None = None
    certifications: list[str] | None = None
    win_rate: float | None = Field(default=None, ge=0.0, le=1.0)


class MedicalStaffUpdate(BaseModel):
    """Update model for medical staff."""

    team_id: str | None = None
    years_with_team: int | None = Field(default=None, ge=0, le=50)
    specialty: MedicalSpecialty | None = None
    qualifications: list[str] | None = None
    license_number: str | None = None


class EquipmentManagerUpdate(BaseModel):
    """Update model for equipment managers."""

    team_id: str | None = None
    years_with_team: int | None = Field(default=None, ge=0, le=50)
    responsibilities: list[str] | None = None
    is_head_kitman: bool | None = None


# Union for updates - also demonstrates oneOf
TeamMemberUpdate = Annotated[
    PlayerUpdate | CoachUpdate | MedicalStaffUpdate | EquipmentManagerUpdate,
    Field(
        description="Update data for a team member - type determines which fields are valid"
    ),
]
