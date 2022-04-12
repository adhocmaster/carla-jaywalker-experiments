# Two ways:

1. On episode learning: changes parameters during and episode
2. Off episode learning: works at the strategic level.

## Some simple ideas:

1. State = {TG, TTC, walker-distance-to-conflict-point, walker-speed-towards-conflict-point, walker-speed-orthogonal-to-conflict-point}, reward = TG/TTC/Survival Mode, action = {relaxation_time up, relaxation_time down}. We are hacking into urgency actually
2. State = A sequence of OGs, reward = TTC/Survival Mode, action = {relaxation_time up, relaxation_time down}. We are hacking into urgency actually. This is better for the network to learn relative movement and also road structure.


# Implementation

We follow the similar structure to Gym environments so that existing ML libraries can easily use the environment and also extend the functionality.

# Action periods
When an action is chosen, there should be some period when no other action can be taken. How fast can a pedestrian make a decision change? If they can change decision every second, then we need to wait (1/time_delta) ticks.
So, we do not need to produce a state where the agent cannot take an action?

so, env.step(action) -> returns next state when the agent can take next action.