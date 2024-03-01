
![NavPoint Realization](./images/adaptive/stop-speed-up-slow-down.PNG)
![NavPoint Realization](./images/adaptive/flinch-retreat.PNG)
## Behavior Primitives
1. **Evasive Stop**: It represents a complete stop inside a road while crossing. %This can happen due to different factors such as a vehicle passing fast in front, occlusions, or sudden blindness due to headlights. Evasive stop lasts until the conflict is resolved. This can happen due to different factors such as a vehicle passing fast in front, occlusions, or sudden blindness due to headlights. Evasive stop lasts until the conflict is resolved. Refer to [Evasive Stop](./evasive-stop.md) for current model.

2. **Evasive Flinch**: It is similar to an Evasive Stop with an additional backward movement pattern that happens involuntarily and within a fraction of a second. %In this case, the pedestrian moves back a little bit into another lane as a physical instinct. This behavior creates a dangerous situation in the lane the pedestrian enters. In this case, the pedestrian moves back a little bit into another lane as a physical instinct. This behavior creates a dangerous situation in the lane the pedestrian enters.
3. **Evasive Retreat**: In this one, the pedestrian voluntarily moves back until they are safe from an approaching vehicle which can take a few seconds.
4. **Evasive Speedup**: This primitive modifies the pedestrian's trajectory to a higher speed to evade the approaching vehicle. 
5. **Evasive Slowdown**: In this case, the pedestrian slows down to let the vehicle pass. Often this results in near-collision situations.

## Behavior Matcher

Identifying behavior primitives in trajectories is our active research topic. The primitive matching methods are constraint-based search methods over previous and next NavPoints of the NavPoint being tagged with behaviors. Unless specified all the behavior primitive has one common constraint of the current NavPoint being in front of the ego vehicle. The constraints for each primitive are set forth below: Code at [BehaviorMatcher.py](../agents/pedestrians/soft/BehaviorMatcher.py).

### Terms
<!-- $P$ = The pedestrian -->

$E$ = The ego vehicle

$N_{curr}$ = NavPoint currently being tagged

$N_{prev}$ = Previous NavPoint

$N_{next}$ = Next NavPoint

$N_{future}$ = Any future NavPoint

$dLon(X, Y)$ = distance in meters between the X and Y on the vehicle travel axis

$dLat(X, Y)$ = distance in lane-sections between the X and Y on the vehicle lateral axis

$side(X, Y)$ = Whether Y is on the left, same, or right side of X.

$frontEgo(N)$ = Navpoint N is in front of the Ego

$behindEgo(N)$ = Navpoint N is behind the Ego

$speed(N)$ = Pedestrian Speed at the NavPoint

$direction(X, Y)$ = direction from X to Y

$angle(X, Y)$ = angle between X and Y in degrees

$between(N_a, N_b)$ = A NavPoint between NavPoint a and b in time



1. **Evasive Stop**: the NavPoint a speed less than the evasive stop threshold (defaults to 0.1 m/s). 
$$
Stop(N) = 
    \begin{cases} 
    True \mid speed(N) < Threshold_{stop} \\
    False \mid Otherwise
    \end{cases}
$$
2. **Evasive Flinch**: all of the following must hold: All of the following must hold: 
    - The previous and the next NavPoints are on the same side of the current one.
    - The next NavPoint is at under lateral displacement threshold (defaults to one lane section distance) from the current.
    - The previous and the next NavPoints are under displacement threshold along the vehicle travel axis (defaults to 0.5 meters). 
$$
Flinch(N)= 
    \begin{cases} 
    True \mid \begin{split}
                side(N_{curr}, N_{prev}) ==  side(N_{curr}, N_{next}) \\
                \wedge \; dLat(N_{curr}, N_{next}) < Threshold_{flinch\_lat}\\
                \wedge \; dLon(N_{next}, N_{prev})\\
                < Threshold_{flinch\_lon}
              \end{split}
    \\
    False \mid Otherwise
    \end{cases}
$$

3. **Evasive Retreat**: There is a future NavPoint at over lateral displacement threshold (defaults to two lane section distance) from the current and: 
    - and the future NavPoint and the previous NavPoint of the current must be on the same side of the current.
    - and the future NavPoint and the previous NavPoint of the current are under displacement threshold along the vehicle travel axis (defaults to 0.5 meters). 
$$
Retreat(N)= 
    \begin{cases} 
    True \mid \exists N_{future} \mid \begin{split}
                dLat(N_{curr}, N_{future}) > Threshold_{retreat\_lat}\\
                \wedge \; side(N_{curr}, N_{prev}) ==  side(N_{curr}, N_{future}) \\
                \wedge \; dLon(N_{future}, N_{prev})\\ < Threshold_{retreat\_lon}
              \end{split}
    \\
    False \mid Otherwise
    \end{cases}
$$

4. **Evasive Speedup**: all of the following must hold: 
    - There exists a future NavPoint which is in front of the vehicle and on the vehicle lane.
    - That future NavPoint has a higher speed than the current.
    - The direction from the current and the future is the same as the pedestrian's crossing direction.
    - No other NavPoint between the current and the future
$$
Speedup(N)= 
    \begin{cases} 
    True \mid \exists N_{future} \mid \begin{split}
                frontEgo(N_{future})\\
                \wedge \; speed(N_{future}) > speed(N_{curr}) \\
                \wedge \; side(Ego, N_{curr}) <>  side(Ego, N_{future}) \\
                \wedge \; angle(direction(N_{curr}, N_{future}), direction(N_{first}, N_{last})) < 90^{\circ}\\
                between(N_{curr}, N_{future}) == null
              \end{split}
    \\
    False \mid Otherwise
    \end{cases}
$$

5. **Evasive Slowdown**: In this case there is a future NavPoint which:  
    - is on the same side as the current.
    - lower speed than the current.
    - has no future NavPoints in front of the ego.
    - current is within a threshold later distance from the Ego
    - The direction from the current and the future is the same as the pedestrian's crossing direction.
$$
Slowdown(N)= 
    \begin{cases} 
    True \mid \exists N_{future} \mid \begin{split}
                speed(N_{future}) < speed(N_{curr}) \\
                \wedge \; side(Ego, N_{curr}) == side(Ego, N_{future}) \\
                \wedge \; angle(direction(N_{curr}, N_{future}), direction(N_{first}, N_{last})) < 90^{\circ}\\
                \wedge \; \nexists N_{future2} \mid frontEgo(N_{future2}) 
              \end{split}
    \\
    False \mid Otherwise
    \end{cases}
$$
### Issues with the Behavior Matcher
1. **Conflicting Behaviors:** A NavPoint can have multiple Behavior Primitive candidates. For instance, a pedestrian might momentarily stop and then begin retreating. In such cases, the Behavior Matcher tags the NavPoint with Evasive Retreat only. However, based on real-world scenarios it may also make sense to choose Stop over Retreat, so ordering is exposed as a parameter of the Behavior Matcher. The default priority is as follows (higher mentioned earlier): *Retreat > Flinch > Stop > Speedup > Slowdown*.
