# Microscopic Behavior Models

Microscopic Behavior Models are pluggable models to our Pedestrian Agent. They capture different kinds of events and interactions. These models are highly interactive and adapts to different situations, implemented with rule-based and physics-based approaches.

1. **Destination Model** - it creates an attractive force toward the destination based on Helbing's social-force-based approach.
2. **Oncoming Vehicle Model** - it captures the event where a pedestrian speeds up to cross in front of an approaching vehicle.
3. **Evasive Stop Model** - it captures the event where pedestrian makes an stop to let the approaching vehicle pass.
4. **Drunken Model** - it captures the event where the pedestrian follows a sinosuidal direction change to mimmic a drunk trajectory.
