"""API Versioning middleware for header-based version negotiation.

Uses date-based versioning (YYYY-MM-DD format) to clearly differentiate
API versions from SDK semantic versions.

Supports version headers:
- X-API-Version (primary)
- API-Version (alternative)

Response headers:
- X-API-Version: The version used for the request
- X-API-Supported-Versions: Comma-separated list of supported versions
- X-API-Deprecated: Present if requested version is deprecated
"""

import re
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Supported API versions (newest first) - using date format YYYY-MM-DD
SUPPORTED_VERSIONS = ["2026-01-20"]
DEFAULT_VERSION = "2026-01-20"
DEPRECATED_VERSIONS: set[str] = set()  # Add deprecated versions here as needed

# Version pattern: YYYY-MM-DD date format
VERSION_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

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


def _is_valid_date(version: str) -> bool:
    """Check if the version string is a valid date.

    Args:
        version: Version string in YYYY-MM-DD format

    Returns:
        True if the date is valid
    """
    try:
        year, month, day = map(int, version.split("-"))
        # Basic validation
        if year < 2020 or year > 2100:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        return True
    except (ValueError, AttributeError):
        return False


def _find_best_version(requested: str) -> str | None:
    """Find the best matching supported version for a request.

    For date-based versioning, we use exact matching.
    The requested version must be in the supported versions list.

    Args:
        requested: The requested version string (YYYY-MM-DD)

    Returns:
        The matching supported version, or None if no match
    """
    if requested in SUPPORTED_VERSIONS:
        return requested
    return None


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Middleware for handling API version headers.

    This middleware:
    1. Reads version from X-API-Version or API-Version headers
    2. Validates the version format (YYYY-MM-DD) and availability
    3. Sets response headers with version information
    4. Returns 400 for invalid version format
    5. Returns 406 for unsupported versions
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle versioning."""
        # Extract version from headers (X-API-Version takes precedence)
        requested_version = request.headers.get("X-API-Version") or request.headers.get(
            "API-Version"
        )

        # Default to current version if no header provided
        if not requested_version:
            version_to_use = DEFAULT_VERSION
        else:
            # Validate version format (YYYY-MM-DD)
            if not VERSION_PATTERN.match(requested_version):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid Version Format",
                        "message": f"The API version '{requested_version}' is not a valid format. "
                        "Expected format: YYYY-MM-DD (e.g., 2026-01-20)",
                        "ted_advice": "Sometimes we gotta follow the rules, friend. "
                        "But once you know 'em, you can really start to play!",
                        "supported_versions": SUPPORTED_VERSIONS,
                    },
                )

            # Validate it's a reasonable date
            if not _is_valid_date(requested_version):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid Version Date",
                        "message": f"The API version '{requested_version}' is not a valid date.",
                        "ted_advice": "Dates are like memories - they gotta make sense!",
                        "supported_versions": SUPPORTED_VERSIONS,
                    },
                )

            # Find matching version
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
