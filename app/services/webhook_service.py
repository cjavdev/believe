"""Webhook service for registration and event delivery."""

import base64
import hashlib
import hmac
import secrets
import time
import uuid
from datetime import datetime, timezone

import httpx

from app.models.webhooks import (
    ALL_EVENT_TYPES,
    EventType,
    MatchCompletedData,
    MatchCompletedPayload,
    RegisteredWebhook,
    TeamMemberTransferredData,
    TeamMemberTransferredPayload,
    WebhookDeliveryResult,
    WebhookEventPayload,
)

# In-memory storage for registered webhooks
_webhooks: dict[str, RegisteredWebhook] = {}


def generate_webhook_id() -> str:
    """Generate a unique webhook ID."""
    return f"wh_{secrets.token_hex(12)}"


def generate_webhook_secret() -> str:
    """Generate a webhook secret key (base64 encoded with whsec_ prefix)."""
    secret_bytes = secrets.token_bytes(32)
    return f"whsec_{base64.b64encode(secret_bytes).decode()}"


def register_webhook(
    url: str,
    event_types: list[EventType] | None = None,
    description: str | None = None,
) -> RegisteredWebhook:
    """Register a new webhook endpoint."""
    webhook_id = generate_webhook_id()
    secret = generate_webhook_secret()

    # Default to all event types if none specified
    if event_types is None:
        event_types = list(ALL_EVENT_TYPES)

    webhook = RegisteredWebhook(
        id=webhook_id,
        url=url,
        event_types=event_types,
        description=description,
        created_at=datetime.now(timezone.utc),
        secret=secret,
    )

    _webhooks[webhook_id] = webhook
    return webhook


def get_webhook(webhook_id: str) -> RegisteredWebhook | None:
    """Get a webhook by ID."""
    return _webhooks.get(webhook_id)


def list_webhooks() -> list[RegisteredWebhook]:
    """List all registered webhooks."""
    return list(_webhooks.values())


def delete_webhook(webhook_id: str) -> bool:
    """Delete a webhook by ID. Returns True if deleted, False if not found."""
    if webhook_id in _webhooks:
        del _webhooks[webhook_id]
        return True
    return False


def get_webhooks_for_event(event_type: EventType) -> list[RegisteredWebhook]:
    """Get all webhooks subscribed to a specific event type."""
    return [wh for wh in _webhooks.values() if event_type in wh.event_types]


def compute_signature(payload: str, secret: str, timestamp: int) -> str:
    """
    Compute webhook signature using Standard Webhooks specification.

    The signature is computed as HMAC-SHA256 of "{webhook_id}.{timestamp}.{payload}"
    """
    # Remove whsec_ prefix if present
    if secret.startswith("whsec_"):
        secret = secret[6:]

    # Decode the base64 secret
    secret_bytes = base64.b64decode(secret)

    # Create the signed payload: timestamp.payload
    signed_payload = f"{timestamp}.{payload}"

    # Compute HMAC-SHA256
    signature = hmac.new(
        secret_bytes,
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    # Return base64 encoded signature with v1 prefix
    return f"v1,{base64.b64encode(signature).decode()}"


def generate_sample_payload(event_type: EventType) -> WebhookEventPayload:
    """Generate a sample payload for testing."""
    if event_type == "match.completed":
        return MatchCompletedPayload(
            event_type="match.completed",
            data=MatchCompletedData(
                match_id=f"match-{secrets.token_hex(4)}",
                home_team_id="afc-richmond",
                away_team_id="west-ham-united",
                home_score=2,
                away_score=1,
                result="home_win",
                match_type="league",
                completed_at=datetime.now(timezone.utc),
                man_of_the_match="Jamie Tartt",
                lesson_learned="Every game is a chance to believe in something bigger than yourself.",
                ted_post_match_quote="You know what the happiest animal on Earth is? It's a goldfish. Y'know why? Got a 10-second memory.",
            ),
        )
    else:  # team_member.transferred
        return TeamMemberTransferredPayload(
            event_type="team_member.transferred",
            data=TeamMemberTransferredData(
                team_member_id=f"tm-{secrets.token_hex(4)}",
                character_id="dani-rojas",
                character_name="Dani Rojas",
                member_type="player",
                transfer_type="joined",
                team_id="afc-richmond",
                team_name="AFC Richmond",
                previous_team_id="guadalajara-fc",
                previous_team_name="Guadalajara FC",
                years_with_previous_team=3,
                transfer_fee_gbp="8000000.00",
                ted_reaction="Football is life! And so is welcoming new friends to the family!",
            ),
        )


async def deliver_webhook(
    webhook: RegisteredWebhook,
    event_id: str,
    event_type: EventType,
    payload: WebhookEventPayload,
) -> WebhookDeliveryResult:
    """
    Deliver a webhook event to a single endpoint.

    Uses Standard Webhooks specification for signatures:
    - webhook-id: Unique message ID
    - webhook-timestamp: Unix timestamp
    - webhook-signature: HMAC-SHA256 signature
    """
    # Build the full event payload
    timestamp = int(time.time())
    full_payload = {
        "event_type": event_type,
        "event_id": event_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data": payload.data.model_dump(mode="json"),
    }

    import json

    payload_str = json.dumps(full_payload, separators=(",", ":"), sort_keys=True)

    # Compute signature
    signature = compute_signature(payload_str, webhook.secret, timestamp)

    # Prepare headers per Standard Webhooks spec
    headers = {
        "Content-Type": "application/json",
        "webhook-id": event_id,
        "webhook-timestamp": str(timestamp),
        "webhook-signature": signature,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                str(webhook.url),
                content=payload_str,
                headers=headers,
            )

        return WebhookDeliveryResult(
            webhook_id=webhook.id,
            url=str(webhook.url),
            success=200 <= response.status_code < 300,
            status_code=response.status_code,
            error=None if response.status_code < 400 else response.text[:200],
        )
    except httpx.TimeoutException:
        return WebhookDeliveryResult(
            webhook_id=webhook.id,
            url=str(webhook.url),
            success=False,
            status_code=None,
            error="Request timed out",
        )
    except httpx.RequestError as e:
        return WebhookDeliveryResult(
            webhook_id=webhook.id,
            url=str(webhook.url),
            success=False,
            status_code=None,
            error=str(e)[:200],
        )


async def trigger_event(
    event_type: EventType,
    payload: WebhookEventPayload | None = None,
) -> tuple[str, list[WebhookDeliveryResult]]:
    """
    Trigger a webhook event and deliver to all subscribed endpoints.

    Returns the event ID and list of delivery results.
    """
    event_id = f"evt_{uuid.uuid4().hex[:24]}"

    # Use provided payload or generate a sample one
    if payload is None:
        payload = generate_sample_payload(event_type)

    # Get all webhooks subscribed to this event type
    webhooks = get_webhooks_for_event(event_type)

    # Deliver to each webhook
    results = []
    for webhook in webhooks:
        result = await deliver_webhook(webhook, event_id, event_type, payload)
        results.append(result)

    return event_id, results
