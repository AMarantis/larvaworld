"""
Test configuration and fixtures for Larvaworld tests.

This module provides essential fixtures for:
- Deterministic testing (fixed seeds)
- Headless operation (no GUI windows)
- Temporary directory for test outputs (via tmp_path)
- Registry isolation (via parallel execution with pytest-xdist)
"""

import os
import random
import numpy as np
import pytest


@pytest.fixture(autouse=True, scope="session")
def deterministic():
    """Fix all randomness for reproducible tests"""
    random.seed(42)
    np.random.seed(42)


@pytest.fixture(autouse=True)
def headless_mode(monkeypatch):
    """Force headless backends to prevent GUI windows during tests"""
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Reusable test data directory for session-scoped test data"""
    return tmp_path_factory.mktemp("test_data")


# Registry isolation strategy:
# 
# With parallel execution (pytest -n auto), each worker runs in a separate process 
# with its own registry. This automatically solves the test pollution problem.
#
# Benefits:
# - Each test gets a fresh Python interpreter
# - No shared state between tests
# - Fixes the CLI test failures (test_cli_replay_args, test_cli_evaluation_args)
#
# For debugging individual tests (pytest -n 0 or single test):
# - Tests may experience pollution in serial mode
# - Option A: Run tests in isolation: pytest tests/test_cli.py::test_specific_function
# - Option B: Use --forked flag (requires pytest-forked)
# - Option C: Clean cache between runs: python clean_cache_cold_start.py
#
# Note: We allow tests to use the real registry and data directories.
# Test artifacts should be cleaned up manually if needed (see clean_cache_cold_start.py)
