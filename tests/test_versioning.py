"""Tests for API versioning middleware."""

import pytest

from app.middleware.versioning import (
    DEFAULT_VERSION,
    DEPRECATED_VERSIONS,
    SUPPORTED_VERSIONS,
    _find_best_version,
    _is_valid_date,
)


class TestVersionHelpers:
    """Tests for version helper functions."""

    def test_is_valid_date_valid(self):
        """Test valid date formats."""
        assert _is_valid_date("2026-01-20") is True
        assert _is_valid_date("2025-12-31") is True
        assert _is_valid_date("2024-06-15") is True

    def test_is_valid_date_invalid_format(self):
        """Test invalid date formats."""
        assert _is_valid_date("invalid") is False
        assert _is_valid_date("2026-13-01") is False  # Invalid month
        assert _is_valid_date("2026-00-01") is False  # Invalid month
        assert _is_valid_date("2026-01-32") is False  # Invalid day
        assert _is_valid_date("2026-01-00") is False  # Invalid day

    def test_is_valid_date_out_of_range_year(self):
        """Test years outside valid range."""
        assert _is_valid_date("2019-01-01") is False  # Too old
        assert _is_valid_date("2101-01-01") is False  # Too far in future

    def test_find_best_version_exact_match(self):
        """Test finding best version with exact match."""
        result = _find_best_version("2026-01-20")
        assert result == "2026-01-20"

    def test_find_best_version_unsupported(self):
        """Test finding best version for unsupported version."""
        result = _find_best_version("2099-01-01")
        assert result is None


class TestVersionMiddlewareResponses:
    """Tests for version middleware HTTP responses."""

    @pytest.mark.asyncio
    async def test_no_version_header_uses_default(self, client):
        """Test that requests without version header use default version."""
        response = await client.get("/")
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == DEFAULT_VERSION
        assert "X-API-Supported-Versions" in response.headers

    @pytest.mark.asyncio
    async def test_x_api_version_header(self, client):
        """Test X-API-Version header is recognized."""
        response = await client.get("/", headers={"X-API-Version": "2026-01-20"})
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "2026-01-20"

    @pytest.mark.asyncio
    async def test_api_version_header_alternative(self, client):
        """Test API-Version header (alternative) is recognized."""
        response = await client.get("/", headers={"API-Version": "2026-01-20"})
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "2026-01-20"

    @pytest.mark.asyncio
    async def test_x_api_version_takes_precedence(self, client):
        """Test that X-API-Version takes precedence over API-Version."""
        response = await client.get(
            "/",
            headers={
                "X-API-Version": "2026-01-20",
                "API-Version": "2026-01-20",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "2026-01-20"

    @pytest.mark.asyncio
    async def test_invalid_version_format(self, client):
        """Test that invalid version format returns 400."""
        response = await client.get("/", headers={"X-API-Version": "invalid"})
        assert response.status_code == 400
        data = response.json()
        assert "Invalid Version Format" in data["error"]
        assert "supported_versions" in data
        assert "ted_advice" in data

    @pytest.mark.asyncio
    async def test_invalid_version_format_semantic(self, client):
        """Test that semantic version format returns 400 (we use dates)."""
        response = await client.get("/", headers={"X-API-Version": "1.0.0"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_version_format_partial_date(self, client):
        """Test that partial date format returns 400."""
        response = await client.get("/", headers={"X-API-Version": "2026-01"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_version_date_bad_month(self, client):
        """Test that invalid month in date returns 400."""
        response = await client.get("/", headers={"X-API-Version": "2026-13-01"})
        assert response.status_code == 400
        data = response.json()
        assert "Invalid Version Date" in data["error"]

    @pytest.mark.asyncio
    async def test_invalid_version_date_bad_day(self, client):
        """Test that invalid day in date returns 400."""
        response = await client.get("/", headers={"X-API-Version": "2026-01-32"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unsupported_version(self, client):
        """Test that unsupported version returns 406."""
        response = await client.get("/", headers={"X-API-Version": "2099-01-01"})
        assert response.status_code == 406
        data = response.json()
        assert "Unsupported API Version" in data["error"]
        assert "supported_versions" in data
        assert "default_version" in data
        assert "ted_advice" in data

    @pytest.mark.asyncio
    async def test_supported_versions_header_in_response(self, client):
        """Test that supported versions are included in response headers."""
        response = await client.get("/")
        assert "X-API-Supported-Versions" in response.headers
        supported = response.headers["X-API-Supported-Versions"]
        for version in SUPPORTED_VERSIONS:
            assert version in supported


class TestVersionEndpoint:
    """Tests for the /version endpoint."""

    @pytest.mark.asyncio
    async def test_version_endpoint_returns_info(self, client):
        """Test that /version endpoint returns version information."""
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "current_version" in data
        assert "default_version" in data
        assert "supported_versions" in data
        assert "versioning" in data
        assert "ted_says" in data

    @pytest.mark.asyncio
    async def test_version_endpoint_with_header(self, client):
        """Test that /version endpoint respects version header."""
        response = await client.get("/version", headers={"X-API-Version": "2026-01-20"})
        assert response.status_code == 200
        data = response.json()
        assert data["current_version"] == "2026-01-20"

    @pytest.mark.asyncio
    async def test_version_endpoint_shows_header_info(self, client):
        """Test that /version endpoint includes header usage information."""
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["versioning"]["header"] == "X-API-Version"
        assert data["versioning"]["alternative_header"] == "API-Version"
        assert "YYYY-MM-DD" in data["versioning"]["format"]


class TestRootEndpointVersionInfo:
    """Tests for version info in root endpoint."""

    @pytest.mark.asyncio
    async def test_root_includes_version_info(self, client):
        """Test that root endpoint includes version information."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "supported_versions" in data
        assert "default_version" in data

    @pytest.mark.asyncio
    async def test_root_version_reflects_header(self, client):
        """Test that root endpoint version reflects request header."""
        response = await client.get("/", headers={"X-API-Version": "2026-01-20"})
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2026-01-20"


class TestVersioningAcrossEndpoints:
    """Tests for versioning behavior across different endpoints."""

    @pytest.mark.asyncio
    async def test_versioning_on_teams_endpoint(self, client):
        """Test that versioning works on /teams endpoint."""
        response = await client.get(
            "/teams",
            headers={"X-API-Version": "2026-01-20"},
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "2026-01-20"

    @pytest.mark.asyncio
    async def test_versioning_on_health_endpoint(self, client):
        """Test that versioning works on /health endpoint."""
        response = await client.get(
            "/health",
            headers={"X-API-Version": "2026-01-20"},
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "2026-01-20"

    @pytest.mark.asyncio
    async def test_invalid_version_blocked_before_endpoint(self, client):
        """Test that invalid version is blocked before reaching endpoint."""
        response = await client.get(
            "/teams",
            headers={"X-API-Version": "invalid"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unsupported_version_blocked_before_endpoint(self, client):
        """Test that unsupported version is blocked before reaching endpoint."""
        response = await client.get(
            "/teams",
            headers={"X-API-Version": "2099-12-31"},
        )
        assert response.status_code == 406


class TestVersionConstants:
    """Tests for version constants and configuration."""

    def test_supported_versions_not_empty(self):
        """Test that there is at least one supported version."""
        assert len(SUPPORTED_VERSIONS) > 0

    def test_default_version_in_supported(self):
        """Test that default version is in supported versions."""
        assert DEFAULT_VERSION in SUPPORTED_VERSIONS

    def test_deprecated_versions_subset(self):
        """Test that deprecated versions are subset of supported."""
        for version in DEPRECATED_VERSIONS:
            assert version in SUPPORTED_VERSIONS

    def test_versions_are_date_format(self):
        """Test that all versions use YYYY-MM-DD format."""
        import re

        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for version in SUPPORTED_VERSIONS:
            assert date_pattern.match(version), (
                f"Version {version} is not in YYYY-MM-DD format"
            )
        assert date_pattern.match(DEFAULT_VERSION)
