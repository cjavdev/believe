"""Tests for the teams router."""

import pytest


@pytest.mark.asyncio
async def test_list_teams(client):
    """Test listing all teams."""
    response = await client.get("/teams")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check AFC Richmond is in the list
    names = [t["name"] for t in data]
    assert "AFC Richmond" in names


@pytest.mark.asyncio
async def test_list_teams_filter_by_league(client):
    """Test filtering teams by league."""
    response = await client.get("/teams?league=Premier League")
    assert response.status_code == 200
    data = response.json()
    assert all(t["league"] == "Premier League" for t in data)


@pytest.mark.asyncio
async def test_list_teams_filter_by_culture(client):
    """Test filtering teams by minimum culture score."""
    response = await client.get("/teams?min_culture_score=80")
    assert response.status_code == 200
    data = response.json()
    assert all(t["culture_score"] >= 80 for t in data)


@pytest.mark.asyncio
async def test_get_team(client):
    """Test getting a specific team."""
    response = await client.get("/teams/afc-richmond")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "afc-richmond"
    assert data["name"] == "AFC Richmond"
    assert "values" in data
    assert data["values"]["primary_value"] == "Believe"


@pytest.mark.asyncio
async def test_get_team_not_found(client):
    """Test getting a non-existent team."""
    response = await client.get("/teams/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_team(client, sample_team):
    """Test creating a new team."""
    response = await client.post("/teams", json=sample_team)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_team["name"]
    assert data["id"] == "test-fc"


@pytest.mark.asyncio
async def test_create_team_duplicate(client, sample_team):
    """Test creating a duplicate team fails."""
    # First creation should succeed
    await client.post("/teams", json=sample_team)
    # Second creation should fail
    response = await client.post("/teams", json=sample_team)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_team(client):
    """Test updating a team."""
    response = await client.patch(
        "/teams/afc-richmond",
        json={"culture_score": 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["culture_score"] == 100


@pytest.mark.asyncio
async def test_update_team_not_found(client):
    """Test updating a non-existent team."""
    response = await client.patch(
        "/teams/nonexistent",
        json={"name": "New Name"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_team_rivals(client):
    """Test getting a team's rivals."""
    response = await client.get("/teams/afc-richmond/rivals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_team_culture(client):
    """Test getting team culture details."""
    response = await client.get("/teams/afc-richmond/culture")
    assert response.status_code == 200
    data = response.json()
    assert "team_name" in data
    assert "culture_score" in data
    assert "values" in data
    assert "culture_assessment" in data
