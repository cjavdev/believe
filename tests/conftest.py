"""Pytest configuration and fixtures for Ted Lasso API tests."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

# Set API key for testing before importing the app
os.environ["API_KEY"] = "test-api-key"

from app.main import app


@pytest.fixture
async def client():
    """Create an async test client with authentication."""
    transport = ASGITransport(app=app)
    headers = {"Authorization": "Bearer test-api-key"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


@pytest.fixture
def sample_character():
    """Sample character data for testing."""
    return {
        "name": "Test Character",
        "role": "player",
        "team_id": "afc-richmond",
        "background": "A test character created for unit testing purposes",
        "personality_traits": ["brave", "curious", "kind"],
        "emotional_stats": {
            "optimism": 80,
            "vulnerability": 70,
            "empathy": 85,
            "resilience": 75,
            "curiosity": 90,
        },
        "signature_quotes": ["Test quote one", "Test quote two"],
        "growth_arcs": [],
    }


@pytest.fixture
def sample_team():
    """Sample team data for testing."""
    return {
        "name": "Test FC",
        "nickname": "The Testers",
        "league": "Premier League",
        "stadium": "Test Stadium",
        "founded_year": 2024,
        "culture_score": 85,
        "values": {
            "primary_value": "Testing",
            "secondary_values": ["Quality", "Reliability"],
            "team_motto": "Test is life!",
        },
        "rival_teams": [],
    }


@pytest.fixture
def sample_quote():
    """Sample quote data for testing."""
    return {
        "text": "This is a test quote for testing purposes.",
        "character_id": "ted-lasso",
        "episode_id": "s01e01",
        "context": "During a test scenario",
        "theme": "belief",
        "secondary_themes": ["wisdom"],
        "moment_type": "casual",
        "is_inspirational": True,
        "is_funny": False,
    }


@pytest.fixture
def sample_believe_request():
    """Sample believe request for testing."""
    return {
        "situation": "I'm feeling nervous about my upcoming presentation at work.",
        "situation_type": "work_challenge",
        "context": "It's my first big presentation to the executives.",
        "intensity": 7,
    }


@pytest.fixture
def sample_conflict_request():
    """Sample conflict request for testing."""
    return {
        "parties_involved": ["Me", "My coworker"],
        "conflict_type": "interpersonal",
        "description": "We had a disagreement about the project direction and haven't talked since.",
        "attempts_made": ["Avoided the topic"],
    }


@pytest.fixture
def sample_reframe_request():
    """Sample reframe request for testing."""
    return {
        "negative_thought": "I'm not good enough for this job.",
        "recurring": True,
    }


@pytest.fixture
def sample_press_request():
    """Sample press conference request for testing."""
    return {
        "question": "Ted, your team just lost their fifth game in a row. How do you explain this?",
        "hostile": True,
        "topic": "match_result",
    }
