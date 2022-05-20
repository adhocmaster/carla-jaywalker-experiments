# Planner

Every pedestrian has a planner which manages the behavior models of the pedestrian. The overall structure is explained in [How-to-use](./How-to-use.md).


# Improvement ideas:

1. Suppose we want to turn of some of the factors (force models) for some time. These can be done in two different ways at the planner level. 
   1. Using coefficients for factors: We can define the coefficients at the force model level which can be manipulated from outside of the planner. However, this will get complicated when multiple sources change the coefficients simultaneously. But we can turn off a factor by setting its coefficient to zero.
   2. Measuring the right value of the coefficient is complicated. We can use a binary coefficients in such a case.
   3. In the forces based models, the coffecients are calibrated in such a way that force from one model has a component that can reverse the effect of another force from another model. Borrowing this idea, we can add reverse force components whenever needed.

