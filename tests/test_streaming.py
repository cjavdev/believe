"""Tests for the streaming endpoints."""

import json

import pytest


@pytest.mark.asyncio
async def test_stream_pep_talk(client):
    """Test the pep talk SSE stream."""
    async with client.stream("GET", "/pep-talk/stream") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        chunks = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                chunks.append(data)
                # Stop after a few chunks for testing
                if len(chunks) >= 3:
                    break

        assert len(chunks) >= 1
        # Check structure of first chunk
        assert "chunk_id" in chunks[0]
        assert "text" in chunks[0]
        assert "is_final" in chunks[0]


@pytest.mark.asyncio
async def test_stream_match_commentary(client):
    """Test the match commentary SSE stream."""
    async with client.stream(
        "POST", "/matches/match-001/commentary/stream"
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        events = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                events.append(data)
                # Stop after a few events for testing
                if len(events) >= 3:
                    break

        assert len(events) >= 1
        # Check structure of first event
        assert "event_id" in events[0]
        assert "minute" in events[0]
        assert "event_type" in events[0]
        assert "commentary" in events[0]


@pytest.mark.asyncio
async def test_stream_match_commentary_new_match(client):
    """Test streaming commentary for a new match ID."""
    async with client.stream(
        "POST", "/matches/match-new/commentary/stream"
    ) as response:
        assert response.status_code == 200

        events = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                events.append(data)
                if len(events) >= 2:
                    break

        assert len(events) >= 1


@pytest.mark.asyncio
async def test_stream_test_endpoint(client):
    """Test the SSE test endpoint."""
    async with client.stream("GET", "/stream/test") as response:
        assert response.status_code == 200

        messages = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                messages.append(data)

        # Should have all 6 test messages
        assert len(messages) == 6
        assert messages[0]["sequence"] == 1
        assert "Believe!" in messages[2]["message"]
        assert messages[4]["message"] == "Stream complete. You're all set!"
        assert messages[5]["message"] == "[done]"
