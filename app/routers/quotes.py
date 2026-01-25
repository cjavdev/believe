"""Quotes router for Ted Lasso API."""

import random
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.data import QUOTES
from app.models.quotes import Quote, QuoteCreate, QuoteUpdate, QuoteTheme, QuoteMoment
from app.pagination import PaginationParams, PaginatedResponse, paginate

router = APIRouter(prefix="/quotes", tags=["Quotes"])

# In-memory storage (copy of seed data)
_quotes_db: dict[str, dict] = dict(QUOTES)

# Counter for generating IDs
_quote_counter = len(_quotes_db) + 1


@router.get(
    "",
    response_model=PaginatedResponse[Quote],
    summary="List all quotes",
    description="Get a paginated list of all memorable Ted Lasso quotes with optional filtering.",
    responses={
        200: {
            "description": "Paginated list of quotes",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "quote-001",
                                "text": "Be curious, not judgmental.",
                                "character_id": "ted-lasso",
                                "episode_id": "s01e08",
                                "context": "Ted playing darts against Rupert in the pub, explaining his philosophy",
                                "theme": "curiosity",
                                "secondary_themes": ["wisdom", "kindness"],
                                "moment_type": "pub",
                                "is_inspirational": True,
                                "is_funny": False,
                            }
                        ],
                        "total": 50,
                        "skip": 0,
                        "limit": 20,
                        "has_more": True,
                        "page": 1,
                        "pages": 3,
                    }
                }
            },
        }
    },
)
async def list_quotes(
    pagination: PaginationParams = Depends(),
    character_id: Optional[str] = Query(None, description="Filter by character"),
    theme: Optional[QuoteTheme] = Query(None, description="Filter by theme"),
    moment_type: Optional[QuoteMoment] = Query(None, description="Filter by moment type"),
    inspirational: Optional[bool] = Query(None, description="Filter inspirational quotes"),
    funny: Optional[bool] = Query(None, description="Filter funny quotes"),
) -> PaginatedResponse[Quote]:
    """List all quotes with optional filters and pagination."""
    quotes = list(_quotes_db.values())

    if character_id:
        quotes = [q for q in quotes if q["character_id"] == character_id]

    if theme:
        quotes = [
            q
            for q in quotes
            if q["theme"] == theme.value or theme.value in q.get("secondary_themes", [])
        ]

    if moment_type:
        quotes = [q for q in quotes if q["moment_type"] == moment_type.value]

    if inspirational is not None:
        quotes = [q for q in quotes if q.get("is_inspirational") == inspirational]

    if funny is not None:
        quotes = [q for q in quotes if q.get("is_funny") == funny]

    paginated, total = paginate(quotes, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Quote(**q) for q in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/random",
    response_model=Quote,
    summary="Get a random quote",
    description="Get a random Ted Lasso quote, optionally filtered.",
    responses={
        200: {
            "description": "A random quote",
            "content": {
                "application/json": {
                    "example": {
                        "id": "quote-007",
                        "text": "I believe in believe.",
                        "character_id": "ted-lasso",
                        "episode_id": "s01e01",
                        "context": "Ted explaining his coaching philosophy",
                        "theme": "belief",
                        "secondary_themes": ["leadership"],
                        "moment_type": "locker_room",
                        "is_inspirational": True,
                        "is_funny": False,
                    }
                }
            },
        },
        404: {
            "description": "No quotes found matching criteria",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No quotes found matching your criteria. Try being more curious and less specific!"
                    }
                }
            },
        },
    },
)
async def get_random_quote(
    character_id: Optional[str] = Query(None, description="Filter by character"),
    theme: Optional[QuoteTheme] = Query(None, description="Filter by theme"),
    inspirational: Optional[bool] = Query(None, description="Filter inspirational quotes"),
) -> Quote:
    """Get a random quote."""
    quotes = list(_quotes_db.values())

    if character_id:
        quotes = [q for q in quotes if q["character_id"] == character_id]

    if theme:
        quotes = [
            q
            for q in quotes
            if q["theme"] == theme.value or theme.value in q.get("secondary_themes", [])
        ]

    if inspirational is not None:
        quotes = [q for q in quotes if q.get("is_inspirational") == inspirational]

    if not quotes:
        raise HTTPException(
            status_code=404,
            detail="No quotes found matching your criteria. Try being more curious and less specific!",
        )

    return Quote(**random.choice(quotes))


@router.get(
    "/{quote_id}",
    response_model=Quote,
    summary="Get a quote by ID",
    description="Retrieve a specific quote by its ID.",
    responses={
        200: {
            "description": "Quote details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "quote-001",
                        "text": "Be curious, not judgmental.",
                        "character_id": "ted-lasso",
                        "episode_id": "s01e08",
                        "context": "Ted playing darts against Rupert in the pub, explaining his philosophy",
                        "theme": "curiosity",
                        "secondary_themes": ["wisdom", "kindness"],
                        "moment_type": "pub",
                        "is_inspirational": True,
                        "is_funny": False,
                    }
                }
            },
        },
        404: {
            "description": "Quote not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Quote 'quote-999' not found. The wisdom you seek is elsewhere!"
                    }
                }
            },
        },
    },
)
async def get_quote(quote_id: str) -> Quote:
    """Get a specific quote by ID."""
    if quote_id not in _quotes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Quote '{quote_id}' not found. The wisdom you seek is elsewhere!",
        )
    return Quote(**_quotes_db[quote_id])


@router.post(
    "",
    response_model=Quote,
    status_code=201,
    summary="Create a new quote",
    description="Add a new memorable quote to the collection.",
    responses={
        201: {
            "description": "Quote created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "quote-051",
                        "text": "Football is life! But also, football is death. And football is football too.",
                        "character_id": "dani-rojas",
                        "episode_id": "s02e01",
                        "context": "Dani reflecting on the deeper meaning of the game",
                        "theme": "philosophy",
                        "secondary_themes": ["resilience", "humor"],
                        "moment_type": "training",
                        "is_inspirational": True,
                        "is_funny": True,
                    }
                }
            },
        }
    },
)
async def create_quote(quote: QuoteCreate) -> Quote:
    """Create a new quote."""
    global _quote_counter

    quote_id = f"quote-{_quote_counter:03d}"
    _quote_counter += 1

    quote_data = {"id": quote_id, **quote.model_dump()}
    _quotes_db[quote_id] = quote_data

    return Quote(**quote_data)


@router.patch(
    "/{quote_id}",
    response_model=Quote,
    summary="Update a quote",
    description="Update specific fields of an existing quote.",
    responses={
        200: {
            "description": "Quote updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "quote-001",
                        "text": "Be curious, not judgmental.",
                        "character_id": "ted-lasso",
                        "episode_id": "s01e08",
                        "context": "Ted playing darts against Rupert in the pub, teaching him a lesson about assumptions",
                        "theme": "curiosity",
                        "secondary_themes": ["wisdom", "kindness", "leadership"],
                        "moment_type": "pub",
                        "is_inspirational": True,
                        "is_funny": False,
                    }
                }
            },
        },
        404: {
            "description": "Quote not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Quote 'quote-999' not found."}
                }
            },
        },
    },
)
async def update_quote(quote_id: str, updates: QuoteUpdate) -> Quote:
    """Update an existing quote."""
    if quote_id not in _quotes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Quote '{quote_id}' not found.",
        )

    quote_data = _quotes_db[quote_id]

    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            quote_data[key] = value

    return Quote(**quote_data)


@router.delete(
    "/{quote_id}",
    status_code=204,
    summary="Delete a quote",
    description="Remove a quote from the collection.",
    responses={
        204: {"description": "Quote deleted successfully"},
        404: {
            "description": "Quote not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Quote 'quote-999' not found."}
                }
            },
        },
    },
)
async def delete_quote(quote_id: str) -> None:
    """Delete a quote."""
    if quote_id not in _quotes_db:
        raise HTTPException(
            status_code=404,
            detail=f"Quote '{quote_id}' not found.",
        )

    del _quotes_db[quote_id]


@router.get(
    "/themes/{theme}",
    response_model=PaginatedResponse[Quote],
    summary="Get quotes by theme",
    description="Get a paginated list of quotes related to a specific theme.",
    responses={
        200: {
            "description": "Paginated list of quotes for the theme",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "quote-001",
                                "text": "Be curious, not judgmental.",
                                "character_id": "ted-lasso",
                                "episode_id": "s01e08",
                                "context": "Ted playing darts against Rupert",
                                "theme": "curiosity",
                                "secondary_themes": ["wisdom", "kindness"],
                                "moment_type": "pub",
                                "is_inspirational": True,
                                "is_funny": False,
                            }
                        ],
                        "total": 8,
                        "skip": 0,
                        "limit": 20,
                        "has_more": False,
                        "page": 1,
                        "pages": 1,
                    }
                }
            },
        },
        404: {
            "description": "No quotes found for theme",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No quotes found for theme 'celebration'. We'll add some soon!"
                    }
                }
            },
        },
    },
)
async def get_quotes_by_theme(
    theme: QuoteTheme,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[Quote]:
    """Get quotes by theme with pagination."""
    quotes = [
        q
        for q in _quotes_db.values()
        if q["theme"] == theme.value or theme.value in q.get("secondary_themes", [])
    ]

    if not quotes:
        raise HTTPException(
            status_code=404,
            detail=f"No quotes found for theme '{theme.value}'. We'll add some soon!",
        )

    paginated, total = paginate(quotes, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Quote(**q) for q in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/characters/{character_id}",
    response_model=PaginatedResponse[Quote],
    summary="Get all quotes by a character",
    description="Get a paginated list of quotes from a specific character.",
    responses={
        200: {
            "description": "Paginated list of quotes from the character",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "quote-010",
                                "text": "He's here, he's there, he's every-f***ing-where, Roy Kent!",
                                "character_id": "roy-kent",
                                "episode_id": "s01e03",
                                "context": "The fans chanting Roy's famous song",
                                "theme": "celebration",
                                "secondary_themes": ["identity"],
                                "moment_type": "celebration",
                                "is_inspirational": False,
                                "is_funny": True,
                            }
                        ],
                        "total": 12,
                        "skip": 0,
                        "limit": 20,
                        "has_more": False,
                        "page": 1,
                        "pages": 1,
                    }
                }
            },
        },
        404: {
            "description": "No quotes found for character",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No quotes found for character 'unknown-character'. Maybe they're the strong, silent type!"
                    }
                }
            },
        },
    },
)
async def get_character_quotes(
    character_id: str,
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse[Quote]:
    """Get all quotes by a character with pagination."""
    quotes = [q for q in _quotes_db.values() if q["character_id"] == character_id]

    if not quotes:
        raise HTTPException(
            status_code=404,
            detail=f"No quotes found for character '{character_id}'. Maybe they're the strong, silent type!",
        )

    paginated, total = paginate(quotes, pagination.skip, pagination.limit)
    return PaginatedResponse(
        data=[Quote(**q) for q in paginated],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )
