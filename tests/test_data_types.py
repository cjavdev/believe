"""Tests for the data types demo router."""

import pytest


@pytest.mark.asyncio
async def test_list_data_types(client):
    """Test listing all data type showcase entries."""
    response = await client.get("/data-types")
    assert response.status_code == 200
    result = response.json()
    # Check pagination structure
    assert "data" in result
    assert "total" in result
    assert "skip" in result
    assert "limit" in result
    data = result["data"]
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_create_data_types_entry(client):
    """Test creating a data types showcase entry."""
    entry = {
        "name": "Test Entry",
        "description": "A test entry for data types",
        "count": 10,
        "score": 75,
        "rating": 4.5,
        "percentage": 50.5,
        "price": "19.99",
        "is_active": True,
        "is_public": True,
        "event_date": "2024-06-15",
        "start_time": "10:00:00",
        "created_at": "2024-06-15T10:00:00Z",
        "duration_seconds": 1800,
        "reference_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "contact": {
            "email": "test@example.com",
            "website": "https://example.com",
            "phone": "+1234567890",
        },
        "priority": "high",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
        },
        "budget": {
            "amount": "500.00",
            "currency": "USD",
        },
        "tags": ["test", "demo"],
        "scores_history": [80, 85, 90],
        "measurements": [1.1, 2.2, 3.3],
        "time_slots": [
            {"start_time": "09:00:00", "end_time": "12:00:00"},
        ],
        "metadata": {"key": "value"},
        "string_map": {"en": "Test"},
    }
    response = await client.post("/data-types", json=entry)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Entry"
    assert data["rating"] == 4.5
    assert data["price"] == "19.99"
    assert "id" in data


@pytest.mark.asyncio
async def test_date_types_demo(client):
    """Test date/time types demo endpoint."""
    response = await client.get("/data-types/types/dates")
    assert response.status_code == 200
    data = response.json()
    assert "date_only" in data
    assert "time_only" in data
    assert "datetime_utc" in data
    assert "datetime_iso" in data


@pytest.mark.asyncio
async def test_number_types_demo(client):
    """Test numeric types demo endpoint."""
    response = await client.get("/data-types/types/numbers")
    assert response.status_code == 200
    data = response.json()
    assert data["integer"] == 42
    assert data["float"] == 3.14159
    assert data["decimal_price"] == "29.99"
    assert "negative_integer" in data
    assert "large_integer" in data


@pytest.mark.asyncio
async def test_string_types_demo(client):
    """Test string types demo endpoint."""
    response = await client.get("/data-types/types/strings")
    assert response.status_code == 200
    data = response.json()
    assert "simple" in data
    assert "unicode" in data
    assert "email" in data
    assert "url" in data
    assert "uuid" in data
    assert "base64" in data


@pytest.mark.asyncio
async def test_collection_types_demo(client):
    """Test collection types demo endpoint."""
    response = await client.get("/data-types/types/collections")
    assert response.status_code == 200
    data = response.json()
    assert "string_array" in data
    assert "integer_array" in data
    assert "nested_array" in data
    assert "object" in data
    assert "nested_object" in data
    assert "string_map" in data


@pytest.mark.asyncio
async def test_special_types_demo(client):
    """Test special types demo endpoint."""
    response = await client.get("/data-types/types/special")
    assert response.status_code == 200
    data = response.json()
    assert data["boolean_true"] is True
    assert data["boolean_false"] is False
    assert data["null_value"] is None
    assert "enum_priority" in data
    assert "enum_currency" in data


@pytest.mark.asyncio
async def test_file_upload(client):
    """Test file upload endpoint."""
    # Create a simple test file content
    file_content = b"Hello, this is a test file!"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = await client.post("/data-types/files/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["metadata"]["filename"] == "test.txt"
    assert data["metadata"]["content_type"] == "text/plain"
    assert data["metadata"]["size_bytes"] == len(file_content)
    assert "checksum_sha256" in data["metadata"]


@pytest.mark.asyncio
async def test_file_upload_and_download(client):
    """Test file upload and download round-trip."""
    # Upload file
    file_content = b"Test content for download"
    files = {"file": ("download_test.txt", file_content, "text/plain")}
    upload_response = await client.post("/data-types/files/upload", files=files)
    assert upload_response.status_code == 201
    file_id = upload_response.json()["id"]

    # Download file
    download_response = await client.get(f"/data-types/files/{file_id}")
    assert download_response.status_code == 200
    assert download_response.content == file_content


@pytest.mark.asyncio
async def test_binary_data(client):
    """Test binary data (base64) endpoint."""
    import base64

    original_data = b"Binary test data"
    encoded_data = base64.b64encode(original_data).decode()

    request_body = {
        "name": "test_binary",
        "data_base64": encoded_data,
        "content_type": "application/octet-stream",
    }
    response = await client.post("/data-types/binary", json=request_body)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_binary"
    assert data["size_bytes"] == len(original_data)
    assert "checksum_sha256" in data


@pytest.mark.asyncio
async def test_content_collection(client):
    """Test content collection (union types) endpoint."""
    response = await client.post(
        "/data-types/content-collections?title=Test%20Collection"
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Collection"
    assert "items" in data
    # Check we have mixed content types
    item_types = [item["type"] for item in data["items"]]
    assert "text" in item_types
    assert "image" in item_types
    assert "link" in item_types


@pytest.mark.asyncio
async def test_get_nonexistent_entry(client):
    """Test getting a non-existent data types entry."""
    response = await client.get(
        "/data-types/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_data_types_entry(client):
    """Test updating a data types entry."""
    # First get an entry
    list_response = await client.get("/data-types")
    entries = list_response.json()["data"]
    if entries:
        entry_id = entries[0]["id"]
        # Update it
        update_response = await client.patch(
            f"/data-types/{entry_id}",
            json={"name": "Updated Name", "score": 99},
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Name"
        assert data["score"] == 99
        assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_delete_file_not_found(client):
    """Test deleting a non-existent file."""
    response = await client.delete(
        "/data-types/files/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
