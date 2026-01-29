"""Webhook registration and event models."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl

# Event type literals
EventType = Literal["match.completed", "team_member.transferred"]

ALL_EVENT_TYPES: list[EventType] = ["match.completed", "team_member.transferred"]


# --- Webhook Registration Models ---


class WebhookRegistrationRequest(BaseModel):
    """Request to register a new webhook endpoint."""

    url: HttpUrl = Field(
        ...,
        description="The URL to send webhook events to",
        examples=["https://example.com/webhooks"],
    )
    event_types: list[EventType] | None = Field(
        default=None,
        description="List of event types to subscribe to. If not provided, subscribes to all events.",
        examples=[["match.completed", "team_member.transferred"]],
    )
    description: str | None = Field(
        default=None,
        description="Optional description for this webhook",
        examples=["Production webhook for match notifications"],
    )


class RegisteredWebhook(BaseModel):
    """A registered webhook endpoint."""

    id: str = Field(
        ...,
        description="Unique webhook identifier",
        examples=["wh_abc123"],
    )
    url: HttpUrl = Field(
        ...,
        description="The URL to send webhook events to",
    )
    event_types: list[EventType] = Field(
        ...,
        description="List of event types this webhook is subscribed to",
    )
    description: str | None = Field(
        default=None,
        description="Optional description for this webhook",
    )
    created_at: datetime = Field(
        ...,
        description="When the webhook was registered",
    )
    secret: str = Field(
        ...,
        description="The secret key for verifying webhook signatures (base64 encoded)",
        examples=["whsec_abc123def456..."],
    )


class WebhookRegistrationResponse(BaseModel):
    """Response after registering a webhook."""

    webhook: RegisteredWebhook = Field(
        ...,
        description="The registered webhook details",
    )
    message: str = Field(
        default="Webhook registered successfully",
        description="Status message",
    )
    ted_says: str = Field(
        default="You know what? Staying connected is what it's all about. Welcome to the team!",
        description="Ted's reaction",
    )


# --- Event Payload Models ---


class MatchCompletedData(BaseModel):
    """Data payload for a match completed event."""

    match_id: str = Field(..., description="Unique match identifier")
    home_team_id: str = Field(..., description="Home team ID")
    away_team_id: str = Field(..., description="Away team ID")
    home_score: int = Field(..., ge=0, description="Final home team score")
    away_score: int = Field(..., ge=0, description="Final away team score")
    result: Literal["home_win", "away_win", "draw"] = Field(
        ..., description="Match result from home team perspective"
    )
    match_type: Literal["league", "cup", "friendly", "playoff", "final"] = Field(
        ..., description="Type of match"
    )
    completed_at: datetime = Field(..., description="When the match completed")
    man_of_the_match: str | None = Field(
        default=None, description="Player of the match (if awarded)"
    )
    lesson_learned: str | None = Field(
        default=None, description="Ted's lesson from the match"
    )
    ted_post_match_quote: str = Field(..., description="Ted's post-match wisdom")


class TeamMemberTransferredData(BaseModel):
    """Data payload for a team member transfer event."""

    team_member_id: str = Field(..., description="ID of the team member")
    character_id: str = Field(
        ..., description="ID of the character (links to /characters)"
    )
    character_name: str = Field(..., description="Name of the character")
    member_type: Literal["player", "coach", "medical_staff", "equipment_manager"] = (
        Field(..., description="Type of team member")
    )
    transfer_type: Literal["joined", "departed"] = Field(
        ..., description="Whether the member joined or departed"
    )
    team_id: str = Field(..., description="ID of the team involved")
    team_name: str = Field(..., description="Name of the team involved")
    previous_team_id: str | None = Field(
        default=None, description="Previous team ID (for joins from another team)"
    )
    previous_team_name: str | None = Field(
        default=None, description="Previous team name (for joins from another team)"
    )
    years_with_previous_team: int | None = Field(
        default=None, ge=0, description="Years spent with previous team"
    )
    transfer_fee_gbp: str | None = Field(
        default=None, description="Transfer fee in GBP (for players)"
    )
    ted_reaction: str = Field(..., description="Ted's reaction to the transfer")


class MatchCompletedPayload(BaseModel):
    """Payload for match.completed event."""

    event_type: Literal["match.completed"] = Field(
        default="match.completed", description="The type of webhook event"
    )
    data: MatchCompletedData = Field(..., description="Event data")


class TeamMemberTransferredPayload(BaseModel):
    """Payload for team_member.transferred event."""

    event_type: Literal["team_member.transferred"] = Field(
        default="team_member.transferred", description="The type of webhook event"
    )
    data: TeamMemberTransferredData = Field(..., description="Event data")


# Union type for trigger request payload
WebhookEventPayload = Annotated[
    MatchCompletedPayload | TeamMemberTransferredPayload,
    Field(discriminator="event_type"),
]


class TriggerEventRequest(BaseModel):
    """Request to trigger a webhook event."""

    event_type: EventType = Field(
        ...,
        description="The type of event to trigger",
        examples=["match.completed"],
    )
    payload: WebhookEventPayload | None = Field(
        default=None,
        description="Optional event payload. If not provided, a sample payload will be generated.",
    )


class WebhookDeliveryResult(BaseModel):
    """Result of delivering a webhook to a single endpoint."""

    webhook_id: str = Field(..., description="ID of the webhook")
    url: str = Field(..., description="URL the webhook was sent to")
    success: bool = Field(..., description="Whether delivery was successful")
    status_code: int | None = Field(
        default=None, description="HTTP status code from the endpoint"
    )
    error: str | None = Field(
        default=None, description="Error message if delivery failed"
    )


class TriggerEventResponse(BaseModel):
    """Response after triggering webhook events."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="The type of event triggered")
    deliveries: list[WebhookDeliveryResult] = Field(
        ..., description="Results of webhook deliveries"
    )
    total_webhooks: int = Field(
        ..., description="Total number of webhooks that received this event"
    )
    successful_deliveries: int = Field(
        ..., description="Number of successful deliveries"
    )
    ted_says: str = Field(..., description="Ted's reaction")
