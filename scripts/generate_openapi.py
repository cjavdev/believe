#!/usr/bin/env python3
"""Generate OpenAPI specification from FastAPI app."""

import json
import sys
from pathlib import Path

# Add parent directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402

# WebSocket schemas to add to components/schemas
WEBSOCKET_SCHEMAS = {
    "WebSocketMatchStartMessage": {
        "type": "object",
        "description": "Message sent when a match simulation starts.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["match_start"],
                "description": "Message type",
            },
            "match_id": {
                "type": "string",
                "description": "Unique match identifier",
            },
            "home_team": {
                "type": "string",
                "description": "Home team name",
            },
            "away_team": {
                "type": "string",
                "description": "Away team name",
            },
            "message": {
                "type": "string",
                "description": "Welcome message",
            },
        },
        "required": ["type", "match_id", "home_team", "away_team", "message"],
    },
    "WebSocketMatchEventMessage": {
        "type": "object",
        "description": "Message containing a live match event.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["match_event"],
                "description": "Message type",
            },
            "event": {
                "$ref": "#/components/schemas/WebSocketLiveMatchEvent",
            },
        },
        "required": ["type", "event"],
    },
    "WebSocketLiveMatchEvent": {
        "type": "object",
        "description": "A live match event with full details.",
        "properties": {
            "event_id": {
                "type": "integer",
                "description": "Unique event sequence number",
            },
            "event_type": {
                "type": "string",
                "enum": [
                    "match_start",
                    "goal",
                    "possession_change",
                    "foul",
                    "yellow_card",
                    "red_card",
                    "penalty_awarded",
                    "penalty_scored",
                    "penalty_missed",
                    "substitution",
                    "injury",
                    "offside",
                    "corner",
                    "free_kick",
                    "shot_on_target",
                    "shot_off_target",
                    "save",
                    "halftime",
                    "second_half_start",
                    "added_time",
                    "match_end",
                ],
                "description": "Type of match event",
            },
            "minute": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120,
                "description": "Match minute",
            },
            "added_time": {
                "type": "integer",
                "minimum": 0,
                "maximum": 15,
                "nullable": True,
                "description": "Added/injury time minutes",
            },
            "team": {
                "type": "string",
                "enum": ["home", "away"],
                "nullable": True,
                "description": "Which team the event relates to",
            },
            "player": {
                "$ref": "#/components/schemas/WebSocketPlayerInfo",
                "nullable": True,
            },
            "secondary_player": {
                "$ref": "#/components/schemas/WebSocketPlayerInfo",
                "nullable": True,
                "description": "Second player involved (e.g., assist, replaced player)",
            },
            "description": {
                "type": "string",
                "description": "Human-readable event description",
            },
            "score": {
                "$ref": "#/components/schemas/WebSocketMatchScore",
            },
            "stats": {
                "$ref": "#/components/schemas/WebSocketMatchStats",
            },
            "ted_reaction": {
                "type": "string",
                "nullable": True,
                "description": "Ted Lasso's sideline reaction",
            },
            "crowd_reaction": {
                "type": "string",
                "nullable": True,
                "description": "Crowd reaction to the event",
            },
            "commentary": {
                "type": "string",
                "description": "Match commentary for this event",
            },
        },
        "required": [
            "event_id",
            "event_type",
            "minute",
            "description",
            "score",
            "stats",
            "commentary",
        ],
    },
    "WebSocketPlayerInfo": {
        "type": "object",
        "description": "Information about a player involved in an event.",
        "properties": {
            "name": {
                "type": "string",
                "description": "Player name",
            },
            "number": {
                "type": "integer",
                "minimum": 1,
                "maximum": 99,
                "description": "Jersey number",
            },
            "position": {
                "type": "string",
                "description": "Player position",
            },
        },
        "required": ["name", "number", "position"],
    },
    "WebSocketMatchScore": {
        "type": "object",
        "description": "Current match score.",
        "properties": {
            "home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team score",
            },
            "away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team score",
            },
        },
        "required": ["home", "away"],
    },
    "WebSocketMatchStats": {
        "type": "object",
        "description": "Current match statistics.",
        "properties": {
            "possession_home": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Home team possession %",
            },
            "possession_away": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Away team possession %",
            },
            "shots_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team total shots",
            },
            "shots_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team total shots",
            },
            "shots_on_target_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team shots on target",
            },
            "shots_on_target_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team shots on target",
            },
            "corners_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team corners",
            },
            "corners_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team corners",
            },
            "fouls_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team fouls",
            },
            "fouls_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team fouls",
            },
            "yellow_cards_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team yellow cards",
            },
            "yellow_cards_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team yellow cards",
            },
            "red_cards_home": {
                "type": "integer",
                "minimum": 0,
                "description": "Home team red cards",
            },
            "red_cards_away": {
                "type": "integer",
                "minimum": 0,
                "description": "Away team red cards",
            },
        },
        "required": [
            "possession_home",
            "possession_away",
            "shots_home",
            "shots_away",
            "shots_on_target_home",
            "shots_on_target_away",
            "corners_home",
            "corners_away",
            "fouls_home",
            "fouls_away",
            "yellow_cards_home",
            "yellow_cards_away",
            "red_cards_home",
            "red_cards_away",
        ],
    },
    "WebSocketMatchEndMessage": {
        "type": "object",
        "description": "Message sent when a match simulation ends.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["match_end"],
                "description": "Message type",
            },
            "match_id": {
                "type": "string",
                "description": "Match identifier",
            },
            "final_score": {
                "$ref": "#/components/schemas/WebSocketMatchScore",
            },
            "final_stats": {
                "$ref": "#/components/schemas/WebSocketMatchStats",
            },
            "man_of_the_match": {
                "type": "string",
                "description": "Man of the match",
            },
            "ted_post_match": {
                "type": "string",
                "description": "Ted's post-match thoughts",
            },
        },
        "required": [
            "type",
            "match_id",
            "final_score",
            "final_stats",
            "man_of_the_match",
            "ted_post_match",
        ],
    },
    "WebSocketErrorMessage": {
        "type": "object",
        "description": "Error message for WebSocket communication.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["error"],
                "description": "Message type",
            },
            "code": {
                "type": "string",
                "description": "Error code",
            },
            "message": {
                "type": "string",
                "description": "Error description",
            },
        },
        "required": ["type", "code", "message"],
    },
    "WebSocketPongMessage": {
        "type": "object",
        "description": "Pong response to client ping.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["pong"],
                "description": "Message type",
            },
        },
        "required": ["type"],
    },
    "WebSocketClientPingMessage": {
        "type": "object",
        "description": "Ping message from client.",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["ping"],
                "description": "Action to perform",
            },
        },
        "required": ["action"],
    },
    "WebSocketTestWelcomeMessage": {
        "type": "object",
        "description": "Welcome message sent when connecting to the test WebSocket.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["welcome"],
                "description": "Message type",
            },
            "message": {
                "type": "string",
                "description": "Welcome message",
            },
            "ted_says": {
                "type": "string",
                "description": "Ted's greeting",
            },
        },
        "required": ["type", "message", "ted_says"],
    },
    "WebSocketTestEchoMessage": {
        "type": "object",
        "description": "Echo response from the test WebSocket.",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["echo"],
                "description": "Message type",
            },
            "message": {
                "type": "string",
                "description": "The echoed message",
            },
            "ted_says": {
                "type": "string",
                "description": "Ted's response",
            },
        },
        "required": ["type", "message", "ted_says"],
    },
    "WebSocketServerMessage": {
        "oneOf": [
            {"$ref": "#/components/schemas/WebSocketMatchStartMessage"},
            {"$ref": "#/components/schemas/WebSocketMatchEventMessage"},
            {"$ref": "#/components/schemas/WebSocketMatchEndMessage"},
            {"$ref": "#/components/schemas/WebSocketErrorMessage"},
            {"$ref": "#/components/schemas/WebSocketPongMessage"},
        ],
        "description": "Messages sent by the server during live match simulation.",
    },
    "WebSocketTestServerMessage": {
        "oneOf": [
            {"$ref": "#/components/schemas/WebSocketTestWelcomeMessage"},
            {"$ref": "#/components/schemas/WebSocketTestEchoMessage"},
        ],
        "description": "Messages sent by the test WebSocket endpoint.",
    },
}

# WebSocket path definitions
WEBSOCKET_PATHS = {
    "/matches/live": {
        "get": {
            "summary": "Live Match Simulation WebSocket",
            "description": """WebSocket endpoint for real-time live match simulation.

Connect to receive a stream of match events as they happen in a simulated football match.

## Connection

Connect via WebSocket with optional query parameters to customize the simulation.

## Example WebSocket URL

```
ws://localhost:8000/matches/live?home_team=AFC%20Richmond&away_team=Manchester%20City&speed=2.0&excitement_level=7
```

## Server Messages

The server sends JSON messages with these types:
- `match_start` - When the match begins
- `match_event` - For each match event (goals, fouls, cards, etc.)
- `match_end` - When the match concludes
- `error` - If an error occurs
- `pong` - Response to client ping

## Client Messages

Send JSON to control the simulation:
- `{"action": "ping"}` - Server responds with `{"type": "pong"}`
""",
            "operationId": "live_match_websocket",
            "tags": ["WebSocket"],
            "parameters": [
                {
                    "name": "home_team",
                    "in": "query",
                    "description": "Home team name",
                    "required": False,
                    "schema": {
                        "type": "string",
                        "default": "AFC Richmond",
                    },
                },
                {
                    "name": "away_team",
                    "in": "query",
                    "description": "Away team name",
                    "required": False,
                    "schema": {
                        "type": "string",
                        "default": "West Ham United",
                    },
                },
                {
                    "name": "speed",
                    "in": "query",
                    "description": "Simulation speed multiplier (1.0 = real-time)",
                    "required": False,
                    "schema": {
                        "type": "number",
                        "minimum": 0.1,
                        "maximum": 10.0,
                        "default": 1.0,
                    },
                },
                {
                    "name": "excitement_level",
                    "in": "query",
                    "description": "How eventful the match should be (1=boring, 10=chaos)",
                    "required": False,
                    "schema": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                    },
                },
            ],
            "responses": {
                "101": {
                    "description": "Switching Protocols - WebSocket connection established",
                }
            },
            "callbacks": {
                "onMatchEvent": {
                    "{$request.query.callback}": {
                        "post": {
                            "summary": "Match event callback",
                            "description": "Server sends match events over the WebSocket connection",
                            "requestBody": {
                                "description": "Match event message from server",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/WebSocketServerMessage"
                                        },
                                        "examples": {
                                            "match_start": {
                                                "summary": "Match start message",
                                                "value": {
                                                    "type": "match_start",
                                                    "match_id": "abc123",
                                                    "home_team": "AFC Richmond",
                                                    "away_team": "West Ham United",
                                                    "message": "Welcome to Nelson Road! AFC Richmond vs West Ham United is about to begin. BELIEVE!",
                                                },
                                            },
                                            "goal_event": {
                                                "summary": "Goal scored event",
                                                "value": {
                                                    "type": "match_event",
                                                    "event": {
                                                        "event_id": 15,
                                                        "event_type": "goal",
                                                        "minute": 23,
                                                        "team": "home",
                                                        "player": {
                                                            "name": "Jamie Tartt",
                                                            "number": 9,
                                                            "position": "Forward",
                                                        },
                                                        "description": "GOAL! Jamie Tartt scores with a brilliant strike!",
                                                        "score": {"home": 1, "away": 0},
                                                        "stats": {
                                                            "possession_home": 55.0,
                                                            "possession_away": 45.0,
                                                            "shots_home": 5,
                                                            "shots_away": 3,
                                                            "shots_on_target_home": 2,
                                                            "shots_on_target_away": 1,
                                                            "corners_home": 2,
                                                            "corners_away": 1,
                                                            "fouls_home": 3,
                                                            "fouls_away": 4,
                                                            "yellow_cards_home": 0,
                                                            "yellow_cards_away": 1,
                                                            "red_cards_home": 0,
                                                            "red_cards_away": 0,
                                                        },
                                                        "ted_reaction": "Football is life!",
                                                        "crowd_reaction": "The crowd at Nelson Road erupts!",
                                                        "commentary": "What a strike from Jamie Tartt! He's done it again!",
                                                    },
                                                },
                                            },
                                            "match_end": {
                                                "summary": "Match end message",
                                                "value": {
                                                    "type": "match_end",
                                                    "match_id": "abc123",
                                                    "final_score": {
                                                        "home": 2,
                                                        "away": 1,
                                                    },
                                                    "final_stats": {
                                                        "possession_home": 52.0,
                                                        "possession_away": 48.0,
                                                        "shots_home": 12,
                                                        "shots_away": 9,
                                                        "shots_on_target_home": 5,
                                                        "shots_on_target_away": 3,
                                                        "corners_home": 6,
                                                        "corners_away": 4,
                                                        "fouls_home": 10,
                                                        "fouls_away": 12,
                                                        "yellow_cards_home": 1,
                                                        "yellow_cards_away": 2,
                                                        "red_cards_home": 0,
                                                        "red_cards_away": 0,
                                                    },
                                                    "man_of_the_match": "Jamie Tartt",
                                                    "ted_post_match": "Win, lose, or draw - I'm proud of every single one of you. Now who wants to grab some barbecue?",
                                                },
                                            },
                                        },
                                    }
                                },
                            },
                            "responses": {"200": {"description": "Message received"}},
                        }
                    }
                },
                "onClientMessage": {
                    "{$request.query.callback}": {
                        "post": {
                            "summary": "Client message",
                            "description": "Client can send control messages over the WebSocket",
                            "requestBody": {
                                "description": "Control message from client",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/WebSocketClientPingMessage"
                                        },
                                        "examples": {
                                            "ping": {
                                                "summary": "Ping message",
                                                "value": {"action": "ping"},
                                            }
                                        },
                                    }
                                },
                            },
                            "responses": {"200": {"description": "Message sent"}},
                        }
                    }
                },
            },
        }
    },
    "/ws/test": {
        "get": {
            "summary": "WebSocket Test Endpoint",
            "description": """Simple WebSocket test endpoint for connectivity testing.

Connect to test WebSocket functionality. The server will:
1. Send a welcome message on connection
2. Echo back any message you send

## Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test');
ws.onmessage = (event) => console.log(event.data);
ws.send('Hello!');  // Server responds with echo
```
""",
            "operationId": "websocket_test",
            "tags": ["WebSocket"],
            "responses": {
                "101": {
                    "description": "Switching Protocols - WebSocket connection established",
                }
            },
            "callbacks": {
                "onMessage": {
                    "{$request.query.callback}": {
                        "post": {
                            "summary": "Server message",
                            "description": "Messages sent by the test WebSocket",
                            "requestBody": {
                                "description": "Message from server",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/WebSocketTestServerMessage"
                                        },
                                        "examples": {
                                            "welcome": {
                                                "summary": "Welcome message on connect",
                                                "value": {
                                                    "type": "welcome",
                                                    "message": "Welcome to the Ted Lasso API WebSocket test! Send any message and I'll echo it back.",
                                                    "ted_says": "Hey there, friend! This WebSocket connection is working smoother than a fresh jar of peanut butter!",
                                                },
                                            },
                                            "echo": {
                                                "summary": "Echo response",
                                                "value": {
                                                    "type": "echo",
                                                    "message": "Hello!",
                                                    "ted_says": "I heard you loud and clear, partner!",
                                                },
                                            },
                                        },
                                    }
                                },
                            },
                            "responses": {"200": {"description": "Message received"}},
                        }
                    }
                }
            },
        }
    },
}

# SSE streaming schemas to add to components/schemas
SSE_SCHEMAS = {
    "PepTalkChunk": {
        "type": "object",
        "description": "A chunk of a streaming pep talk from Ted.",
        "properties": {
            "chunk_id": {
                "type": "integer",
                "description": "Chunk sequence number",
            },
            "text": {
                "type": "string",
                "description": "The text of this chunk",
            },
            "is_final": {
                "type": "boolean",
                "description": "Is this the final chunk",
                "default": False,
            },
            "emotional_beat": {
                "type": "string",
                "nullable": True,
                "description": "The emotional purpose of this chunk (e.g., greeting, acknowledgment, wisdom, affirmation, encouragement)",
            },
        },
        "required": ["chunk_id", "text", "is_final"],
    },
    "MatchCommentaryEvent": {
        "type": "object",
        "description": "A single commentary event during a match stream.",
        "properties": {
            "event_id": {
                "type": "integer",
                "description": "Event sequence number",
            },
            "minute": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120,
                "description": "Match minute",
            },
            "event_type": {
                "type": "string",
                "enum": [
                    "kickoff",
                    "goal",
                    "near_miss",
                    "save",
                    "foul",
                    "substitution",
                    "halftime",
                    "ted_reaction",
                    "crowd_moment",
                    "final_whistle",
                ],
                "description": "Type of event",
            },
            "description": {
                "type": "string",
                "description": "What happened",
            },
            "commentary": {
                "type": "string",
                "description": "Commentator's call",
            },
            "ted_sideline_reaction": {
                "type": "string",
                "nullable": True,
                "description": "Ted's reaction on the sideline",
            },
            "crowd_reaction": {
                "type": "string",
                "nullable": True,
                "description": "How the crowd reacted",
            },
            "is_final": {
                "type": "boolean",
                "description": "Is this the final event",
                "default": False,
            },
        },
        "required": [
            "event_id",
            "minute",
            "event_type",
            "description",
            "commentary",
            "is_final",
        ],
    },
    "TestStreamChunk": {
        "type": "object",
        "description": "A test stream chunk for SSE connectivity testing.",
        "properties": {
            "sequence": {
                "type": "integer",
                "description": "The sequence number of this chunk (1-5)",
            },
            "message": {
                "type": "string",
                "description": "The message content for this chunk",
            },
        },
        "required": ["sequence", "message"],
    },
}

# Mapping of endpoint paths to their SSE schema refs
SSE_ENDPOINT_SCHEMAS = {
    "/pep-talk": "PepTalkChunk",
    "/matches/{match_id}/commentary/stream": "MatchCommentaryEvent",
    "/stream/test": "TestStreamChunk",
}


def generate_openapi_spec() -> dict:
    """Generate the OpenAPI specification from the FastAPI app."""
    spec = app.openapi()

    # Add schemas to components/schemas
    if "components" not in spec:
        spec["components"] = {}
    if "schemas" not in spec["components"]:
        spec["components"]["schemas"] = {}

    # Add WebSocket schemas
    spec["components"]["schemas"].update(WEBSOCKET_SCHEMAS)

    # Add SSE schemas
    spec["components"]["schemas"].update(SSE_SCHEMAS)

    # Add WebSocket paths
    if "paths" not in spec:
        spec["paths"] = {}
    spec["paths"].update(WEBSOCKET_PATHS)

    # Update SSE endpoints to use $ref instead of inline schemas
    for path, schema_name in SSE_ENDPOINT_SCHEMAS.items():
        if path in spec.get("paths", {}):
            path_item = spec["paths"][path]
            # Check both GET and POST methods
            for method in ["get", "post"]:
                if method in path_item:
                    responses = path_item[method].get("responses", {})
                    if "200" in responses:
                        content = responses["200"].get("content", {})
                        if "text/event-stream" in content:
                            # Replace inline schema with $ref
                            content["text/event-stream"]["schema"] = {
                                "$ref": f"#/components/schemas/{schema_name}"
                            }

    return spec


def main():
    """Generate and output the OpenAPI specification."""
    spec = generate_openapi_spec()
    # Output with consistent formatting for diffing
    print(json.dumps(spec, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
