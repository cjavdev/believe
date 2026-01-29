"""Episode models for Ted Lasso API."""

from datetime import date

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
    air_date: date = Field(
        description="Original air date",
        json_schema_extra={"example": "2020-08-14"},
    )
    runtime_minutes: int = Field(ge=20, le=60, description="Episode runtime in minutes")
    viewer_rating: float | None = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="Viewer rating out of 10",
        json_schema_extra={"example": 8.7},
    )
    us_viewers_millions: float | None = Field(
        default=None,
        ge=0.0,
        description="US viewership in millions",
        json_schema_extra={"example": 1.25},
    )
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
    biscuits_with_boss_moment: str | None = Field(
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "season": 1,
                "episode_number": 8,
                "title": "The Diamond Dogs",
                "director": "MJ Delaney",
                "writer": "Jason Sudeikis, Brendan Hunt, Joe Kelly",
                "air_date": "2020-10-02",
                "runtime_minutes": 29,
                "viewer_rating": 9.1,
                "us_viewers_millions": 1.42,
                "synopsis": "Ted creates a support group for the coaching staff while Rebecca faces a difficult decision about her future.",
                "main_theme": "The power of vulnerability and male friendship",
                "ted_wisdom": "There's two buttons I never like to hit: that's panic and snooze.",
                "biscuits_with_boss_moment": "Ted and Rebecca have an honest conversation about trust.",
                "character_focus": ["ted-lasso", "coach-beard", "higgins", "nate"],
                "memorable_moments": [
                    "First Diamond Dogs meeting",
                    "The famous dart scene with Rupert",
                    "Be curious, not judgmental speech",
                ],
            }
        }
    }


class EpisodeUpdate(BaseModel):
    """Model for updating an episode (all fields optional)."""

    season: int | None = Field(default=None, ge=1, le=3)
    episode_number: int | None = Field(default=None, ge=1, le=12)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    director: str | None = None
    writer: str | None = None
    air_date: date | None = None
    runtime_minutes: int | None = Field(default=None, ge=20, le=60)
    viewer_rating: float | None = Field(default=None, ge=0.0, le=10.0)
    us_viewers_millions: float | None = Field(default=None, ge=0.0)
    synopsis: str | None = None
    main_theme: str | None = None
    ted_wisdom: str | None = None
    biscuits_with_boss_moment: str | None = None
    character_focus: list[str] | None = None
    memorable_moments: list[str] | None = None


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
                "viewer_rating": 8.7,
                "us_viewers_millions": 1.25,
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
