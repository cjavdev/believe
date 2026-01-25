"""Tests for the characters router."""

import pytest


@pytest.mark.asyncio
async def test_list_characters(client):
    """Test listing all characters."""
    response = await client.get("/characters")
    assert response.status_code == 200
    result = response.json()
    # Check pagination structure
    assert "data" in result
    assert "total" in result
    assert "skip" in result
    assert "limit" in result
    assert "has_more" in result
    assert "page" in result
    assert "pages" in result
    data = result["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    # Check Ted Lasso is in the list
    names = [c["name"] for c in data]
    assert "Ted Lasso" in names


@pytest.mark.asyncio
async def test_list_characters_filter_by_role(client):
    """Test filtering characters by role."""
    response = await client.get("/characters?role=coach")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(c["role"] == "coach" for c in data)


@pytest.mark.asyncio
async def test_list_characters_filter_by_team(client):
    """Test filtering characters by team."""
    response = await client.get("/characters?team_id=afc-richmond")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(c["team_id"] == "afc-richmond" for c in data)


@pytest.mark.asyncio
async def test_list_characters_filter_by_optimism(client):
    """Test filtering characters by minimum optimism."""
    response = await client.get("/characters?min_optimism=80")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(c["emotional_stats"]["optimism"] >= 80 for c in data)


@pytest.mark.asyncio
async def test_list_characters_pagination(client):
    """Test pagination parameters."""
    # Test with custom limit
    response = await client.get("/characters?limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) <= 2
    assert result["limit"] == 2
    assert result["skip"] == 0

    # Test with skip
    response = await client.get("/characters?skip=1&limit=2")
    assert response.status_code == 200
    result = response.json()
    assert result["skip"] == 1
    assert result["limit"] == 2


@pytest.mark.asyncio
async def test_get_character(client):
    """Test getting a specific character."""
    response = await client.get("/characters/ted-lasso")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "ted-lasso"
    assert data["name"] == "Ted Lasso"
    assert data["role"] == "coach"
    assert "emotional_stats" in data
    assert "signature_quotes" in data


@pytest.mark.asyncio
async def test_get_character_not_found(client):
    """Test getting a non-existent character."""
    response = await client.get("/characters/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_character(client, sample_character):
    """Test creating a new character."""
    response = await client.post("/characters", json=sample_character)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_character["name"]
    assert data["id"] == "test-character"


@pytest.mark.asyncio
async def test_create_character_duplicate(client, sample_character):
    """Test creating a duplicate character fails."""
    # First creation should succeed
    await client.post("/characters", json=sample_character)
    # Second creation should fail
    response = await client.post("/characters", json=sample_character)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_character(client):
    """Test updating a character."""
    response = await client.patch(
        "/characters/ted-lasso",
        json={"personality_traits": ["optimistic", "kind", "updated"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "updated" in data["personality_traits"]


@pytest.mark.asyncio
async def test_update_character_not_found(client):
    """Test updating a non-existent character."""
    response = await client.patch(
        "/characters/nonexistent",
        json={"name": "New Name"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_character_quotes(client):
    """Test getting a character's quotes."""
    response = await client.get("/characters/ted-lasso/quotes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_character_quotes_not_found(client):
    """Test getting quotes for a non-existent character."""
    response = await client.get("/characters/nonexistent/quotes")
    assert response.status_code == 404
