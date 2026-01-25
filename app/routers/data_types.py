"""Data Types Demo Router - Showcasing all API data types.

This router demonstrates comprehensive data type support for SDK demos:
- All scalar types (string, int, float, decimal, bool)
- Date/time types (date, time, datetime)
- Identifier types (UUID, URL, email)
- Collection types (arrays, objects, dicts)
- File operations (upload, download, binary)
- Union/polymorphic types
"""

import base64
import hashlib
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.models.data_types import (
    BinaryDataRequest,
    BinaryDataResponse,
    ContentCollection,
    ContactInfo,
    Currency,
    DataTypesShowcase,
    DataTypesShowcaseCreate,
    DataTypesShowcaseUpdate,
    FileMetadata,
    FileType,
    FileUploadResponse,
    GeoLocation,
    ImageContent,
    LinkContent,
    MonetaryAmount,
    Priority,
    TextContent,
    TimeRange,
)
from app.pagination import PaginatedResponse

router = APIRouter(
    prefix="/data-types",
    tags=["Data Types Demo"],
)


# In-memory storage for demo
_data_store: dict[UUID, DataTypesShowcase] = {}
_file_store: dict[UUID, tuple[bytes, FileMetadata]] = {}
_binary_store: dict[UUID, tuple[bytes, str, str]] = {}


def _get_sample_data() -> DataTypesShowcase:
    """Create sample data with all types populated."""
    return DataTypesShowcase(
        id=uuid4(),
        name="Richmond Training Session",
        description="A special training session focused on team building and belief.",
        count=42,
        score=85,
        rating=4.7,
        percentage=87.5,
        price=Decimal("29.99"),
        is_active=True,
        is_public=False,
        event_date=date(2024, 6, 15),
        start_time=time(14, 30, 0),
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        duration_seconds=3600,
        reference_id=uuid4(),
        contact=ContactInfo(
            email="ted.lasso@afcrichmond.com",
            website="https://www.afcrichmond.com",
            phone="+44 20 7946 0958",
        ),
        priority=Priority.HIGH,
        location=GeoLocation(
            latitude=51.4816,
            longitude=-0.1910,
            altitude_meters=15.5,
        ),
        budget=MonetaryAmount(
            amount=Decimal("1299.99"),
            currency=Currency.GBP,
        ),
        tags=["training", "team-building", "believe"],
        scores_history=[78, 82, 91, 85],
        measurements=[1.5, 2.3, 4.1, 3.7],
        time_slots=[
            TimeRange(start_time=time(9, 0), end_time=time(12, 0)),
            TimeRange(start_time=time(14, 0), end_time=time(17, 0)),
        ],
        metadata={"source": "manual", "version": 2, "approved": True},
        string_map={"en": "Believe", "es": "Creer", "fr": "Croire"},
        optional_int=10,
        optional_with_default=5,
    )


def _determine_file_type(content_type: str) -> FileType:
    """Determine file type from content type."""
    if content_type.startswith("image/"):
        return FileType.IMAGE
    elif content_type.startswith("video/"):
        return FileType.VIDEO
    elif content_type.startswith("audio/"):
        return FileType.AUDIO
    elif content_type in [
        "application/pdf",
        "application/msword",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        return FileType.DOCUMENT
    return FileType.OTHER


# =============================================================================
# CRUD OPERATIONS FOR DATA TYPES SHOWCASE
# =============================================================================


@router.get(
    "",
    response_model=PaginatedResponse[DataTypesShowcase],
    summary="List all data type showcase entries",
    description="Retrieve all data type showcase entries with pagination.",
)
async def list_data_types(
    skip: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of items to return"),
) -> PaginatedResponse[DataTypesShowcase]:
    """List all data type showcase entries."""
    # Ensure we have at least one sample entry
    if not _data_store:
        sample = _get_sample_data()
        _data_store[sample.id] = sample

    items = list(_data_store.values())
    total = len(items)
    paginated_items = items[skip : skip + limit]

    return PaginatedResponse[DataTypesShowcase](
        data=paginated_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=DataTypesShowcase,
    status_code=201,
    summary="Create a data types showcase entry",
    description="Create a new entry demonstrating all data types.",
)
async def create_data_types(data: DataTypesShowcaseCreate) -> DataTypesShowcase:
    """Create a new data types showcase entry."""
    entry = DataTypesShowcase(
        id=uuid4(),
        updated_at=None,
        **data.model_dump(),
    )
    _data_store[entry.id] = entry
    return entry


@router.get(
    "/{entry_id}",
    response_model=DataTypesShowcase,
    summary="Get a data types showcase entry",
    description="Retrieve a specific entry by ID (UUID).",
)
async def get_data_types(entry_id: UUID) -> DataTypesShowcase:
    """Get a data types showcase entry by ID."""
    if entry_id not in _data_store:
        raise HTTPException(status_code=404, detail="Entry not found")
    return _data_store[entry_id]


@router.patch(
    "/{entry_id}",
    response_model=DataTypesShowcase,
    summary="Update a data types showcase entry",
    description="Partially update an entry. Only provided fields will be updated.",
)
async def update_data_types(
    entry_id: UUID,
    data: DataTypesShowcaseUpdate,
) -> DataTypesShowcase:
    """Update a data types showcase entry."""
    if entry_id not in _data_store:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry = _data_store[entry_id]
    update_data = data.model_dump(exclude_unset=True)

    # Create updated entry
    entry_data = entry.model_dump()
    entry_data.update(update_data)
    entry_data["updated_at"] = datetime.now(timezone.utc)

    updated_entry = DataTypesShowcase(**entry_data)
    _data_store[entry_id] = updated_entry
    return updated_entry


@router.delete(
    "/{entry_id}",
    status_code=204,
    summary="Delete a data types showcase entry",
    description="Delete an entry by ID.",
)
async def delete_data_types(entry_id: UUID) -> None:
    """Delete a data types showcase entry."""
    if entry_id not in _data_store:
        raise HTTPException(status_code=404, detail="Entry not found")
    del _data_store[entry_id]


# =============================================================================
# FILE UPLOAD/DOWNLOAD ENDPOINTS
# =============================================================================


@router.post(
    "/files/upload",
    response_model=FileUploadResponse,
    status_code=201,
    summary="Upload a file",
    description="Upload a file and receive metadata. Demonstrates file upload handling.",
)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """Upload a file and store it in memory."""
    # Read file content
    content = await file.read()
    file_id = uuid4()

    # Calculate checksum
    checksum = hashlib.sha256(content).hexdigest()

    # Determine file type
    content_type = file.content_type or "application/octet-stream"
    file_type = _determine_file_type(content_type)

    # Create metadata
    metadata = FileMetadata(
        filename=file.filename or "unknown",
        content_type=content_type,
        size_bytes=len(content),
        file_type=file_type,
        checksum_sha256=checksum,
    )

    # Store file
    _file_store[file_id] = (content, metadata)

    return FileUploadResponse(
        id=file_id,
        metadata=metadata,
        upload_url=None,  # In a real app, this would be a CDN URL
        uploaded_at=datetime.now(timezone.utc),
        expires_at=None,
    )


@router.get(
    "/files/{file_id}",
    summary="Download a file",
    description="Download a previously uploaded file by ID.",
    responses={
        200: {
            "description": "File content",
            "content": {"application/octet-stream": {}},
        }
    },
)
async def download_file(file_id: UUID) -> Response:
    """Download a file by ID."""
    if file_id not in _file_store:
        raise HTTPException(status_code=404, detail="File not found")

    content, metadata = _file_store[file_id]

    return Response(
        content=content,
        media_type=metadata.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{metadata.filename}"',
            "Content-Length": str(metadata.size_bytes),
            "X-Checksum-SHA256": metadata.checksum_sha256 or "",
        },
    )


@router.get(
    "/files/{file_id}/metadata",
    response_model=FileUploadResponse,
    summary="Get file metadata",
    description="Get metadata for an uploaded file without downloading it.",
)
async def get_file_metadata(file_id: UUID) -> FileUploadResponse:
    """Get file metadata without downloading."""
    if file_id not in _file_store:
        raise HTTPException(status_code=404, detail="File not found")

    _, metadata = _file_store[file_id]

    return FileUploadResponse(
        id=file_id,
        metadata=metadata,
        upload_url=None,
        uploaded_at=datetime.now(timezone.utc),
        expires_at=None,
    )


@router.delete(
    "/files/{file_id}",
    status_code=204,
    summary="Delete a file",
    description="Delete an uploaded file.",
)
async def delete_file(file_id: UUID) -> None:
    """Delete an uploaded file."""
    if file_id not in _file_store:
        raise HTTPException(status_code=404, detail="File not found")
    del _file_store[file_id]


# =============================================================================
# BINARY DATA ENDPOINTS (Base64)
# =============================================================================


@router.post(
    "/binary",
    response_model=BinaryDataResponse,
    status_code=201,
    summary="Store binary data (base64)",
    description="Accept base64-encoded binary data. Useful for smaller payloads in JSON.",
)
async def store_binary(data: BinaryDataRequest) -> BinaryDataResponse:
    """Store base64-encoded binary data."""
    try:
        decoded = base64.b64decode(data.data_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    binary_id = uuid4()
    checksum = hashlib.sha256(decoded).hexdigest()

    _binary_store[binary_id] = (decoded, data.name, data.content_type)

    return BinaryDataResponse(
        id=binary_id,
        name=data.name,
        size_bytes=len(decoded),
        content_type=data.content_type,
        checksum_sha256=checksum,
        created_at=datetime.now(timezone.utc),
    )


@router.get(
    "/binary/{binary_id}",
    summary="Retrieve binary data",
    description="Retrieve stored binary data.",
    responses={
        200: {
            "description": "Binary content",
            "content": {"application/octet-stream": {}},
        }
    },
)
async def get_binary(binary_id: UUID) -> Response:
    """Retrieve binary data by ID."""
    if binary_id not in _binary_store:
        raise HTTPException(status_code=404, detail="Binary data not found")

    content, name, content_type = _binary_store[binary_id]

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
        },
    )


# =============================================================================
# UNION/POLYMORPHIC TYPE ENDPOINTS
# =============================================================================


@router.post(
    "/content-collections",
    response_model=ContentCollection,
    status_code=201,
    summary="Create a content collection",
    description="Create a collection with mixed content types (text, images, links). "
    "Demonstrates union/polymorphic types.",
)
async def create_content_collection(
    title: str = Query(..., description="Collection title"),
) -> ContentCollection:
    """Create a sample content collection with mixed types."""
    return ContentCollection(
        id=uuid4(),
        title=title,
        items=[
            TextContent(
                text="Believe in yourself! You're stronger than you think.",
            ),
            ImageContent(
                url="https://example.com/believe-sign.jpg",
                alt_text="The famous BELIEVE sign",
                width=800,
                height=600,
            ),
            LinkContent(
                url="https://www.afcrichmond.com",
                title="AFC Richmond Official Site",
                description="The official website of AFC Richmond Football Club.",
            ),
            TextContent(
                text="Be curious, not judgmental. - Ted Lasso",
            ),
        ],
        created_at=datetime.now(timezone.utc),
    )


# =============================================================================
# SPECIALIZED TYPE ENDPOINTS
# =============================================================================


@router.get(
    "/types/dates",
    summary="Date and time types demo",
    description="Returns examples of all date/time types: date, time, datetime.",
)
async def date_types_demo() -> dict:
    """Demonstrate date/time types."""
    now = datetime.now(timezone.utc)
    return {
        "date_only": now.date(),
        "time_only": now.time(),
        "datetime_utc": now,
        "datetime_iso": now.isoformat(),
        "date_formatted": now.strftime("%Y-%m-%d"),
        "time_formatted": now.strftime("%H:%M:%S"),
    }


@router.get(
    "/types/numbers",
    summary="Numeric types demo",
    description="Returns examples of numeric types: int, float, decimal.",
)
async def number_types_demo() -> dict:
    """Demonstrate numeric types."""
    return {
        "integer": 42,
        "negative_integer": -10,
        "float": 3.14159,
        "negative_float": -2.718,
        "decimal_price": "29.99",
        "decimal_percentage": "87.50",
        "large_integer": 9007199254740991,
        "small_float": 0.0001,
    }


@router.get(
    "/types/strings",
    summary="String types demo",
    description="Returns examples of string types and variations.",
)
async def string_types_demo() -> dict:
    """Demonstrate string types."""
    return {
        "simple": "Hello, World!",
        "unicode": "Café résumé naïve 日本語 🎉",
        "multiline": "Line 1\nLine 2\nLine 3",
        "empty": "",
        "email": "ted.lasso@afcrichmond.com",
        "url": "https://www.afcrichmond.com/believe",
        "uuid": str(uuid4()),
        "base64": base64.b64encode(b"Hello World").decode(),
    }


@router.get(
    "/types/collections",
    summary="Collection types demo",
    description="Returns examples of arrays, objects, and maps.",
)
async def collection_types_demo() -> dict:
    """Demonstrate collection types."""
    return {
        "string_array": ["believe", "curious", "goldfish"],
        "integer_array": [1, 2, 3, 4, 5],
        "float_array": [1.1, 2.2, 3.3],
        "mixed_array": ["text", 42, 3.14, True, None],
        "nested_array": [[1, 2], [3, 4], [5, 6]],
        "object": {
            "name": "Ted Lasso",
            "role": "coach",
            "team": "AFC Richmond",
        },
        "nested_object": {
            "character": {
                "name": "Ted",
                "stats": {"optimism": 95, "empathy": 100},
            }
        },
        "string_map": {"en": "Hello", "es": "Hola", "fr": "Bonjour"},
        "empty_array": [],
        "empty_object": {},
    }


@router.get(
    "/types/special",
    summary="Special types demo",
    description="Returns examples of special types: boolean, null, enums.",
)
async def special_types_demo() -> dict:
    """Demonstrate special types."""
    return {
        "boolean_true": True,
        "boolean_false": False,
        "null_value": None,
        "optional_present": "I exist!",
        "optional_missing": None,
        "enum_priority": Priority.HIGH.value,
        "enum_currency": Currency.GBP.value,
        "enum_file_type": FileType.IMAGE.value,
        "all_priorities": [p.value for p in Priority],
        "all_currencies": [c.value for c in Currency],
    }
