"""Interactive endpoints router for Ted Lasso API."""

import random
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.data import COACHING_PRINCIPLES, BISCUITS
from app.pagination import PaginationParams, PaginatedResponse, paginate
from app.models.interactive import (
    BelieveRequest,
    BelieveResponse,
    ConflictRequest,
    ConflictResolution,
    ReframeRequest,
    ReframeResponse,
    PressConferenceRequest,
    PressConferenceResponse,
    CoachingPrinciple,
    Biscuit,
)
from app.services import (
    BelieveEngine,
    ConflictResolver,
    ReframeService,
    PressConferenceSimulator,
)

router = APIRouter(tags=["Interactive"])


# === Custom Error Responses ===


class TooMuchNegativityError(HTTPException):
    """Custom 429 error for too much negativity."""

    def __init__(self):
        super().__init__(
            status_code=429,
            detail={
                "error": "Too Much Negativity",
                "message": "Whoa there, partner! That's a lot of negative energy. Let's take a breath and try again with a little more optimism.",
                "ted_advice": "Be a goldfish. 10-second memory for the bad stuff.",
            },
        )


class JudgmentWithoutCuriosityError(HTTPException):
    """Custom 403 error for judgment without curiosity."""

    def __init__(self):
        super().__init__(
            status_code=403,
            detail={
                "error": "Judgment Without Curiosity",
                "message": "Hold on now - that request felt a bit judgmental. Remember: be curious, not judgmental.",
                "ted_advice": "Try approaching this with an open mind and genuine curiosity.",
            },
        )


class ImABelieverResponse(JSONResponse):
    """Custom 418 response for believers."""

    def __init__(self, content: dict):
        super().__init__(status_code=418, content=content)


# === Believe Engine ===


@router.post(
    "/believe",
    response_model=BelieveResponse,
    summary="The Believe Engine",
    description="Submit your situation and receive Ted Lasso-style motivational guidance.",
    responses={
        200: {"description": "Motivational response generated"},
        418: {"description": "You're already a believer!"},
        429: {"description": "Too much negativity detected"},
    },
)
async def believe_engine(request: BelieveRequest) -> BelieveResponse:
    """Get motivational guidance from the Believe Engine."""
    # Easter egg: if the situation mentions "believe" too much, return 418
    if request.situation.lower().count("believe") >= 3:
        return ImABelieverResponse(
            content={
                "status": "I'm a Believer!",
                "message": "You're already believing so hard, you don't need my help!",
                "ted_says": "Well shoot, you've got more believe in you than a Kansas sunrise. Keep on keeping on!",
                "believe_score": 100,
            }
        )

    # Check for too much negativity
    negative_words = ["hate", "terrible", "awful", "worst", "never", "hopeless", "give up"]
    negativity_count = sum(1 for word in negative_words if word in request.situation.lower())
    if negativity_count >= 4:
        raise TooMuchNegativityError()

    return BelieveEngine.generate_response(request)


# === Conflict Resolution ===


@router.post(
    "/conflicts/resolve",
    response_model=ConflictResolution,
    summary="Resolve Conflicts",
    description="Get Ted Lasso-style advice for resolving conflicts.",
    responses={
        200: {"description": "Conflict resolution guidance"},
        403: {"description": "Too judgmental"},
    },
)
async def resolve_conflict(request: ConflictRequest) -> ConflictResolution:
    """Get conflict resolution advice."""
    # Check for judgmental language
    judgmental_words = ["stupid", "idiot", "wrong", "fault", "blame", "always", "never"]
    description_lower = request.description.lower()
    judgment_count = sum(1 for word in judgmental_words if word in description_lower)

    if judgment_count >= 3:
        raise JudgmentWithoutCuriosityError()

    return ConflictResolver.resolve(request)


# === Reframe Negative Thoughts ===


@router.post(
    "/reframe",
    response_model=ReframeResponse,
    summary="Reframe Negative Thoughts",
    description="Transform negative thoughts into positive perspectives with Ted's help.",
    responses={
        200: {"description": "Reframed perspective"},
        429: {"description": "Too much negativity"},
    },
)
async def reframe_thought(request: ReframeRequest) -> ReframeResponse:
    """Reframe a negative thought positively."""
    return ReframeService.reframe(request)


# === Press Conference Simulator ===


@router.post(
    "/press",
    response_model=PressConferenceResponse,
    summary="Press Conference Simulator",
    description="Get Ted's response to press conference questions.",
    responses={
        200: {"description": "Press conference response"},
    },
)
async def press_conference(request: PressConferenceRequest) -> PressConferenceResponse:
    """Simulate a Ted Lasso press conference response."""
    return PressConferenceSimulator.respond(request)


# === Coaching Principles ===


@router.get(
    "/coaching/principles",
    response_model=PaginatedResponse[CoachingPrinciple],
    summary="Get Coaching Principles",
    description="Get a paginated list of Ted Lasso's core coaching principles and philosophy.",
    responses={
        200: {"description": "Paginated list of coaching principles"},
    },
)
async def get_coaching_principles(
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[CoachingPrinciple]:
    """Get all Ted Lasso coaching principles with pagination."""
    paginated, total = paginate(COACHING_PRINCIPLES, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[CoachingPrinciple(**p) for p in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/coaching/principles/{principle_id}",
    response_model=CoachingPrinciple,
    summary="Get a Specific Coaching Principle",
    description="Get details about a specific coaching principle.",
)
async def get_coaching_principle(principle_id: str) -> CoachingPrinciple:
    """Get a specific coaching principle by ID."""
    for principle in COACHING_PRINCIPLES:
        if principle["id"] == principle_id:
            return CoachingPrinciple(**principle)

    raise HTTPException(
        status_code=404,
        detail=f"Principle '{principle_id}' not found. The best principles are the ones you discover yourself!",
    )


@router.get(
    "/coaching/principles/random",
    response_model=CoachingPrinciple,
    summary="Get a Random Coaching Principle",
    description="Get a random coaching principle to inspire your day.",
)
async def get_random_principle() -> CoachingPrinciple:
    """Get a random coaching principle."""
    return CoachingPrinciple(**random.choice(COACHING_PRINCIPLES))


# === Biscuits as a Service ===


@router.get(
    "/biscuits",
    response_model=PaginatedResponse[Biscuit],
    summary="Biscuits as a Service",
    description="Get a paginated list of Ted's famous homemade biscuits! Each comes with a heartwarming message.",
    responses={
        200: {"description": "Paginated list of fresh biscuits from Ted's kitchen"},
    },
)
async def get_biscuits(
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[Biscuit]:
    """Get all available biscuits with pagination."""
    paginated, total = paginate(BISCUITS, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Biscuit(**b) for b in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/biscuits/fresh",
    response_model=Biscuit,
    summary="Get a Fresh Biscuit",
    description="Get a single fresh biscuit with a personalized message from Ted.",
)
async def get_fresh_biscuit() -> Biscuit:
    """Get a single fresh biscuit."""
    biscuit = random.choice(BISCUITS).copy()

    # Add some personalization
    extra_notes = [
        "P.S. You're doing amazing, sweetie!",
        "P.S. Remember: be curious, not judgmental!",
        "P.S. Today's gonna be a good day, I can feel it!",
        "P.S. You've got more heart than a cardiologist's convention!",
    ]
    biscuit["ted_note"] = f"{biscuit['ted_note']} {random.choice(extra_notes)}"
    biscuit["warmth_level"] = 10  # Fresh from the oven!

    return Biscuit(**biscuit)


@router.get(
    "/biscuits/{biscuit_id}",
    response_model=Biscuit,
    summary="Get a Specific Biscuit",
    description="Get a specific type of biscuit by ID.",
)
async def get_biscuit(biscuit_id: str) -> Biscuit:
    """Get a specific biscuit by ID."""
    for biscuit in BISCUITS:
        if biscuit["id"] == biscuit_id:
            return Biscuit(**biscuit)

    raise HTTPException(
        status_code=404,
        detail=f"Biscuit '{biscuit_id}' not found. Must have been eaten already!",
    )
