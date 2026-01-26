#!/usr/bin/env python3
"""Generate OpenAPI specification from FastAPI app."""

import json
import sys
from pathlib import Path

# Add parent directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402


def generate_openapi_spec() -> dict:
    """Generate the OpenAPI specification from the FastAPI app."""
    return app.openapi()


def main():
    """Generate and output the OpenAPI specification."""
    spec = generate_openapi_spec()
    # Output with consistent formatting for diffing
    print(json.dumps(spec, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
