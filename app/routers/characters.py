"""Characters router for Ted Lasso API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.data import CHARACTERS
from app.models.characters import Character, CharacterCreate, CharacterUpdate, CharacterRole
from app.pagination import PaginationParams, PaginatedResponse, paginate

router = APIRouter(prefix="/characters", tags=["Characters"])

# In-memory storage (copy of seed data)
_characters_db: dict[str, dict] = dict(CHARACTERS)


def _generate_id(name: str) -> str:
    """Generate a URL-friendly ID from a name."""
    return name.lower().replace(" ", "-").replace("'", "")


@router.get(
    "",
    response_model=PaginatedResponse[Character],
    summary="List all characters",
    description="Get a paginated list of all Ted Lasso characters with optional filtering.",
    responses={
        200: {
            "description": "Paginated list of characters",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "ted-lasso",
                                "name": "Ted Lasso",
                                "role": "coach",
                                "team_id": "afc-richmond",
                                "background": "Former American football coach from Kansas who moved to London to coach AFC Richmond",
                                "personality_traits": ["optimistic", "kind", "folksy", "persistent"],
                                "emotional_stats": {
                                    "optimism": 95,
                                    "vulnerability": 80,
                                    "empathy": 100,
                                    "resilience": 90,
                                    "curiosity": 99,
                                },
                                "signature_quotes": [
                                    "I believe in believe.",
                                    "Be curious, not judgmental.",
                                ],
                                "growth_arcs": [],
                            }
                        ],
                        "total": 15,
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
async def list_characters(
    pagination: PaginationParams = Depends(),
    role: Optional[CharacterRole] = Query(None, description="Filter by role"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    min_optimism: Optional[int] = Query(None, ge=0, le=100, description="Minimum optimism score"),
) -> PaginatedResponse[Character]:
    """List all characters with optional filters and pagination."""
    characters = list(_characters_db.values())

    if role:
        characters = [c for c in characters if c["role"] == role.value]

    if team_id:
        characters = [c for c in characters if c.get("team_id") == team_id]

    if min_optimism is not None:
        characters = [
            c for c in characters if c["emotional_stats"]["optimism"] >= min_optimism
        ]

    paginated, total = paginate(characters, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Character(**c) for c in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{character_id}",
    response_model=Character,
    summary="Get a character by ID",
    description="Retrieve detailed information about a specific character.",
    responses={
        200: {
            "description": "Character details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ted-lasso",
                        "name": "Ted Lasso",
                        "role": "coach",
                        "team_id": "afc-richmond",
                        "background": "Former American football coach from Kansas who moved to London to coach AFC Richmond",
                        "personality_traits": ["optimistic", "kind", "folksy", "persistent"],
                        "emotional_stats": {
                            "optimism": 95,
                            "vulnerability": 80,
                            "empathy": 100,
                            "resilience": 90,
                            "curiosity": 99,
                        },
                        "signature_quotes": [
                            "I believe in believe.",
                            "Be curious, not judgmental.",
                        ],
                        "growth_arcs": [
                            {
                                "season": 1,
                                "starting_point": "Fish out of water, hiding pain with humor",
                                "challenge": "Earning respect despite inexperience",
                                "breakthrough": "Showing vulnerability about his marriage",
                                "ending_point": "Accepted by the team despite relegation",
                            }
                        ],
                    }
                }
            },
        },
        404: {
            "description": "Character not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Character 'unknown-character' not found. Be curious about who else might be in our roster!"
                    }
                }
            },
        },
    },
)
async def get_character(character_id: str) -> Character:
    """Get a specific character by ID."""
    if character_id not in _characters_db:
        raise HTTPException(
            status_code=404,
            detail=f"Character '{character_id}' not found. Be curious about who else might be in our roster!",
        )
    return Character(**_characters_db[character_id])


@router.post(
    "",
    response_model=Character,
    status_code=201,
    summary="Create a new character",
    description="Add a new character to the Ted Lasso universe.",
    responses={
        201: {
            "description": "Character created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "mae-the-publican",
                        "name": "Mae the Publican",
                        "role": "other",
                        "team_id": None,
                        "background": "Owner of the Crown & Anchor pub near Nelson Road, unofficial heart of Richmond fandom",
                        "personality_traits": ["welcoming", "wise", "supportive", "witty"],
                        "emotional_stats": {
                            "optimism": 75,
                            "vulnerability": 60,
                            "empathy": 85,
                            "resilience": 80,
                            "curiosity": 70,
                        },
                        "signature_quotes": ["This is a pub. People come here to feel better."],
                        "growth_arcs": [],
                    }
                }
            },
        },
        409: {
            "description": "Character already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Character with ID 'ted-lasso' already exists. Everyone's unique, like snowflakes!"
                    }
                }
            },
        },
    },
)
async def create_character(character: CharacterCreate) -> Character:
    """Create a new character."""
    character_id = _generate_id(character.name)

    if character_id in _characters_db:
        raise HTTPException(
            status_code=409,
            detail=f"Character with ID '{character_id}' already exists. Everyone's unique, like snowflakes!",
        )

    character_data = {"id": character_id, **character.model_dump()}
    _characters_db[character_id] = character_data

    return Character(**character_data)


@router.patch(
    "/{character_id}",
    response_model=Character,
    summary="Update a character",
    description="Update specific fields of an existing character.",
    responses={
        200: {
            "description": "Character updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "ted-lasso",
                        "name": "Ted Lasso",
                        "role": "coach",
                        "team_id": "afc-richmond",
                        "background": "Former American football coach from Kansas, now beloved manager of AFC Richmond",
                        "personality_traits": ["optimistic", "kind", "folksy", "persistent", "wise"],
                        "emotional_stats": {
                            "optimism": 98,
                            "vulnerability": 85,
                            "empathy": 100,
                            "resilience": 95,
                            "curiosity": 99,
                        },
                        "signature_quotes": [
                            "I believe in believe.",
                            "Be curious, not judgmental.",
                        ],
                        "growth_arcs": [],
                    }
                }
            },
        },
        404: {
            "description": "Character not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Character 'unknown-character' not found. Can't update someone who doesn't exist... yet!"
                    }
                }
            },
        },
    },
)
async def update_character(character_id: str, updates: CharacterUpdate) -> Character:
    """Update an existing character."""
    if character_id not in _characters_db:
        raise HTTPException(
            status_code=404,
            detail=f"Character '{character_id}' not found. Can't update someone who doesn't exist... yet!",
        )

    character_data = _characters_db[character_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            if isinstance(value, dict) and key in character_data:
                character_data[key].update(value)
            else:
                character_data[key] = value

    return Character(**character_data)


@router.delete(
    "/{character_id}",
    status_code=204,
    summary="Delete a character",
    description="Remove a character from the database.",
    responses={
        204: {"description": "Character deleted successfully"},
        404: {
            "description": "Character not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Character 'unknown-character' not found. Already gone, like yesterday's worries!"
                    }
                }
            },
        },
    },
)
async def delete_character(character_id: str) -> None:
    """Delete a character."""
    if character_id not in _characters_db:
        raise HTTPException(
            status_code=404,
            detail=f"Character '{character_id}' not found. Already gone, like yesterday's worries!",
        )

    del _characters_db[character_id]


@router.get(
    "/{character_id}/quotes",
    response_model=list[str],
    summary="Get character's signature quotes",
    description="Get all signature quotes from a specific character.",
    responses={
        200: {
            "description": "List of signature quotes",
            "content": {
                "application/json": {
                    "example": [
                        "I believe in believe.",
                        "Be curious, not judgmental.",
                        "Taking on a challenge is a lot like riding a horse. If you're comfortable while you're doing it, you're probably doing it wrong.",
                        "You know what the happiest animal on Earth is? It's a goldfish. You know why? Got a 10-second memory.",
                    ]
                }
            },
        },
        404: {
            "description": "Character not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Character 'unknown-character' not found."}
                }
            },
        },
    },
)
async def get_character_quotes(character_id: str) -> list[str]:
    """Get a character's signature quotes."""
    if character_id not in _characters_db:
        raise HTTPException(
            status_code=404,
            detail=f"Character '{character_id}' not found.",
        )

    return _characters_db[character_id].get("signature_quotes", [])
