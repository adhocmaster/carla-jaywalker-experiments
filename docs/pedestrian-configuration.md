# Pedestrian Instantiation

The agents for pedestrians are instantiated through [PedestrianFactory](../agents/pedestrians/PedestrianFactory.py). We have a method to create an agent with [SingleOncomingVehicleLocalPlanner](../agents/pedestrians/planner/SingleOncomingVehicleLocalPlanner.py). This factory class configures the pedestrians with their attributes (called internal factor) and a planner. For different types of pedestrians we should define a factory method for each in this factory class. The default agent is created via:

```python
def createAgent(
    self, 
    walker: carla.Walker, # walker object in the simulator.
    logLevel=logging.INFO, 
    internalFactorsPath = None, # path to the internal factor configuration. 
    optionalFactors: List[Factors] = None, # list of external factors
    config=None # used for logging and debugging configuration
    ) -> PedestrianAgent:
```

The default agent uses the default planner which is created by 
```python
def addPlanners(
        self, 
        agent: PedestrianAgent, 
        internalFactorsPath = None, 
        optionalFactors: List[Factors] = None, 
        logLevel=logging.INFO
    ):
```

Each agent essentially has a planner. So all the factors are consumed by the planner. The factory parses the all the factors and converts them into dictionaries. A planner is instantiated with the configuration dictionaries. It's necessary to override these dictionaries before the planner is instantiated as optional components of the planner are not even initialized if not required by the configuration. So, factors cannot be overriden once the planner is created. 

# Pedestrian Configuration

When we create an agent we can set its internal factors. The default internal factors are defined at [internal_factors_default.yaml](../settings/internal_factors_default.yaml) file as 

```yaml
risk_level: "risky"

# Destination related factors
relaxation_time: 0.5
desired_speed: 2
desired_distance_gap: 2
use_crosswalk_area_model: True
use_random_destination_without_intermediates: False
# desired_time_gap: 1

# speed model
speed_model: "static"
min_crossing_speed: 0.5
# set max to Usain Bolt's speed
max_crossing_speed: 10
median_crossing_speed: 1 
speed_change_probability: 0.1

# relaxation speed model
relaxation_speed_model_coeff: 1

# set this to 0 for no change
oncoming_vehicle_speed_force: 5
acceleration_positive_max: 100
acceleration_negative_min: -100

# GAP params
# for TG_multiplier underestimate TG if less than 1 and overestimate TG if > 1
TG_multiplier: 1
brewer_beta0: 6.2064
brewer_beta1: -0.9420

# survival state
threshold_ttc_survival_state: 1
survival_safety_distance: 3
```
We can create a new pedestrian type by duplicating the default internal factor file. To instantiate the agents, we can supply the path to this new configuration to the **PedestrianFactory.createAgent** method call. Or we can redefine the **addPlanners** method and override factors there.

