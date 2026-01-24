"""Team models for Ted Lasso API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class League(str, Enum):
    """Football leagues."""

    PREMIER_LEAGUE = "Premier League"
    CHAMPIONSHIP = "Championship"
    LEAGUE_ONE = "League One"
    LEAGUE_TWO = "League Two"
    LA_LIGA = "La Liga"
    SERIE_A = "Serie A"
    BUNDESLIGA = "Bundesliga"
    LIGUE_1 = "Ligue 1"


class TeamValues(BaseModel):
    """Core values that define a team's culture."""

    primary_value: str = Field(
        description="The team's primary guiding value",
        json_schema_extra={"example": "Believe"},
    )
    secondary_values: list[str] = Field(
        description="Supporting values",
        json_schema_extra={"example": ["Family", "Resilience", "Joy"]},
    )
    team_motto: str = Field(
        description="Team's motivational motto",
        json_schema_extra={"example": "Football is life!"},
    )


class TeamBase(BaseModel):
    """Base team model."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Team name",
        json_schema_extra={"example": "AFC Richmond"},
    )
    nickname: Optional[str] = Field(
        default=None,
        description="Team nickname",
        json_schema_extra={"example": "The Greyhounds"},
    )
    league: League = Field(description="Current league")
    stadium: str = Field(
        description="Home stadium name",
        json_schema_extra={"example": "Nelson Road"},
    )
    founded_year: int = Field(
        ge=1800,
        le=2030,
        description="Year the club was founded",
        json_schema_extra={"example": 1897},
    )
    culture_score: int = Field(
        ge=0,
        le=100,
        description="Team culture/morale score (0-100)",
        json_schema_extra={"example": 85},
    )
    values: TeamValues = Field(description="Team's core values")
    rival_teams: list[str] = Field(
        default_factory=list,
        description="List of rival team IDs",
        json_schema_extra={"example": ["west-ham", "rupert-fc"]},
    )


class TeamCreate(TeamBase):
    """Model for creating a new team."""

    pass


class TeamUpdate(BaseModel):
    """Model for updating a team (all fields optional)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    nickname: Optional[str] = None
    league: Optional[League] = None
    stadium: Optional[str] = None
    founded_year: Optional[int] = Field(default=None, ge=1800, le=2030)
    culture_score: Optional[int] = Field(default=None, ge=0, le=100)
    values: Optional[TeamValues] = None
    rival_teams: Optional[list[str]] = None


class Team(TeamBase):
    """Full team model with ID."""

    id: str = Field(
        description="Unique identifier", json_schema_extra={"example": "afc-richmond"}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "afc-richmond",
                "name": "AFC Richmond",
                "nickname": "The Greyhounds",
                "league": "Premier League",
                "stadium": "Nelson Road",
                "founded_year": 1897,
                "culture_score": 85,
                "values": {
                    "primary_value": "Believe",
                    "secondary_values": ["Family", "Resilience", "Joy"],
                    "team_motto": "Football is life!",
                },
                "rival_teams": ["west-ham", "rupert-fc"],
            }
        }
    }
