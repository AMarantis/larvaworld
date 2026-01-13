# Arenas and Substrates

This page covers environment configuration: arena geometry, food sources, odorscapes, and obstacles.

---

## Arena Types

### Circular Arena (Petri Dish)

**Default**: `dish` (100 mm diameter)

```python
from larvaworld.lib import reg

# Preconfigured circular arena (dims are in meters)
env_params = reg.conf.Env.getID("dish").get_copy()
print(env_params.arena.geometry, env_params.arena.dims)  # circular (0.1, 0.1)
```

### Rectangular Arena

```python
from larvaworld.lib import reg

# Preconfigured rectangular arena (200 mm x 200 mm)
env_params = reg.conf.Env.getID("arena_200mm").get_copy()
print(env_params.arena.geometry, env_params.arena.dims)  # rectangular (0.2, 0.2)
```

### Preconfigured Arenas

```python
from larvaworld.lib import reg

# List available arenas
env_ids = reg.conf.Env.confIDs
print(env_ids)

# Load arena
env_conf = reg.conf.Env.getID("arena_200mm").get_copy()
```

---

## Food Sources

Larvaworld supports three types of food distributions:

### 1. Discrete Patches

**Purpose**: Localized food sources

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()

# Create 3 food patches (group generator creates N individual sources)
env_params.food_params.source_groups = {
    "patches": {
        "N": 3,  # number of patches
        "mode": "uniform",
        "shape": "rect",
        "loc": (0.0, 0.0),
        "scale": (0.07, 0.07),
        "radius": 0.005,  # 5 mm
        "amount": 3.0,
        "substrate": {"type": "standard", "quality": 1.0},
        "color": "green",
    }
}
```

### 2. Food Grid

**Purpose**: Regular grid of patches

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()

# Place food patches on a regular grid
env_params.food_params.source_groups = {
    "grid": {
        "N": 16,  # total patches (e.g., 4x4)
        "mode": "grid",
        "shape": "rect",
        "loc": (0.0, 0.0),
        "scale": (0.2, 0.2),
        "radius": 0.003,
        "amount": 3.0,
        "substrate": {"type": "standard", "quality": 1.0},
        "color": "green",
    }
}
```

### 3. Uniform Substrate

**Purpose**: Continuous nutritious substrate

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.food_params.source_groups = {}
env_params.food_params.source_units = {}
env_params.food_params.food_grid = {
    "grid_dims": (51, 51),
    "initial_value": 1e-6,
    "substrate": {"type": "standard", "quality": 1.0},
}
```

---

## Nutritious Substrates

Larvaworld implements real experimental substrates.

The following table reproduces the compound densities reported in the Larvaworld paper (see {doc}`../CITATION`).

| Substrate           | Glucose (μg/ml) | Yeast (μg/ml) | Agar (μg/ml) | Source                 |
| ------------------- | --------------- | ------------- | ------------ | ---------------------- |
| **standard-medium** | 100             | 50            | 16           | Kaun et al. (2007)     |
| **PED-tracker**     | 10\*            | 187.5         | 5000         | Schumann et al. (2020) |
| **cornmeal**        | 70.3\*\*        | 14.1          | 6.6          | Wosniack et al. (2021) |
| **sucrose**         | 17.1            | 0             | 4            | Wosniack et al. (2021) |

\*Saccharose instead of glucose
\*\*Dextrose instead of glucose

In Larvaworld configuration, these correspond to `Substrate.type` values:

- `standard-medium` → `standard`
- `PED-tracker` → `PED_tracker`
- `cornmeal` → `cornmeal`
- `sucrose` → `sucrose`

**Usage**:

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.food_params.food_grid = {
    "grid_dims": (51, 51),
    "initial_value": 1e-6,
    "substrate": {"type": "standard", "quality": 1.0},
}
```

---

## Odorscapes

Odor layers are created from **sources** (food patches) that have an `odor.id`.
To enable odor diffusion, set `env_params.odorscape` to `"Gaussian"` or `"Diffusion"`.

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.odorscape = {"odorscape": "Gaussian", "grid_dims": (51, 51)}

# One odorized food patch produces an odor layer with id="apple"
env_params.food_params.source_units = {
    "apple_patch": {
        "pos": (0.02, 0.0),
        "radius": 0.005,
        "amount": 3.0,
        "odor": {"id": "apple", "intensity": 1.0, "spread": 0.02},
        "substrate": {"type": "standard", "quality": 1.0},
        "color": "green",
        "regeneration": False,
    }
}
```

---

## Obstacles and Borders

### Arena Borders

```python
from larvaworld.lib import reg

env_params = reg.conf.Env.getID("arena_200mm").get_copy()

# Borders are configured via env_params.border_list.
# Vertices are interpreted as pairs of points (p0,p1), (p1,p2), ... (p3,p0):
p0, p1, p2, p3 = (-0.1, -0.1), (0.1, -0.1), (0.1, 0.1), (-0.1, 0.1)
env_params.border_list = {
    "wall0": {
        "vertices": [p0, p1, p1, p2, p2, p3, p3, p0],
        "width": 0.001,
    }
}
```

---

## Larva Initial Placement

Control where larvae start:

```python
larva_groups = {
    "explorers": {
        "model": "explorer",
        "distribution": {
            "N": 20,
            "mode": "uniform",       # Distribution mode
            "loc": (0.0, 0.0),       # center (meters)
            "scale": (0.01, 0.01),   # spread (meters)
            "shape": "circle",
        },
    }
}
```

### Distribution Modes

| Mode          | Description                 |
| ------------- | --------------------------- |
| `"uniform"`   | Uniform random within shape |
| `"periphery"` | Ring around center          |
| `"line"`      | Linear arrangement          |
| `"grid"`      | Regular grid                |

See [Table 4](../figures_tables_from_paper/tables/table4_larva_placement.md) for details.

---

## Complete Example

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun
from larvaworld.lib.util import AttrDict

# Start from a built-in experiment template and override env/larvae
exp_params = reg.conf.Exp.getID("dish").get_copy()

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.odorscape = {"odorscape": "Gaussian", "grid_dims": (51, 51)}
env_params.food_params.source_units = {
    "food_patch": {
        "pos": (0.02, 0.0),
        "radius": 0.008,
        "amount": 3.0,
        "odor": {"id": "food_odor", "intensity": 1.0, "spread": 0.03},
        "substrate": {"type": "standard", "quality": 1.0},
        "color": "green",
    }
}

exp_params.env_params = env_params
exp_params.larva_groups = AttrDict(
    {
        "foragers": AttrDict(
            {
                "model": "forager",
                "distribution": {
                    "N": 5,
                    "mode": "periphery",
                    "shape": "circle",
                    "loc": (0.0, 0.0),
                    "scale": (0.08, 0.08),
                },
            }
        )
    }
)

run = ExpRun(experiment="dish", parameters=exp_params, duration=0.2, screen_kws={})
run.simulate()
```

---

## Related Documentation

- {doc}`larva_agent_architecture` - Agent models
- {doc}`../concepts/experiment_types` - Preconfigured experiments
- {doc}`../concepts/experiment_configuration_pipeline` - Configuration system
