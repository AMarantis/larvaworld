# Larvaworld Architecture Diagrams

## 1. Project Structure Diagram

```mermaid
graph TD
    A[larvaworld/] --> B[src/larvaworld/]
    A --> C[docs/]
    A --> D[tests/]
    A --> E[examples/]
    A --> F[templates/]
    A --> G[.github/]
    A --> H[pyproject.toml]
    A --> I[README.md]
    
    B --> J[cli/]
    B --> K[dashboards/]
    B --> L[gui/]
    B --> M[lib/]
    B --> N[data/]
    
    J --> J1[main.py]
    J --> J2[argparser.py]
    
    K --> K1[main.py]
    K --> K2[experiment_viewer.py]
    K --> K3[model_inspector.py]
    K --> K4[track_viewer.py]
    
    L --> L1[main.py]
    L --> L2[gui_aux/]
    L --> L3[tabs/]
    L --> L4[media/]
    
    M --> M1[model/]
    M --> M2[param/]
    M --> M3[plot/]
    M --> M4[process/]
    M --> M5[reg/]
    M --> M6[screen/]
    M --> M7[sim/]
    M --> M8[util/]
    
    M1 --> M1A[agents/]
    M1 --> M1B[envs/]
    M1 --> M1C[modules/]
    M1 --> M1D[deb/]
    
    M1A --> M1A1[_larva.py]
    M1A --> M1A2[_larva_sim.py]
    M1A --> M1A3[_larva_replay.py]
    
    M1B --> M1B1[arena.py]
    M1B --> M1B2[maze.py]
    M1B --> M1B3[obstacle.py]
    
    M1C --> M1C1[oscillator.py]
    M1C --> M1C2[crawler.py]
    M1C --> M1C3[feeder.py]
    M1C --> M1C4[sensor.py]
    M1C --> M1C5[brain.py]
    M1C --> M1C6[memory.py]
```

## 2. System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[Command Line Interface]
        GUI[Graphical User Interface]
        WEB[Web Dashboards]
    end
    
    subgraph "Application Layer"
        SIM[Simulation Engine]
        BATCH[Batch Processing]
        GA[Genetic Algorithm]
        EVAL[Model Evaluation]
    end
    
    subgraph "Core Model Layer"
        AGENT[Agent System]
        ENV[Environment]
        MODULES[Behavioral Modules]
    end
    
    subgraph "Agent Components"
        LARVA[Larva Agent]
        BODY[Body Model]
        BRAIN[Neural System]
        DEB[Energy Budget]
    end
    
    subgraph "Behavioral Modules"
        CRAWL[Crawler]
        FEED[Feeder]
        SENSE[Sensor]
        TURN[Turner]
        MEM[Memory]
        INTER[Intermitter]
    end
    
    subgraph "Environment Components"
        ARENA[Arena]
        FOOD[Food Sources]
        ODOR[Odor Sources]
        OBST[Obstacles]
    end
    
    subgraph "Data Processing"
        IMPORT[Data Import]
        PROCESS[Data Processing]
        ANALYSIS[Behavioral Analysis]
        VISUAL[Visualization]
    end
    
    subgraph "External Libraries"
        AGENTPY[AgentPy]
        BOX2D[Box2D Physics]
        NENGO[Nengo Neural]
        MATPLOT[Matplotlib]
        PANDAS[Pandas]
    end
    
    CLI --> SIM
    GUI --> SIM
    WEB --> SIM
    
    SIM --> AGENT
    SIM --> ENV
    BATCH --> SIM
    GA --> SIM
    EVAL --> SIM
    
    AGENT --> LARVA
    LARVA --> BODY
    LARVA --> BRAIN
    LARVA --> DEB
    
    LARVA --> MODULES
    MODULES --> CRAWL
    MODULES --> FEED
    MODULES --> SENSE
    MODULES --> TURN
    MODULES --> MEM
    MODULES --> INTER
    
    ENV --> ARENA
    ENV --> FOOD
    ENV --> ODOR
    ENV --> OBST
    
    SIM --> IMPORT
    IMPORT --> PROCESS
    PROCESS --> ANALYSIS
    ANALYSIS --> VISUAL
    
    AGENT --> AGENTPY
    BODY --> BOX2D
    BRAIN --> NENGO
    VISUAL --> MATPLOT
    PROCESS --> PANDAS
```

## 3. Larva Model Architecture

```mermaid
graph TB
    subgraph "Larva Agent"
        LARVA[Larva Agent]
        
        subgraph "Physical Body"
            BODY[Segmented Body]
            SENSORS[Olfactory & Touch Sensors]
            MOUTH[Feeding Mouth]
        end
        
        subgraph "Neural System"
            BRAIN[Brain Module]
            OSCILLATORS[Oscillator Modules]
            MEMORY[Memory System]
        end
        
        subgraph "Behavioral Modules"
            CRAWLER[Crawler Module]
            FEEDER[Feeder Module]
            TURNER[Turner Module]
            INTERMITTER[Intermitter Module]
        end
        
        subgraph "Energy System"
            DEB[Dynamic Energy Budget]
            GUT[Gut Model]
            METABOLISM[Metabolism]
        end
        
        subgraph "Motor Control"
            MOTOR[Motor Controller]
            LOCOMOTOR[Locomotor]
            CRAWL_BEND[Crawl-Bend Interference]
        end
    end
    
    LARVA --> BODY
    LARVA --> BRAIN
    LARVA --> DEB
    LARVA --> MOTOR
    
    BODY --> SENSORS
    BODY --> MOUTH
    
    BRAIN --> OSCILLATORS
    BRAIN --> MEMORY
    
    OSCILLATORS --> CRAWLER
    OSCILLATORS --> FEEDER
    OSCILLATORS --> TURNER
    OSCILLATORS --> INTERMITTER
    
    DEB --> GUT
    DEB --> METABOLISM
    
    MOTOR --> LOCOMOTOR
    MOTOR --> CRAWL_BEND
    
    CRAWLER --> LOCOMOTOR
    FEEDER --> MOUTH
    TURNER --> LOCOMOTOR
```

## 4. Data Flow Diagram

```mermaid
flowchart TD
    subgraph "Input Sources"
        EXP_DATA[Experimental Data]
        CONFIG[Configuration Files]
        PARAMS[Model Parameters]
    end
    
    subgraph "Data Processing Pipeline"
        IMPORT[Data Import]
        TRANSFORM[Data Transformation]
        VALIDATE[Data Validation]
        STORE[Data Storage]
    end
    
    subgraph "Simulation Engine"
        INIT[Initialization]
        SIM[Simulation Loop]
        UPDATE[State Updates]
        RECORD[Data Recording]
    end
    
    subgraph "Analysis Pipeline"
        EXTRACT[Feature Extraction]
        ANALYZE[Behavioral Analysis]
        COMPARE[Model Comparison]
        METRICS[Performance Metrics]
    end
    
    subgraph "Output"
        RESULTS[Simulation Results]
        PLOTS[Visualizations]
        VIDEOS[Video Exports]
        REPORTS[Analysis Reports]
    end
    
    EXP_DATA --> IMPORT
    CONFIG --> INIT
    PARAMS --> INIT
    
    IMPORT --> TRANSFORM
    TRANSFORM --> VALIDATE
    VALIDATE --> STORE
    
    STORE --> INIT
    INIT --> SIM
    SIM --> UPDATE
    UPDATE --> RECORD
    RECORD --> SIM
    
    RECORD --> EXTRACT
    EXTRACT --> ANALYZE
    ANALYZE --> COMPARE
    COMPARE --> METRICS
    
    METRICS --> RESULTS
    RESULTS --> PLOTS
    RESULTS --> VIDEOS
    RESULTS --> REPORTS
```

## 5. Module Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant SimEngine
    participant LarvaAgent
    participant Brain
    participant Crawler
    participant Feeder
    participant Sensor
    participant Environment
    
    User->>CLI: Run simulation command
    CLI->>SimEngine: Initialize simulation
    SimEngine->>Environment: Create arena
    SimEngine->>LarvaAgent: Create larva agents
    
    loop Simulation Loop
        SimEngine->>LarvaAgent: Update timestep
        LarvaAgent->>Sensor: Read environment
        Sensor->>Environment: Get sensory input
        Environment-->>Sensor: Return sensory data
        Sensor-->>LarvaAgent: Sensory feedback
        
        LarvaAgent->>Brain: Process sensory input
        Brain->>Crawler: Generate crawling commands
        Brain->>Feeder: Generate feeding commands
        
        Crawler-->>LarvaAgent: Movement commands
        Feeder-->>LarvaAgent: Feeding commands
        
        LarvaAgent->>Environment: Execute actions
        Environment-->>LarvaAgent: Action results
        
        LarvaAgent-->>SimEngine: Update state
        SimEngine->>SimEngine: Record data
    end
    
    SimEngine-->>CLI: Simulation complete
    CLI-->>User: Results available
```

## 6. Technology Stack Diagram

```mermaid
graph TB
    subgraph "Frontend/UI"
        CLI_UI[Command Line Interface]
        GUI_UI[Graphical User Interface]
        WEB_UI[Web Dashboards]
    end
    
    subgraph "Core Framework"
        PYTHON[Python 3.8+]
        AGENTPY[AgentPy Framework]
        PARAM[Param Library]
    end
    
    subgraph "Scientific Computing"
        NUMPY[NumPy]
        PANDAS[Pandas]
        SCIPY[SciPy]
        SKLEARN[Scikit-learn]
    end
    
    subgraph "Visualization"
        MATPLOTLIB[Matplotlib]
        SEABORN[Seaborn]
        HOLOVIEWS[HoloViews]
        PANEL[Panel]
    end
    
    subgraph "Physics & Neural"
        BOX2D[Box2D Physics Engine]
        NENGO[Nengo Neural Simulator]
    end
    
    subgraph "Data Processing"
        GEOPANDAS[GeoPandas]
        SHAPELY[Shapely]
        MOVINGPANDAS[MovingPandas]
    end
    
    subgraph "Development Tools"
        POETRY[Poetry Package Manager]
        PYTEST[Pytest Testing]
        RUFF[Ruff Linting]
        PRECOMMIT[Pre-commit Hooks]
    end
    
    CLI_UI --> PYTHON
    GUI_UI --> PYTHON
    WEB_UI --> PYTHON
    
    PYTHON --> AGENTPY
    PYTHON --> PARAM
    
    AGENTPY --> NUMPY
    AGENTPY --> PANDAS
    AGENTPY --> SCIPY
    
    PYTHON --> MATPLOTLIB
    PYTHON --> SEABORN
    PYTHON --> HOLOVIEWS
    PYTHON --> PANEL
    
    PYTHON --> BOX2D
    PYTHON --> NENGO
    
    PYTHON --> GEOPANDAS
    PYTHON --> SHAPELY
    PYTHON --> MOVINGPANDAS
    
    PYTHON --> POETRY
    PYTHON --> PYTEST
    PYTHON --> RUFF
    PYTHON --> PRECOMMIT
```

## 7. Behavioral Modules Detailed Architecture

```mermaid
graph TB
    subgraph "Oscillator System"
        OSC_BASE[Base Oscillator]
        CRAWL_OSC[Crawling Oscillator]
        BEND_OSC[Bending Oscillator]
        FEED_OSC[Feeding Oscillator]
    end
    
    subgraph "Motor Control System"
        MOTOR_CTRL[Motor Controller]
        CRAWL_CTRL[Crawler Controller]
        TURN_CTRL[Turner Controller]
        FEED_CTRL[Feeder Controller]
    end
    
    subgraph "Sensor System"
        OLFACTORY[Olfactory Sensor]
        TOUCH[Touch Sensor]
        PROPRIOCEPTION[Proprioception]
    end
    
    subgraph "Behavioral Coordination"
        LOCOMOTOR[Locomotor Module]
        CRAWL_BEND_INT[Crawl-Bend Interference]
        INTERMITTER[Intermitter Module]
        BRANCH_INT[Branch Intermitter]
    end
    
    subgraph "Neural Processing"
        BRAIN_MODULE[Brain Module]
        MEMORY_MODULE[Memory Module]
        NENGO_BRAIN[Nengo Brain Interface]
    end
    
    subgraph "Energy & Metabolism"
        DEB_MODULE[DEB Module]
        GUT_MODULE[Gut Module]
        HUNGER[Hunger Drive]
        FORAGING[Foraging Phenotype]
    end
    
    OSC_BASE --> CRAWL_OSC
    OSC_BASE --> BEND_OSC
    OSC_BASE --> FEED_OSC
    
    CRAWL_OSC --> CRAWL_CTRL
    BEND_OSC --> TURN_CTRL
    FEED_OSC --> FEED_CTRL
    
    CRAWL_CTRL --> MOTOR_CTRL
    TURN_CTRL --> MOTOR_CTRL
    FEED_CTRL --> MOTOR_CTRL
    
    MOTOR_CTRL --> LOCOMOTOR
    LOCOMOTOR --> CRAWL_BEND_INT
    
    OLFACTORY --> BRAIN_MODULE
    TOUCH --> BRAIN_MODULE
    PROPRIOCEPTION --> BRAIN_MODULE
    
    BRAIN_MODULE --> MEMORY_MODULE
    BRAIN_MODULE --> NENGO_BRAIN
    
    BRAIN_MODULE --> CRAWL_OSC
    BRAIN_MODULE --> BEND_OSC
    BRAIN_MODULE --> FEED_OSC
    
    DEB_MODULE --> GUT_MODULE
    GUT_MODULE --> HUNGER
    HUNGER --> FORAGING
    
    FORAGING --> BRAIN_MODULE
    HUNGER --> INTERMITTER
    INTERMITTER --> BRANCH_INT
    
    BRANCH_INT --> CRAWL_OSC
    BRANCH_INT --> FEED_OSC
```

## 8. Environment and Arena Architecture

```mermaid
graph TB
    subgraph "Environment System"
        ENV_BASE[Base Environment]
        ARENA[Arena Environment]
        MAZE[Maze Environment]
    end
    
    subgraph "Arena Components"
        BOUNDARIES[Boundaries]
        FOOD_SOURCES[Food Sources]
        ODOR_SOURCES[Odor Sources]
        OBSTACLES[Obstacles]
        VALUE_GRID[Value Grid]
    end
    
    subgraph "Spatial Distributions"
        XY_DISTRO[XY Distribution]
        SPATIAL_PARAMS[Spatial Parameters]
        ORIENTATION[Orientation]
    end
    
    subgraph "Dynamic Elements"
        MOVING_OBJ[Moving Objects]
        DYNAMIC_ODOR[Dynamic Odorscapes]
        TEMPORAL_CHANGES[Temporal Changes]
    end
    
    ENV_BASE --> ARENA
    ENV_BASE --> MAZE
    
    ARENA --> BOUNDARIES
    ARENA --> FOOD_SOURCES
    ARENA --> ODOR_SOURCES
    ARENA --> OBSTACLES
    ARENA --> VALUE_GRID
    
    FOOD_SOURCES --> XY_DISTRO
    ODOR_SOURCES --> XY_DISTRO
    OBSTACLES --> XY_DISTRO
    
    XY_DISTRO --> SPATIAL_PARAMS
    SPATIAL_PARAMS --> ORIENTATION
    
    ODOR_SOURCES --> DYNAMIC_ODOR
    FOOD_SOURCES --> MOVING_OBJ
    ARENA --> TEMPORAL_CHANGES
```

## 9. Simulation Modes and Workflows

```mermaid
graph TD
    subgraph "Simulation Modes"
        SINGLE[Single Simulation]
        BATCH[Batch Run]
        GA[Genetic Algorithm]
        EVAL[Model Evaluation]
        REPLAY[Experiment Replay]
    end
    
    subgraph "Experiment Types"
        EXPLORATION[Free Exploration]
        CHEMOTAXIS[Chemotaxis]
        LEARNING[Olfactory Learning]
        FEEDING[Feeding Behavior]
        FORAGING[Foraging]
        GROWTH[Growth Simulation]
    end
    
    subgraph "Analysis Pipeline"
        IMPORT_ANALYSIS[Data Import]
        FEATURE_EXTRACT[Feature Extraction]
        BEHAVIOR_ANALYSIS[Behavioral Analysis]
        MODEL_COMPARE[Model Comparison]
        STATISTICAL[Statistical Analysis]
    end
    
    subgraph "Output Generation"
        VISUALIZATION[Visualizations]
        VIDEO_EXPORT[Video Export]
        DATA_EXPORT[Data Export]
        REPORTS[Analysis Reports]
    end
    
    SINGLE --> EXPLORATION
    SINGLE --> CHEMOTAXIS
    SINGLE --> LEARNING
    SINGLE --> FEEDING
    SINGLE --> FORAGING
    SINGLE --> GROWTH
    
    BATCH --> EXPLORATION
    BATCH --> CHEMOTAXIS
    BATCH --> LEARNING
    
    GA --> EXPLORATION
    GA --> CHEMOTAXIS
    
    EVAL --> EXPLORATION
    EVAL --> CHEMOTAXIS
    EVAL --> LEARNING
    
    REPLAY --> IMPORT_ANALYSIS
    
    EXPLORATION --> FEATURE_EXTRACT
    CHEMOTAXIS --> FEATURE_EXTRACT
    LEARNING --> FEATURE_EXTRACT
    FEEDING --> FEATURE_EXTRACT
    FORAGING --> FEATURE_EXTRACT
    GROWTH --> FEATURE_EXTRACT
    
    FEATURE_EXTRACT --> BEHAVIOR_ANALYSIS
    BEHAVIOR_ANALYSIS --> MODEL_COMPARE
    MODEL_COMPARE --> STATISTICAL
    
    STATISTICAL --> VISUALIZATION
    STATISTICAL --> VIDEO_EXPORT
    STATISTICAL --> DATA_EXPORT
    STATISTICAL --> REPORTS
```

## 10. Class Hierarchy and Inheritance Diagram

```mermaid
classDiagram
    class NestedConf {
        +unique_id: str
        +__init__(model, unique_id, **kwargs)
        +setup(**kwargs)
    }
    
    class Object {
        +id: str
        +type: str
        +log: dict
        +model: object
        +p: object
        +__repr__()
        +__getattr__(key)
        +__getitem__(key)
        +__setitem__(key, value)
        +vars
        +_log
        +extend_log(l, k, N, v)
        +connect_log(ls)
        +nest_record(reporter_dic)
    }
    
    class GroupedObject {
        +group_id: str
        +group: object
    }
    
    class NonSpatialAgent {
        +agent_type: str
    }
    
    class PointAgent {
        +pos: tuple
        +radius: float
        +draw(v: ScreenManager)
    }
    
    class OrientedAgent {
        +orientation: float
        +initial_orientation: float
    }
    
    class MobileAgent {
        +initial_pos: tuple
        +trajectory: list
        +orientation_trajectory: list
        +cum_dur: float
        +move()
        +step()
    }
    
    class Larva {
        +trajectory: list
        +orientation_trajectory: list
        +cum_dur: float
        +draw(v: ScreenManager)
    }
    
    class LarvaContoured {
        +contour: Contour
        +body_contour: list
    }
    
    class LarvaSegmented {
        +segments: list
        +body_segments: list
        +sensors: list
    }
    
    class LarvaMotile {
        +modules: dict
        +brain: Brain
        +locomotor: Locomotor
        +step()
        +update_modules()
    }
    
    class LarvaSim {
        +modules: dict
        +brain: Brain
        +locomotor: Locomotor
        +step()
        +update_modules()
    }
    
    class LarvaRobot {
        +genome: dict
        +fitness: float
    }
    
    class LarvaReplay {
        +replay_data: dict
        +current_step: int
        +replay_step()
    }
    
    class LarvaOffline {
        +offline_data: dict
        +process_offline()
    }
    
    class Source {
        +source_type: str
        +value: float
        +position: tuple
    }
    
    class Food {
        +food_type: str
        +nutritional_value: float
        +consumed: bool
    }
    
    class BrainModule {
        +modules: dict
        +oscillators: dict
        +sensors: dict
        +update()
        +process_sensory_input()
    }
    
    class Brain {
        +oscillators: dict
        +sensors: dict
        +memory: Memory
        +update()
        +process_sensory_input()
    }
    
    class Locomotor {
        +crawler: Crawler
        +turner: Turner
        +feeder: Feeder
        +intermitter: Intermitter
        +update()
        +execute_motor_commands()
    }
    
    class DEB_model {
        +energy_reserve: float
        +growth_rate: float
        +metabolism: float
        +update()
        +calculate_energy_balance()
    }
    
    class DEB_basic {
        +basic_parameters: dict
        +simplified_model: bool
    }
    
    NestedConf <|-- Object
    Object <|-- GroupedObject
    GroupedObject <|-- NonSpatialAgent
    NonSpatialAgent <|-- PointAgent
    PointAgent <|-- OrientedAgent
    OrientedAgent <|-- MobileAgent
    MobileAgent <|-- Larva
    Larva <|-- LarvaContoured
    Larva <|-- LarvaSegmented
    LarvaSegmented <|-- LarvaMotile
    LarvaMotile <|-- LarvaSim
    LarvaSim <|-- LarvaRobot
    LarvaSim <|-- LarvaReplay
    LarvaSim <|-- LarvaOffline
    
    Object <|-- Source
    Source <|-- Food
    
    NestedConf <|-- BrainModule
    BrainModule <|-- Brain
    NestedConf <|-- Locomotor
    NestedConf <|-- DEB_model
    DEB_model <|-- DEB_basic
```

## Diagram Descriptions

### 1. Project Structure Diagram
Shows the hierarchical structure of the project with main folders and files. Larvaworld has a clean modular structure with separate modules for CLI, GUI, dashboards, and the core library.

### 2. System Architecture Diagram
Illustrates the high-level system architecture with main layers:
- **User Interface Layer**: CLI, GUI, Web interfaces
- **Application Layer**: Simulation engine, batch processing, genetic algorithms
- **Core Model Layer**: Agent system, environment, behavioral modules
- **Data Processing**: Import, analysis, visualization

### 3. Larva Model Architecture
Shows the internal structure of the Larva Agent with main components:
- **Physical Body**: Segmented body with sensors and mouth
- **Neural System**: Brain, oscillators, memory
- **Behavioral Modules**: Crawler, feeder, turner, intermitter
- **Energy System**: Dynamic Energy Budget (DEB) model
- **Motor Control**: Motor controller and locomotor

### 4. Data Flow Diagram
Illustrates the data flow from input sources to output results, showing processing stages, simulation, and analysis.

### 5. Module Interaction Diagram
Shows the interaction between modules during a simulation, with sequence diagram illustrating command and response flow.

### 6. Technology Stack Diagram
Illustrates all technologies and libraries used by the project, organized into categories like frontend, core framework, scientific computing, visualization, etc.

### 7. Behavioral Modules Detailed Architecture
Illustrates the detailed architecture of larvaworld's behavioral modules, showing:
- **Oscillator System**: Basic oscillators for crawling, bending, and feeding
- **Motor Control System**: Controllers that convert oscillator signals to motor commands
- **Sensor System**: Various sensors (olfactory, touch, proprioception)
- **Behavioral Coordination**: Modules that coordinate behavior
- **Neural Processing**: Brain and memory modules
- **Energy & Metabolism**: DEB model and foraging phenotypes

### 8. Environment and Arena Architecture
Shows the environment system architecture with:
- **Environment Types**: Arena, maze environments
- **Arena Components**: Boundaries, food sources, odor sources, obstacles
- **Spatial Distributions**: XY distributions and spatial parameters
- **Dynamic Elements**: Moving objects and dynamic odorscapes

### 9. Simulation Modes and Workflows
Illustrates different simulation modes and workflows:
- **Simulation Modes**: Single, batch, genetic algorithm, evaluation, replay
- **Experiment Types**: Various experiment types
- **Analysis Pipeline**: Data analysis pipeline
- **Output Generation**: Various system outputs

### 10. Class Hierarchy and Inheritance Diagram
Illustrates the class hierarchy and inheritance relationships in the larvaworld project:

**Base Classes:**
- **NestedConf**: Base class for all parameterized objects
- **Object**: Base class for all ABM objects
- **GroupedObject**: Class for objects belonging to groups

**Agent Hierarchy:**
- **NonSpatialAgent**: Base class for agents
- **PointAgent**: Agent with position and radius
- **OrientedAgent**: Agent with orientation
- **MobileAgent**: Agent that can move
- **Larva**: Base class for larva agents

**Larva Specializations:**
- **LarvaContoured**: Larva with contour representation
- **LarvaSegmented**: Larva with segmented body
- **LarvaMotile**: Larva with motor capabilities
- **LarvaSim**: Larva for simulations
- **LarvaRobot**: Larva for genetic algorithms
- **LarvaReplay**: Larva for replay experiments
- **LarvaOffline**: Larva for offline processing

**Environment Objects:**
- **Source**: Base class for sources
- **Food**: Specialized source for food

**Behavioral Modules:**
- **BrainModule**: Base class for brain modules
- **Brain**: Main brain implementation
- **Locomotor**: Motor control system
- **DEB_model**: Dynamic Energy Budget model
- **DEB_basic**: Simplified DEB implementation

These diagrams provide a comprehensive view of the larvaworld project architecture and help understand its structure and functionality.
