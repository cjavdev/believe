"""Streaming endpoints router for Ted Lasso API."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from app.auth import verify_api_key
from app.data import MATCHES
from app.models.interactive import PepTalkResponse
from app.services import StreamingService

router = APIRouter(
    tags=["Streaming"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/pep-talk",
    summary="Get a Pep Talk",
    description="Get a motivational pep talk from Ted Lasso himself. "
    "By default returns the complete pep talk. Add `?stream=true` to get "
    "Server-Sent Events (SSE) streaming the pep talk chunk by chunk.",
    response_model=PepTalkResponse,
    responses={
        200: {
            "description": "Pep talk response (JSON or SSE stream)",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/PepTalkResponse"},
                },
                "text/event-stream": {
                    "schema": {},  # Schema defined in generate_openapi.py as PepTalkChunk
                    "example": 'data: {"chunk_id": 0, "text": "Hey there, friend. ", "is_final": false, "emotional_beat": "greeting"}\n\n',
                },
            },
        }
    },
)
async def get_pep_talk(
    stream: bool = Query(
        default=False,
        description="If true, returns SSE stream instead of full response",
    ),
):
    """Get a motivational pep talk from Ted."""
    if stream:

        async def event_generator():
            async for chunk in StreamingService.stream_pep_talk():
                yield {
                    "event": "pep_talk",
                    "data": json.dumps(chunk.model_dump()),
                }

        return EventSourceResponse(event_generator())

    return StreamingService.get_pep_talk()


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
                    "schema": {},  # Schema defined in generate_openapi.py as MatchCommentaryEvent
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
                    "schema": {},  # Schema defined in generate_openapi.py as TestStreamChunk
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
            "[done]",
        ]

        for i, msg in enumerate(messages):
            yield {
                "event": "test",
                "data": json.dumps({"sequence": i + 1, "message": msg}),
            }
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
