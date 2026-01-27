#!/usr/bin/env python3
"""Generate OpenAPI specification from FastAPI app."""

import json
import sys
from pathlib import Path

# Add parent directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402

# SSE streaming schemas to add to components/schemas
SSE_SCHEMAS = {
    "PepTalkChunk": {
        "type": "object",
        "description": "A chunk of a streaming pep talk from Ted.",
        "properties": {
            "chunk_id": {
                "type": "integer",
                "description": "Chunk sequence number",
            },
            "text": {
                "type": "string",
                "description": "The text of this chunk",
            },
            "is_final": {
                "type": "boolean",
                "description": "Is this the final chunk",
                "default": False,
            },
            "emotional_beat": {
                "type": "string",
                "nullable": True,
                "description": "The emotional purpose of this chunk (e.g., greeting, acknowledgment, wisdom, affirmation, encouragement)",
            },
        },
        "required": ["chunk_id", "text", "is_final"],
    },
    "MatchCommentaryEvent": {
        "type": "object",
        "description": "A single commentary event during a match stream.",
        "properties": {
            "event_id": {
                "type": "integer",
                "description": "Event sequence number",
            },
            "minute": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120,
                "description": "Match minute",
            },
            "event_type": {
                "type": "string",
                "enum": [
                    "kickoff",
                    "goal",
                    "near_miss",
                    "save",
                    "foul",
                    "substitution",
                    "halftime",
                    "ted_reaction",
                    "crowd_moment",
                    "final_whistle",
                ],
                "description": "Type of event",
            },
            "description": {
                "type": "string",
                "description": "What happened",
            },
            "commentary": {
                "type": "string",
                "description": "Commentator's call",
            },
            "ted_sideline_reaction": {
                "type": "string",
                "nullable": True,
                "description": "Ted's reaction on the sideline",
            },
            "crowd_reaction": {
                "type": "string",
                "nullable": True,
                "description": "How the crowd reacted",
            },
            "is_final": {
                "type": "boolean",
                "description": "Is this the final event",
                "default": False,
            },
        },
        "required": [
            "event_id",
            "minute",
            "event_type",
            "description",
            "commentary",
            "is_final",
        ],
    },
    "TestStreamChunk": {
        "type": "object",
        "description": "A test stream chunk for SSE connectivity testing.",
        "properties": {
            "sequence": {
                "type": "integer",
                "description": "The sequence number of this chunk (1-5)",
            },
            "message": {
                "type": "string",
                "description": "The message content for this chunk",
            },
        },
        "required": ["sequence", "message"],
    },
}

# Mapping of endpoint paths to their SSE schema refs
SSE_ENDPOINT_SCHEMAS = {
    "/pep-talk": "PepTalkChunk",
    "/matches/{match_id}/commentary/stream": "MatchCommentaryEvent",
    "/stream/test": "TestStreamChunk",
}


def generate_openapi_spec() -> dict:
    """Generate the OpenAPI specification from the FastAPI app."""
    spec = app.openapi()

    # Add SSE schemas to components/schemas
    if "components" not in spec:
        spec["components"] = {}
    if "schemas" not in spec["components"]:
        spec["components"]["schemas"] = {}

    spec["components"]["schemas"].update(SSE_SCHEMAS)

    # Update SSE endpoints to use $ref instead of inline schemas
    for path, schema_name in SSE_ENDPOINT_SCHEMAS.items():
        if path in spec.get("paths", {}):
            path_item = spec["paths"][path]
            # Check both GET and POST methods
            for method in ["get", "post"]:
                if method in path_item:
                    responses = path_item[method].get("responses", {})
                    if "200" in responses:
                        content = responses["200"].get("content", {})
                        if "text/event-stream" in content:
                            # Replace inline schema with $ref
                            content["text/event-stream"]["schema"] = {
                                "$ref": f"#/components/schemas/{schema_name}"
                            }

    return spec


def main():
    """Generate and output the OpenAPI specification."""
    spec = generate_openapi_spec()
    # Output with consistent formatting for diffing
    print(json.dumps(spec, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
