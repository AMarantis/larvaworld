# Changelog

## v2.1.1 (2026-01-13)

### Documentation

- Update tutorials and visualization guides ([`89af527`](https://github.com/nawrotlab/larvaworld/commit/89af527dae6c6824200f36f1647e0d2b78bf63a8))
- Align docs examples with v2.1.0 api ([`8030d2c`](https://github.com/nawrotlab/larvaworld/commit/8030d2caeaf50d43cf80a21384d0f4ddf0ff7e98))

### Fix

- Sync examples with code and harden eval plots ([`c6b8cc5`](https://github.com/nawrotlab/larvaworld/commit/c6b8cc5adb89985d842e3ead23863de078a43e56))

## v2.1.0 (2025-12-21)

### Documentation

- Add summary of all pr-4c changes to unreleased section ([`c47fcdc`](https://github.com/nawrotlab/larvaworld/commit/c47fcdc7e5eb2b2811f74ac897009b46c366ad7d))
- Add type examples and improve commit message documentation ([`bda3604`](https://github.com/nawrotlab/larvaworld/commit/bda3604831fc411b6a639a25459cbead3cced4ea))
- Remove codecov, poetry, and ruff badges from readme ([`7576a79`](https://github.com/nawrotlab/larvaworld/commit/7576a79e7e3b6f0ade06bdfb5d4ff3d4a16c73ae))
- Fix module-level constant docstrings for autoapi ([`8911126`](https://github.com/nawrotlab/larvaworld/commit/8911126ba30ffb89da0af07d73b33bb5860432f5))
- Update first publication link in publications page ([`6972912`](https://github.com/nawrotlab/larvaworld/commit/6972912dc787e25791a2ace39cce4992bea1438a))
- Add publications page and clarify cli argument order ([`d7cf5c2`](https://github.com/nawrotlab/larvaworld/commit/d7cf5c2a08765d03201ac8bf07f0c3cb8efc8f7b))

### Feature

- Python 3.12 &amp; 3.13 support, collision handling fixes, and code cleanup ([`0842aaf`](https://github.com/nawrotlab/larvaworld/commit/0842aafab994111d3db825243e9704ddfe8acb8d))
- Add storage directory feedback and update python 3.10-3.13 docs ([`e5e975b`](https://github.com/nawrotlab/larvaworld/commit/e5e975bbec53cfa08865f59637543242de9f31f2))

### Build

- Add imageio[ffmpeg] extra and use reg.default_refid ([`45897f1`](https://github.com/nawrotlab/larvaworld/commit/45897f1485bff45b0ee02114f7e71248cc5500d7))

### Fix

- Panel compatibility and add python 3.13 support ([`68cc0d0`](https://github.com/nawrotlab/larvaworld/commit/68cc0d0660d58f4a9b0766c97c0a7b34e9ee1658))
- Python 3.12 support and collision handling fixes ([`e1da5fc`](https://github.com/nawrotlab/larvaworld/commit/e1da5fc9da4dc0cd40e838c1522a4acab636d39a))
- Align timer baseline across time components ([`299eb59`](https://github.com/nawrotlab/larvaworld/commit/299eb59ecd5cf0b2090321ebbe4ca1ca3c0ef3db))

### Refactor

- Remove deprecation warnings and strict import checks ([`2e80eaf`](https://github.com/nawrotlab/larvaworld/commit/2e80eafe9d62a431d947997f4ec1e712c64acc6b))

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
- Rename pytest marker from &#39;slow&#39; to &#39;heavy&#39; ([`333de3c`](https://github.com/nawrotlab/larvaworld/commit/333de3cfd726c6edfb05c67f494e53baacc673e9))

### Build

- Refresh poetry.lock ([`f7c491b`](https://github.com/nawrotlab/larvaworld/commit/f7c491b92806c75b132726d2170970f14e0e7e1e))
- Refresh poetry.lock ([`37e167f`](https://github.com/nawrotlab/larvaworld/commit/37e167fa2ce68f7605a5a525ea14387541daddce))

## v2.0.0 (2025-11-22)

### Style

- Apply pre-commit formatting fixes ([`b2b9071`](https://github.com/nawrotlab/larvaworld/commit/b2b9071e674536b9b08c540733edaf5febd28400))

### Fix

- Update poetry.lock to include sphinxcontrib-mermaid ([`ac9eb33`](https://github.com/nawrotlab/larvaworld/commit/ac9eb33869d3814105e467fbfabdc5d860cd940a))

### Documentation

- Major documentation overhaul with sphinx/readthedocs setup ([`e453018`](https://github.com/nawrotlab/larvaworld/commit/e453018e6576c1806ba7294ea044d5ac1baccb59))
- Update license to mit and fix python version constraints ([`8f136f8`](https://github.com/nawrotlab/larvaworld/commit/8f136f8efb889a4bed72ef6816a3c9f797373851))

### Breaking

- Complete package modernization (phases 1-4) (#3) ([`188bfb7`](https://github.com/nawrotlab/larvaworld/commit/188bfb7643c3c33fb62d8af52ba033473c5984a5))

## v1.0.0 (2025-05-08)

### Feature

- Start semver at 1.0.0 (#35) ([`f532b66`](https://github.com/nawrotlab/larvaworld/commit/f532b6653ad0a5bba8111194c99ec87f2e7e3efe))

## v0.1.0 (2025-05-08)

### Fix

- Semantic versioning ([`a224d62`](https://github.com/nawrotlab/larvaworld/commit/a224d62c2792ec195a8c95885b0f82f10d9f0c4e))
- Semantic versioning ([`a6c3929`](https://github.com/nawrotlab/larvaworld/commit/a6c3929f2a588fdee0e8ba90f8ff0537f0ba37b4))

## v0.1.0-rc.1 (2025-04-22)

### Fix

- Run venv test only on linux ([`cb2bcee`](https://github.com/nawrotlab/larvaworld/commit/cb2bcee20be0205db39d88bb0b8750d3c9e2fed8))
- Remove importlib dependency ([`a065475`](https://github.com/nawrotlab/larvaworld/commit/a06547572c2fac881e16172519c1b6ac2339e1a2))
- Add missing docopts dependency ([`248611c`](https://github.com/nawrotlab/larvaworld/commit/248611cc3fc478cabd93d0059c474ef96741645b))

### Feature

- Add venv install test to github action ([`edd69f5`](https://github.com/nawrotlab/larvaworld/commit/edd69f503754dda864236356cda3cc7c4cc06b49))
- Add venv install test to github action ([`09f218f`](https://github.com/nawrotlab/larvaworld/commit/09f218f14b4b9fc65e1fe152604facc7a81099bf))
- Add example code for remote brian interface and tutorial notebook ([`00e0b0c`](https://github.com/nawrotlab/larvaworld/commit/00e0b0ca88c0a21f099e048c30dd0a3feeec15bc))
- Add tutorial notebooks on library interface and custom modules ([`ec1dbd5`](https://github.com/nawrotlab/larvaworld/commit/ec1dbd5cd2c41af9f9fea01dac2ca76dd9dfccca))

## v0.0.1-rc.1 (2024-11-24)

### Fix

- Use master instead of main branch ([`a1d054b`](https://github.com/nawrotlab/larvaworld/commit/a1d054ba24ea5c1c8dab525a6b45be3678cbde47))
