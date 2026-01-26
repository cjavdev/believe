"""Quote models for Ted Lasso API."""

from enum import Enum

from pydantic import BaseModel, Field


class QuoteTheme(str, Enum):
    """Themes that quotes can be categorized under."""

    BELIEF = "belief"
    TEAMWORK = "teamwork"
    CURIOSITY = "curiosity"
    KINDNESS = "kindness"
    RESILIENCE = "resilience"
    VULNERABILITY = "vulnerability"
    GROWTH = "growth"
    HUMOR = "humor"
    WISDOM = "wisdom"
    LEADERSHIP = "leadership"
    LOVE = "love"
    FORGIVENESS = "forgiveness"
    PHILOSOPHY = "philosophy"
    ROMANCE = "romance"
    CULTURAL_PRIDE = "cultural-pride"
    CULTURAL_DIFFERENCES = "cultural-differences"
    ANTAGONISM = "antagonism"
    CELEBRATION = "celebration"
    IDENTITY = "identity"
    ISOLATION = "isolation"
    POWER = "power"
    SACRIFICE = "sacrifice"
    STANDARDS = "standards"
    CONFIDENCE = "confidence"
    CONFLICT = "conflict"
    HONESTY = "honesty"
    INTEGRITY = "integrity"


class QuoteMoment(str, Enum):
    """Types of moments when quotes occur."""

    HALFTIME_SPEECH = "halftime_speech"
    PRESS_CONFERENCE = "press_conference"
    LOCKER_ROOM = "locker_room"
    TRAINING = "training"
    BISCUITS_WITH_BOSS = "biscuits_with_boss"
    PUB = "pub"
    ONE_ON_ONE = "one_on_one"
    CELEBRATION = "celebration"
    CRISIS = "crisis"
    CASUAL = "casual"
    CONFRONTATION = "confrontation"


class QuoteBase(BaseModel):
    """Base quote model."""

    text: str = Field(
        min_length=1,
        description="The quote text",
        json_schema_extra={"example": "Be curious, not judgmental."},
    )
    character_id: str = Field(
        description="ID of the character who said it",
        json_schema_extra={"example": "ted-lasso"},
    )
    episode_id: str | None = Field(
        default=None,
        description="Episode where the quote appears",
        json_schema_extra={"example": "s01e08"},
    )
    context: str = Field(
        description="Context in which the quote was said",
        json_schema_extra={
            "example": "Ted playing darts against Rupert in the pub, explaining his philosophy"
        },
    )
    theme: QuoteTheme = Field(
        description="Primary theme of the quote",
        json_schema_extra={"example": "curiosity"},
    )
    secondary_themes: list[QuoteTheme] = Field(
        default_factory=list,
        description="Additional themes",
        json_schema_extra={"example": ["wisdom", "kindness"]},
    )
    moment_type: QuoteMoment = Field(
        description="Type of moment when the quote was said",
        json_schema_extra={"example": "pub"},
    )
    is_inspirational: bool = Field(
        default=True, description="Whether this quote is inspirational"
    )
    is_funny: bool = Field(default=False, description="Whether this quote is humorous")
    popularity_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Popularity/virality score (0-100)",
        json_schema_extra={"example": 95.5},
    )
    times_shared: int | None = Field(
        default=None,
        ge=0,
        description="Number of times shared on social media",
        json_schema_extra={"example": 150000},
    )


class QuoteCreate(QuoteBase):
    """Model for creating a new quote."""

    pass


class QuoteUpdate(BaseModel):
    """Model for updating a quote (all fields optional)."""

    text: str | None = Field(default=None, min_length=1)
    character_id: str | None = None
    episode_id: str | None = None
    context: str | None = None
    theme: QuoteTheme | None = None
    secondary_themes: list[QuoteTheme] | None = None
    moment_type: QuoteMoment | None = None
    is_inspirational: bool | None = None
    is_funny: bool | None = None
    popularity_score: float | None = Field(default=None, ge=0.0, le=100.0)
    times_shared: int | None = Field(default=None, ge=0)


class Quote(QuoteBase):
    """Full quote model with ID."""

    id: str = Field(
        description="Unique identifier", json_schema_extra={"example": "quote-001"}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "quote-001",
                "text": "Be curious, not judgmental.",
                "character_id": "ted-lasso",
                "episode_id": "s01e08",
                "context": "Ted playing darts against Rupert in the pub, explaining his philosophy",
                "theme": "curiosity",
                "secondary_themes": ["wisdom", "kindness"],
                "moment_type": "pub",
                "is_inspirational": True,
                "is_funny": False,
                "popularity_score": 95.5,
                "times_shared": 150000,
            }
        }
    }
