"""Tests for the matches router."""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_list_matches(client):
    """Test listing all matches."""
    response = await client.get("/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_matches_filter_by_team(client):
    """Test filtering matches by team."""
    response = await client.get("/matches?team_id=afc-richmond")
    assert response.status_code == 200
    data = response.json()
    assert all(
        m["home_team_id"] == "afc-richmond" or m["away_team_id"] == "afc-richmond"
        for m in data
    )


@pytest.mark.asyncio
async def test_list_matches_filter_by_result(client):
    """Test filtering matches by result."""
    response = await client.get("/matches?result=draw")
    assert response.status_code == 200
    data = response.json()
    assert all(m["result"] == "draw" for m in data)


@pytest.mark.asyncio
async def test_get_match(client):
    """Test getting a specific match."""
    response = await client.get("/matches/match-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "match-001"
    assert "turning_points" in data
    assert "lesson_learned" in data


@pytest.mark.asyncio
async def test_get_match_not_found(client):
    """Test getting a non-existent match."""
    response = await client.get("/matches/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_match(client):
    """Test creating a new match."""
    match_data = {
        "home_team_id": "afc-richmond",
        "away_team_id": "tottenham",
        "match_type": "league",
        "date": datetime.now().isoformat(),
        "home_score": 0,
        "away_score": 0,
        "result": "pending",
        "turning_points": [],
    }
    response = await client.post("/matches", json=match_data)
    assert response.status_code == 201
    data = response.json()
    assert data["home_team_id"] == "afc-richmond"
    assert data["id"].startswith("match-")


@pytest.mark.asyncio
async def test_update_match(client):
    """Test updating a match."""
    response = await client.patch(
        "/matches/match-001",
        json={"home_score": 5, "away_score": 0, "result": "win"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["home_score"] == 5


@pytest.mark.asyncio
async def test_update_match_not_found(client):
    """Test updating a non-existent match."""
    response = await client.patch(
        "/matches/nonexistent",
        json={"home_score": 1},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_turning_points(client):
    """Test getting match turning points."""
    response = await client.get("/matches/match-001/turning-points")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_match_lesson(client):
    """Test getting the lesson from a match."""
    response = await client.get("/matches/match-001/lesson")
    assert response.status_code == 200
    data = response.json()
    assert "match_id" in data
    assert "lesson_learned" in data
