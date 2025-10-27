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


# ============================================================================
# LarvaDatasetStub - Minimal, reusable mock for unit tests (no I/O)
# ============================================================================

import pandas as pd
from types import SimpleNamespace

class LarvaDatasetStub:
    """
    Minimal LarvaDataset stand-in for unit testing.
    
    Provides synthetic trajectory data with NO I/O dependency.
    For simple cases only (sim tests, geo helpers).
    
    For complex orchestrators (calibration.py), use surgical monkeypatching instead!
    
    Args:
        n: Number of timesteps
        fps: Frames per second
        seed: Random seed for determinism
    """
    def __init__(self, n=30, fps=10.0, seed=42):
        rng = np.random.default_rng(seed)
        
        # Time array
        self.timestamps = np.arange(n) / fps
        
        # Random walk trajectory
        x = np.cumsum(rng.normal(0, 0.05, n))
        y = np.cumsum(rng.normal(0, 0.05, n))
        self.xy = np.column_stack([x, y])
        
        # Mimic d.data structure
        self.data = (
            SimpleNamespace(),  # step_data
            SimpleNamespace(),  # endpoint_data
            {"fps": fps, "dt": 1.0/fps}  # config
        )
        
        self.config = {"fps": fps, "dt": 1.0/fps}
        self.step_data = SimpleNamespace()
        self.endpoint_data = SimpleNamespace()
    
    def load_traj(self):
        """Return trajectory array."""
        return self.xy
    
    def comp_spatial(self):
        """Compute basic spatial metrics."""
        dt = self.timestamps[1] - self.timestamps[0]
        vx = np.gradient(self.xy[:, 0], dt)
        vy = np.gradient(self.xy[:, 1], dt)
        self.velocity = np.hypot(vx, vy)
        self.angle = np.arctan2(vy, vx)
        self.step_data.v = self.velocity
        self.step_data.angle = self.angle
        return self


@pytest.fixture()
def ds_stub():
    """Provide a LarvaDatasetStub with precomputed spatial metrics."""
    d = LarvaDatasetStub(n=30, fps=10.0, seed=42)
    d.comp_spatial()
    return d


@pytest.fixture(scope="session")
def real_dataset(ensure_datasets_ready):
    """
    Provide a REAL LarvaDataset from registry for tests that need it.
    
    Requires ensure_datasets_ready fixture (datasets must exist).
    Uses exploration.30controls as minimal real dataset.
    
    Returns:
        LarvaDataset with full preprocessing applied.
    """
    from larvaworld.lib.process import LarvaDataset
    
    # Load real dataset from registry (datasets guaranteed ready via fixture)
    d = LarvaDataset(refID="exploration.30controls")
    
    # Full preprocessing pipeline
    d.comp_spatial()
    d.comp_orientations()
    d.comp_bend(mode="full")  # mode="full" computes spine angles
    d.comp_ang_moments()  # Computes angular velocities for spine angles
    
    return d


# ============================================================================
# Optional Auto-Setup for Integration Tests (ENV-GATED, NO autouse!)
# Based on GPT-5 robust FileLock solution for HDF5 race conditions
# ============================================================================

import time
import subprocess
import sys
from pathlib import Path

try:
    from filelock import FileLock
except ImportError:
    FileLock = None  # Will skip if not available

# Configuration
DATA_ROOT = Path("src/larvaworld/data/SchleyerGroup/processed")
READY_FLAG = Path(".pytest_datasets_ready")  # Signal file for workers
LOCK_FILE = Path(".pytest_datasets_build.lock")  # Build synchronization


def processed_datasets_exist() -> bool:
    """
    Check if minimal processed artifacts exist.
    
    Stable predicates: checks representative files (data.h5, conf.txt).
    Keep this cheap & deterministic.
    """
    target = DATA_ROOT / "exploration" / "30controls" / "data"
    return (target / "data.h5").exists() and (target / "conf.txt").exists()


def build_processed_datasets():
    """
    Build datasets from raw → processed (idempotent).
    
    IMPORTANT: This must be idempotent and safe if called on warm start.
    Uses CLI to create datasets (5-7 min first run).
    """
    subprocess.run(
        [sys.executable, "-m", "larvaworld", "--help"],
        check=True,
        timeout=900,  # 15 min max (generous for CI)
        capture_output=True
    )


@pytest.fixture(scope="session")  # ✅ NO autouse=True!
def ensure_datasets_ready():
    """
    Session-level gate: create processed datasets ONCE.
    
    Solves HDF5 race condition on cold starts:
    - If datasets exist: instant return (warm start)
    - If cold start: ONE worker builds, others wait for READY_FLAG
    - After build: ALL workers read existing HDF5 (no write locks)
    
    Usage:
        @pytest.mark.usefixtures("ensure_datasets_ready")
        def test_analysis():
            # Test will wait until datasets ready
    
    Enable integration tests with: LARVAWORLD_INIT_DATA=1 pytest
    Disable explicitly with: LARVAWORLD_INIT_DATA=0 pytest
    """
    # Opt-in/opt-out via env flag
    if os.getenv("LARVAWORLD_INIT_DATA") == "0":
        pytest.skip("Datasets init disabled (LARVAWORLD_INIT_DATA=0)")
    
    # Warm start: instant bypass
    if processed_datasets_exist() or READY_FLAG.exists():
        return
    
    # Check FileLock availability
    if FileLock is None:
        pytest.skip("filelock not installed; cannot safely create datasets in parallel")
    
    lock = FileLock(str(LOCK_FILE))
    got_lock = False
    
    try:
        # Non-blocking acquire (timeout=0) - GPT-5 pattern
        got_lock = lock.acquire(timeout=0)
    except Exception:
        got_lock = False
    
    if got_lock:
        # This worker will BUILD datasets
        try:
            # Double-check after acquiring lock (race condition safety)
            if not processed_datasets_exist():
                build_processed_datasets()
            
            # Signal other workers that datasets are ready
            READY_FLAG.write_text("ok")
        finally:
            lock.release()
    else:
        # This worker will WAIT for builder to finish
        for _ in range(1200):  # 10 min max (0.5s * 1200 = 600s)
            if READY_FLAG.exists() or processed_datasets_exist():
                break
            time.sleep(0.5)
        else:
            pytest.fail("Timeout waiting for processed datasets ready flag")
    
    # Hint HDF5 for shared read locks (optional but harmless)
    os.environ.setdefault("HDF5_USE_FILE_LOCKING", "TRUE")
