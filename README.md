# Ted Lasso API

A comprehensive API celebrating the wisdom, humor, and heart of Ted Lasso. Perfect for SDK demos showcasing various REST API features.

## Features

- **Full CRUD Operations**: Create, Read, Update, Delete for all resources
- **Rich Data Models**: Characters, Teams, Matches, Episodes, and Quotes
- **Interactive Endpoints**: Believe Engine, Conflict Resolution, and more
- **SSE Streaming**: Real-time pep talks and match commentary
- **Custom Easter Eggs**: Special HTTP status codes for fun
- **OpenAPI Documentation**: Full Swagger/ReDoc support

## Important: In-Memory Data Storage

This API uses **in-memory storage only** — there is no database. This has important implications:

- **Data is ephemeral**: All data created via POST, PATCH, or DELETE operations is stored in Python dictionaries and will be **lost when the server restarts**
- **Seed data reloads on startup**: Each time the server starts, it loads fresh seed data from `app/data/seed_data.py`
- **No persistence**: Changes you make during a session do not persist across restarts
- **Designed for demos**: This API is intended for SDK demonstrations and testing, not production use cases requiring persistent data

This design keeps the API simple and dependency-free, making it easy to run anywhere without database setup.

## Installation

### Prerequisites

- Python 3.10+
- pip or uv

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ted-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Core Resources (CRUD)

#### Characters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/characters` | List all characters |
| GET | `/characters/{id}` | Get a character |
| POST | `/characters` | Create a character |
| PATCH | `/characters/{id}` | Update a character |
| DELETE | `/characters/{id}` | Delete a character |
| GET | `/characters/{id}/quotes` | Get character's quotes |

#### Teams
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | List all teams |
| GET | `/teams/{id}` | Get a team |
| POST | `/teams` | Create a team |
| PATCH | `/teams/{id}` | Update a team |
| DELETE | `/teams/{id}` | Delete a team |
| GET | `/teams/{id}/rivals` | Get team rivals |
| GET | `/teams/{id}/culture` | Get team culture details |

#### Matches
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/matches` | List all matches |
| GET | `/matches/{id}` | Get a match |
| POST | `/matches` | Create a match |
| PATCH | `/matches/{id}` | Update a match |
| DELETE | `/matches/{id}` | Delete a match |
| GET | `/matches/{id}/turning-points` | Get match turning points |
| GET | `/matches/{id}/lesson` | Get match lesson |

#### Episodes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/episodes` | List all episodes |
| GET | `/episodes/{id}` | Get an episode |
| POST | `/episodes` | Create an episode |
| PATCH | `/episodes/{id}` | Update an episode |
| DELETE | `/episodes/{id}` | Delete an episode |
| GET | `/episodes/{id}/wisdom` | Get episode wisdom |
| GET | `/episodes/seasons/{number}` | Get season episodes |

#### Quotes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quotes` | List all quotes |
| GET | `/quotes/random` | Get a random quote |
| GET | `/quotes/{id}` | Get a quote |
| POST | `/quotes` | Create a quote |
| PATCH | `/quotes/{id}` | Update a quote |
| DELETE | `/quotes/{id}` | Delete a quote |
| GET | `/quotes/themes/{theme}` | Get quotes by theme |
| GET | `/quotes/characters/{id}` | Get character quotes |

### Interactive Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/believe` | The Believe Engine - motivational guidance |
| POST | `/conflicts/resolve` | Conflict resolution advice |
| POST | `/reframe` | Reframe negative thoughts |
| POST | `/press` | Press conference simulator |
| GET | `/coaching/principles` | Get coaching principles |
| GET | `/coaching/principles/{id}` | Get specific principle |
| GET | `/biscuits` | Biscuits as a Service |
| GET | `/biscuits/fresh` | Get a fresh biscuit |

### SSE Streaming Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/pep-talk/stream` | Stream a motivational pep talk |
| POST | `/matches/{id}/commentary/stream` | Stream live match commentary |
| GET | `/stream/test` | Test SSE connection |

## Example Requests

### Get Ted Lasso's Character

```bash
curl http://localhost:8000/characters/ted-lasso
```

Response:
```json
{
  "id": "ted-lasso",
  "name": "Ted Lasso",
  "role": "coach",
  "team_id": "afc-richmond",
  "background": "Former American football coach from Kansas...",
  "personality_traits": ["optimistic", "kind", "folksy"],
  "emotional_stats": {
    "optimism": 95,
    "vulnerability": 80,
    "empathy": 100,
    "resilience": 90,
    "curiosity": 99
  },
  "signature_quotes": [
    "I believe in believe.",
    "Be curious, not judgmental."
  ]
}
```

### Use the Believe Engine

```bash
curl -X POST http://localhost:8000/believe \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "I am nervous about my upcoming presentation",
    "situation_type": "work_challenge",
    "intensity": 7
  }'
```

Response:
```json
{
  "ted_response": "Taking on a challenge is a lot like riding a horse...",
  "relevant_quote": "I believe in believe.",
  "action_suggestion": "Take one small step today. Just one.",
  "goldfish_wisdom": "Be a goldfish. 10-second memory for the bad stuff.",
  "believe_score": 84
}
```

### Get a Random Quote

```bash
curl http://localhost:8000/quotes/random?character_id=ted-lasso&theme=belief
```

### Stream a Pep Talk (SSE)

```bash
curl -N http://localhost:8000/pep-talk/stream
```

### Get Fresh Biscuits

```bash
curl http://localhost:8000/biscuits/fresh
```

## Easter Eggs

The API includes some fun custom HTTP status codes:

- **418 "I'm a Believer!"** - When you believe too much in `/believe`
- **429 "Too Much Negativity"** - When your request is too negative
- **403 "Judgment Without Curiosity"** - When you're too judgmental

## Running Tests

Install test dependencies:
```bash
pip install -e ".[dev]"
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app
```

Run specific test file:
```bash
pytest tests/test_characters.py
```

Run tests verbosely:
```bash
pytest -v
```

## OpenAPI Specification

The API's OpenAPI specification is stored in `openapi.json` at the repository root. This file is used for SDK generation and must be kept in sync with the API.

### Regenerating the OpenAPI Spec

After making changes to the API (routes, models, etc.), regenerate the spec:

```bash
python scripts/generate_openapi.py > openapi.json
```

### Checking if the Spec is Up to Date

To verify the spec matches the current API:

```bash
./scripts/check_openapi.sh
```

### Pre-commit Hook Setup

To automatically check the OpenAPI spec before each commit, set up a git pre-commit hook:

```bash
# Create the hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/check_openapi.sh
EOF

# Make it executable
chmod +x .git/hooks/pre-commit
```

Now git will prevent commits if the OpenAPI spec is out of date.

## Linting

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Check formatting
ruff format --check .

# Apply formatting
ruff format .
```

## Project Structure

```
ted-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── characters.py
│   │   ├── teams.py
│   │   ├── matches.py
│   │   ├── episodes.py
│   │   ├── quotes.py
│   │   └── interactive.py
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── characters.py
│   │   ├── teams.py
│   │   ├── matches.py
│   │   ├── episodes.py
│   │   ├── quotes.py
│   │   ├── interactive.py
│   │   └── streaming.py
│   ├── data/                # Seed data
│   │   ├── __init__.py
│   │   └── seed_data.py
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── believe_engine.py
│       ├── conflict_resolver.py
│       ├── reframe_service.py
│       ├── press_conference.py
│       └── streaming.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_characters.py
│   ├── test_teams.py
│   ├── test_matches.py
│   ├── test_episodes.py
│   ├── test_quotes.py
│   ├── test_interactive.py
│   ├── test_streaming.py
│   └── test_root.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Characters Included

- **Ted Lasso** - The eternally optimistic coach
- **Coach Beard** - Ted's loyal and mysterious assistant
- **Roy Kent** - The legendary midfielder turned coach
- **Rebecca Welton** - AFC Richmond's owner
- **Jamie Tartt** - The talented but troubled striker
- **Keeley Jones** - Marketing genius and emotional backbone
- **Nate Shelley** - From kit man to coach
- **Sam Obisanya** - The principled Nigerian winger
- **Higgins** - Director of Football Operations
- **Trent Crimm** - The Independent journalist
- **Dr. Sharon Fieldstone** - Sports psychologist

## Teams Included

- AFC Richmond (The Greyhounds)
- Manchester City
- West Ham United
- Tottenham Hotspur

## Quote Themes

- belief, teamwork, curiosity, kindness
- resilience, vulnerability, growth, humor
- wisdom, leadership, love, forgiveness

## License

MIT License

---

*"Be curious, not judgmental."* - Ted Lasso
