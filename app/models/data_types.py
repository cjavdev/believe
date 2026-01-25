"""Comprehensive data types models for demonstrating full API type coverage.

This module showcases all common API data types for SDK demos:
- Scalar types: string, integer, float, decimal, boolean
- Date/time types: date, time, datetime, duration/timedelta
- Identifier types: UUID, URL, Email
- Collection types: arrays, objects, dictionaries
- Binary types: bytes, file uploads
- Special types: enums, optional, unions
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# =============================================================================
# ENUM TYPES
# =============================================================================


class Priority(str, Enum):
    """Priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class FileType(str, Enum):
    """Supported file types."""

    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class Currency(str, Enum):
    """Supported currencies."""

    USD = "USD"
    GBP = "GBP"
    EUR = "EUR"


# =============================================================================
# NESTED OBJECT TYPES
# =============================================================================


class GeoLocation(BaseModel):
    """Geographic coordinates."""

    latitude: float = Field(
        ge=-90.0,
        le=90.0,
        description="Latitude in degrees",
        json_schema_extra={"example": 51.4816},
    )
    longitude: float = Field(
        ge=-180.0,
        le=180.0,
        description="Longitude in degrees",
        json_schema_extra={"example": -0.1910},
    )
    altitude_meters: Optional[float] = Field(
        default=None,
        description="Altitude in meters above sea level",
        json_schema_extra={"example": 15.5},
    )


class MonetaryAmount(BaseModel):
    """Monetary value with currency."""

    amount: Decimal = Field(
        decimal_places=2,
        description="Amount in the specified currency",
        json_schema_extra={"example": "1299.99"},
    )
    currency: Currency = Field(
        default=Currency.GBP,
        description="Currency code",
    )


class TimeRange(BaseModel):
    """Time range with start and end."""

    start_time: time = Field(
        description="Start time",
        json_schema_extra={"example": "09:00:00"},
    )
    end_time: time = Field(
        description="End time",
        json_schema_extra={"example": "17:30:00"},
    )


class DateRange(BaseModel):
    """Date range with start and end."""

    start_date: date = Field(
        description="Start date",
        json_schema_extra={"example": "2024-01-01"},
    )
    end_date: date = Field(
        description="End date",
        json_schema_extra={"example": "2024-12-31"},
    )


class ContactInfo(BaseModel):
    """Contact information with validated types."""

    email: EmailStr = Field(
        description="Email address",
        json_schema_extra={"example": "ted.lasso@afcrichmond.com"},
    )
    website: Optional[HttpUrl] = Field(
        default=None,
        description="Website URL",
        json_schema_extra={"example": "https://www.afcrichmond.com"},
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number",
        json_schema_extra={"example": "+44 20 7946 0958"},
    )


class FileMetadata(BaseModel):
    """Metadata for uploaded files."""

    filename: str = Field(
        description="Original filename",
        json_schema_extra={"example": "team_photo.jpg"},
    )
    content_type: str = Field(
        description="MIME type",
        json_schema_extra={"example": "image/jpeg"},
    )
    size_bytes: int = Field(
        ge=0,
        description="File size in bytes",
        json_schema_extra={"example": 1048576},
    )
    file_type: FileType = Field(
        description="Categorized file type",
    )
    checksum_sha256: Optional[str] = Field(
        default=None,
        description="SHA-256 checksum of the file",
        json_schema_extra={"example": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    )


# =============================================================================
# COMPREHENSIVE DATA TYPES DEMO MODEL
# =============================================================================


class DataTypesShowcaseBase(BaseModel):
    """Base model demonstrating all common API data types.

    This is designed for SDK demos to show comprehensive type coverage.
    """

    # -------------------------------------------------------------------------
    # STRING TYPES
    # -------------------------------------------------------------------------
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Simple string with length constraints",
        json_schema_extra={"example": "Richmond Training Session"},
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional longer text field",
        json_schema_extra={"example": "A special training session focused on team building."},
    )

    # -------------------------------------------------------------------------
    # NUMERIC TYPES
    # -------------------------------------------------------------------------
    count: int = Field(
        ge=0,
        description="Non-negative integer",
        json_schema_extra={"example": 42},
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Bounded integer (0-100)",
        json_schema_extra={"example": 85},
    )
    rating: float = Field(
        ge=0.0,
        le=5.0,
        description="Floating point rating (0.0-5.0)",
        json_schema_extra={"example": 4.7},
    )
    percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Percentage as float",
        json_schema_extra={"example": 87.5},
    )
    price: Decimal = Field(
        decimal_places=2,
        description="Precise decimal for monetary values",
        json_schema_extra={"example": "29.99"},
    )

    # -------------------------------------------------------------------------
    # BOOLEAN TYPE
    # -------------------------------------------------------------------------
    is_active: bool = Field(
        default=True,
        description="Boolean flag",
        json_schema_extra={"example": True},
    )
    is_public: bool = Field(
        description="Required boolean",
        json_schema_extra={"example": False},
    )

    # -------------------------------------------------------------------------
    # DATE AND TIME TYPES
    # -------------------------------------------------------------------------
    event_date: date = Field(
        description="Date only (no time component)",
        json_schema_extra={"example": "2024-06-15"},
    )
    start_time: time = Field(
        description="Time only (no date component)",
        json_schema_extra={"example": "14:30:00"},
    )
    created_at: datetime = Field(
        description="Full datetime with timezone",
        json_schema_extra={"example": "2024-06-15T14:30:00Z"},
    )
    duration_seconds: int = Field(
        ge=0,
        description="Duration represented as seconds",
        json_schema_extra={"example": 3600},
    )

    # -------------------------------------------------------------------------
    # IDENTIFIER TYPES
    # -------------------------------------------------------------------------
    reference_id: UUID = Field(
        description="UUID identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )

    # -------------------------------------------------------------------------
    # CONTACT/URL TYPES
    # -------------------------------------------------------------------------
    contact: ContactInfo = Field(
        description="Nested contact information with email and URL validation",
    )

    # -------------------------------------------------------------------------
    # ENUM TYPE
    # -------------------------------------------------------------------------
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Enum value for priority",
    )

    # -------------------------------------------------------------------------
    # LOCATION TYPE
    # -------------------------------------------------------------------------
    location: Optional[GeoLocation] = Field(
        default=None,
        description="Geographic coordinates",
    )

    # -------------------------------------------------------------------------
    # MONETARY TYPE
    # -------------------------------------------------------------------------
    budget: Optional[MonetaryAmount] = Field(
        default=None,
        description="Monetary amount with currency",
    )

    # -------------------------------------------------------------------------
    # ARRAY/LIST TYPES
    # -------------------------------------------------------------------------
    tags: list[str] = Field(
        default_factory=list,
        description="Array of strings",
        json_schema_extra={"example": ["training", "team-building", "believe"]},
    )
    scores_history: list[int] = Field(
        default_factory=list,
        description="Array of integers",
        json_schema_extra={"example": [78, 82, 91, 85]},
    )
    measurements: list[float] = Field(
        default_factory=list,
        description="Array of floats",
        json_schema_extra={"example": [1.5, 2.3, 4.1, 3.7]},
    )

    # -------------------------------------------------------------------------
    # NESTED OBJECT TYPES
    # -------------------------------------------------------------------------
    time_slots: list[TimeRange] = Field(
        default_factory=list,
        description="Array of nested objects (time ranges)",
    )

    # -------------------------------------------------------------------------
    # DICTIONARY/MAP TYPE
    # -------------------------------------------------------------------------
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible key-value metadata",
        json_schema_extra={"example": {"source": "manual", "version": 2}},
    )
    string_map: dict[str, str] = Field(
        default_factory=dict,
        description="String to string mapping",
        json_schema_extra={"example": {"en": "Hello", "es": "Hola"}},
    )

    # -------------------------------------------------------------------------
    # OPTIONAL WITH DEFAULTS
    # -------------------------------------------------------------------------
    optional_int: Optional[int] = Field(
        default=None,
        description="Optional integer that can be null",
        json_schema_extra={"example": 10},
    )
    optional_with_default: int = Field(
        default=0,
        description="Integer with default value",
        json_schema_extra={"example": 0},
    )


class DataTypesShowcaseCreate(DataTypesShowcaseBase):
    """Model for creating a new data types showcase entry."""

    pass


class DataTypesShowcaseUpdate(BaseModel):
    """Model for updating a data types showcase entry (all fields optional)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    count: Optional[int] = Field(default=None, ge=0)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    price: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    created_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    reference_id: Optional[UUID] = None
    contact: Optional[ContactInfo] = None
    priority: Optional[Priority] = None
    location: Optional[GeoLocation] = None
    budget: Optional[MonetaryAmount] = None
    tags: Optional[list[str]] = None
    scores_history: Optional[list[int]] = None
    measurements: Optional[list[float]] = None
    time_slots: Optional[list[TimeRange]] = None
    metadata: Optional[dict[str, Any]] = None
    string_map: Optional[dict[str, str]] = None
    optional_int: Optional[int] = None
    optional_with_default: Optional[int] = None


class DataTypesShowcase(DataTypesShowcaseBase):
    """Full data types showcase model with ID and timestamps."""

    id: UUID = Field(
        description="Unique UUID identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp",
        json_schema_extra={"example": "2024-06-16T10:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Richmond Training Session",
                "description": "A special training session focused on team building.",
                "count": 42,
                "score": 85,
                "rating": 4.7,
                "percentage": 87.5,
                "price": "29.99",
                "is_active": True,
                "is_public": False,
                "event_date": "2024-06-15",
                "start_time": "14:30:00",
                "created_at": "2024-06-15T14:30:00Z",
                "updated_at": "2024-06-16T10:00:00Z",
                "duration_seconds": 3600,
                "reference_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact": {
                    "email": "ted.lasso@afcrichmond.com",
                    "website": "https://www.afcrichmond.com",
                    "phone": "+44 20 7946 0958",
                },
                "priority": "high",
                "location": {
                    "latitude": 51.4816,
                    "longitude": -0.1910,
                    "altitude_meters": 15.5,
                },
                "budget": {
                    "amount": "1299.99",
                    "currency": "GBP",
                },
                "tags": ["training", "team-building", "believe"],
                "scores_history": [78, 82, 91, 85],
                "measurements": [1.5, 2.3, 4.1, 3.7],
                "time_slots": [
                    {"start_time": "09:00:00", "end_time": "12:00:00"},
                    {"start_time": "14:00:00", "end_time": "17:00:00"},
                ],
                "metadata": {"source": "manual", "version": 2},
                "string_map": {"en": "Hello", "es": "Hola"},
                "optional_int": 10,
                "optional_with_default": 0,
            }
        }
    }


# =============================================================================
# FILE UPLOAD/DOWNLOAD MODELS
# =============================================================================


class FileUploadResponse(BaseModel):
    """Response model for file uploads."""

    id: UUID = Field(
        description="Unique file identifier",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )
    metadata: FileMetadata = Field(
        description="File metadata",
    )
    upload_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL where the file can be accessed",
        json_schema_extra={"example": "https://storage.afcrichmond.com/files/a1b2c3d4.jpg"},
    )
    uploaded_at: datetime = Field(
        description="Upload timestamp",
        json_schema_extra={"example": "2024-06-15T14:30:00Z"},
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Expiration timestamp if temporary",
        json_schema_extra={"example": "2024-06-22T14:30:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "metadata": {
                    "filename": "team_photo.jpg",
                    "content_type": "image/jpeg",
                    "size_bytes": 1048576,
                    "file_type": "image",
                    "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                },
                "upload_url": "https://storage.afcrichmond.com/files/a1b2c3d4.jpg",
                "uploaded_at": "2024-06-15T14:30:00Z",
                "expires_at": "2024-06-22T14:30:00Z",
            }
        }
    }


class BinaryDataRequest(BaseModel):
    """Request model demonstrating base64 binary data."""

    name: str = Field(
        description="Name for the binary data",
        json_schema_extra={"example": "signature"},
    )
    data_base64: str = Field(
        description="Base64 encoded binary data",
        json_schema_extra={"example": "SGVsbG8gV29ybGQh"},
    )
    content_type: str = Field(
        description="MIME type of the binary data",
        json_schema_extra={"example": "application/octet-stream"},
    )


class BinaryDataResponse(BaseModel):
    """Response model for binary data operations."""

    id: UUID = Field(
        description="Unique identifier",
    )
    name: str = Field(
        description="Name of the binary data",
    )
    size_bytes: int = Field(
        description="Size of decoded binary data",
    )
    content_type: str = Field(
        description="MIME type",
    )
    checksum_sha256: str = Field(
        description="SHA-256 checksum",
    )
    created_at: datetime = Field(
        description="Creation timestamp",
    )


# =============================================================================
# UNION/POLYMORPHIC TYPES
# =============================================================================


class TextContent(BaseModel):
    """Text content type."""

    type: str = Field(default="text", description="Content type discriminator")
    text: str = Field(description="The text content")


class ImageContent(BaseModel):
    """Image content type."""

    type: str = Field(default="image", description="Content type discriminator")
    url: HttpUrl = Field(description="Image URL")
    alt_text: Optional[str] = Field(default=None, description="Alternative text")
    width: Optional[int] = Field(default=None, description="Image width in pixels")
    height: Optional[int] = Field(default=None, description="Image height in pixels")


class LinkContent(BaseModel):
    """Link content type."""

    type: str = Field(default="link", description="Content type discriminator")
    url: HttpUrl = Field(description="Link URL")
    title: str = Field(description="Link title")
    description: Optional[str] = Field(default=None, description="Link description")


# Union type for polymorphic content
ContentItem = Union[TextContent, ImageContent, LinkContent]


class ContentCollection(BaseModel):
    """Collection demonstrating union/polymorphic types."""

    id: UUID = Field(description="Collection identifier")
    title: str = Field(description="Collection title")
    items: list[ContentItem] = Field(
        description="Mixed content items (text, images, or links)",
    )
    created_at: datetime = Field(description="Creation timestamp")
