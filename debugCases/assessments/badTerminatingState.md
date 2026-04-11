# badTerminatingState

## Situation

Similar to `badInitialState`, but the issue is that C changes to a different value before the simulation terminates. The goal is to identify which component has the bad value just prior to termination.

![badTerminatingState flowchart](../story_flowcharts/badTerminatingState.png)


## To try it out:

`sst --interactive-start badTerminatingState.py`

-or-

`./doit badTerminatingState`

## Approach 1 -- Print prior to termination

We'll run the simulation to completion and then observe the state of all components:

```
run 1000ns
p A
p B
p C     # x.value is 3 when we expect it to be 1!
p D
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> run 1000ns
Entering interactive mode at time 1000000
Ran clock for 1000000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 3 (int)
 visited = 0 (int)
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> run 1ns
Simulation is complete, simulated time: 1 us
```

- I don't think there's anyway to do this precisely (at termination) you can only do it at the clock cycle before.
- I think we should update the image to show that c is the component with the bad state not B.