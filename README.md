# Ted Lasso API

A comprehensive API celebrating the wisdom, humor, and heart of Ted Lasso. Perfect for SDK demos showcasing various REST API features.

## Features

- Full CRUD operations for Characters, Teams, Matches, Episodes, and Quotes
- Interactive endpoints: Believe Engine, Conflict Resolution, and more
- SSE streaming for real-time pep talks and match commentary
- OpenAPI documentation with Swagger UI and ReDoc

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone git@github.com:cjavdev/believe.git
cd believe
uv pip install -e ".[dev]"
```

### Run the Server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Important: In-Memory Storage

This API uses in-memory storage only — no database. Data resets on server restart. This design keeps the API simple and dependency-free for demo purposes.

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Regenerate OpenAPI spec (required after API changes)
uv run python scripts/generate_openapi.py > openapi.json
```

## License

MIT License

---

*"Be curious, not judgmental."* - Ted Lasso
