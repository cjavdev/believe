"""API Versioning middleware for header-based version negotiation.

Supports version headers:
- X-API-Version (primary)
- API-Version (alternative)

Response headers:
- X-API-Version: The version used for the request
- X-API-Supported-Versions: Comma-separated list of supported versions
- X-API-Deprecated: Present if requested version is deprecated
"""

import re
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Supported API versions (newest first)
SUPPORTED_VERSIONS = ["1.0.0"]
DEFAULT_VERSION = "1.0.0"
DEPRECATED_VERSIONS: set[str] = set()  # Add deprecated versions here as needed

# Version pattern: major.minor.patch or major.minor
VERSION_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?$")

# Request context for storing version info
_request_version: dict[int, str] = {}


def get_api_version(request: Request) -> str:
    """Get the API version for the current request.

    This can be used in route handlers to implement version-specific logic.

    Args:
        request: The FastAPI request object

    Returns:
        The API version string being used for this request
    """
    return _request_version.get(id(request), DEFAULT_VERSION)


def _normalize_version(version: str) -> str:
    """Normalize version string to major.minor.patch format.

    Args:
        version: Version string (e.g., "1.0" or "1.0.0")

    Returns:
        Normalized version string (e.g., "1.0.0")
    """
    parts = version.split(".")
    if len(parts) == 2:
        return f"{version}.0"
    return version


def _is_version_compatible(requested: str, supported: str) -> bool:
    """Check if a requested version is compatible with a supported version.

    Uses semantic versioning compatibility:
    - Exact match is always compatible
    - Major version must match
    - Requested minor version must be <= supported minor version

    Args:
        requested: The requested version
        supported: A supported version to check against

    Returns:
        True if the versions are compatible
    """
    req_parts = [int(x) for x in requested.split(".")]
    sup_parts = [int(x) for x in supported.split(".")]

    # Major version must match exactly
    if req_parts[0] != sup_parts[0]:
        return False

    # For exact version requests, check exact match or compatible
    if req_parts[1] <= sup_parts[1]:
        return True

    return False


def _find_best_version(requested: str) -> str | None:
    """Find the best matching supported version for a request.

    Args:
        requested: The requested version string

    Returns:
        The best matching supported version, or None if no match
    """
    normalized = _normalize_version(requested)

    # First try exact match
    if normalized in SUPPORTED_VERSIONS:
        return normalized

    # Then try compatibility matching
    for supported in SUPPORTED_VERSIONS:
        if _is_version_compatible(normalized, supported):
            return supported

    return None


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Middleware for handling API version headers.

    This middleware:
    1. Reads version from X-API-Version or API-Version headers
    2. Validates the version format and availability
    3. Sets response headers with version information
    4. Returns 400 for invalid version format
    5. Returns 406 for unsupported versions
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process the request and handle versioning."""
        # Extract version from headers (X-API-Version takes precedence)
        requested_version = (
            request.headers.get("X-API-Version")
            or request.headers.get("API-Version")
        )

        # Default to current version if no header provided
        if not requested_version:
            version_to_use = DEFAULT_VERSION
        else:
            # Validate version format
            if not VERSION_PATTERN.match(requested_version):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid Version Format",
                        "message": f"The API version '{requested_version}' is not a valid format. "
                        "Expected format: major.minor.patch (e.g., 1.0.0) or major.minor (e.g., 1.0)",
                        "ted_advice": "Sometimes we gotta follow the rules, friend. "
                        "But once you know 'em, you can really start to play!",
                        "supported_versions": SUPPORTED_VERSIONS,
                    },
                )

            # Find compatible version
            version_to_use = _find_best_version(requested_version)

            if not version_to_use:
                return JSONResponse(
                    status_code=406,
                    content={
                        "error": "Unsupported API Version",
                        "message": f"The API version '{requested_version}' is not supported.",
                        "ted_advice": "We can't go backwards, only forwards. "
                        "But don't worry, our supported versions are pretty great!",
                        "supported_versions": SUPPORTED_VERSIONS,
                        "default_version": DEFAULT_VERSION,
                    },
                )

        # Store version in request context for route handlers
        _request_version[id(request)] = version_to_use

        try:
            # Process the request
            response = await call_next(request)

            # Add version headers to response
            response.headers["X-API-Version"] = version_to_use
            response.headers["X-API-Supported-Versions"] = ", ".join(SUPPORTED_VERSIONS)

            # Add deprecation warning if applicable
            if version_to_use in DEPRECATED_VERSIONS:
                response.headers["X-API-Deprecated"] = "true"
                response.headers["X-API-Deprecation-Notice"] = (
                    f"API version {version_to_use} is deprecated. "
                    f"Please upgrade to {DEFAULT_VERSION}."
                )

            return response
        finally:
            # Clean up request context
            _request_version.pop(id(request), None)
