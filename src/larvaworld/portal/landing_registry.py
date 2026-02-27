from __future__ import annotations

from larvaworld.portal.registry_types import LaneSpec, LandingItem, LearnMore

DOCS_ROOT = "https://larvaworld.readthedocs.io/en/latest/"
GITHUB_ROOT = "https://github.com/nawrotlab/larvaworld"
GITHUB_ISSUES = f"{GITHUB_ROOT}/issues"

DOCS_WEB_APPS = f"{DOCS_ROOT}visualization/web_applications.html"
DOCS_EXPERIMENT_VIEWER = f"{DOCS_WEB_APPS}#experiment-viewer"
DOCS_TRACK_VIEWER = f"{DOCS_WEB_APPS}#track-viewer"
DOCS_MODEL_INSPECTOR = f"{DOCS_WEB_APPS}#model-inspector"
DOCS_MODULE_INSPECTOR = f"{DOCS_WEB_APPS}#module-inspector"
DOCS_LATERAL_OSCILLATOR = f"{DOCS_WEB_APPS}#lateral-oscillator-inspector"

DOCS_SINGLE_EXPERIMENTS = f"{DOCS_ROOT}working_with_larvaworld/single_experiments.html"
DOCS_EXPERIMENT_TYPES = f"{DOCS_ROOT}concepts/experiment_types.html"
DOCS_BATCH_RUNS = f"{DOCS_ROOT}working_with_larvaworld/batch_runs_advanced.html"

DOCS_REFERENCE_DATASETS = f"{DOCS_ROOT}data_pipeline/reference_datasets.html"
DOCS_DATA_PROCESSING = f"{DOCS_ROOT}data_pipeline/data_processing.html"
DOCS_PLOTTING_API = f"{DOCS_ROOT}visualization/plotting_api.html"

DOCS_ARENAS_SUBSTRATES = f"{DOCS_ROOT}agents_environments/arenas_and_substrates.html"
DOCS_AGENT_ARCHITECTURE = f"{DOCS_ROOT}agents_environments/larva_agent_architecture.html"

DOCS_MODEL_EVALUATION = f"{DOCS_ROOT}working_with_larvaworld/model_evaluation.html"
DOCS_GA_OPTIMIZATION = f"{DOCS_ROOT}working_with_larvaworld/ga_optimization_advanced.html"
DOCS_COMPARE_DATASETS = f"{DOCS_MODEL_EVALUATION}#statistical-comparison-plots"

NOTEBOOK_TUTORIAL_BY_ITEM_ID: dict[str, str] = {
    "experiment_viewer": "single_simulation.ipynb",
    "wf.run_experiment": "single_simulation.ipynb",
    "wf.experiment_catalog": "CONFTYPES.ipynb",
    "wf.open_dataset": "import_datasets.ipynb",
    "track_viewer": "replay.ipynb",
    "wf.dataset_manager": "import_datasets.ipynb",
    "larva_models": "library_interface.ipynb",
    "locomotory_modules": "custom_module.ipynb",
    "wf.environment_builder": "environment_configuration.ipynb",
    "wf.model_evaluation": "model_evaluation.ipynb",
    "wf.ga_optimization": "genetic_algorithm_optimization.ipynb",
    "wf.compare_datasets": "model_evaluation.ipynb",
}


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
        subtitle=(
            "Replay larval trajectories frame-by-frame.\n"
            "Inspect motion quality and path structure.\n"
            "Quickly compare individuals in one view."
        ),
        cta="Replay",
        panel_app_id="track_viewer",
        learn_more=LearnMore(docs_url=DOCS_TRACK_VIEWER),
    ),
    "experiment_viewer": LandingItem(
        id="experiment_viewer",
        kind="panel_app",
        status="ready",
        lane="simulate",
        level="core",
        title="Experiment Viewer",
        subtitle=(
            "Step through a completed experiment run.\n"
            "Inspect state changes across time.\n"
            "Review outputs before deeper analysis."
        ),
        cta="Preview",
        panel_app_id="experiment_viewer",
        learn_more=LearnMore(docs_url=DOCS_EXPERIMENT_VIEWER),
    ),
    "larva_models": LandingItem(
        id="larva_models",
        kind="panel_app",
        status="ready",
        lane="models",
        level="core",
        title="Model Inspector",
        subtitle=(
            "Browse available larva model presets.\n"
            "Inspect key parameters and defaults.\n"
            "Compare configurations before simulation."
        ),
        cta="Inspect",
        panel_app_id="larva_models",
        learn_more=LearnMore(docs_url=DOCS_MODEL_INSPECTOR),
    ),
    "locomotory_modules": LandingItem(
        id="locomotory_modules",
        kind="panel_app",
        status="ready",
        lane="models",
        level="core",
        title="Module Inspector",
        subtitle=(
            "Inspect locomotory and sensorimotor modules.\n"
            "Review module parameters and behavior roles.\n"
            "Understand how modules combine in control."
        ),
        cta="Inspect",
        panel_app_id="locomotory_modules",
        learn_more=LearnMore(docs_url=DOCS_MODULE_INSPECTOR),
    ),
    "lateral_oscillator": LandingItem(
        id="lateral_oscillator",
        kind="panel_app",
        status="ready",
        lane="demos",
        level="demo",
        title="Lateral Oscillator",
        subtitle=(
            "Explore the lateral oscillator controller.\n"
            "Visualize oscillation and coupling behavior.\n"
            "Inspect parameters for rhythmic motion."
        ),
        cta="Open",
        panel_app_id="lateral_oscillator",
        learn_more=LearnMore(docs_url=DOCS_LATERAL_OSCILLATOR),
    ),
    # ---- External links ----
    "link.docs": LandingItem(
        id="link.docs",
        kind="external_link",
        status="ready",
        lane="demos",
        level="demo",
        title="Docs",
        subtitle=(
            "Open the Larvaworld documentation portal.\n"
            "Browse guides, tutorials, and references.\n"
            "Find details for each workflow."
        ),
        cta="Open",
        url=DOCS_ROOT,
        learn_more=LearnMore(docs_url=DOCS_ROOT),
    ),
    "link.github": LandingItem(
        id="link.github",
        kind="external_link",
        status="ready",
        lane="demos",
        level="demo",
        title="GitHub",
        subtitle=(
            "Open the Larvaworld GitHub repository.\n"
            "Track issues, roadmap, and development.\n"
            "Follow implementation progress."
        ),
        cta="Open",
        url=GITHUB_ROOT,
        learn_more=LearnMore(docs_url=f"{DOCS_ROOT}contributing.html"),
    ),
    # ---- Planned workflows / placeholders ----
    "wf.run_experiment": LandingItem(
        id="wf.run_experiment",
        kind="placeholder",
        status="planned",
        lane="simulate",
        level="core",
        title="Run Experiment",
        subtitle=(
            "Select a preset and configure key options.\n"
            "Run one simulation from the web workflow.\n"
            "Store outputs for immediate follow-up."
        ),
        cta="Run",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_SINGLE_EXPERIMENTS,
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
        subtitle=(
            "Browse available datasets in your workspace.\n"
            "Select one dataset as the active context.\n"
            "Reuse it across viewers and analysis."
        ),
        cta="Open",
        prereq_hint="Dataset selection is currently handled inside each app.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_REFERENCE_DATASETS,
        ),
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
        subtitle=(
            "Compare model outputs against references.\n"
            "Compute metrics and summary scores.\n"
            "Generate plots for model validation."
        ),
        cta="Evaluate",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_MODEL_EVALUATION,
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
        subtitle=(
            "Browse the curated experiment library.\n"
            "Filter presets by purpose and complexity.\n"
            "Open one preset to start quickly."
        ),
        cta="Browse",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_EXPERIMENT_TYPES,
        ),
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
        subtitle=(
            "Launch many configurations in parallel.\n"
            "Track status, logs, and produced outputs.\n"
            "Rerun failed jobs with minimal effort."
        ),
        cta="Open",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_BATCH_RUNS,
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
        subtitle=(
            "Organize datasets and attach metadata.\n"
            "Tag runs for easier filtering and reuse.\n"
            "Inspect summary info before analysis."
        ),
        cta="Manage",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_DATA_PROCESSING,
        ),
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
        subtitle=(
            "Export plots, tables, and media outputs.\n"
            "Package selected results for sharing.\n"
            "Create reproducible report artifacts."
        ),
        cta="Export",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_PLOTTING_API,
        ),
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
        subtitle=(
            "Design arenas, borders, and obstacles.\n"
            "Compose sensory and substrate landscapes.\n"
            "Save reusable environment presets."
        ),
        cta="Create",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_ARENAS_SUBSTRATES,
        ),
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
        subtitle=(
            "Inspect DEB energetics assumptions.\n"
            "Explore metabolic parameter effects.\n"
            "Relate energy state to behavior."
        ),
        cta="Explore",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=f"{DOCS_AGENT_ARCHITECTURE}#4-energy-system",
        ),
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
        subtitle=(
            "Tune model parameters with GA search.\n"
            "Optimize against reference objectives.\n"
            "Compare candidate solutions and fitness."
        ),
        cta="Optimize",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_GA_OPTIMIZATION,
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
        subtitle=(
            "Compare multiple runs side by side.\n"
            "Inspect metric differences across conditions.\n"
            "Summarize effects with common plots."
        ),
        cta="Compare",
        prereq_hint="Not available yet in the web UI.",
        learn_more=LearnMore(
            issue_url=GITHUB_ISSUES,
            docs_url=DOCS_COMPARE_DATASETS,
        ),
        preview_md=(
            "### Compare Datasets (Planned)\n"
            "- Select multiple runs or conditions\n"
            "- Compare metrics and summary plots\n"
        ),
    ),
}
