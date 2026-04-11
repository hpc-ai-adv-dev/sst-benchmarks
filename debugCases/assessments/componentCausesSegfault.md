# componentCausesSegfault

## Situation

Component C asserts once its clock reaches cycle 50 or later. The goal is to identify which component is responsible for the segfault and at what point in time the segfault occurs.

![componentCausesSegfault flowchart](../story_flowcharts/componentCausesSegfault.png)


## To try it out:

`sst --interactive-start componentCausesSegfault.py`

-or-

`./doit componentCausesSegfault`

## Approach 1 -- run and fail

For this lets simply `run` the simulation and watch it fail:

```
Entering interactive mode at time 0
Interactive start at 0
> run
Assertion failed: (false), function clockTick_componentCausesSegfault, file Node.cpp, line 308.
```

Notes:
- You could certainly step through this to figure out what timestep the segfault occurs at but I'm unsure if there's any way you could figure out what component was being processed at the time it faulted.