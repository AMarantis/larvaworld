"""
Integration tests for SchleyerGroup dataset imports.

Requires processed datasets to be available (handled by ensure_datasets_ready).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.mark.requires_data
def test_import_schleyer_datasets(tmp_path, dataset_lock):
    """Import merged and single-dish datasets and ensure processing succeeds."""
    import larvaworld.lib.reg as reg
    import larvaworld.lib.process.dataset

    lab = reg.conf.LabFormat.get("Schleyer")
    base_kwargs = {"group_id": "exploration"}
    proc_folder = tmp_path / "processed"

    merged_kwargs = {
        "parent_dir": "exploration",
        "merged": True,
        "color": "green",
        "max_Nagents": 10,
        "min_duration_in_sec": 30,
        "id": "merged_test",
        "refID": "exploration.merged_test",
        "proc_folder": str(proc_folder),
        "save_dataset": True,
        **base_kwargs,
    }

    single_kwargs = {
        "parent_dir": "exploration/dish02",
        "merged": False,
        "color": "red",
        "min_duration_in_sec": 60,
        "max_Nagents": 10,
        "id": "dish02_test",
        "refID": "exploration.dish02_test",
        "proc_folder": str(proc_folder),
        "save_dataset": True,
        **base_kwargs,
    }

    for kwargs in (merged_kwargs, single_kwargs):
        dataset = lab.import_dataset(**kwargs)
        assert isinstance(dataset, larvaworld.lib.process.dataset.LarvaDataset)

        dataset.process(is_last=False)
        dataset.annotate(is_last=True)

        assert isinstance(dataset.s, pd.DataFrame)

        data_dir = Path(dataset.config.dir) / "data"
        assert data_dir.exists()
        assert (data_dir / "data.h5").exists()
