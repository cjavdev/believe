"""Tests for the interactive endpoints."""

import pytest


@pytest.mark.asyncio
async def test_believe_engine(client, sample_believe_request):
    """Test the Believe Engine endpoint."""
    response = await client.post("/believe", json=sample_believe_request)
    assert response.status_code == 200
    data = response.json()
    assert "ted_response" in data
    assert "relevant_quote" in data
    assert "action_suggestion" in data
    assert "goldfish_wisdom" in data
    assert "believe_score" in data
    assert 0 <= data["believe_score"] <= 100


@pytest.mark.asyncio
async def test_believe_engine_easter_egg(client):
    """Test the 418 easter egg when believing too much."""
    request = {
        "situation": "I believe in believe and I believe that believing will help me believe more!",
        "situation_type": "self_doubt",
        "intensity": 5,
    }
    response = await client.post("/believe", json=request)
    assert response.status_code == 418
    data = response.json()
    assert "I'm a Believer" in data.get("status", "")


@pytest.mark.asyncio
async def test_believe_engine_too_negative(client):
    """Test the 429 error for too much negativity."""
    request = {
        "situation": "I hate everything, it's terrible and awful. The worst hopeless situation ever. I give up.",
        "situation_type": "personal_setback",
        "intensity": 10,
    }
    response = await client.post("/believe", json=request)
    assert response.status_code == 429
    data = response.json()
    assert "Too Much Negativity" in data["detail"]["error"]


@pytest.mark.asyncio
async def test_conflict_resolution(client, sample_conflict_request):
    """Test the conflict resolution endpoint."""
    response = await client.post("/conflicts/resolve", json=sample_conflict_request)
    assert response.status_code == 200
    data = response.json()
    assert "diagnosis" in data
    assert "ted_approach" in data
    assert "diamond_dogs_advice" in data
    assert "steps_to_resolution" in data
    assert "potential_outcome" in data
    assert "barbecue_sauce_wisdom" in data


@pytest.mark.asyncio
async def test_conflict_resolution_judgmental(client):
    """Test the 403 error for judgmental language."""
    request = {
        "parties_involved": ["Me", "That stupid idiot"],
        "conflict_type": "interpersonal",
        "description": "It's always their fault and they're always wrong. They're such an idiot who is stupid.",
    }
    response = await client.post("/conflicts/resolve", json=request)
    assert response.status_code == 403
    data = response.json()
    assert "Judgment Without Curiosity" in data["detail"]["error"]


@pytest.mark.asyncio
async def test_reframe_thought(client, sample_reframe_request):
    """Test the reframe endpoint."""
    response = await client.post("/reframe", json=sample_reframe_request)
    assert response.status_code == 200
    data = response.json()
    assert "original_thought" in data
    assert "reframed_thought" in data
    assert "ted_perspective" in data
    assert "daily_affirmation" in data
    # Since recurring=True, should have Dr. Sharon insight
    assert "dr_sharon_insight" in data


@pytest.mark.asyncio
async def test_reframe_thought_not_recurring(client):
    """Test reframe without recurring flag."""
    request = {
        "negative_thought": "I made a mistake today.",
        "recurring": False,
    }
    response = await client.post("/reframe", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data.get("dr_sharon_insight") is None


@pytest.mark.asyncio
async def test_press_conference(client, sample_press_request):
    """Test the press conference simulator."""
    response = await client.post("/press", json=sample_press_request)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "actual_wisdom" in data
    assert "reporter_reaction" in data
    assert "follow_up_dodge" in data


@pytest.mark.asyncio
async def test_press_conference_hostile(client):
    """Test press conference with hostile question."""
    request = {
        "question": "Ted, aren't you just a fraud who knows nothing about football?",
        "hostile": True,
    }
    response = await client.post("/press", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "deflection_humor" in data
    assert data["deflection_humor"] is not None


@pytest.mark.asyncio
async def test_get_coaching_principles(client):
    """Test getting all coaching principles."""
    response = await client.get("/coaching/principles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure
    assert "principle" in data[0]
    assert "explanation" in data[0]
    assert "ted_quote" in data[0]


@pytest.mark.asyncio
async def test_get_coaching_principle(client):
    """Test getting a specific coaching principle."""
    response = await client.get("/coaching/principles/principle-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "principle-001"
    assert "principle" in data


@pytest.mark.asyncio
async def test_get_coaching_principle_not_found(client):
    """Test getting a non-existent principle."""
    response = await client.get("/coaching/principles/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_biscuits(client):
    """Test getting all biscuits."""
    response = await client.get("/biscuits")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure
    assert "type" in data[0]
    assert "message" in data[0]
    assert "ted_note" in data[0]


@pytest.mark.asyncio
async def test_get_fresh_biscuit(client):
    """Test getting a fresh biscuit."""
    response = await client.get("/biscuits/fresh")
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "message" in data
    assert data["warmth_level"] == 10  # Fresh from the oven!


@pytest.mark.asyncio
async def test_get_specific_biscuit(client):
    """Test getting a specific biscuit."""
    response = await client.get("/biscuits/biscuit-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "biscuit-001"


@pytest.mark.asyncio
async def test_get_biscuit_not_found(client):
    """Test getting a non-existent biscuit."""
    response = await client.get("/biscuits/nonexistent")
    assert response.status_code == 404
