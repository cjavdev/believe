"""Tests for API versioning middleware."""

import pytest

from app.middleware.versioning import (
    SUPPORTED_VERSIONS,
    DEFAULT_VERSION,
    DEPRECATED_VERSIONS,
    _normalize_version,
    _is_version_compatible,
    _find_best_version,
)


class TestVersionHelpers:
    """Tests for version helper functions."""

    def test_normalize_version_with_patch(self):
        """Test normalizing a version that already has patch number."""
        assert _normalize_version("1.0.0") == "1.0.0"
        assert _normalize_version("2.1.5") == "2.1.5"

    def test_normalize_version_without_patch(self):
        """Test normalizing a version without patch number."""
        assert _normalize_version("1.0") == "1.0.0"
        assert _normalize_version("2.1") == "2.1.0"

    def test_is_version_compatible_exact_match(self):
        """Test compatibility check with exact version match."""
        assert _is_version_compatible("1.0.0", "1.0.0") is True
        assert _is_version_compatible("2.1.0", "2.1.0") is True

    def test_is_version_compatible_minor_version(self):
        """Test compatibility with different minor versions."""
        # Lower minor version should be compatible with higher
        assert _is_version_compatible("1.0.0", "1.1.0") is True
        assert _is_version_compatible("1.0.0", "1.5.0") is True
        # Higher minor version should not be compatible with lower
        assert _is_version_compatible("1.5.0", "1.0.0") is False

    def test_is_version_compatible_major_version_mismatch(self):
        """Test that different major versions are not compatible."""
        assert _is_version_compatible("2.0.0", "1.0.0") is False
        assert _is_version_compatible("1.0.0", "2.0.0") is False

    def test_find_best_version_exact_match(self):
        """Test finding best version with exact match."""
        result = _find_best_version("1.0.0")
        assert result == "1.0.0"

    def test_find_best_version_with_normalization(self):
        """Test finding best version with version normalization."""
        result = _find_best_version("1.0")
        assert result == "1.0.0"

    def test_find_best_version_unsupported(self):
        """Test finding best version for unsupported version."""
        result = _find_best_version("99.0.0")
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
        response = await client.get("/", headers={"X-API-Version": "1.0.0"})
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"

    @pytest.mark.asyncio
    async def test_api_version_header_alternative(self, client):
        """Test API-Version header (alternative) is recognized."""
        response = await client.get("/", headers={"API-Version": "1.0.0"})
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"

    @pytest.mark.asyncio
    async def test_x_api_version_takes_precedence(self, client):
        """Test that X-API-Version takes precedence over API-Version."""
        response = await client.get(
            "/",
            headers={
                "X-API-Version": "1.0.0",
                "API-Version": "1.0.0",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"

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
    async def test_invalid_version_format_partial(self, client):
        """Test that partial version format returns 400."""
        response = await client.get("/", headers={"X-API-Version": "1"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_version_format_too_many_parts(self, client):
        """Test that version with too many parts returns 400."""
        response = await client.get("/", headers={"X-API-Version": "1.0.0.0"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_version_format_letters(self, client):
        """Test that version with letters returns 400."""
        response = await client.get("/", headers={"X-API-Version": "v1.0.0"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unsupported_version(self, client):
        """Test that unsupported version returns 406."""
        response = await client.get("/", headers={"X-API-Version": "99.0.0"})
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

    @pytest.mark.asyncio
    async def test_version_short_format_accepted(self, client):
        """Test that short version format (1.0) is accepted and normalized."""
        response = await client.get("/", headers={"X-API-Version": "1.0"})
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"


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
        response = await client.get("/version", headers={"X-API-Version": "1.0.0"})
        assert response.status_code == 200
        data = response.json()
        assert data["current_version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_version_endpoint_shows_header_info(self, client):
        """Test that /version endpoint includes header usage information."""
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert data["versioning"]["header"] == "X-API-Version"
        assert data["versioning"]["alternative_header"] == "API-Version"


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
        response = await client.get("/", headers={"X-API-Version": "1.0.0"})
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"


class TestVersioningAcrossEndpoints:
    """Tests for versioning behavior across different endpoints."""

    @pytest.mark.asyncio
    async def test_versioning_on_teams_endpoint(self, client):
        """Test that versioning works on /teams endpoint."""
        response = await client.get(
            "/teams",
            headers={"X-API-Version": "1.0.0"},
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"

    @pytest.mark.asyncio
    async def test_versioning_on_health_endpoint(self, client):
        """Test that versioning works on /health endpoint."""
        response = await client.get(
            "/health",
            headers={"X-API-Version": "1.0.0"},
        )
        assert response.status_code == 200
        assert response.headers.get("X-API-Version") == "1.0.0"

    @pytest.mark.asyncio
    async def test_invalid_version_blocked_before_endpoint(self, client):
        """Test that invalid version is blocked before reaching endpoint."""
        response = await client.get(
            "/characters",
            headers={"X-API-Version": "invalid"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unsupported_version_blocked_before_endpoint(self, client):
        """Test that unsupported version is blocked before reaching endpoint."""
        response = await client.get(
            "/characters",
            headers={"X-API-Version": "99.0.0"},
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
