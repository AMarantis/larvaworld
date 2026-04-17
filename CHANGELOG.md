# Changelog

## v1.1.0 (2026-04-17)

### Test

- Normalize import adapter path assertions ([`f318540`](https://github.com/AMarantis/larvaworld/commit/f3185403375ea2049be743dc84a7db08e7d5f03a))

### Fix

- Stabilize portal regressions and arena edge cases ([`2a4f578`](https://github.com/AMarantis/larvaworld/commit/2a4f578131fdaab6399ef686620dc76af3ecbdcf))
- Refine environment builder interactions ([`00efa2f`](https://github.com/AMarantis/larvaworld/commit/00efa2fc52bb8f6c6ece8b5235dc2721674cdbdc))
- Correct quick-start tab layering and active styling ([`55c29ca`](https://github.com/AMarantis/larvaworld/commit/55c29cabcc0782bd676d72f2126ddad3c944c951))
- Restore full-tile click overlay navigation ([`8dcbc54`](https://github.com/AMarantis/larvaworld/commit/8dcbc542928997192420528f41c04ddb56208bc0))
- Sync examples with code and harden eval plots ([`c6b8cc5`](https://github.com/AMarantis/larvaworld/commit/c6b8cc5adb89985d842e3ead23863de078a43e56))
- Panel compatibility and add python 3.13 support ([`68cc0d0`](https://github.com/AMarantis/larvaworld/commit/68cc0d0660d58f4a9b0766c97c0a7b34e9ee1658))
- Python 3.12 support and collision handling fixes ([`e1da5fc`](https://github.com/AMarantis/larvaworld/commit/e1da5fc9da4dc0cd40e838c1522a4acab636d39a))
- Align timer baseline across time components ([`299eb59`](https://github.com/AMarantis/larvaworld/commit/299eb59ecd5cf0b2090321ebbe4ca1ca3c0ef3db))
- Improve installation docs, ci workflow, and simulation handling ([`670f66b`](https://github.com/AMarantis/larvaworld/commit/670f66b74c37cfd5a20d3e29534b7aef88302592))
- Improve simulation window handling and pause feedback ([`304ce80`](https://github.com/AMarantis/larvaworld/commit/304ce807e3ae5f202653b3ce24ce9568e9f15286))
- Properly detect linting errors vs formatting changes ([`679821c`](https://github.com/AMarantis/larvaworld/commit/679821cfd268c9732a276d05cce04661750ee53f))
- Correct has_changes variable check in lint job ([`484bb00`](https://github.com/AMarantis/larvaworld/commit/484bb0041fcb941fbaaaf800854c4ef1fefb8b0f))
- Broken documentation references to tutorials/index ([`6b3a41c`](https://github.com/AMarantis/larvaworld/commit/6b3a41c6f815f7d46c9f5eb1b647771256ae1c9e))
- Simulation termination and visualization documentation ([`6b56f91`](https://github.com/AMarantis/larvaworld/commit/6b56f91a3f316739e828ad5bb91f0eae6c75db38))
- Update poetry.lock to include sphinxcontrib-mermaid ([`ac9eb33`](https://github.com/AMarantis/larvaworld/commit/ac9eb33869d3814105e467fbfabdc5d860cd940a))

### Feature

- Add experimental dataset import app ([`661ae93`](https://github.com/AMarantis/larvaworld/commit/661ae936a69a7518c5f8c7f4b2d900038bcdb51e))
- Add workspace-first dataset adapters ([`d8edf4c`](https://github.com/AMarantis/larvaworld/commit/d8edf4c878db71e93e29514475a25d2062afb519))
- Refine environment builder editor workflows ([`758d1b1`](https://github.com/AMarantis/larvaworld/commit/758d1b1d0d36690b0a4c814ad3dac27a5ed036d3))
- Harden environment builder presets and validation ([`33e4f12`](https://github.com/AMarantis/larvaworld/commit/33e4f124a61fd9755b17ee630715a44ed0639b97))
- Add single experiment workflow ([`3ef872e`](https://github.com/AMarantis/larvaworld/commit/3ef872ec45a811eaf28043ee500944b77bd7846d))
- Expand environment builder workflow ([`f666163`](https://github.com/AMarantis/larvaworld/commit/f66616341c63dbcf39e2ada6272b0a1f65ddb675))
- Enforce workspace-first startup flow ([`612bb1f`](https://github.com/AMarantis/larvaworld/commit/612bb1fd6ad2d3e55f5de9de8b8fbbc41236cd7b))
- Add shared workspace management ([`31569d3`](https://github.com/AMarantis/larvaworld/commit/31569d38eeff343f4aa25957528494beb84467f4))
- Add gui_v2 desktop shell scaffold ([`58499b7`](https://github.com/AMarantis/larvaworld/commit/58499b7d54477a49d05c153cc28050d919a53078))
- Add rotating gif showcase banner on landing ([`4f1a3d5`](https://github.com/AMarantis/larvaworld/commit/4f1a3d5fd3ebfcb317277f2ff62a7656c0b7ce29))
- Add quick-start modes and bootstrap loading flow ([`2527b24`](https://github.com/AMarantis/larvaworld/commit/2527b2402975a25af4c41baa9bc4a24c33a27009))
- Add environment builder app and startup loader ([`6961d3f`](https://github.com/AMarantis/larvaworld/commit/6961d3f9990c52ba24e271989d4ec78cad7816b4))
- Remove demos lane and add persistent footer ([`e725eb9`](https://github.com/AMarantis/larvaworld/commit/e725eb90fa406edd98828bb9a433507a389fcd06))
- Harden notebook launch flow and lane-styled notebook actions ([`e1e3b13`](https://github.com/AMarantis/larvaworld/commit/e1e3b13cea23e42efb10b86d100ba66d856802c6))
- Add tutorial notebook actions with workspace copies ([`52b8c54`](https://github.com/AMarantis/larvaworld/commit/52b8c54107a524601d84d1a85dba8d0f17589f26))
- Add lane accents and stronger hover tint ([`128b49a`](https://github.com/AMarantis/larvaworld/commit/128b49af8600c11328e0c97e6f65cf6f1c39ba93))
- Python 3.12 &amp; 3.13 support, collision handling fixes, and code cleanup ([`0842aaf`](https://github.com/AMarantis/larvaworld/commit/0842aafab994111d3db825243e9704ddfe8acb8d))
- Add storage directory feedback and update python 3.10-3.13 docs ([`e5e975b`](https://github.com/AMarantis/larvaworld/commit/e5e975bbec53cfa08865f59637543242de9f31f2))

### Build

- Refresh poetry lockfile ([`8943cc2`](https://github.com/AMarantis/larvaworld/commit/8943cc2d84d4ea811ae753bc899296247907e126))
- Add imageio[ffmpeg] extra and use reg.default_refid ([`45897f1`](https://github.com/AMarantis/larvaworld/commit/45897f1485bff45b0ee02114f7e71248cc5500d7))
- Refresh poetry.lock ([`f7c491b`](https://github.com/AMarantis/larvaworld/commit/f7c491b92806c75b132726d2170970f14e0e7e1e))
- Refresh poetry.lock ([`37e167f`](https://github.com/AMarantis/larvaworld/commit/37e167fa2ce68f7605a5a525ea14387541daddce))

### Refactor

- Remove demo mode and preview route ([`3506f72`](https://github.com/AMarantis/larvaworld/commit/3506f72f251232778d208e7fea8828ab6e2c79bf))
- Remove deprecation warnings and strict import checks ([`2e80eaf`](https://github.com/AMarantis/larvaworld/commit/2e80eafe9d62a431d947997f4ec1e712c64acc6b))
- Documentation improvements, ci enhancements, and test marker refactoring ([`838b554`](https://github.com/AMarantis/larvaworld/commit/838b55431584b9aa9c0ba18ce89a87fe79c09b0d))
- Rename pytest marker from &#39;slow&#39; to &#39;heavy&#39; ([`333de3c`](https://github.com/AMarantis/larvaworld/commit/333de3cfd726c6edfb05c67f494e53baacc673e9))

### Documentation

- Update installation and optional deps ([`b286045`](https://github.com/AMarantis/larvaworld/commit/b286045a815c4347962779ee686cc2902f6e52bd))
- Update tutorials and visualization guides ([`89af527`](https://github.com/AMarantis/larvaworld/commit/89af527dae6c6824200f36f1647e0d2b78bf63a8))
- Align docs examples with v2.1.0 api ([`8030d2c`](https://github.com/AMarantis/larvaworld/commit/8030d2caeaf50d43cf80a21384d0f4ddf0ff7e98))
- Add summary of all pr-4c changes to unreleased section ([`c47fcdc`](https://github.com/AMarantis/larvaworld/commit/c47fcdc7e5eb2b2811f74ac897009b46c366ad7d))
- Add type examples and improve commit message documentation ([`bda3604`](https://github.com/AMarantis/larvaworld/commit/bda3604831fc411b6a639a25459cbead3cced4ea))
- Remove codecov, poetry, and ruff badges from readme ([`7576a79`](https://github.com/AMarantis/larvaworld/commit/7576a79e7e3b6f0ade06bdfb5d4ff3d4a16c73ae))
- Fix module-level constant docstrings for autoapi ([`8911126`](https://github.com/AMarantis/larvaworld/commit/8911126ba30ffb89da0af07d73b33bb5860432f5))
- Update first publication link in publications page ([`6972912`](https://github.com/AMarantis/larvaworld/commit/6972912dc787e25791a2ace39cce4992bea1438a))
- Add publications page and clarify cli argument order ([`d7cf5c2`](https://github.com/AMarantis/larvaworld/commit/d7cf5c2a08765d03201ac8bf07f0c3cb8efc8f7b))
- Expand video examples ([`f13ee97`](https://github.com/AMarantis/larvaworld/commit/f13ee97575a02f93dd4bf4ad2a7c6ca7fe18ba04))
- Hide tutorials toctree from main page, keep in sidebar ([`c9537ec`](https://github.com/AMarantis/larvaworld/commit/c9537ec6cd622c694243b0aac925e1a3f569ac73))
- Remove :hidden: from tutorials toctree to show in sidebar ([`a473fdd`](https://github.com/AMarantis/larvaworld/commit/a473fddb298aae15fcbdd827173e8bf4a28e98df))
- Restore tutorial subsections structure with .rst files ([`8aad1a5`](https://github.com/AMarantis/larvaworld/commit/8aad1a5bb3b532b50d66ce8709fb51bcf564f9c3))
- Create tutorial subsections with index files (configuration, simulation, data, development) ([`a27d098`](https://github.com/AMarantis/larvaworld/commit/a27d098dde933ec959e0ccabb945d4f2bdfade10))
- Organize tutorials into subsections (configuration, simulation, data, development) ([`6f60d95`](https://github.com/AMarantis/larvaworld/commit/6f60d958b302c50ffdbae3dbae361cfba0819338))
- Remove duplicate myst_parser extension (included in myst_nb) ([`c2e63d1`](https://github.com/AMarantis/larvaworld/commit/c2e63d1c1380d15a74e5e31c5c6278f2952b3de5))
- Switch from nbsphinx to myst_nb and add pygments style ([`76ffea2`](https://github.com/AMarantis/larvaworld/commit/76ffea2de6bfd9046f14b21592986d2797bc0f40))
- Switch to sphinx_rtd_theme and rename autoapi entry ([`e92eac0`](https://github.com/AMarantis/larvaworld/commit/e92eac0062d325426c5daf141e570a6f7e1caf3c))
- Fix sidebar navigation and use default furo theme ([`6597030`](https://github.com/AMarantis/larvaworld/commit/659703028960614eb45c47d6c06401c97bc38767))
- Reorganize concepts and index ([`4d6a563`](https://github.com/AMarantis/larvaworld/commit/4d6a56347080b4afed96ec63d64b87491f4ce016))
- Major documentation overhaul with sphinx/readthedocs setup ([`e453018`](https://github.com/AMarantis/larvaworld/commit/e453018e6576c1806ba7294ea044d5ac1baccb59))
- Update license to mit and fix python version constraints ([`8f136f8`](https://github.com/AMarantis/larvaworld/commit/8f136f8efb889a4bed72ef6816a3c9f797373851))

### Style

- Apply pre-commit formatting fixes ([`b2b9071`](https://github.com/AMarantis/larvaworld/commit/b2b9071e674536b9b08c540733edaf5febd28400))

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
