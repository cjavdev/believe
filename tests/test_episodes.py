"""Tests for the episodes router."""

import pytest


@pytest.mark.asyncio
async def test_list_episodes(client):
    """Test listing all episodes."""
    response = await client.get("/episodes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_episodes_filter_by_season(client):
    """Test filtering episodes by season."""
    response = await client.get("/episodes?season=1")
    assert response.status_code == 200
    data = response.json()
    assert all(e["season"] == 1 for e in data)


@pytest.mark.asyncio
async def test_list_episodes_filter_by_character(client):
    """Test filtering episodes by character focus."""
    response = await client.get("/episodes?character_focus=ted-lasso")
    assert response.status_code == 200
    data = response.json()
    assert all("ted-lasso" in e["character_focus"] for e in data)


@pytest.mark.asyncio
async def test_get_episode(client):
    """Test getting a specific episode."""
    response = await client.get("/episodes/s01e01")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "s01e01"
    assert data["title"] == "Pilot"
    assert "ted_wisdom" in data


@pytest.mark.asyncio
async def test_get_episode_not_found(client):
    """Test getting a non-existent episode."""
    response = await client.get("/episodes/s99e99")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_episode(client):
    """Test creating a new episode."""
    episode_data = {
        "season": 3,
        "episode_number": 12,
        "title": "Test Episode",
        "director": "Test Director",
        "writer": "Test Writer",
        "air_date": "2024-01-01",
        "runtime_minutes": 30,
        "synopsis": "A test episode for testing purposes.",
        "main_theme": "Testing is believing",
        "ted_wisdom": "Every test is a chance to learn something new.",
        "character_focus": ["ted-lasso"],
        "memorable_moments": ["The test begins"],
    }
    response = await client.post("/episodes", json=episode_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "s03e12"
    assert data["title"] == "Test Episode"


@pytest.mark.asyncio
async def test_update_episode(client):
    """Test updating an episode."""
    response = await client.patch(
        "/episodes/s01e01",
        json={"runtime_minutes": 35},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["runtime_minutes"] == 35


@pytest.mark.asyncio
async def test_get_episode_wisdom(client):
    """Test getting episode wisdom."""
    response = await client.get("/episodes/s01e01/wisdom")
    assert response.status_code == 200
    data = response.json()
    assert "ted_wisdom" in data
    assert "main_theme" in data
    assert "memorable_moments" in data


@pytest.mark.asyncio
async def test_get_season_episodes(client):
    """Test getting all episodes from a season."""
    response = await client.get("/episodes/seasons/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(e["season"] == 1 for e in data)


@pytest.mark.asyncio
async def test_get_season_episodes_not_found(client):
    """Test getting episodes from a non-existent season."""
    response = await client.get("/episodes/seasons/99")
    assert response.status_code == 404
