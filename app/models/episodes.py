"""Episode models for Ted Lasso API."""

from typing import Optional

from pydantic import BaseModel, Field


class EpisodeBase(BaseModel):
    """Base episode model."""

    season: int = Field(ge=1, le=3, description="Season number")
    episode_number: int = Field(ge=1, le=12, description="Episode number within season")
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Episode title",
        json_schema_extra={"example": "Pilot"},
    )
    director: str = Field(description="Episode director")
    writer: str = Field(description="Episode writer(s)")
    air_date: str = Field(
        description="Original air date (YYYY-MM-DD)",
        json_schema_extra={"example": "2020-08-14"},
    )
    runtime_minutes: int = Field(ge=20, le=60, description="Episode runtime in minutes")
    synopsis: str = Field(
        description="Brief plot synopsis",
        json_schema_extra={
            "example": "American football coach Ted Lasso is hired to manage AFC Richmond, a struggling English Premier League team."
        },
    )
    main_theme: str = Field(
        description="Central theme of the episode",
        json_schema_extra={"example": "Taking chances and believing in yourself"},
    )
    ted_wisdom: str = Field(
        description="Key piece of Ted wisdom from the episode",
        json_schema_extra={
            "example": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong."
        },
    )
    biscuits_with_boss_moment: Optional[str] = Field(
        default=None,
        description="Notable biscuits with the boss scene",
        json_schema_extra={
            "example": "Ted brings Rebecca homemade biscuits for the first time, beginning their bonding ritual."
        },
    )
    character_focus: list[str] = Field(
        description="Characters with significant development",
        json_schema_extra={"example": ["ted-lasso", "rebecca-welton"]},
    )
    memorable_moments: list[str] = Field(
        default_factory=list,
        description="Standout moments from the episode",
        json_schema_extra={
            "example": [
                "Ted's first press conference",
                "The BELIEVE sign goes up",
            ]
        },
    )


class EpisodeCreate(EpisodeBase):
    """Model for creating a new episode."""

    pass


class EpisodeUpdate(BaseModel):
    """Model for updating an episode (all fields optional)."""

    season: Optional[int] = Field(default=None, ge=1, le=3)
    episode_number: Optional[int] = Field(default=None, ge=1, le=12)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    director: Optional[str] = None
    writer: Optional[str] = None
    air_date: Optional[str] = None
    runtime_minutes: Optional[int] = Field(default=None, ge=20, le=60)
    synopsis: Optional[str] = None
    main_theme: Optional[str] = None
    ted_wisdom: Optional[str] = None
    biscuits_with_boss_moment: Optional[str] = None
    character_focus: Optional[list[str]] = None
    memorable_moments: Optional[list[str]] = None


class Episode(EpisodeBase):
    """Full episode model with ID."""

    id: str = Field(
        description="Unique identifier (format: s##e##)",
        json_schema_extra={"example": "s01e01"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "s01e01",
                "season": 1,
                "episode_number": 1,
                "title": "Pilot",
                "director": "Tom Marshall",
                "writer": "Jason Sudeikis, Bill Lawrence, Brendan Hunt, Joe Kelly",
                "air_date": "2020-08-14",
                "runtime_minutes": 32,
                "synopsis": "American football coach Ted Lasso is hired to manage AFC Richmond, a struggling English Premier League team.",
                "main_theme": "Taking chances and believing in yourself",
                "ted_wisdom": "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                "biscuits_with_boss_moment": "Ted brings Rebecca homemade biscuits for the first time.",
                "character_focus": ["ted-lasso", "rebecca-welton", "coach-beard"],
                "memorable_moments": [
                    "Ted's first press conference",
                    "The BELIEVE sign goes up",
                    "Ted tastes his first 'garbage water' (English tea)",
                ],
            }
        }
    }
