# Claude Code Instructions

Project-specific instructions for Claude Code when working on this repository.

## Package Management

**Always use `uv` instead of `pip` for package management.**

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Install a new package
uv pip install <package>

# Run Python with the venv
uv run python <script.py>

# Or use the venv directly
.venv/bin/python <script.py>
```

## Common Commands

```bash
# Run the API server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest -v

# Run linting
uv run ruff check .
uv run ruff format .

# Regenerate OpenAPI spec (required after API changes)
uv run python scripts/generate_openapi.py > openapi.json

# Check if OpenAPI spec is up to date
./scripts/check_openapi.sh
```

## Project Structure

- `app/` - FastAPI application code
  - `models/` - Pydantic models
  - `routers/` - API route handlers
  - `services/` - Business logic
  - `data/` - Seed data
- `tests/` - Test suite (pytest)
- `scripts/` - Utility scripts
- `openapi.json` - Generated OpenAPI specification (must be kept in sync)

## Important Notes

- This API uses **in-memory storage** - no database. Data resets on server restart.
- After modifying routes or models, always regenerate `openapi.json`
- The pre-commit hook will fail if the OpenAPI spec is out of date
