# Web Applications

Larvaworld provides interactive web dashboards built with **Panel** (Holoviz stack) for exploration, configuration, and analysis.

---

## Launching the App

```bash
larvaworld-app
```

**Access**: `http://localhost:5006`

:::{note}
The current `larvaworld-app` launcher serves the dashboards on port **5006** (hardcoded in `larvaworld.dashboards.main`).
Stop the server with **Ctrl+C**.
:::

---

## Available Dashboards

All dashboards are served from a single Panel/Bokeh process. The Panel index page lists the following apps (IDs shown in parentheses):

| Dashboard              | App ID               | Purpose                                |
| ---------------------- | -------------------- | -------------------------------------- |
| **Experiment Viewer**  | `experiment_viewer`  | View experiment results interactively  |
| **Track Viewer**       | `track_viewer`       | Inspect trajectories                   |
| **Model Inspector**    | `larva_models`       | Explore locomotory models              |
| **Module Inspector**   | `locomotory_modules` | Inspect behavioral modules             |
| **Lateral Oscillator** | `lateral_oscillator` | Visualize the neural oscillator module |

---

## Experiment Viewer

**Purpose**: Interactive exploration of simulation results

**Features**:

- Load saved experiments
- Plot trajectories, metrics, distributions
- Filter by time window, agent ID
- Export plots as PNG/SVG

**Access**: Main dashboard landing page

---

## Track Viewer

**Purpose**: Detailed trajectory inspection

**Features**:

- 2D trajectory plots
- Velocity/acceleration profiles
- Zoom and pan
- Multi-agent comparison

---

## Model Inspector

**Purpose**: Explore model parameters

**Features**:

- Browse available models
- View parameter values
- Compare model configurations
- Test parameter combinations

---

## Module Inspector

**Purpose**: Inspect behavioral modules

**Features**:

- Crawler, Turner, Feeder modules
- Real-time parameter adjustment
- Behavior visualization

---

## Lateral Oscillator Inspector

**Purpose**: Visualize the neural oscillator (CPG) module

**Features**:

- Phase plots
- Oscillation frequency analysis
- Coupling visualization

---

## Web App Architecture

![Web App](../figures_tables_from_paper/figures/fig8_web_app.png)

**Figure**: Screenshot of Larvaworld web application showing interactive visualization and control panels.

---

## Status

:::{note}
Web applications are **functional but under active development**. Some features may change in future releases. For production use, prefer CLI/Python API.
:::

---

## Related Documentation

- {doc}`keyboard_controls` - Interactive controls
- {doc}`visualization_snapshots` - Visualization examples
- {doc}`../concepts/architecture_overview` - Platform architecture
