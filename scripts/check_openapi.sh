#!/bin/bash
# Check if the OpenAPI spec is up to date
# This script can be used as a pre-commit hook

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Generate the spec to a temp file
TEMP_SPEC=$(mktemp)
trap "rm -f $TEMP_SPEC" EXIT

# Try to find Python - prefer venv if it exists
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python"
fi

$PYTHON scripts/generate_openapi.py > "$TEMP_SPEC"

# Compare with committed spec
if ! diff -q openapi.json "$TEMP_SPEC" > /dev/null 2>&1; then
    echo "ERROR: OpenAPI spec is out of date!"
    echo ""
    echo "The committed openapi.json does not match the generated spec."
    echo "Please run the following command and commit the changes:"
    echo ""
    echo "  python scripts/generate_openapi.py > openapi.json"
    echo ""
    exit 1
fi

echo "OpenAPI spec is up to date."
