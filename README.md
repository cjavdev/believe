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

#### Live Match Simulation (`/matches/live`)

Streams a full 90-minute football match simulation with real-time events.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `home_team` | string | "AFC Richmond" | Home team name |
| `away_team` | string | "West Ham United" | Away team name |
| `speed` | float | 1.0 | Simulation speed (0.1-10.0) |
| `excitement_level` | int | 5 | How eventful the match is (1-10) |

**Server Message Types:**

| Type | Description |
|------|-------------|
| `match_start` | Sent when match begins with team info |
| `match_event` | Live events (goals, fouls, cards, etc.) |
| `match_end` | Final score, stats, and man of the match |
| `error` | Error information |
| `pong` | Response to client ping |

**Client Messages:**

Send `{"action": "ping"}` to receive a `{"type": "pong"}` response.

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/matches/live?speed=5&excitement_level=8');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case 'match_start':
      console.log(`${msg.home_team} vs ${msg.away_team}`);
      break;
    case 'match_event':
      console.log(`[${msg.event.minute}'] ${msg.event.description}`);
      break;
    case 'match_end':
      console.log(`Final: ${msg.final_score.home}-${msg.final_score.away}`);
      break;
  }
};
```

**Example (websocat):**
```bash
websocat "ws://localhost:8000/matches/live?home_team=AFC%20Richmond&away_team=Manchester%20City&speed=3"
```

#### Test Endpoint (`/ws/test`)

Simple echo endpoint for testing WebSocket connectivity.

**Server Messages:**
- `welcome` - Sent immediately on connection
- `echo` - Echoes back any message you send

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test');
ws.onopen = () => ws.send('Hello Ted!');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
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
