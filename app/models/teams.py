"""Team models for Ted Lasso API."""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class GeoLocation(BaseModel):
    """Geographic coordinates for a location."""

    latitude: float = Field(
        ge=-90.0,
        le=90.0,
        description="Latitude in degrees",
        json_schema_extra={"example": 51.4816},
    )
    longitude: float = Field(
        ge=-180.0,
        le=180.0,
        description="Longitude in degrees",
        json_schema_extra={"example": -0.1910},
    )


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
    nickname: str | None = Field(
        default=None,
        description="Team nickname",
        json_schema_extra={"example": "The Greyhounds"},
    )
    league: League = Field(description="Current league")
    stadium: str = Field(
        description="Home stadium name",
        json_schema_extra={"example": "Nelson Road"},
    )
    stadium_location: GeoLocation | None = Field(
        default=None,
        description="Geographic coordinates of the stadium",
        json_schema_extra={"example": {"latitude": 51.4816, "longitude": -0.1910}},
    )
    founded_year: int = Field(
        ge=1800,
        le=2030,
        description="Year the club was founded",
        json_schema_extra={"example": 1897},
    )
    website: HttpUrl | None = Field(
        default=None,
        description="Official team website",
        json_schema_extra={"example": "https://www.afcrichmond.com"},
    )
    contact_email: EmailStr | None = Field(
        default=None,
        description="Team contact email",
        json_schema_extra={"example": "info@afcrichmond.com"},
    )
    annual_budget_gbp: Decimal | None = Field(
        default=None,
        decimal_places=2,
        description="Annual budget in GBP",
        json_schema_extra={"example": "50000000.00"},
    )
    average_attendance: float | None = Field(
        default=None,
        ge=0,
        description="Average match attendance",
        json_schema_extra={"example": 24500.5},
    )
    win_percentage: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Season win percentage",
        json_schema_extra={"example": 45.5},
    )
    culture_score: int = Field(
        ge=0,
        le=100,
        description="Team culture/morale score (0-100)",
        json_schema_extra={"example": 85},
    )
    is_active: bool = Field(
        default=True,
        description="Whether the team is currently active",
    )
    values: TeamValues = Field(description="Team's core values")
    rival_teams: list[str] = Field(
        default_factory=list,
        description="List of rival team IDs",
        json_schema_extra={"example": ["west-ham", "rupert-fc"]},
    )
    primary_color: str | None = Field(
        default=None,
        description="Primary team color (hex)",
        json_schema_extra={"example": "#0033A0"},
    )
    secondary_color: str | None = Field(
        default=None,
        description="Secondary team color (hex)",
        json_schema_extra={"example": "#FFFFFF"},
    )


class TeamCreate(TeamBase):
    """Model for creating a new team."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "West Ham United",
                "nickname": "The Hammers",
                "league": "Premier League",
                "stadium": "London Stadium",
                "stadium_location": {"latitude": 51.5387, "longitude": -0.0166},
                "founded_year": 1895,
                "website": "https://www.whufc.com",
                "contact_email": "info@westhamunited.co.uk",
                "annual_budget_gbp": "150000000.00",
                "average_attendance": 59988.0,
                "win_percentage": 52.3,
                "culture_score": 70,
                "is_active": True,
                "values": {
                    "primary_value": "Pride",
                    "secondary_values": ["History", "Community", "Passion"],
                    "team_motto": "Forever Blowing Bubbles",
                },
                "rival_teams": ["afc-richmond", "tottenham"],
                "primary_color": "#7A263A",
                "secondary_color": "#1BB1E7",
            }
        }
    }


class TeamUpdate(BaseModel):
    """Model for updating a team (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    nickname: str | None = None
    league: League | None = None
    stadium: str | None = None
    stadium_location: GeoLocation | None = None
    founded_year: int | None = Field(default=None, ge=1800, le=2030)
    website: HttpUrl | None = None
    contact_email: EmailStr | None = None
    annual_budget_gbp: Decimal | None = Field(default=None, decimal_places=2)
    average_attendance: float | None = Field(default=None, ge=0)
    win_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    culture_score: int | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None
    values: TeamValues | None = None
    rival_teams: list[str] | None = None
    primary_color: str | None = None
    secondary_color: str | None = None


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
                "stadium_location": {"latitude": 51.4816, "longitude": -0.1910},
                "founded_year": 1897,
                "website": "https://www.afcrichmond.com",
                "contact_email": "info@afcrichmond.com",
                "annual_budget_gbp": "50000000.00",
                "average_attendance": 24500.5,
                "win_percentage": 45.5,
                "culture_score": 85,
                "is_active": True,
                "values": {
                    "primary_value": "Believe",
                    "secondary_values": ["Family", "Resilience", "Joy"],
                    "team_motto": "Football is life!",
                },
                "rival_teams": ["west-ham", "rupert-fc"],
                "primary_color": "#0033A0",
                "secondary_color": "#FFFFFF",
            }
        }
    }
