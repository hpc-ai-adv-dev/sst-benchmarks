# broadcastStorm

## Situation

An event is broadcast too broadly from A to all six neighbors at startup.

![broadcastStorm flowchart](../story_flowcharts/broadcastStorm.png)


## To try it out:

`sst --interactive-start broadcastStorm.py`

-or-

`./doit broadcastStorm`

## Approach 1 -- print values of neighbors

```
> run 2ns # Let's move forward long enough for all events to be pushed and processed

# We now observe all of A's neighboring components to see that they have received an event
> p B
> p C
> p D
> p E
> p F
> p G
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
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
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> p E
E (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = E (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> p F
F (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = F (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> p G
G (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = G (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
```
