"""Interactive endpoint models for Ted Lasso API."""

from enum import Enum

from pydantic import BaseModel, Field

# === Believe Engine Models ===


class SituationType(str, Enum):
    """Types of situations the Believe Engine can handle."""

    WORK_CHALLENGE = "work_challenge"
    PERSONAL_SETBACK = "personal_setback"
    TEAM_CONFLICT = "team_conflict"
    SELF_DOUBT = "self_doubt"
    BIG_DECISION = "big_decision"
    FAILURE = "failure"
    NEW_BEGINNING = "new_beginning"
    RELATIONSHIP = "relationship"


class BelieveRequest(BaseModel):
    """Request for the Believe Engine."""

    situation: str = Field(
        min_length=10,
        description="Describe your situation",
        json_schema_extra={
            "example": "I just got passed over for a promotion I've been working toward for two years."
        },
    )
    situation_type: SituationType = Field(
        description="Type of situation",
        json_schema_extra={"example": "work_challenge"},
    )
    context: str | None = Field(
        default=None,
        description="Additional context",
        json_schema_extra={
            "example": "I've always tried to be a team player and support my colleagues."
        },
    )
    intensity: int = Field(
        ge=1,
        le=10,
        default=5,
        description="How intense is the response needed (1=gentle, 10=full Ted)",
    )


class BelieveResponse(BaseModel):
    """Response from the Believe Engine."""

    ted_response: str = Field(description="Ted's motivational response")
    relevant_quote: str = Field(description="A relevant Ted Lasso quote")
    action_suggestion: str = Field(description="Suggested action to take")
    goldfish_wisdom: str = Field(
        description="A reminder to have a goldfish memory when needed"
    )
    believe_score: int = Field(
        ge=0, le=100, description="Your current believe-o-meter score"
    )


# === Conflict Resolution Models ===


class ConflictType(str, Enum):
    """Types of conflicts."""

    INTERPERSONAL = "interpersonal"
    TEAM_DYNAMICS = "team_dynamics"
    LEADERSHIP = "leadership"
    EGO = "ego"
    MISCOMMUNICATION = "miscommunication"
    COMPETITION = "competition"


class ConflictRequest(BaseModel):
    """Request for conflict resolution."""

    parties_involved: list[str] = Field(
        min_length=2,
        description="Who is involved in the conflict",
        json_schema_extra={"example": ["Me", "My teammate Alex"]},
    )
    conflict_type: ConflictType = Field(
        description="Type of conflict", json_schema_extra={"example": "interpersonal"}
    )
    description: str = Field(
        min_length=20,
        description="Describe the conflict",
        json_schema_extra={
            "example": "Alex keeps taking credit for my ideas in meetings and I'm getting resentful."
        },
    )
    attempts_made: list[str] | None = Field(
        default=None,
        description="What you've already tried",
        json_schema_extra={"example": ["Mentioned it casually", "Avoided them"]},
    )


class ConflictResolution(BaseModel):
    """Conflict resolution response."""

    diagnosis: str = Field(description="Understanding the root cause")
    ted_approach: str = Field(description="How Ted would handle this")
    diamond_dogs_advice: str = Field(
        description="Advice from the Diamond Dogs support group"
    )
    steps_to_resolution: list[str] = Field(
        description="Concrete steps to resolve the conflict"
    )
    potential_outcome: str = Field(description="What resolution could look like")
    barbecue_sauce_wisdom: str = Field(
        description="A folksy metaphor to remember"
    )


# === Reframe Models ===


class ReframeRequest(BaseModel):
    """Request to reframe a negative thought."""

    negative_thought: str = Field(
        min_length=5,
        description="The negative thought to reframe",
        json_schema_extra={"example": "I'm not good enough for this job."},
    )
    recurring: bool = Field(
        default=False, description="Is this a recurring thought?"
    )


class ReframeResponse(BaseModel):
    """Reframed perspective response."""

    original_thought: str = Field(description="The original negative thought")
    reframed_thought: str = Field(description="The thought reframed positively")
    ted_perspective: str = Field(description="Ted's take on this thought")
    dr_sharon_insight: str | None = Field(
        default=None, description="Dr. Sharon's therapeutic insight"
    )
    daily_affirmation: str = Field(description="A daily affirmation to practice")


# === Press Conference Models ===


class PressConferenceRequest(BaseModel):
    """Request for press conference response."""

    question: str = Field(
        min_length=10,
        description="The press question to answer",
        json_schema_extra={
            "example": "Ted, your team just lost 5-0. How do you explain this embarrassing defeat?"
        },
    )
    hostile: bool = Field(
        default=False, description="Is this a hostile question from Trent Crimm?"
    )
    topic: str | None = Field(
        default=None,
        description="Topic category",
        json_schema_extra={"example": "match_result"},
    )


class PressConferenceResponse(BaseModel):
    """Ted's press conference response."""

    response: str = Field(description="Ted's press conference answer")
    deflection_humor: str | None = Field(
        default=None, description="Humorous deflection if appropriate"
    )
    actual_wisdom: str = Field(description="The actual wisdom beneath the humor")
    reporter_reaction: str = Field(description="How reporters would react")
    follow_up_dodge: str = Field(description="How Ted would dodge a follow-up")


# === Coaching Principles ===


class CoachingPrinciple(BaseModel):
    """A Ted Lasso coaching principle."""

    id: str = Field(description="Principle identifier")
    principle: str = Field(description="The coaching principle")
    explanation: str = Field(description="What this principle means")
    application: str = Field(description="How to apply this principle")
    example_from_show: str = Field(description="Example from the show")
    ted_quote: str = Field(description="Related Ted quote")


# === Biscuits ===


class BiscuitType(str, Enum):
    """Types of biscuits."""

    CLASSIC = "classic"
    SHORTBREAD = "shortbread"
    CHOCOLATE_CHIP = "chocolate_chip"
    OATMEAL_RAISIN = "oatmeal_raisin"


class Biscuit(BaseModel):
    """A biscuit from Ted."""

    id: str = Field(description="Biscuit identifier")
    type: BiscuitType = Field(description="Type of biscuit")
    message: str = Field(description="Message that comes with the biscuit")
    warmth_level: int = Field(ge=1, le=10, description="How warm and fresh (1-10)")
    pairs_well_with: str = Field(description="What this biscuit pairs well with")
    ted_note: str = Field(description="A handwritten note from Ted")


# === Streaming Models ===


class PepTalkChunk(BaseModel):
    """A chunk of a streaming pep talk."""

    chunk_id: int = Field(description="Chunk sequence number")
    text: str = Field(description="The text of this chunk")
    is_final: bool = Field(default=False, description="Is this the final chunk")
    emotional_beat: str | None = Field(
        default=None, description="The emotional purpose of this chunk"
    )


class CommentaryEventType(str, Enum):
    """Types of match commentary events."""

    KICKOFF = "kickoff"
    GOAL = "goal"
    NEAR_MISS = "near_miss"
    SAVE = "save"
    FOUL = "foul"
    SUBSTITUTION = "substitution"
    HALFTIME = "halftime"
    TED_REACTION = "ted_reaction"
    CROWD_MOMENT = "crowd_moment"
    FINAL_WHISTLE = "final_whistle"


class MatchCommentaryEvent(BaseModel):
    """A single commentary event during a match stream."""

    event_id: int = Field(description="Event sequence number")
    minute: int = Field(ge=0, le=120, description="Match minute")
    event_type: CommentaryEventType = Field(description="Type of event")
    description: str = Field(description="What happened")
    commentary: str = Field(description="Commentator's call")
    ted_sideline_reaction: str | None = Field(
        default=None, description="Ted's reaction on the sideline"
    )
    crowd_reaction: str | None = Field(
        default=None, description="How the crowd reacted"
    )
    is_final: bool = Field(default=False, description="Is this the final event")
