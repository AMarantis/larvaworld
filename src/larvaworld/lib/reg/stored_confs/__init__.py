"""
This module sets up and stores configuration parameter sets for diverse elements of the platform
 including experiments, environments, larva models and tracker-specific data formats
 used to import experimental datasets from different labs.
"""

from . import data_conf, essay_conf, sim_conf

__displayname__ = "Available configurations"

def __getattr__(name):
    """Lazy import for Model_dict to avoid deep imports."""
    if name == "Model_dict":
        from importlib import import_module
        return getattr(import_module("larvaworld.lib.model.modules.module_modes"), "Model_dict")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
