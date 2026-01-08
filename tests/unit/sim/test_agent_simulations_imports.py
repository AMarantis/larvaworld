"""
Unit tests for larvaworld.lib.sim.agent_simulations.

Keep these tests light: validate imports and basic dataframe/index construction
without running heavy simulations.
"""

import pandas as pd
import pytest

from larvaworld.lib.sim.agent_simulations import sim_model, sim_multi_agents


@pytest.mark.fast
def test_sim_multi_agents_zero_sizes_returns_empty_frames():
    """
    Regression test: sim_multi_agents should not crash due to missing pandas import.
    """
    s, e = sim_multi_agents(Nticks=0, Nids=0, ms=[], group_id="t", dt=0.1)

    assert isinstance(s, pd.DataFrame)
    assert isinstance(e, pd.DataFrame)
    assert s.empty
    assert e.empty


@pytest.mark.fast
def test_sim_model_imports_larvadataset_via_process_facade(tmp_path):
    """
    Regression test: sim_model should import LarvaDataset from larvaworld.lib.process
    (not a non-existent larvaworld.process package).
    """
    d = sim_model(
        mID="explorer",
        Nids=1,
        duration=0.0,
        enrichment=False,
        dir=str(tmp_path),
    )

    # Avoid deep imports in tests: just validate that an object is returned
    # with the expected dataset interface.
    assert hasattr(d, "set_data")
    assert hasattr(d, "config")
