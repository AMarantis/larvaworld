from __future__ import annotations

from larvaworld.portal.registry_types import LaneSpec, LandingItem, LearnMore

DOCS_ROOT = "https://larvaworld.readthedocs.io/en/latest/"
GITHUB_ROOT = "https://github.com/nawrotlab/larvaworld"
GITHUB_ISSUES = f"{GITHUB_ROOT}/issues"


# ---- Deterministic ordering: these lists define display order. ----

PINNED_QUICK_START: list[str] = [
    "wf.run_experiment",
    "wf.open_dataset",
    "track_viewer",
    "wf.model_evaluation",
]

LANES: list[LaneSpec] = [
    LaneSpec(
        title="Simulate",
        lane="simulate",
        item_ids=[
            "experiment_viewer",
            "wf.run_experiment",
            "wf.experiment_catalog",
            "wf.batch_runs",
        ],
    ),
    LaneSpec(
        title="Data & Visualization",
        lane="data",
        item_ids=[
            "wf.open_dataset",
            "track_viewer",
            "wf.dataset_manager",
            "wf.export_center",
        ],
    ),
    LaneSpec(
        title="Models & Architecture",
        lane="models",
        item_ids=[
            "larva_models",
            "locomotory_modules",
            "wf.environment_builder",
            "wf.deb_explorer",
        ],
    ),
    LaneSpec(
        title="Evaluation & Optimization",
        lane="eval",
        item_ids=[
            "wf.model_evaluation",
            "wf.ga_optimization",
            "wf.compare_datasets",
        ],
    ),
    LaneSpec(
        title="Demos & Tutorials",
        lane="demos",
        item_ids=[
            "lateral_oscillator",
            "link.docs",
            "link.github",
        ],
        collapsed_by_default=True,
    ),
]


ITEMS: dict[str, LandingItem] = {
    # ---- Real Panel apps (id == panel_app_id) ----
    "track_viewer": LandingItem(
        id="track_viewer",
        kind="panel_app",
        status="ready",
        lane="data",
        level="core",
        title="Track Viewer",
        subtitle="Replay trajectories and perform quick QC.",
        cta="Replay",
        panel_app_id="track_viewer",
    ),
    "experiment_viewer": LandingItem(
        id="experiment_viewer",
        kind="panel_app",
        status="ready",
        lane="simulate",
        level="core",
        title="Experiment Viewer",
        subtitle="Preview an experiment run and step through time.",
        cta="Preview",
        panel_app_id="experiment_viewer",
    ),
    "larva_models": LandingItem(
        id="larva_models",
        kind="panel_app",
        status="ready",
        lane="models",
        level="core",
        title="Model Inspector",
        subtitle="Inspect larva model presets and parameters.",
        cta="Inspect",
        panel_app_id="larva_models",
    ),
    "locomotory_modules": LandingItem(
        id="locomotory_modules",
        kind="panel_app",
        status="ready",
        lane="models",
        level="core",
        title="Module Inspector",
        subtitle="Inspect locomotion/sensorimotor modules.",
        cta="Inspect",
        panel_app_id="locomotory_modules",
    ),
    "lateral_oscillator": LandingItem(
        id="lateral_oscillator",
        kind="panel_app",
        status="ready",
        lane="demos",
        level="demo",
        title="Lateral Oscillator",
        subtitle="Interactive demo for oscillatory control components.",
        cta="Open",
        panel_app_id="lateral_oscillator",
    ),
    # ---- External links ----
    "link.docs": LandingItem(
        id="link.docs",
        kind="external_link",
        status="ready",
        lane="demos",
        level="demo",
        title="Docs",
        subtitle="Open the Larvaworld documentation.",
        cta="Open",
        url=DOCS_ROOT,
    ),
    "link.github": LandingItem(
        id="link.github",
        kind="external_link",
        status="ready",
        lane="demos",
        level="demo",
        title="GitHub",
        subtitle="Open the repository and issues.",
        cta="Open",
        url=GITHUB_ROOT,
    ),
    # ---- Planned workflows / placeholders ----
    "wf.run_experiment": LandingItem(
        id="wf.run_experiment",
        kind="placeholder",
        status="planned",
        lane="simulate",
        level="core",
        title="Run Experiment",
        subtitle="Choose a preset and run a single simulation.",
        cta="Run",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=f"{DOCS_ROOT}working_with_larvaworld/single_experiments.html",
        ),
        preview_md=(
            "### Run Experiment (Planned)\n"
            "- Pick an experiment preset (curated list)\n"
            "- Adjust key parameters (model/env/seed)\n"
            "- Run and persist dataset outputs\n"
            "- One-click open in Track Viewer / Evaluation\n"
        ),
    ),
    "wf.open_dataset": LandingItem(
        id="wf.open_dataset",
        kind="placeholder",
        status="planned",
        lane="data",
        level="core",
        title="Open Dataset",
        subtitle="Select an existing dataset and set it as active.",
        cta="Open",
        prereq_hint="Dataset selection is currently handled inside each app.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Open Dataset (Planned)\n"
            "- Browse datasets under the configured data directory\n"
            "- Preview metadata (duration, N, timestamps)\n"
            "- Set active dataset for downstream tools\n"
        ),
    ),
    "wf.model_evaluation": LandingItem(
        id="wf.model_evaluation",
        kind="placeholder",
        status="planned",
        lane="eval",
        level="core",
        title="Model Evaluation",
        subtitle="Compare outputs to reference data and score models.",
        cta="Evaluate",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=f"{DOCS_ROOT}working_with_larvaworld/model_evaluation.html",
        ),
        preview_md=(
            "### Model Evaluation (Planned)\n"
            "- Select simulation output + reference dataset\n"
            "- Compute metrics and summary scores\n"
            "- Generate a report with comparison plots\n"
        ),
    ),
    "wf.experiment_catalog": LandingItem(
        id="wf.experiment_catalog",
        kind="placeholder",
        status="planned",
        lane="simulate",
        level="core",
        title="Experiment Catalog",
        subtitle="Browse curated experiment presets.",
        cta="Browse",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Experiment Catalog (Planned)\n"
            "- Search and filter experiment presets\n"
            "- See a short description and default parameters\n"
            "- Open a preset in Run Experiment\n"
        ),
    ),
    "wf.batch_runs": LandingItem(
        id="wf.batch_runs",
        kind="placeholder",
        status="planned",
        lane="simulate",
        level="advanced",
        title="Batch Runs",
        subtitle="Run many configs and manage outputs.",
        cta="Open",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=f"{DOCS_ROOT}working_with_larvaworld/batch_runs_advanced.html",
        ),
        preview_md=(
            "### Batch Runs (Planned)\n"
            "- Define a parameter sweep\n"
            "- Run many simulations and track outputs\n"
            "- Export results and re-run failed jobs\n"
        ),
    ),
    "wf.dataset_manager": LandingItem(
        id="wf.dataset_manager",
        kind="placeholder",
        status="planned",
        lane="data",
        level="core",
        title="Dataset Manager",
        subtitle="Organize, tag, and preview dataset metadata.",
        cta="Manage",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Dataset Manager (Planned)\n"
            "- View datasets in a workspace\n"
            "- Tag and annotate runs\n"
            "- Quick metadata preview and actions\n"
        ),
    ),
    "wf.export_center": LandingItem(
        id="wf.export_center",
        kind="placeholder",
        status="planned",
        lane="data",
        level="advanced",
        title="Export Center",
        subtitle="Export plots, tables, and videos from a dataset.",
        cta="Export",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Export Center (Planned)\n"
            "- Export plots/tables/videos\n"
            "- Bundle configs and results for sharing\n"
        ),
    ),
    "wf.environment_builder": LandingItem(
        id="wf.environment_builder",
        kind="placeholder",
        status="planned",
        lane="models",
        level="core",
        title="Environment Builder",
        subtitle="Create arenas, obstacles, and sensory landscapes.",
        cta="Create",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Environment Builder (Planned)\n"
            "- Configure arena geometry and obstacles\n"
            "- Define sensory landscapes\n"
            "- Save and reuse environment presets\n"
        ),
    ),
    "wf.deb_explorer": LandingItem(
        id="wf.deb_explorer",
        kind="placeholder",
        status="planned",
        lane="models",
        level="advanced",
        title="DEB Explorer",
        subtitle="Explore energetics constraints and DEB parameters.",
        cta="Explore",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### DEB Explorer (Planned)\n"
            "- Inspect energetics assumptions and constraints\n"
            "- Explore DEB parameter presets\n"
        ),
    ),
    "wf.ga_optimization": LandingItem(
        id="wf.ga_optimization",
        kind="placeholder",
        status="planned",
        lane="eval",
        level="advanced",
        title="GA Optimization",
        subtitle="Optimize model parameters via genetic algorithms.",
        cta="Optimize",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=f"{DOCS_ROOT}working_with_larvaworld/ga_optimization_advanced.html",
        ),
        preview_md=(
            "### GA Optimization (Planned)\n"
            "- Define a scoring objective\n"
            "- Run GA to tune parameters\n"
            "- Compare candidate solutions\n"
        ),
    ),
    "wf.compare_datasets": LandingItem(
        id="wf.compare_datasets",
        kind="placeholder",
        status="planned",
        lane="eval",
        level="advanced",
        title="Compare Datasets",
        subtitle="Compare multiple runs and conditions side-by-side.",
        cta="Compare",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(issue_url=GITHUB_ISSUES),
        preview_md=(
            "### Compare Datasets (Planned)\n"
            "- Select multiple runs or conditions\n"
            "- Compare metrics and summary plots\n"
        ),
    ),
}

