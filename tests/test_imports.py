"""Test that all modules can be imported successfully.

This catches missing dependencies early in CI before more complex tests run.
"""


def test_app_imports():
    """Test that the main app module can be imported."""
    from app.main import app

    assert app is not None


def test_all_routers_import():
    """Test that all routers can be imported."""
    from app.routers import (
        characters_router,
        episodes_router,
        interactive_router,
        matches_router,
        quotes_router,
        streaming_router,
        team_members_router,
        teams_router,
        webhooks_router,
        websocket_router,
    )

    assert characters_router is not None
    assert episodes_router is not None
    assert interactive_router is not None
    assert matches_router is not None
    assert quotes_router is not None
    assert streaming_router is not None
    assert team_members_router is not None
    assert teams_router is not None
    assert webhooks_router is not None
    assert websocket_router is not None


def test_all_services_import():
    """Test that all services can be imported."""
    from app.services import (
        believe_engine,
        conflict_resolver,
        match_simulation,
        press_conference,
        reframe_service,
        streaming,
        webhook_service,
    )

    assert believe_engine is not None
    assert conflict_resolver is not None
    assert match_simulation is not None
    assert press_conference is not None
    assert reframe_service is not None
    assert streaming is not None
    assert webhook_service is not None


def test_openapi_generation():
    """Test that OpenAPI spec can be generated without errors."""
    from scripts.generate_openapi import generate_openapi_spec

    spec = generate_openapi_spec()

    assert spec is not None
    assert "openapi" in spec
    assert "paths" in spec
    assert "components" in spec
    assert "webhooks" in spec
