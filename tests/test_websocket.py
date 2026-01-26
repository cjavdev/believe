"""Tests for WebSocket live match simulation."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_websocket_test_endpoint():
    """Test the simple WebSocket test endpoint."""
    with client.websocket_connect("/ws/test") as websocket:
        # Should receive welcome message
        data = websocket.receive_json()
        assert data["type"] == "welcome"
        assert "ted_says" in data

        # Send a message and get echo
        websocket.send_text("Hello Ted!")
        data = websocket.receive_json()
        assert data["type"] == "echo"
        assert data["message"] == "Hello Ted!"
        assert "ted_says" in data


def test_live_match_simulation():
    """Test the live match WebSocket endpoint."""
    with client.websocket_connect(
        "/matches/live?home_team=AFC%20Richmond&away_team=West%20Ham&speed=10.0&excitement_level=3"
    ) as websocket:
        # Should receive match start message
        data = websocket.receive_json()
        assert data["type"] == "match_start"
        assert data["home_team"] == "AFC Richmond"
        assert data["away_team"] == "West Ham"
        assert "match_id" in data

        # Collect some events
        events_received = []
        match_ended = False

        while not match_ended and len(events_received) < 50:
            data = websocket.receive_json()

            if data["type"] == "match_event":
                events_received.append(data["event"])
                assert "event_id" in data["event"]
                assert "event_type" in data["event"]
                assert "minute" in data["event"]
                assert "score" in data["event"]
                assert "stats" in data["event"]
                assert "commentary" in data["event"]
            elif data["type"] == "match_end":
                match_ended = True
                assert "final_score" in data
                assert "final_stats" in data
                assert "man_of_the_match" in data
                assert "ted_post_match" in data

        # Should have received some events
        assert len(events_received) > 0

        # Check that we got the expected event structure
        first_event = events_received[0]
        assert first_event["event_type"] == "match_start"


def test_live_match_default_teams():
    """Test live match with default team names."""
    with client.websocket_connect("/matches/live?speed=10.0") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "match_start"
        assert data["home_team"] == "AFC Richmond"
        assert data["away_team"] == "West Ham United"
        websocket.close()


def test_live_match_event_types():
    """Test that various event types are generated."""
    with client.websocket_connect(
        "/matches/live?speed=10.0&excitement_level=10"
    ) as websocket:
        # Skip match start message
        websocket.receive_json()

        event_types_seen = set()

        # Collect events until match ends or we've seen enough
        while len(event_types_seen) < 5:
            data = websocket.receive_json()
            if data["type"] == "match_event":
                event_types_seen.add(data["event"]["event_type"])
            elif data["type"] == "match_end":
                break

        # Should see at least match_start event
        assert "match_start" in event_types_seen


def test_live_match_score_tracking():
    """Test that scores are tracked correctly across events."""
    with client.websocket_connect(
        "/matches/live?speed=10.0&excitement_level=8"
    ) as websocket:
        # Skip match start message
        websocket.receive_json()

        last_score = {"home": 0, "away": 0}
        goals_counted = 0

        while True:
            data = websocket.receive_json()

            if data["type"] == "match_event":
                event = data["event"]
                current_score = event["score"]

                # If this is a goal event, score should have increased
                if event["event_type"] in ["goal", "penalty_scored"]:
                    total_before = last_score["home"] + last_score["away"]
                    total_after = current_score["home"] + current_score["away"]
                    assert total_after == total_before + 1
                    goals_counted += 1

                # Score should never decrease
                assert current_score["home"] >= last_score["home"]
                assert current_score["away"] >= last_score["away"]

                last_score = current_score

            elif data["type"] == "match_end":
                break

        # Final score in match_end should match last event score
        assert data["final_score"]["home"] == last_score["home"]
        assert data["final_score"]["away"] == last_score["away"]
