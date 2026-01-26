"""API Key Authentication for Ted Lasso API.

Implements Bearer token authentication using API keys.
"""

import os

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# API key from environment variable
API_KEY = os.environ.get("API_KEY")

# Security scheme for Bearer token
security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Verify the API key from the Authorization header.

    Args:
        credentials: The Bearer token credentials from the Authorization header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or not configured.
    """
    if API_KEY is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Server Configuration Error",
                "message": "API key not configured on server. "
                "Even Ted needs his playbook set up right!",
            },
        )

    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "message": "Invalid API key. "
                "As Ted would say, 'Be curious, not judgmental' - "
                "but we do need the right key!",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
