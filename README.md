# Ted Lasso API

A comprehensive API celebrating the wisdom, humor, and heart of Ted Lasso. Perfect for SDK demos showcasing various REST API features.

## Features

- Full CRUD operations for Characters, Teams, Matches, Episodes, and Quotes
- Interactive endpoints: Believe Engine, Conflict Resolution, and more
- SSE streaming for real-time pep talks and match commentary
- WebSocket support for interactive match simulations
- OpenAPI documentation with Swagger UI and ReDoc

## Streaming Endpoints

This API offers two streaming approaches: **SSE (Server-Sent Events)** and **WebSockets**.

### SSE Endpoints

Server-Sent Events provide unidirectional streaming from server to client over HTTP.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pep-talk` | GET | Returns full pep talk (add `?stream=true` for SSE) |
| `/matches/{match_id}/commentary/stream` | POST | Streams live match commentary events |
| `/stream/test` | GET | Test endpoint that streams 5 messages |

**Example (curl):**
```bash
# Full response
curl -H "X-API-Key: your-key" http://localhost:8000/pep-talk

# Streaming
curl -N -H "X-API-Key: your-key" http://localhost:8000/pep-talk?stream=true
```

### WebSocket Endpoints

WebSockets provide bidirectional communication over a persistent connection.

| Endpoint | Description |
|----------|-------------|
| `/matches/live` | Full interactive match simulation with real-time events |
| `/ws/test` | Echo test endpoint for connectivity testing |

**Example (websocat):**
```bash
websocat "ws://localhost:8000/matches/live?home_team=AFC%20Richmond&away_team=Manchester%20City"
```

### SSE vs WebSocket: When to Use Which

| Aspect | SSE | WebSocket |
|--------|-----|-----------|
| **Direction** | Server → Client only | Bidirectional |
| **Protocol** | HTTP (`text/event-stream`) | `ws://` or `wss://` |
| **Client input** | Cannot send data mid-stream | Can send messages anytime |
| **Reconnection** | Built-in browser auto-reconnect | Must implement manually |
| **Best for** | Simple streaming (commentary, feeds) | Interactive features (live controls) |

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
