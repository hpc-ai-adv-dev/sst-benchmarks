# unexpectedDisappear

## Situation

The intended path is A -> B -> C -> D, but the event vanishes at C because it is never forwarded onward.

![unexpectedDisappear flowchart](../story_flowcharts/unexpectedDisappear.png)


## To try it out:

`sst --interactive-start unexpectedDisappear.py`

-or-

`./doit unexpectedDisappear`

## Approach 1 -- run step by step and print

```
p A         # We see the event has been setup
run 2ns     # We need to wait 2ns before we can observe that component B has received it
p B         # Component B has received it
run 1ns     # We take the next step
p C         # Component C has received it
run 1ns     # We take the next step
p D         # We expect D to have received it, but it has not!
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 2ns
Entering interactive mode at time 2000
Ran clock for 2000 sim cycles
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 1ns
Entering interactive mode at time 3000
Ran clock for 1000 sim cycles
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 1ns
Entering interactive mode at time 4000
Ran clock for 1000 sim cycles
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 0 (int)
```
