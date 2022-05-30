
Findings / Brainstorm: 

StateTransitionManager.py: tranisition the states of the pedestrians.

SurvivalDestinationModel.py: goes back and forth base on a safe distance. 

 - canSwitchToCrossing function could be modified for our purpose,
   instead of crossing, it could be canSwitchToFreeze. We can keep the
   original code where the pedestrian return back to suriving mode.
   Having a while loop with a timer that we are going to randomize, once
   out of the loop, we will resume to surival model.
 - getNewState function seems like the place where we could include the
   new state. Creating a new time variable that is ranomized base on the
   time to cross. Secondly, we could focus on what happens after time to
   cross exhausts. Line 78 looks promising. Instead of changing to
   survival mode when pedestrian is close to a collision, we could
   transition to freeze mode. then after certain time, we could go back
   to survial mode. Maybe the transition state to survival could be
   removed to see whether car crashes into the pedestrian.
 - calculateForce function calculates the froce equation. Line 110 - 114
   would be where the force equation is calculated.

Pedutils.py: Find how long to freeze base on the waypoint. Explanation on Waypoint.




> 5/23 Notes:
- use research logs to see the weights of the forces
- default skeleton just has calc force to return none, will need to be replaced by a 3D carla vector (x, y, z)
- two functions to work on which will be freeze and unfreeze
  - have ped frozen for some amount of ticks then unfreeze
  - ttc and tg to randomize tick threshold, should be a value under tg
  - ex) randomizing the range of  (0 - ttc) 
- calculate force runs every tick, a counter can be implemented here (have while loop to count)

USE CONFLICT POINTS TO FREEZE AND TO UNFREEZE WOULD BE THE RANGE OF 0 - TCC


5/25
- implementing the pedestrian to freeze near the TTC (around when TTC is at 2 or less)
- then have pedestrian unfreeze after TTC > 10

5/30
- This model would freeze as TTC gets close. It would freeze for a randomized time. 
- Implemented the freezing zone near TTC as stated previously.
- Modified the freezingperiod from a randomized range from 5 to 20. 
- The model could unfreeze when the freezing period of zero and there is no threat (TTC is none or greater than 12) else we can want to decrease the unfreeze period.
TODO:
- figure out how to decrease according to simulation's clock
- define the unfreeze period range base on papers