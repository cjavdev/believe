"""Tests for root endpoints."""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root welcome endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Believe" in data["message"]
    assert "endpoints" in data
    assert "ted_says" in data


@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "believe_level" in data


@pytest.mark.asyncio
async def test_404_handler(client):
    """Test custom 404 error handler."""
    response = await client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "ted_advice" in data
