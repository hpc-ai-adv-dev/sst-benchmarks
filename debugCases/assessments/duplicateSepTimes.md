# duplicateSepTimes

## Situation

D is expected to receive a given event once, but A injects it at setup and again on later ticks, so repeated deliveries occur at different times.

![duplicateSepTimes flowchart](../story_flowcharts/duplicateSepTimes.png)


## To try it out:

`sst --interactive-start duplicateSepTimes.py`

-or-

`./doit duplicateSepTimes`

## Approach 1 --

I can run to completion and observe that **D** has received multiple events.

```
Entering interactive mode at time 0
Interactive start at 0
> run 10ns
Entering interactive mode at time 10000
Ran clock for 10000 sim cycles
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 2 (int)
```

If I restart, I can switch to observing when the events are originally constructed from **A**.

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
> run 1ns
Entering interactive mode at time 1000
Ran clock for 1000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 1ns
Entering interactive mode at time 2000
Ran clock for 1000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 2 (int)
```


Notes:
- Would probably be good to use tracepoints to see when events get built at A and received by D.