"""WebSocket models for Ted Lasso API - Live Match Simulation."""

from enum import Enum
from typing import Literal

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

    model_config = {"json_schema_extra": {"example": {"home": 2, "away": 1}}}


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "possession_home": 54.3,
                "possession_away": 45.7,
                "shots_home": 12,
                "shots_away": 8,
                "shots_on_target_home": 5,
                "shots_on_target_away": 3,
                "corners_home": 6,
                "corners_away": 4,
                "fouls_home": 9,
                "fouls_away": 11,
                "yellow_cards_home": 1,
                "yellow_cards_away": 2,
                "red_cards_home": 0,
                "red_cards_away": 0,
            }
        }
    }


class PlayerInfo(BaseModel):
    """Information about a player involved in an event."""

    name: str = Field(description="Player name")
    number: int = Field(ge=1, le=99, description="Jersey number")
    position: str = Field(description="Player position")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Jamie Tartt", "number": 9, "position": "Forward"}
        }
    }


class LiveMatchEvent(BaseModel):
    """A live match event sent over WebSocket."""

    event_id: int = Field(description="Unique event sequence number")
    event_type: LiveMatchEventType = Field(description="Type of match event")
    minute: int = Field(ge=0, le=120, description="Match minute")
    added_time: int | None = Field(
        default=None, ge=0, le=15, description="Added/injury time minutes"
    )
    team: TeamSide | None = Field(
        default=None, description="Which team the event relates to"
    )
    player: PlayerInfo | None = Field(
        default=None, description="Player involved in the event"
    )
    secondary_player: PlayerInfo | None = Field(
        default=None,
        description="Second player involved (e.g., assist, replaced player)",
    )
    description: str = Field(description="Human-readable event description")
    score: MatchScore = Field(description="Current score after this event")
    stats: MatchStats = Field(description="Current match statistics")
    ted_reaction: str | None = Field(
        default=None, description="Ted Lasso's sideline reaction"
    )
    crowd_reaction: str | None = Field(
        default=None, description="Crowd reaction to the event"
    )
    commentary: str = Field(description="Match commentary for this event")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": 23,
                "event_type": "goal",
                "minute": 73,
                "added_time": None,
                "team": "home",
                "player": {"name": "Jamie Tartt", "number": 9, "position": "Forward"},
                "secondary_player": {
                    "name": "Sam Obisanya",
                    "number": 24,
                    "position": "Midfielder",
                },
                "description": "Jamie Tartt scores! Assisted by Sam Obisanya with a beautiful cross.",
                "score": {"home": 2, "away": 1},
                "stats": {
                    "possession_home": 54.3,
                    "possession_away": 45.7,
                    "shots_home": 12,
                    "shots_away": 8,
                    "shots_on_target_home": 5,
                    "shots_on_target_away": 3,
                    "corners_home": 6,
                    "corners_away": 4,
                    "fouls_home": 9,
                    "fouls_away": 11,
                    "yellow_cards_home": 1,
                    "yellow_cards_away": 2,
                    "red_cards_home": 0,
                    "red_cards_away": 0,
                },
                "ted_reaction": "Ted pumps his fist and does a little shimmy on the sideline!",
                "crowd_reaction": "Nelson Road is absolutely bouncing! The fans are singing Jamie's song!",
                "commentary": "GOAL! Richmond take the lead! Jamie Tartt with a clinical finish from Sam's pinpoint cross!",
            }
        }
    }


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "home_team": "AFC Richmond",
                "away_team": "Manchester City",
                "speed": 2.0,
                "excitement_level": 7,
            }
        }
    }


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

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "match_start",
                "match_id": "match-2024-01-15-richmond-city",
                "home_team": "AFC Richmond",
                "away_team": "Manchester City",
                "message": "Welcome to Nelson Road! The Greyhounds take on Manchester City in what promises to be a thrilling Premier League encounter!",
            }
        }
    }


class MatchEventMessage(WebSocketMessage):
    """Message containing a match event."""

    type: Literal["match_event"] = "match_event"
    event: LiveMatchEvent = Field(description="The match event")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "match_event",
                "event": {
                    "event_id": 23,
                    "event_type": "goal",
                    "minute": 73,
                    "added_time": None,
                    "team": "home",
                    "player": {
                        "name": "Jamie Tartt",
                        "number": 9,
                        "position": "Forward",
                    },
                    "secondary_player": {
                        "name": "Sam Obisanya",
                        "number": 24,
                        "position": "Midfielder",
                    },
                    "description": "Jamie Tartt scores! Assisted by Sam Obisanya.",
                    "score": {"home": 2, "away": 1},
                    "stats": {
                        "possession_home": 54.3,
                        "possession_away": 45.7,
                        "shots_home": 12,
                        "shots_away": 8,
                        "shots_on_target_home": 5,
                        "shots_on_target_away": 3,
                        "corners_home": 6,
                        "corners_away": 4,
                        "fouls_home": 9,
                        "fouls_away": 11,
                        "yellow_cards_home": 1,
                        "yellow_cards_away": 2,
                        "red_cards_home": 0,
                        "red_cards_away": 0,
                    },
                    "ted_reaction": "Ted pumps his fist on the sideline!",
                    "crowd_reaction": "Nelson Road erupts!",
                    "commentary": "GOAL! Jamie Tartt puts Richmond ahead!",
                },
            }
        }
    }


class MatchEndMessage(WebSocketMessage):
    """Message sent when a match ends."""

    type: Literal["match_end"] = "match_end"
    match_id: str = Field(description="Match identifier")
    final_score: MatchScore = Field(description="Final score")
    final_stats: MatchStats = Field(description="Final match statistics")
    man_of_the_match: str = Field(description="Man of the match")
    ted_post_match: str = Field(description="Ted's post-match thoughts")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "match_end",
                "match_id": "match-2024-01-15-richmond-city",
                "final_score": {"home": 2, "away": 2},
                "final_stats": {
                    "possession_home": 48.5,
                    "possession_away": 51.5,
                    "shots_home": 14,
                    "shots_away": 16,
                    "shots_on_target_home": 6,
                    "shots_on_target_away": 7,
                    "corners_home": 7,
                    "corners_away": 8,
                    "fouls_home": 12,
                    "fouls_away": 10,
                    "yellow_cards_home": 2,
                    "yellow_cards_away": 1,
                    "red_cards_home": 0,
                    "red_cards_away": 0,
                },
                "man_of_the_match": "Sam Obisanya",
                "ted_post_match": "You know what? A draw against Manchester City at home? That's like finding a twenty-dollar bill in your winter coat. Sure, it ain't a hundred, but it sure beats a hole in your pocket!",
            }
        }
    }


class ErrorMessage(WebSocketMessage):
    """Error message for WebSocket communication."""

    type: Literal["error"] = "error"
    code: str = Field(description="Error code")
    message: str = Field(description="Error description")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "error",
                "code": "INVALID_CONFIG",
                "message": "Invalid match configuration: excitement_level must be between 1 and 10",
            }
        }
    }


# Client -> Server Messages


class ClientAction(str, Enum):
    """Actions that clients can send to control the match simulation."""

    PING = "ping"
    PAUSE = "pause"
    RESUME = "resume"
    SET_SPEED = "set_speed"
    GET_STATUS = "get_status"


class BaseClientMessage(BaseModel):
    """Base model for client messages."""

    action: str = Field(description="Action to perform")


class PingMessage(BaseClientMessage):
    """Ping message for keep-alive."""

    action: Literal["ping"] = "ping"

    model_config = {"json_schema_extra": {"example": {"action": "ping"}}}


class PauseMessage(BaseClientMessage):
    """Pause the match simulation."""

    action: Literal["pause"] = "pause"

    model_config = {"json_schema_extra": {"example": {"action": "pause"}}}


class ResumeMessage(BaseClientMessage):
    """Resume a paused match simulation."""

    action: Literal["resume"] = "resume"

    model_config = {"json_schema_extra": {"example": {"action": "resume"}}}


class SetSpeedMessage(BaseClientMessage):
    """Change the simulation playback speed."""

    action: Literal["set_speed"] = "set_speed"
    speed: float = Field(
        ge=0.1,
        le=10.0,
        description="Simulation speed multiplier (0.1 = slow motion, 10.0 = 10x faster)",
    )

    model_config = {
        "json_schema_extra": {"example": {"action": "set_speed", "speed": 2.0}}
    }


class GetStatusMessage(BaseClientMessage):
    """Request current match status."""

    action: Literal["get_status"] = "get_status"

    model_config = {"json_schema_extra": {"example": {"action": "get_status"}}}


# Union type for all client messages
WebSocketClientMessage = (
    PingMessage | PauseMessage | ResumeMessage | SetSpeedMessage | GetStatusMessage
)
