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
        200: {
            "description": "Motivational response generated",
            "content": {
                "application/json": {
                    "example": {
                        "ted_response": "Now hold on just a second there, friend. Getting passed over for a promotion ain't about you not being good enough - it's just the universe saying 'not yet.' You know what I always say? It's not about the wins and losses, it's about the journey.",
                        "relevant_quote": "Be curious, not judgmental.",
                        "action_suggestion": "Take your colleague who got the promotion out for coffee. Celebrate them, and ask what you can learn from them.",
                        "goldfish_wisdom": "Remember, a goldfish has a 10-second memory. Let this setback swim on by.",
                        "believe_score": 75,
                    }
                }
            },
        },
        418: {
            "description": "You're already a believer!",
            "content": {
                "application/json": {
                    "example": {
                        "status": "I'm a Believer!",
                        "message": "You're already believing so hard, you don't need my help!",
                        "ted_says": "Well shoot, you've got more believe in you than a Kansas sunrise. Keep on keeping on!",
                        "believe_score": 100,
                    }
                }
            },
        },
        429: {
            "description": "Too much negativity detected",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Much Negativity",
                        "message": "Whoa there, partner! That's a lot of negative energy. Let's take a breath and try again with a little more optimism.",
                        "ted_advice": "Be a goldfish. 10-second memory for the bad stuff.",
                    }
                }
            },
        },
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
        200: {
            "description": "Conflict resolution guidance",
            "content": {
                "application/json": {
                    "example": {
                        "diagnosis": "This sounds like a classic case of miscommunication mixed with some bruised egos. Alex probably doesn't realize they're doing it, and you've been bottling up your frustration.",
                        "ted_approach": "Ted would invite both of you for biscuits and have an honest conversation. He'd remind you that you're both on the same team.",
                        "diamond_dogs_advice": "The Diamond Dogs suggest: WWBBD - What Would Beard's Book Do? Talk it out, acknowledge the feelings, and find common ground.",
                        "steps_to_resolution": [
                            "Ask Alex for a one-on-one chat over coffee",
                            "Use 'I feel' statements instead of accusations",
                            "Acknowledge what Alex does well",
                            "Clearly state what you need going forward",
                            "Agree on how to handle credit for collaborative work",
                        ],
                        "potential_outcome": "You and Alex could become an even stronger team, with clear communication about contributions and shared success.",
                        "barbecue_sauce_wisdom": "You know, resolving conflict is like making barbecue sauce - you gotta let things simmer, but don't let it boil over.",
                    }
                }
            },
        },
        403: {
            "description": "Too judgmental",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Judgment Without Curiosity",
                        "message": "Hold on now - that request felt a bit judgmental. Remember: be curious, not judgmental.",
                        "ted_advice": "Try approaching this with an open mind and genuine curiosity.",
                    }
                }
            },
        },
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
        200: {
            "description": "Reframed perspective",
            "content": {
                "application/json": {
                    "example": {
                        "original_thought": "I'm not good enough for this job.",
                        "reframed_thought": "I'm still learning and growing in this role, and every challenge is an opportunity to become even better.",
                        "ted_perspective": "Now shoot, feeling like you're not good enough? That just means you care! The day you stop caring is the day you should worry. You wouldn't be in this job if someone didn't believe in you.",
                        "dr_sharon_insight": "That critical voice isn't telling you the truth - it's telling you a story. What evidence do you have that contradicts this thought?",
                        "daily_affirmation": "I am capable, I am learning, and I belong here. I bring unique value that no one else can.",
                    }
                }
            },
        },
        429: {
            "description": "Too much negativity",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Too Much Negativity",
                        "message": "Whoa there, partner! That's a lot of negative energy. Let's take a breath and try again with a little more optimism.",
                        "ted_advice": "Be a goldfish. 10-second memory for the bad stuff.",
                    }
                }
            },
        },
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
        200: {
            "description": "Press conference response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Well, I'll tell you what - that was quite a game out there today. Did we lose? Sure. Did we lose big? You betcha. But you know what we didn't lose? Our spirit, our togetherness, and our belief that tomorrow's gonna be a better day.",
                        "deflection_humor": "Speaking of numbers, did you know a group of flamingos is called a 'flamboyance'? Now THAT'S embarrassing!",
                        "actual_wisdom": "Setbacks are setups for comebacks. The score doesn't define who we are as people or as a team.",
                        "reporter_reaction": "The reporters exchange confused glances but can't help smiling.",
                        "follow_up_dodge": "Great question! Hey, does anyone know if there's a good barbecue place around here? I'm in the mood for some brisket.",
                    }
                }
            },
        }
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
        200: {
            "description": "Paginated list of coaching principles",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "believe",
                                "principle": "Believe",
                                "explanation": "Having faith in yourself, your team, and the process, even when things look bleak.",
                                "application": "Put up a BELIEVE sign where you can see it daily. When doubt creeps in, remember why you started.",
                                "example_from_show": "Ted hangs the BELIEVE sign in the locker room, and it becomes a rallying symbol for the team.",
                                "ted_quote": "I believe in believe.",
                            }
                        ],
                        "total": 10,
                        "skip": 0,
                        "limit": 20,
                        "has_more": False,
                        "page": 1,
                        "pages": 1,
                    }
                }
            },
        }
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
    responses={
        200: {
            "description": "Coaching principle details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "curiosity",
                        "principle": "Be Curious, Not Judgmental",
                        "explanation": "Approach people and situations with genuine curiosity rather than jumping to conclusions.",
                        "application": "When someone frustrates you, ask questions to understand their perspective before forming opinions.",
                        "example_from_show": "Ted explains this principle while beating Rupert at darts, revealing that Rupert never bothered to learn that Ted was a dart champion.",
                        "ted_quote": "Be curious, not judgmental.",
                    }
                }
            },
        },
        404: {
            "description": "Principle not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Principle 'unknown-principle' not found. The best principles are the ones you discover yourself!"
                    }
                }
            },
        },
    },
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
    responses={
        200: {
            "description": "A random coaching principle",
            "content": {
                "application/json": {
                    "example": {
                        "id": "goldfish",
                        "principle": "Be a Goldfish",
                        "explanation": "Don't dwell on mistakes or setbacks. A goldfish has a 10-second memory - be like the goldfish.",
                        "application": "When you make a mistake, acknowledge it, learn from it, and move on quickly.",
                        "example_from_show": "Ted tells Sam to 'be a goldfish' after he misses a shot, helping him shake off the disappointment.",
                        "ted_quote": "You know what the happiest animal on Earth is? It's a goldfish. You know why? It's got a 10-second memory.",
                    }
                }
            },
        }
    },
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
        200: {
            "description": "Paginated list of fresh biscuits from Ted's kitchen",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "classic-shortbread",
                                "type": "shortbread",
                                "message": "You're doing great, boss!",
                                "warmth_level": 8,
                                "pairs_well_with": "A cup of English breakfast tea and a good chat",
                                "ted_note": "Made these thinking of you. Hope they brighten your day!",
                            }
                        ],
                        "total": 4,
                        "skip": 0,
                        "limit": 20,
                        "has_more": False,
                        "page": 1,
                        "pages": 1,
                    }
                }
            },
        }
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
    responses={
        200: {
            "description": "A fresh biscuit from Ted's kitchen",
            "content": {
                "application/json": {
                    "example": {
                        "id": "classic-shortbread",
                        "type": "shortbread",
                        "message": "You're doing great, boss!",
                        "warmth_level": 10,
                        "pairs_well_with": "A cup of English breakfast tea and a good chat",
                        "ted_note": "Made these thinking of you. Hope they brighten your day! P.S. You're doing amazing, sweetie!",
                    }
                }
            },
        }
    },
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
    responses={
        200: {
            "description": "Biscuit details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "chocolate-chip",
                        "type": "chocolate_chip",
                        "message": "Life is like a box of biscuits - you never know which one's gonna have the most chocolate chips!",
                        "warmth_level": 7,
                        "pairs_well_with": "A glass of cold milk and a football match on the telly",
                        "ted_note": "Added extra chocolate chips because you deserve it!",
                    }
                }
            },
        },
        404: {
            "description": "Biscuit not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Biscuit 'mystery-flavor' not found. Must have been eaten already!"
                    }
                }
            },
        },
    },
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
