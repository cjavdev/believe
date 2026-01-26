"""Streaming endpoints router for Ted Lasso API."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.auth import verify_api_key
from app.data import MATCHES
from app.services import StreamingService

router = APIRouter(
    tags=["Streaming"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/pep-talk/stream",
    summary="Stream a Pep Talk",
    description="Get a streaming motivational pep talk from Ted Lasso himself. "
    "Uses Server-Sent Events (SSE) to stream the pep talk chunk by chunk.",
    responses={
        200: {
            "description": "SSE stream of pep talk chunks",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "object",
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
                    "example": 'data: {"chunk_id": 0, "text": "Hey there, friend. ", "is_final": false, "emotional_beat": "greeting"}\n\n',
                }
            },
        }
    },
)
async def stream_pep_talk():
    """Stream a motivational pep talk from Ted."""

    async def event_generator():
        async for chunk in StreamingService.stream_pep_talk():
            yield {
                "event": "pep_talk",
                "data": json.dumps(chunk.model_dump()),
            }

    return EventSourceResponse(event_generator())


@router.post(
    "/matches/{match_id}/commentary/stream",
    summary="Stream Match Commentary",
    description="Stream live match commentary for a specific match. "
    "Uses Server-Sent Events (SSE) to stream commentary events in real-time.",
    responses={
        200: {
            "description": "SSE stream of match commentary events",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "object",
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
                    "example": 'data: {"event_id": 0, "minute": 0, "event_type": "kickoff", "description": "The match kicks off", "commentary": "And we\'re off!", "ted_sideline_reaction": "Ted claps enthusiastically", "crowd_reaction": "The crowd roars", "is_final": false}\n\n',
                }
            },
        },
        404: {
            "description": "Match not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Match 'invalid-match' not found. Try one of our existing matches or use format 'match-XXX'!"
                    }
                }
            },
        },
    },
)
async def stream_match_commentary(match_id: str):
    """Stream live match commentary."""
    # Validate match exists (or allow any match_id for demo purposes)
    if match_id not in MATCHES and not match_id.startswith("match-"):
        raise HTTPException(
            status_code=404,
            detail=f"Match '{match_id}' not found. Try one of our existing matches or use format 'match-XXX'!",
        )

    async def event_generator():
        async for event in StreamingService.stream_match_commentary(match_id):
            yield {
                "event": "commentary",
                "data": json.dumps(event.model_dump()),
            }

    return EventSourceResponse(event_generator())


@router.get(
    "/stream/test",
    summary="Test SSE Connection",
    description="A simple SSE test endpoint that streams numbers 1-5.",
    responses={
        200: {
            "description": "SSE stream of test messages",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "object",
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
                    "example": 'data: {"sequence": 1, "message": "Testing... 1, 2, 3..."}\n\ndata: {"sequence": 2, "message": "Is this thing on?"}\n\ndata: {"sequence": 3, "message": "Believe!"}\n\n',
                }
            },
        }
    },
)
async def test_stream():
    """Test SSE streaming functionality."""
    import asyncio

    async def event_generator():
        messages = [
            "Testing... 1, 2, 3...",
            "Is this thing on?",
            "Believe!",
            "Football is life!",
            "Stream complete. You're all set!",
        ]

        for i, msg in enumerate(messages):
            yield {
                "event": "test",
                "data": json.dumps({"sequence": i + 1, "message": msg}),
            }
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
