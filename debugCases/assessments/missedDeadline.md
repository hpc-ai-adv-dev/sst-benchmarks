# missedDeadline

## Situation

D is expected to receive an event by a target time, but the A -> B -> C -> D path uses enough link latency that arrival is late; the goal is to locate which link is causing the slowdown.

![missedDeadline flowchart](../story_flowcharts/missedDeadline.png)


## To try it out:

`sst --interactive-start missedDeadline.py`

-or-

`./doit missedDeadline`

## Approach 1 -- run step by step and print

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
> run 11ns
Entering interactive mode at time 11000
Ran clock for 11000 sim cycles
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 10ns
Entering interactive mode at time 21000
Ran clock for 10000 sim cycles
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 0 (int)
> run 10ns
Entering interactive mode at time 31000
Ran clock for 10000 sim cycles
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
```
