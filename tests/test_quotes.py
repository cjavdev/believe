"""Tests for the quotes router."""

import pytest


@pytest.mark.asyncio
async def test_list_quotes(client):
    """Test listing all quotes."""
    response = await client.get("/quotes")
    assert response.status_code == 200
    result = response.json()
    # Check pagination structure
    assert "data" in result
    assert "total" in result
    data = result["data"]
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_quotes_filter_by_character(client):
    """Test filtering quotes by character."""
    response = await client.get("/quotes?character_id=ted-lasso")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(q["character_id"] == "ted-lasso" for q in data)


@pytest.mark.asyncio
async def test_list_quotes_filter_by_theme(client):
    """Test filtering quotes by theme."""
    response = await client.get("/quotes?theme=belief")
    assert response.status_code == 200
    data = response.json()["data"]
    # Check that theme matches primary or secondary
    for q in data:
        themes = [q["theme"]] + q.get("secondary_themes", [])
        assert "belief" in themes


@pytest.mark.asyncio
async def test_list_quotes_filter_by_moment_type(client):
    """Test filtering quotes by moment type."""
    response = await client.get("/quotes?moment_type=press_conference")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(q["moment_type"] == "press_conference" for q in data)


@pytest.mark.asyncio
async def test_list_quotes_filter_inspirational(client):
    """Test filtering inspirational quotes."""
    response = await client.get("/quotes?inspirational=true")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(q["is_inspirational"] is True for q in data)


@pytest.mark.asyncio
async def test_list_quotes_pagination(client):
    """Test pagination parameters."""
    response = await client.get("/quotes?limit=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) <= 5
    assert result["limit"] == 5


@pytest.mark.asyncio
async def test_get_random_quote(client):
    """Test getting a random quote."""
    response = await client.get("/quotes/random")
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "character_id" in data


@pytest.mark.asyncio
async def test_get_random_quote_filtered(client):
    """Test getting a random filtered quote."""
    response = await client.get("/quotes/random?character_id=ted-lasso")
    assert response.status_code == 200
    data = response.json()
    assert data["character_id"] == "ted-lasso"


@pytest.mark.asyncio
async def test_get_quote(client):
    """Test getting a specific quote."""
    response = await client.get("/quotes/quote-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "quote-001"
    assert "text" in data


@pytest.mark.asyncio
async def test_get_quote_not_found(client):
    """Test getting a non-existent quote."""
    response = await client.get("/quotes/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_quote(client, sample_quote):
    """Test creating a new quote."""
    response = await client.post("/quotes", json=sample_quote)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == sample_quote["text"]
    assert data["id"].startswith("quote-")


@pytest.mark.asyncio
async def test_update_quote(client):
    """Test updating a quote."""
    response = await client.patch(
        "/quotes/quote-001",
        json={"is_funny": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_funny"] is True


@pytest.mark.asyncio
async def test_get_quotes_by_theme(client):
    """Test getting quotes by theme."""
    response = await client.get("/quotes/themes/belief")
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    data = result["data"]
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_character_quotes(client):
    """Test getting all quotes by a character."""
    response = await client.get("/quotes/characters/ted-lasso")
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    data = result["data"]
    assert isinstance(data, list)
    assert all(q["character_id"] == "ted-lasso" for q in data)
