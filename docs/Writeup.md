## Name of the Model 
Freezing Model 

## Intended behavior of the model 
This model introduces a frozen factor in the pedestrian movement when crossing the street. This can occur in situations when the pedestrian is in shock or distracted. This is an inportant model because it defies a hug assumption that pedestrians all always in motion.
## Why this is an interesting model for testing autonomous vehicles 
This is an interesting model because it adds more real-world scenarios and diversity to the way we train autonomous checiles. We still would the car to recognize that the inanimate person is actually a pedestrian and not an object. 
This can hopefully we used to make the vehicle safer.
## How the behavior actually works 
We have an introduced a frozen factor that determines how long the pedestrian will cross. We also rely on the TTC
To create a frozen affect on the pedestrian we create a force in the opposite direction to make the summation of forces to be equivalent to 0 forcing the pedestrian to stop. 

## How the different parts of the model interact
We react with the state machine and the states. 
We introduce a Frozen State. 

Other information 

1 tick in the simulation is equivalent to 0.007 seconds. 
