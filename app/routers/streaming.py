"""Streaming endpoints router for Ted Lasso API."""

import json
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.data import MATCHES
from app.services import StreamingService

router = APIRouter(tags=["Streaming"])


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
                    "example": 'data: {"chunk_id": 0, "text": "Hey there, friend. ", "is_final": false, "emotional_beat": "greeting"}\n\n'
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
                    "example": 'data: {"event_id": 0, "minute": 0, "event_type": "kickoff", "description": "The match kicks off", "commentary": "And we\'re off!", "is_final": false}\n\n'
                }
            },
        },
        404: {"description": "Match not found"},
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
