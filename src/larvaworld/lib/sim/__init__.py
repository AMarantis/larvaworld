"""
Launchers of the diverse available simulation modes
"""

__displayname__ = "Simulation"

__all__ = [
    "ABModel", "BaseRun", "ReplayRun",
    "ExpRun", "Exec",
    "BatchRun", "OptimizationOps",
    "GAlauncher", "EvalRun",
]

_NAME_TO_MODULE = {
    "ABModel": "larvaworld.lib.sim.ABM_model",
    "BaseRun": "larvaworld.lib.sim.base_run",
    "ReplayRun": "larvaworld.lib.sim.dataset_replay",
    "ExpRun": "larvaworld.lib.sim.single_run",
    "Exec": "larvaworld.lib.sim.subprocess_run",
    "BatchRun": "larvaworld.lib.sim.batch_run",
    "OptimizationOps": "larvaworld.lib.sim.batch_run",
    "GAlauncher": "larvaworld.lib.sim.genetic_algorithm",
    "EvalRun": "larvaworld.lib.sim.model_evaluation",
}

def __getattr__(name):
    module_path = _NAME_TO_MODULE.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    mod = import_module(module_path)
    obj = getattr(mod, name)
    globals()[name] = obj
    return obj

def __dir__():
    return sorted(list(globals().keys()) + __all__)
