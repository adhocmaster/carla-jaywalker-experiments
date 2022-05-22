Findings / Brainstorm:
StateTransitionManager.py: tranisition the states of the pedestrians.

SurvivalDestinationModel.py: goes back and forth base on a safe distance. 
	canSwitchToCrossing function could be modified for our purpose, instead of crossing, it could be canSwitchToFreeze. We can keep the original code where the pedestrian return back to suriving mode. Having a while loop with a timer that we are going to randomize, once out of the loop, we will resume to surival model. 
	getNewState function seems like the place where we could include the new state. Creating a new time variable that is ranomized base on the time to cross. Secondly, we could focus on what happens after time to cross exhausts.
		Line 78 looks promising. Instead of changing to survival mode when pedestrian is close to a collision, we could transition to freeze mode. then after certain time, we could go back to survial mode. Maybe the transition state to survival could be removed to see whether car crashes into the pedestrian.
	calculateForce function calculates the froce equation. Line 110 - 114 would be where the force equation is calculated.
 
Pedutils.py:
	Find how long to freeze base on the waypoint. Explanation on Waypoint.
