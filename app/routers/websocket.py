"""WebSocket router for Ted Lasso API - Live Match Simulation."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import ValidationError

from app.models.websocket import (
    MatchConfig,
    MatchStartMessage,
    MatchEventMessage,
    MatchEndMessage,
    ErrorMessage,
)
from app.services.match_simulation import MatchSimulationService

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_json(self, client_id: str, data: dict):
        """Send JSON data to a specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(data)


manager = ConnectionManager()


@router.websocket("/matches/live")
async def live_match_simulation(
    websocket: WebSocket,
    home_team: str = Query(default="AFC Richmond", description="Home team name"),
    away_team: str = Query(default="West Ham United", description="Away team name"),
    speed: float = Query(default=1.0, ge=0.1, le=10.0, description="Simulation speed"),
    excitement_level: int = Query(default=5, ge=1, le=10, description="Match excitement"),
):
    """
    WebSocket endpoint for live match simulation.

    Connect to this endpoint to receive real-time match events as they happen
    in a simulated football match.

    ## Connection

    Connect via WebSocket to `/matches/live` with optional query parameters:
    - `home_team`: Home team name (default: "AFC Richmond")
    - `away_team`: Away team name (default: "West Ham United")
    - `speed`: Simulation speed multiplier, 1.0 = normal pace (default: 1.0)
    - `excitement_level`: How eventful the match is, 1-10 (default: 5)

    ## Example WebSocket URL

    ```
    ws://localhost:8000/matches/live?home_team=AFC%20Richmond&away_team=Manchester%20City&speed=2.0&excitement_level=7
    ```

    ## Messages

    The server will send JSON messages with the following types:

    ### match_start
    Sent when the match begins:
    ```json
    {
        "type": "match_start",
        "match_id": "abc123",
        "home_team": "AFC Richmond",
        "away_team": "West Ham United",
        "message": "Welcome to Nelson Road!"
    }
    ```

    ### match_event
    Sent for each match event:
    ```json
    {
        "type": "match_event",
        "event": {
            "event_id": 1,
            "event_type": "goal",
            "minute": 23,
            "team": "home",
            "player": {"name": "Jamie Tartt", "number": 9, "position": "Forward"},
            "description": "GOAL! Jamie Tartt scores!",
            "score": {"home": 1, "away": 0},
            "stats": {...},
            "ted_reaction": "Football is life!",
            "crowd_reaction": "The crowd goes wild!",
            "commentary": "What a strike!"
        }
    }
    ```

    ### match_end
    Sent when the match concludes:
    ```json
    {
        "type": "match_end",
        "match_id": "abc123",
        "final_score": {"home": 2, "away": 1},
        "final_stats": {...},
        "man_of_the_match": "Jamie Tartt",
        "ted_post_match": "Win or lose, I'm proud of every single one of you!"
    }
    ```

    ## Client Messages

    You can send JSON messages to control the simulation:
    - `{"action": "ping"}` - Server responds with `{"type": "pong"}`

    ## Event Types

    - `match_start` - Match kicks off
    - `goal` - A goal is scored
    - `possession_change` - Ball changes possession
    - `foul` - Foul committed
    - `yellow_card` - Yellow card shown
    - `red_card` - Red card shown
    - `penalty_awarded` - Penalty kick awarded
    - `penalty_scored` - Penalty converted
    - `penalty_missed` - Penalty missed/saved
    - `substitution` - Player substituted
    - `injury` - Player injured
    - `offside` - Offside called
    - `corner` - Corner kick
    - `free_kick` - Free kick awarded
    - `shot_on_target` - Shot on target
    - `shot_off_target` - Shot off target
    - `save` - Goalkeeper save
    - `halftime` - End of first half
    - `second_half_start` - Second half begins
    - `added_time` - Injury time announced
    - `match_end` - Full time whistle
    """
    # Generate a unique client ID
    import uuid
    client_id = str(uuid.uuid4())[:8]

    try:
        # Accept the connection
        await manager.connect(websocket, client_id)

        # Create match configuration from query parameters
        config = MatchConfig(
            home_team=home_team,
            away_team=away_team,
            speed=speed,
            excitement_level=excitement_level,
        )

        # Initialize the match simulation
        simulation = MatchSimulationService(config)

        # Send match start message
        start_message = MatchStartMessage(
            match_id=simulation.match_id,
            home_team=config.home_team,
            away_team=config.away_team,
            message=f"Welcome to Nelson Road! {config.home_team} vs {config.away_team} is about to begin. BELIEVE!",
        )
        await websocket.send_json(start_message.model_dump())

        # Stream match events
        final_event = None
        async for event in simulation.simulate_match():
            event_message = MatchEventMessage(event=event)
            await websocket.send_json(event_message.model_dump())
            final_event = event

            # Check for any client messages (non-blocking)
            try:
                # Use receive with a very short timeout to check for messages
                import asyncio
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=0.01
                    )
                    # Handle client commands
                    try:
                        message = json.loads(data)
                        if message.get("action") == "ping":
                            await websocket.send_json({"type": "pong"})
                    except json.JSONDecodeError:
                        pass
                except asyncio.TimeoutError:
                    pass
            except Exception:
                pass

        # Send match end message
        if final_event:
            end_message = MatchEndMessage(
                match_id=simulation.match_id,
                final_score=simulation.score,
                final_stats=simulation.stats,
                man_of_the_match=simulation._get_player(
                    "home" if simulation.score.home >= simulation.score.away else "away"
                ).name,
                ted_post_match="Win, lose, or draw - I'm proud of every single one of you. "
                "Now who wants to grab some barbecue?",
            )
            await websocket.send_json(end_message.model_dump())

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except ValidationError as e:
        error_message = ErrorMessage(
            code="validation_error",
            message=f"Invalid configuration: {str(e)}",
        )
        await websocket.send_json(error_message.model_dump())
        await websocket.close()
    except Exception as e:
        try:
            error_message = ErrorMessage(
                code="internal_error",
                message=f"An error occurred: {str(e)}",
            )
            await websocket.send_json(error_message.model_dump())
            await websocket.close()
        except Exception:
            pass
    finally:
        manager.disconnect(client_id)


@router.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """
    Simple WebSocket test endpoint.

    Connect to test WebSocket connectivity. Echoes back any message you send.

    ## Example

    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/test');
    ws.onmessage = (event) => console.log(event.data);
    ws.send('Hello!');  // Server responds: {"type": "echo", "message": "Hello!"}
    ```
    """
    await websocket.accept()

    # Send welcome message
    await websocket.send_json({
        "type": "welcome",
        "message": "Welcome to the Ted Lasso API WebSocket test! Send any message and I'll echo it back.",
        "ted_says": "Hey there, friend! This WebSocket connection is working smoother than a fresh jar of peanut butter!",
    })

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo",
                "message": data,
                "ted_says": "I heard you loud and clear, partner!",
            })
    except WebSocketDisconnect:
        pass
