# Evasive stop

The evasive 
Current model is a piecewise force function of maximum actuation time and starting velocity of the pedestrian (*when the model is activated*). Between the start and maximum actuation time the velocity is linearly decreased every simulation step to 0. However, because of floating point errors, we add another force after the maximum actuation time to compensate for it.


$$ \vec{F}_{stop} = 
    \begin{cases} 
      \frac{(\vec{V}_{start} * (1 - \frac{t_{elasped}}{t_{max}}) - \vec{V}_{current})}{t_{delta}} 
            & t_{elasped} <= t_{max} \\
      -(\frac{\vec{V}_{current}}{t_{delta}})
            & t_{elasped} > t_{max} \\
    \end{cases}
    \\
$$

Where,

$\vec{F}_{stop}$ = force applied on the pedestrian

$t_{delta}$ = simulation timestep

$t_{elasped}$ = time elapsed since model activation

$t_{max}$ = maximum actuation time

$\vec{V}_{start}$ = starting velocity of the pedestrian

$\vec{V}_{current}$ = current velocity of the pedestrian

The maximum actuation time is uniformly sampled from [0.5, 1.5]

## Limitations

The current model unfreezes when the time-gap with the the vehicle is more than 1 second and distance to the vehicle is more than 0.5 meter. However, in real world scenario, the pedestrian can un-freeze early. See PSI 2.0, Video 0015 for an example.
