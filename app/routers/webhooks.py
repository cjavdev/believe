"""Webhook management endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_api_key
from app.models.webhooks import (
    RegisteredWebhook,
    TriggerEventRequest,
    TriggerEventResponse,
    WebhookRegistrationRequest,
    WebhookRegistrationResponse,
)
from app.services import webhook_service

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "",
    response_model=WebhookRegistrationResponse,
    summary="Register a webhook endpoint",
    description="""
Register a new webhook endpoint to receive event notifications.

## Event Types

Available event types to subscribe to:
- `match.completed` - Fired when a football match ends
- `team_member.transferred` - Fired when a player/coach joins or leaves a team

If no event types are specified, the webhook will receive all event types.

## Webhook Signatures

All webhook deliveries include Standard Webhooks signature headers:
- `webhook-id` - Unique message identifier
- `webhook-timestamp` - Unix timestamp of when the webhook was sent
- `webhook-signature` - HMAC-SHA256 signature in format `v1,{base64_signature}`

Store the returned `secret` securely - you'll need it to verify webhook signatures.
""",
    responses={
        200: {
            "description": "Webhook registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "webhook": {
                            "id": "wh_abc123def456",
                            "url": "https://example.com/webhooks",
                            "event_types": [
                                "match.completed",
                                "team_member.transferred",
                            ],
                            "description": "Production webhook",
                            "created_at": "2024-01-15T10:00:00Z",
                            "secret": "whsec_dGVzdHNlY3JldGtleQ==",
                        },
                        "message": "Webhook registered successfully",
                        "ted_says": "You know what? Staying connected is what it's all about. Welcome to the team!",
                    }
                }
            },
        }
    },
)
async def register_webhook(
    request: WebhookRegistrationRequest,
) -> WebhookRegistrationResponse:
    """Register a new webhook endpoint."""
    webhook = webhook_service.register_webhook(
        url=str(request.url),
        event_types=request.event_types,
        description=request.description,
    )

    return WebhookRegistrationResponse(
        webhook=webhook,
        message="Webhook registered successfully",
        ted_says="You know what? Staying connected is what it's all about. Welcome to the team!",
    )


@router.get(
    "",
    response_model=list[RegisteredWebhook],
    summary="List registered webhooks",
    description="Get a list of all registered webhook endpoints.",
)
async def list_webhooks() -> list[RegisteredWebhook]:
    """List all registered webhooks."""
    return webhook_service.list_webhooks()


@router.get(
    "/{webhook_id}",
    response_model=RegisteredWebhook,
    summary="Get a webhook",
    description="Get details of a specific webhook endpoint.",
    responses={
        404: {
            "description": "Webhook not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Webhook not found. But hey, every ending is a new beginning!"
                    }
                }
            },
        }
    },
)
async def get_webhook(webhook_id: str) -> RegisteredWebhook:
    """Get a specific webhook by ID."""
    webhook = webhook_service.get_webhook(webhook_id)
    if webhook is None:
        raise HTTPException(
            status_code=404,
            detail="Webhook not found. But hey, every ending is a new beginning!",
        )
    return webhook


@router.delete(
    "/{webhook_id}",
    summary="Delete a webhook",
    description="Unregister a webhook endpoint. It will no longer receive events.",
    responses={
        200: {
            "description": "Webhook deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Webhook deleted successfully",
                        "ted_says": "Goodbyes ain't easy, but sometimes we gotta make room for new hellos.",
                    }
                }
            },
        },
        404: {
            "description": "Webhook not found",
        },
    },
)
async def delete_webhook(webhook_id: str) -> dict:
    """Delete a webhook endpoint."""
    deleted = webhook_service.delete_webhook(webhook_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Webhook not found. But hey, every ending is a new beginning!",
        )

    return {
        "message": "Webhook deleted successfully",
        "ted_says": "Goodbyes ain't easy, but sometimes we gotta make room for new hellos.",
    }


@router.post(
    "/trigger",
    response_model=TriggerEventResponse,
    summary="Trigger a webhook event",
    description="""
Trigger a webhook event and deliver it to all subscribed endpoints.

This endpoint is useful for testing your webhook integration. It will:
1. Generate an event with the specified type and payload
2. Find all webhooks subscribed to that event type
3. Send a POST request to each webhook URL with signature headers
4. Return the delivery results

## Event Payload

You can provide a custom payload, or leave it empty to use a sample payload.

## Webhook Signature Headers

Each webhook delivery includes:
- `webhook-id` - Unique event identifier (e.g., `evt_abc123...`)
- `webhook-timestamp` - Unix timestamp
- `webhook-signature` - HMAC-SHA256 signature (`v1,{base64}`)

To verify signatures, compute:
```
signature = HMAC-SHA256(
    key = base64_decode(secret_without_prefix),
    message = "{timestamp}.{raw_json_payload}"
)
```
""",
    responses={
        200: {
            "description": "Event triggered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "event_id": "evt_abc123def456789012345678",
                        "event_type": "match.completed",
                        "deliveries": [
                            {
                                "webhook_id": "wh_xyz789",
                                "url": "https://example.com/webhooks",
                                "success": True,
                                "status_code": 200,
                                "error": None,
                            }
                        ],
                        "total_webhooks": 1,
                        "successful_deliveries": 1,
                        "ted_says": "Message delivered! Communication is key, just like in any good relationship.",
                    }
                }
            },
        }
    },
)
async def trigger_event(request: TriggerEventRequest) -> TriggerEventResponse:
    """Trigger a webhook event and deliver to all subscribed endpoints."""
    event_id, results = await webhook_service.trigger_event(
        event_type=request.event_type,
        payload=request.payload,
    )

    successful = sum(1 for r in results if r.success)
    total = len(results)

    # Choose Ted's reaction based on results
    if total == 0:
        ted_says = "No webhooks registered for this event type yet. But that's okay - every team starts somewhere!"
    elif successful == total:
        ted_says = "Message delivered! Communication is key, just like in any good relationship."
    elif successful > 0:
        ted_says = "Some webhooks received the message, some didn't. That's life - we learn and try again!"
    else:
        ted_says = "None of the webhooks responded successfully. But hey, be a goldfish - we'll try again!"

    return TriggerEventResponse(
        event_id=event_id,
        event_type=request.event_type,
        deliveries=results,
        total_webhooks=total,
        successful_deliveries=successful,
        ted_says=ted_says,
    )
