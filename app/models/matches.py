"""Match models for Ted Lasso API."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class MatchResult(str, Enum):
    """Match result types."""

    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    PENDING = "pending"


class MatchType(str, Enum):
    """Types of matches."""

    LEAGUE = "league"
    CUP = "cup"
    FRIENDLY = "friendly"
    PLAYOFF = "playoff"
    FINAL = "final"


class TurningPoint(BaseModel):
    """A pivotal moment in a match."""

    minute: int = Field(ge=0, le=120, description="Minute of the match")
    description: str = Field(description="What happened")
    emotional_impact: str = Field(
        description="How this affected the team emotionally",
        json_schema_extra={"example": "Galvanized the team's fighting spirit"},
    )
    character_involved: str | None = Field(
        default=None,
        description="Character ID who was central to this moment",
        json_schema_extra={"example": "jamie-tartt"},
    )


class MatchBase(BaseModel):
    """Base match model."""

    home_team_id: str = Field(
        description="Home team ID", json_schema_extra={"example": "afc-richmond"}
    )
    away_team_id: str = Field(
        description="Away team ID", json_schema_extra={"example": "manchester-city"}
    )
    match_type: MatchType = Field(description="Type of match")
    date: datetime = Field(description="Match date and time")
    home_score: int = Field(ge=0, default=0, description="Home team score")
    away_score: int = Field(ge=0, default=0, description="Away team score")
    result: MatchResult = Field(
        default=MatchResult.PENDING, description="Match result from home team perspective"
    )
    episode_id: str | None = Field(
        default=None,
        description="Episode ID where this match is featured",
        json_schema_extra={"example": "s01e10"},
    )
    turning_points: list[TurningPoint] = Field(
        default_factory=list, description="Key moments that changed the match"
    )
    lesson_learned: str | None = Field(
        default=None,
        description="The life lesson learned from this match",
        json_schema_extra={
            "example": "It's not about the wins and losses, it's about helping these young fellas be the best versions of themselves."
        },
    )
    ted_halftime_speech: str | None = Field(
        default=None,
        description="Ted's inspirational halftime speech",
        json_schema_extra={
            "example": "You know what the happiest animal on Earth is? It's a goldfish. You know why? It's got a 10-second memory."
        },
    )
    attendance: int | None = Field(
        default=None,
        ge=0,
        description="Match attendance",
        json_schema_extra={"example": 24500},
    )
    ticket_revenue_gbp: Decimal | None = Field(
        default=None,
        decimal_places=2,
        description="Total ticket revenue in GBP",
        json_schema_extra={"example": "735000.00"},
    )
    possession_percentage: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Home team possession percentage",
        json_schema_extra={"example": 52.3},
    )
    weather_temp_celsius: float | None = Field(
        default=None,
        ge=-30.0,
        le=50.0,
        description="Temperature at kickoff in Celsius",
        json_schema_extra={"example": 14.5},
    )


class MatchCreate(MatchBase):
    """Model for creating a new match."""

    pass


class MatchUpdate(BaseModel):
    """Model for updating a match (all fields optional)."""

    home_team_id: str | None = None
    away_team_id: str | None = None
    match_type: MatchType | None = None
    date: datetime | None = None
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)
    result: MatchResult | None = None
    episode_id: str | None = None
    turning_points: list[TurningPoint] | None = None
    lesson_learned: str | None = None
    ted_halftime_speech: str | None = None
    attendance: int | None = Field(default=None, ge=0)
    ticket_revenue_gbp: Decimal | None = Field(default=None, decimal_places=2)
    possession_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    weather_temp_celsius: float | None = Field(default=None, ge=-30.0, le=50.0)


class Match(MatchBase):
    """Full match model with ID."""

    id: str = Field(
        description="Unique identifier", json_schema_extra={"example": "match-001"}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "match-001",
                "home_team_id": "afc-richmond",
                "away_team_id": "manchester-city",
                "match_type": "league",
                "date": "2024-01-15T15:00:00Z",
                "home_score": 2,
                "away_score": 2,
                "result": "draw",
                "episode_id": "s01e10",
                "turning_points": [
                    {
                        "minute": 89,
                        "description": "Jamie Tartt passes to Sam instead of shooting",
                        "emotional_impact": "Showed Jamie's growth from selfish to team player",
                        "character_involved": "jamie-tartt",
                    }
                ],
                "lesson_learned": "Sometimes a tie feels like a win when you've grown as people.",
                "ted_halftime_speech": "Guys, I want you to know, I don't care if we win or lose today. I just want you to go out there and play the best football of your lives.",
                "attendance": 24500,
                "ticket_revenue_gbp": "735000.00",
                "possession_percentage": 52.3,
                "weather_temp_celsius": 14.5,
            }
        }
    }
