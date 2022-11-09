# Environments with Gym interface

We provide Open AI Gym environment to run our research

## Usage

### Creating an environment
```
from research.adversaries.EnvironmentFactory import EnvironmentFactory, AvailableEnvironments

env = EnvironmentFactory.create(AvailableEnvironments.R1V1Env1)

```

## Implementation

### Available environments
there is a enum class that lists the available environments: **research.adversaries.EnvironmentFactory.AvailableEnvironments**

### Components

```mermaid
sequenceDiagram
    participant EF as EnvironmentFactory
    participant E as Environment
    participant RF as ResearchFactory
    participant R as Research

    Note over EF: sets client host and port
    EF->>E:create environment
    Note over E: sets mode to synchronization <br> and default log level
    E->>RF:create research
    Note over RF: sets map, settings, stats collection
    RF->>R:create
    RF-->>E: research object
    activate E
    Note over E: set tickCounter = None <br> setObsActionSpaces 
    E->>E:reset()
    E->>R:reset()
    E-->>EF: environment object
    deactivate E

```

### Environment setup

#### Creating a research in synchronized mode and collect statistics of episodes
```mermaid
flowchart TD
    init[init] --> ls[Set log path and simulation mode]
    ls --> ws[Initialize World settings]
    ws-->viz[Initialize Visualizer]
    init-->setup
    setup-->loadSettings[load settings for the map]
    loadSettings-->act[Set actor and actor agents to None]
    act-->settings[get actor spawn points, destinations]
    settings-->sim[set simulator to none]
    sim-->stats[initialize stat dictionary]
```

### Environment reset

```mermaid
sequenceDiagram
    participant E as Environment
    participant R as Research
    participant PF as PedestrianFactory
    participant VF as VehicleFactory
    participant BR as BaseResearch
    participant MM as MapManager

    activate E
    Note over E: resetting environment
    E->>R:reset()
    activate R
    R->>PF:reset()
    R->>VF:reset()
    R->>BR:reset()
    BR->>MM:reload()

    Note over R: first the vehicle <br> and then the walker is created
    R->>R:createDynamicAgents()
    R->>R:setupSimulator(episodic=True)
    deactivate R
    deactivate E
```

### Simulator lifecycle

#### Episodic simulator

```mermaid
flowchart LR
    Created --> Ticking --> Ending
    Ticking --> onTickStart --> onTick --> Ticking
```

### Environment step

```mermaid
flowchart LR
    up[update behavior] --> tick[tick until the Action is finished] --> ret[return state, done, reward, info]
```