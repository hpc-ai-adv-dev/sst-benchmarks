# infiniteLoop

## Situation

An event is supposed to move onward to D, but A, B, and C keep forwarding it in a cycle, creating an infinite loop.

![infiniteLoop flowchart](../story_flowcharts/infiniteLoop.png)


## To try it out:

`sst --interactive-start infiniteLoop.py`

-or-

`./doit infiniteLoop`

## Approach 1 -- run step by step and print

```
> p A           # We see the event has been setup
> run 2ns       # We need to wait 2ns before we can observe that component B has received it
> p B           # Yep, we can see component B has received it
> run 1ns       # Allow the event to continue to propagate
> p C           # We can see that C has now received it
> run 1ns       # Allow the event to continue to propagate
> p D           # We expect D to receive it, but it has not
> p A           # Instead we see A has the event1
> run 3ns       # Let's continue three steps to see if the event will cycle again
> p A           # We see that A has no received the event multiple times (it's cycle back)
> p D           # And D still has not been visited
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
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 2 (int)
> run 3ns
Entering interactive mode at time 7000
Ran clock for 3000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 3 (int)
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