# Changelog

## Unreleased

- Relaxed version constraints for scientific dependencies in `pyproject.toml` to allow newer minor/patch releases within the same major version, while ensuring availability of wheels on Python 3.12. Changed from strict pinning (e.g., `"1.24.*"`) to range constraints (e.g., `">=1.24,<2.0"`). Affected packages:
  - `geopandas`: `"0.13.*"` → `">=0.13,<1.0"`
  - `holoviews`: `"1.17.*"` → `">=1.17,<2.0"`
  - `hvplot`: `"0.10.*"` → `">=0.10,<1.0"`
  - `imageio`: `"2.35.*"` → `">=2.35,<3.0"` (with `[ffmpeg]` extra for video export)
  - `matplotlib`: `"3.7.*"` → `">=3.7,<4.0"`
  - `movingpandas`: `"0.19.*"` → `">=0.19,<1.0"`
  - `numpy`: `"1.24.*"` → `">=1.24,<2.0"`
  - `panel`: `"1.2.*"` → `">=1.2,<2.0"` (pinned to fix `larvaworld-app` hang on Python 3.12/3.13)
  - `pandas`: `"2.0.*"` → `">=2.0,<3.0"`
  - `pint`: `"0.21.*"` → `">=0.21,<1.0"`
  - `pint_pandas`: `"0.3"` → `">=0.3,<1.0"`
  - `pygame`: `"2.6.*"` → `">=2.6,<3.0"`
  - `pypdf`: `"5.0.*"` → `">=5.0,<6.0"`
  - `seaborn`: `"0.13.*"` → `">=0.13,<1.0"`
  - `scikit-learn`: `"1.3.*"` → `">=1.3,<2.0"`
  - `scipy`: `"1.9.*"` → `">=1.9,<2.0"`
  - `shapely`: `"2.0.*"` → `">=2.0,<3.0"`
  - `typing-extensions`: `"4.12.*"` → `">=4.12,<5.0"`
  - `param` remains pinned to `"2.1.*"` for backward compatibility with existing parameter definitions.
- Added Python 3.13 support by updating Python version constraint from `">=3.10,<3.13"` to `">=3.10,<3.14"`.
- Added `SALib <1.5.2` constraint to ensure compatibility with numpy 1.x.
- Pinned `panel` to `"1.2.*"` (from `">=1.2,<2.0"`) to fix `larvaworld-app` hang issue on Python 3.12 and 3.13. Panel 1.8.x has compatibility issues with `pn.serve()` that prevent the web app from starting.
- Fixed collision handling bugs: introduced `_has_larva_collision()` helper in `LarvaSim` and normalized shapes to Shapely geometries in `ExpRun.get_larva_bodies()`.
- Added UI feedback for larva overlap toggle (keyboard shortcut `Y`).
- Added simulation storage directory feedback via `vprint` messages (verbosity level 2) for all simulation types (Exp, Batch, GA, Eval).
- Updated tests to use `reg.default_refID` instead of hardcoded dataset IDs for better flexibility.
- Removed deprecation warning infrastructure (`LARVAWORLD_STRICT_DEPRECATIONS` checks) from 25 files (~288 lines removed).
- Updated documentation: added publications page, improved contributing.md with commit message examples, removed outdated badges from README, updated Python version support across all docs.
- Minor fixes: timer baseline alignment, module-level constant docstrings for autoapi, end-of-file formatting.
- Updated `poetry.lock` to match `pyproject.toml` dependency changes.

## v2.0.1 (2025-11-25)

### Fix

- Improve installation docs, ci workflow, and simulation handling ([`670f66b`](https://github.com/nawrotlab/larvaworld/commit/670f66b74c37cfd5a20d3e29534b7aef88302592))
- Improve simulation window handling and pause feedback ([`304ce80`](https://github.com/nawrotlab/larvaworld/commit/304ce807e3ae5f202653b3ce24ce9568e9f15286))
- Properly detect linting errors vs formatting changes ([`679821c`](https://github.com/nawrotlab/larvaworld/commit/679821cfd268c9732a276d05cce04661750ee53f))
- Correct has_changes variable check in lint job ([`484bb00`](https://github.com/nawrotlab/larvaworld/commit/484bb0041fcb941fbaaaf800854c4ef1fefb8b0f))
- Broken documentation references to tutorials/index ([`6b3a41c`](https://github.com/nawrotlab/larvaworld/commit/6b3a41c6f815f7d46c9f5eb1b647771256ae1c9e))
- Simulation termination and visualization documentation ([`6b56f91`](https://github.com/nawrotlab/larvaworld/commit/6b56f91a3f316739e828ad5bb91f0eae6c75db38))

### Documentation

- Expand video examples ([`f13ee97`](https://github.com/nawrotlab/larvaworld/commit/f13ee97575a02f93dd4bf4ad2a7c6ca7fe18ba04))
- Hide tutorials toctree from main page, keep in sidebar ([`c9537ec`](https://github.com/nawrotlab/larvaworld/commit/c9537ec6cd622c694243b0aac925e1a3f569ac73))
- Remove :hidden: from tutorials toctree to show in sidebar ([`a473fdd`](https://github.com/nawrotlab/larvaworld/commit/a473fddb298aae15fcbdd827173e8bf4a28e98df))
- Restore tutorial subsections structure with .rst files ([`8aad1a5`](https://github.com/nawrotlab/larvaworld/commit/8aad1a5bb3b532b50d66ce8709fb51bcf564f9c3))
- Create tutorial subsections with index files (configuration, simulation, data, development) ([`a27d098`](https://github.com/nawrotlab/larvaworld/commit/a27d098dde933ec959e0ccabb945d4f2bdfade10))
- Organize tutorials into subsections (configuration, simulation, data, development) ([`6f60d95`](https://github.com/nawrotlab/larvaworld/commit/6f60d958b302c50ffdbae3dbae361cfba0819338))
- Remove duplicate myst_parser extension (included in myst_nb) ([`c2e63d1`](https://github.com/nawrotlab/larvaworld/commit/c2e63d1c1380d15a74e5e31c5c6278f2952b3de5))
- Switch from nbsphinx to myst_nb and add pygments style ([`76ffea2`](https://github.com/nawrotlab/larvaworld/commit/76ffea2de6bfd9046f14b21592986d2797bc0f40))
- Switch to sphinx_rtd_theme and rename autoapi entry ([`e92eac0`](https://github.com/nawrotlab/larvaworld/commit/e92eac0062d325426c5daf141e570a6f7e1caf3c))
- Fix sidebar navigation and use default furo theme ([`6597030`](https://github.com/nawrotlab/larvaworld/commit/659703028960614eb45c47d6c06401c97bc38767))
- Reorganize concepts and index ([`4d6a563`](https://github.com/nawrotlab/larvaworld/commit/4d6a56347080b4afed96ec63d64b87491f4ce016))

### Refactor

- Documentation improvements, ci enhancements, and test marker refactoring ([`838b554`](https://github.com/nawrotlab/larvaworld/commit/838b55431584b9aa9c0ba18ce89a87fe79c09b0d))
- Rename pytest marker from 'slow' to 'heavy' ([`333de3c`](https://github.com/nawrotlab/larvaworld/commit/333de3cfd726c6edfb05c67f494e53baacc673e9))

## v1.0.0 (2025-11-12)

### Breaking

- Complete package modernization (phases 1-4) (#3) ([`188bfb7`](https://github.com/AMarantis/larvaworld/commit/188bfb7643c3c33fb62d8af52ba033473c5984a5))

### Feature

- Start semver at 1.0.0 (#35) ([`f532b66`](https://github.com/AMarantis/larvaworld/commit/f532b6653ad0a5bba8111194c99ec87f2e7e3efe))
- Add venv install test to github action ([`edd69f5`](https://github.com/AMarantis/larvaworld/commit/edd69f503754dda864236356cda3cc7c4cc06b49))
- Add venv install test to github action ([`09f218f`](https://github.com/AMarantis/larvaworld/commit/09f218f14b4b9fc65e1fe152604facc7a81099bf))
- Add example code for remote brian interface and tutorial notebook ([`00e0b0c`](https://github.com/AMarantis/larvaworld/commit/00e0b0ca88c0a21f099e048c30dd0a3feeec15bc))
- Add tutorial notebooks on library interface and custom modules ([`ec1dbd5`](https://github.com/AMarantis/larvaworld/commit/ec1dbd5cd2c41af9f9fea01dac2ca76dd9dfccca))

### Fix

- Semantic versioning ([`a224d62`](https://github.com/AMarantis/larvaworld/commit/a224d62c2792ec195a8c95885b0f82f10d9f0c4e))
- Semantic versioning ([`a6c3929`](https://github.com/AMarantis/larvaworld/commit/a6c3929f2a588fdee0e8ba90f8ff0537f0ba37b4))
- Run venv test only on linux ([`cb2bcee`](https://github.com/AMarantis/larvaworld/commit/cb2bcee20be0205db39d88bb0b8750d3c9e2fed8))
- Remove importlib dependency ([`a065475`](https://github.com/AMarantis/larvaworld/commit/a06547572c2fac881e16172519c1b6ac2339e1a2))
- Add missing docopts dependency ([`248611c`](https://github.com/AMarantis/larvaworld/commit/248611cc3fc478cabd93d0059c474ef96741645b))
- Use master instead of main branch ([`a1d054b`](https://github.com/AMarantis/larvaworld/commit/a1d054ba24ea5c1c8dab525a6b45be3678cbde47))
