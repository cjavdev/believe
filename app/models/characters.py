"""Character models for Ted Lasso API."""

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CharacterRole(str, Enum):
    """Roles characters can have."""

    COACH = "coach"
    PLAYER = "player"
    OWNER = "owner"
    MANAGER = "manager"
    STAFF = "staff"
    JOURNALIST = "journalist"
    FAMILY = "family"
    FRIEND = "friend"
    FAN = "fan"
    OTHER = "other"


class EmotionalStats(BaseModel):
    """Emotional intelligence statistics for a character."""

    optimism: int = Field(
        ge=0,
        le=100,
        description="Level of optimism (0-100)",
        json_schema_extra={"example": 95},
    )
    vulnerability: int = Field(
        ge=0,
        le=100,
        description="Willingness to be vulnerable (0-100)",
        json_schema_extra={"example": 80},
    )
    empathy: int = Field(
        ge=0,
        le=100,
        description="Capacity for empathy (0-100)",
        json_schema_extra={"example": 100},
    )
    resilience: int = Field(
        ge=0,
        le=100,
        description="Bounce-back ability (0-100)",
        json_schema_extra={"example": 90},
    )
    curiosity: int = Field(
        ge=0,
        le=100,
        description="Level of curiosity over judgment (0-100)",
        json_schema_extra={"example": 99},
    )


class GrowthArc(BaseModel):
    """Character development arc."""

    season: int = Field(ge=1, le=3, description="Season number")
    starting_point: str = Field(description="Where the character starts emotionally")
    challenge: str = Field(description="Main challenge faced")
    breakthrough: str = Field(description="Key breakthrough moment")
    ending_point: str = Field(description="Where the character ends up")


class CharacterBase(BaseModel):
    """Base character model with common fields."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Character's full name",
        json_schema_extra={"example": "Ted Lasso"},
    )
    role: CharacterRole = Field(
        description="Character's role", json_schema_extra={"example": "coach"}
    )
    team_id: str | None = Field(
        default=None,
        description="ID of the team they belong to",
        json_schema_extra={"example": "afc-richmond"},
    )
    date_of_birth: date | None = Field(
        default=None,
        description="Character's date of birth",
        json_schema_extra={"example": "1970-09-22"},
    )
    email: EmailStr | None = Field(
        default=None,
        description="Character's email address",
        json_schema_extra={"example": "ted.lasso@afcrichmond.com"},
    )
    profile_image_url: HttpUrl | None = Field(
        default=None,
        description="URL to character's profile image",
        json_schema_extra={"example": "https://afcrichmond.com/images/ted-lasso.jpg"},
    )
    salary_gbp: Decimal | None = Field(
        default=None,
        decimal_places=2,
        description="Annual salary in GBP",
        json_schema_extra={"example": "150000.00"},
    )
    height_meters: float | None = Field(
        default=None,
        ge=1.0,
        le=2.5,
        description="Height in meters",
        json_schema_extra={"example": 1.83},
    )
    background: str = Field(
        description="Character background and history",
        json_schema_extra={
            "example": "Former American football coach from Kansas who moved to London to coach AFC Richmond"
        },
    )
    personality_traits: list[str] = Field(
        description="Key personality traits",
        json_schema_extra={"example": ["optimistic", "kind", "folksy", "persistent"]},
    )
    emotional_stats: EmotionalStats = Field(description="Emotional intelligence stats")
    signature_quotes: list[str] = Field(
        default_factory=list,
        description="Memorable quotes from this character",
        json_schema_extra={
            "example": [
                "I believe in believe.",
                "Be curious, not judgmental.",
            ]
        },
    )
    growth_arcs: list[GrowthArc] = Field(
        default_factory=list, description="Character development across seasons"
    )


class CharacterCreate(CharacterBase):
    """Model for creating a new character."""

    pass


class CharacterUpdate(BaseModel):
    """Model for updating a character (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    role: CharacterRole | None = None
    team_id: str | None = None
    date_of_birth: date | None = None
    email: EmailStr | None = None
    profile_image_url: HttpUrl | None = None
    salary_gbp: Decimal | None = Field(default=None, decimal_places=2)
    height_meters: float | None = Field(default=None, ge=1.0, le=2.5)
    background: str | None = None
    personality_traits: list[str] | None = None
    emotional_stats: EmotionalStats | None = None
    signature_quotes: list[str] | None = None
    growth_arcs: list[GrowthArc] | None = None


class Character(CharacterBase):
    """Full character model with ID."""

    id: str = Field(
        description="Unique identifier", json_schema_extra={"example": "ted-lasso"}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ted-lasso",
                "name": "Ted Lasso",
                "role": "coach",
                "team_id": "afc-richmond",
                "date_of_birth": "1970-09-22",
                "email": "ted.lasso@afcrichmond.com",
                "profile_image_url": "https://afcrichmond.com/images/ted-lasso.jpg",
                "salary_gbp": "150000.00",
                "height_meters": 1.83,
                "background": "Former American football coach from Kansas who moved to London to coach AFC Richmond",
                "personality_traits": ["optimistic", "kind", "folksy", "persistent"],
                "emotional_stats": {
                    "optimism": 95,
                    "vulnerability": 80,
                    "empathy": 100,
                    "resilience": 90,
                    "curiosity": 99,
                },
                "signature_quotes": [
                    "I believe in believe.",
                    "Be curious, not judgmental.",
                ],
                "growth_arcs": [
                    {
                        "season": 1,
                        "starting_point": "Fish out of water, hiding pain with humor",
                        "challenge": "Earning respect despite inexperience",
                        "breakthrough": "Showing vulnerability about his marriage",
                        "ending_point": "Accepted by the team despite relegation",
                    }
                ],
            }
        }
    }
