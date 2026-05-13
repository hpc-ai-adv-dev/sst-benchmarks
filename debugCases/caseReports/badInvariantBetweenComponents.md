# badInvariantBetweenComponents

## Situation

A cross-component invariant is supposed to hold, but C follows a different update rule when it receives certain values, breaking the invariant.

![badInvariantBetweenComponents flowchart](../story_flowcharts/badInvariantBetweenComponents.png)


## To try it out:

`sst --interactive-start badInvariantBetweenComponents.py`

-or-

`./doit badInvariantBetweenComponents`

## Approach 1 -- print before and after invalidity

```
run 10ns   # We advance to just before the invariant is violated
p A        # A.value is 9
p B        # B.value is 19
p C        # And C.value is the sum, 28
run 1ns    # We advance to the next timestep
p A        # A.value is 10
p B        # B.value is 20
p C        # But C.value is now incorrectly set to 50!
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> run 10ns
Entering interactive mode at time 10000
Ran clock for 10000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 9 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 19 (int)
 visited = 0 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 28 (int)
 visited = 0 (int)
> run 1ns
Entering interactive mode at time 11000
Ran clock for 1000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 10 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 20 (int)
 visited = 0 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 50 (int)
 visited = 0 (int)
```

When the simulation starts we have A.value =0, B.value = 10, and C.value = 10.
Every timestep we increment A and B by 1 and C by 2 but at some point this doesn't happen. How do we detect when?
Ideally I'd be able to set a kind of conditional watchpoint that references the values of other components.
Absent that I could take a bisecting strategy to narrow down at what time this happens.

## Thoughts and wishlist items

### Specify an invariant, break when invalid