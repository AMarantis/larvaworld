"""
Integration tests configuration.

Auto-applies ensure_datasets_ready fixture to all tests in this folder.
This solves the timing issue where imports trigger dataset loading before
the fixture has a chance to run.
"""
import pytest


@pytest.fixture(autouse=True, scope="session")
def _auto_ensure_datasets(ensure_datasets_ready):
    """
    Auto-apply ensure_datasets_ready to all integration tests.
    
    This ensures datasets are created BEFORE any imports that trigger
    registry initialization. Prevents HDF5 race conditions on cold start.
    
    autouse=True is SAFE here because:
    - Only applies to tests/integration/ folder
    - Unit tests in tests/unit/ are NOT affected
    - Session scope = runs once per test session
    """
    pass

