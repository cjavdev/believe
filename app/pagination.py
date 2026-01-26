"""Pagination utilities for the Ted Lasso API.

This module provides reusable pagination components following FastAPI best practices:
- PaginationParams: Dependency for extracting pagination query parameters
- PaginatedResponse: Generic response wrapper with pagination metadata
- paginate: Utility function to apply pagination to any list
"""

from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, computed_field

T = TypeVar("T")

# Default pagination settings
DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class PaginationParams:
    """Dependency for pagination query parameters.

    Usage:
        @router.get("/items")
        async def list_items(pagination: PaginationParams = Depends()):
            ...
    """

    def __init__(
        self,
        skip: int = Query(
            default=0,
            ge=0,
            description="Number of items to skip (offset)",
            examples=[0, 20, 40],
        ),
        limit: int = Query(
            default=DEFAULT_LIMIT,
            ge=1,
            le=MAX_LIMIT,
            description=f"Maximum number of items to return (max: {MAX_LIMIT})",
            examples=[10, 20, 50],
        ),
    ):
        self.skip = skip
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Provides consistent pagination metadata across all list endpoints.
    """

    data: list[T]
    total: int
    skip: int
    limit: int

    @computed_field
    @property
    def has_more(self) -> bool:
        """Whether there are more items after this page."""
        return self.skip + len(self.data) < self.total

    @computed_field
    @property
    def page(self) -> int:
        """Current page number (1-indexed, for display purposes)."""
        if self.limit == 0:
            return 1
        return (self.skip // self.limit) + 1

    @computed_field
    @property
    def pages(self) -> int:
        """Total number of pages."""
        if self.limit == 0:
            return 1
        return (self.total + self.limit - 1) // self.limit


def paginate(
    items: Sequence[T],
    skip: int,
    limit: int,
) -> tuple[list[T], int]:
    """Apply pagination to a sequence of items.

    Args:
        items: The full list of items to paginate
        skip: Number of items to skip
        limit: Maximum number of items to return

    Returns:
        A tuple of (paginated_items, total_count)

    Example:
        items, total = paginate(all_quotes, pagination.skip, pagination.limit)
        return PaginatedResponse(data=items, total=total, skip=skip, limit=limit)
    """
    total = len(items)
    paginated = list(items)[skip : skip + limit]
    return paginated, total
