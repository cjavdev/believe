"""WebSocket models for Ted Lasso API - Live Match Simulation."""

from enum import Enum
from typing import Optional, Literal, Annotated
from pydantic import BaseModel, Field


class LiveMatchEventType(str, Enum):
    """Types of live match events sent over WebSocket."""

    MATCH_START = "match_start"
    GOAL = "goal"
    POSSESSION_CHANGE = "possession_change"
    FOUL = "foul"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    PENALTY_AWARDED = "penalty_awarded"
    PENALTY_SCORED = "penalty_scored"
    PENALTY_MISSED = "penalty_missed"
    SUBSTITUTION = "substitution"
    INJURY = "injury"
    OFFSIDE = "offside"
    CORNER = "corner"
    FREE_KICK = "free_kick"
    SHOT_ON_TARGET = "shot_on_target"
    SHOT_OFF_TARGET = "shot_off_target"
    SAVE = "save"
    HALFTIME = "halftime"
    SECOND_HALF_START = "second_half_start"
    ADDED_TIME = "added_time"
    MATCH_END = "match_end"


class TeamSide(str, Enum):
    """Which team the event relates to."""

    HOME = "home"
    AWAY = "away"


class MatchScore(BaseModel):
    """Current match score."""

    home: int = Field(ge=0, description="Home team score")
    away: int = Field(ge=0, description="Away team score")


class MatchStats(BaseModel):
    """Current match statistics."""

    possession_home: float = Field(ge=0, le=100, description="Home team possession %")
    possession_away: float = Field(ge=0, le=100, description="Away team possession %")
    shots_home: int = Field(ge=0, description="Home team total shots")
    shots_away: int = Field(ge=0, description="Away team total shots")
    shots_on_target_home: int = Field(ge=0, description="Home team shots on target")
    shots_on_target_away: int = Field(ge=0, description="Away team shots on target")
    corners_home: int = Field(ge=0, description="Home team corners")
    corners_away: int = Field(ge=0, description="Away team corners")
    fouls_home: int = Field(ge=0, description="Home team fouls")
    fouls_away: int = Field(ge=0, description="Away team fouls")
    yellow_cards_home: int = Field(ge=0, description="Home team yellow cards")
    yellow_cards_away: int = Field(ge=0, description="Away team yellow cards")
    red_cards_home: int = Field(ge=0, description="Home team red cards")
    red_cards_away: int = Field(ge=0, description="Away team red cards")


class PlayerInfo(BaseModel):
    """Information about a player involved in an event."""

    name: str = Field(description="Player name")
    number: int = Field(ge=1, le=99, description="Jersey number")
    position: str = Field(description="Player position")


class LiveMatchEvent(BaseModel):
    """A live match event sent over WebSocket."""

    event_id: int = Field(description="Unique event sequence number")
    event_type: LiveMatchEventType = Field(description="Type of match event")
    minute: int = Field(ge=0, le=120, description="Match minute")
    added_time: Optional[int] = Field(
        default=None, ge=0, le=15, description="Added/injury time minutes"
    )
    team: Optional[TeamSide] = Field(
        default=None, description="Which team the event relates to"
    )
    player: Optional[PlayerInfo] = Field(
        default=None, description="Player involved in the event"
    )
    secondary_player: Optional[PlayerInfo] = Field(
        default=None, description="Second player involved (e.g., assist, replaced player)"
    )
    description: str = Field(description="Human-readable event description")
    score: MatchScore = Field(description="Current score after this event")
    stats: MatchStats = Field(description="Current match statistics")
    ted_reaction: Optional[str] = Field(
        default=None, description="Ted Lasso's sideline reaction"
    )
    crowd_reaction: Optional[str] = Field(
        default=None, description="Crowd reaction to the event"
    )
    commentary: str = Field(description="Match commentary for this event")


class MatchConfig(BaseModel):
    """Configuration for starting a match simulation."""

    home_team: str = Field(
        default="AFC Richmond",
        description="Home team name",
        json_schema_extra={"example": "AFC Richmond"},
    )
    away_team: str = Field(
        default="West Ham United",
        description="Away team name",
        json_schema_extra={"example": "West Ham United"},
    )
    speed: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Simulation speed multiplier (1.0 = real-time pacing, 10.0 = 10x faster)",
    )
    excitement_level: int = Field(
        default=5,
        ge=1,
        le=10,
        description="How eventful the match should be (1=boring, 10=chaos)",
    )


class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""

    type: str = Field(description="Message type")


class MatchStartMessage(WebSocketMessage):
    """Message sent when a match starts."""

    type: Literal["match_start"] = "match_start"
    match_id: str = Field(description="Unique match identifier")
    home_team: str = Field(description="Home team name")
    away_team: str = Field(description="Away team name")
    message: str = Field(description="Welcome message")


class MatchEventMessage(WebSocketMessage):
    """Message containing a match event."""

    type: Literal["match_event"] = "match_event"
    event: LiveMatchEvent = Field(description="The match event")


class MatchEndMessage(WebSocketMessage):
    """Message sent when a match ends."""

    type: Literal["match_end"] = "match_end"
    match_id: str = Field(description="Match identifier")
    final_score: MatchScore = Field(description="Final score")
    final_stats: MatchStats = Field(description="Final match statistics")
    man_of_the_match: str = Field(description="Man of the match")
    ted_post_match: str = Field(description="Ted's post-match thoughts")


class ErrorMessage(WebSocketMessage):
    """Error message for WebSocket communication."""

    type: Literal["error"] = "error"
    code: str = Field(description="Error code")
    message: str = Field(description="Error description")
