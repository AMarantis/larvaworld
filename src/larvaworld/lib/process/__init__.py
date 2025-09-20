"""
This module contains all methods and classes relevant in data management,analysis, storage
 as well as the methods supporting the import of experimental tracker datasets
"""

__displayname__ = "Data management"

# Public API: expose core dataset classes, evaluation helpers, and lab importers.
__all__ = [
    # Datasets
    "ParamLarvaDataset", "BaseLarvaDataset", "LarvaDataset", "LarvaDatasetCollection",
    # Evaluation
    "Evaluation", "DataEvaluation",
    # Lab-specific importers
    "import_Schleyer", "import_Jovanic", "import_Berni", "import_Arguello",
    "lab_specific_import_functions",
]

_NAME_TO_MODULE = {
    # Datasets
    "ParamLarvaDataset": "larvaworld.lib.process.dataset",
    "BaseLarvaDataset": "larvaworld.lib.process.dataset",
    "LarvaDataset": "larvaworld.lib.process.dataset",
    "LarvaDatasetCollection": "larvaworld.lib.process.dataset",
    # Evaluation
    "Evaluation": "larvaworld.lib.process.evaluation",
    "DataEvaluation": "larvaworld.lib.process.evaluation",
    # Lab importers
    "import_Schleyer": "larvaworld.lib.process.importing",
    "import_Jovanic": "larvaworld.lib.process.importing",
    "import_Berni": "larvaworld.lib.process.importing",
    "import_Arguello": "larvaworld.lib.process.importing",
    "lab_specific_import_functions": "larvaworld.lib.process.importing",
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
