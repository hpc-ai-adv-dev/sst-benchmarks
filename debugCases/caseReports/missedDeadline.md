# missedDeadline

## Situation

D is expected to receive an event by a target time, but the A -> B -> C -> D path uses enough link latency that arrival is late; the goal is to locate which link is causing the slowdown.

![missedDeadline flowchart](../story_flowcharts/missedDeadline.png)


## To try it out:

`sst --interactive-start missedDeadline.py`

-or-

`./doit missedDeadline`

## Approach 1 -- step and print

```
p A         # We see the event has been setup
run 11ns    # We expect a 10ns latency for an event to get to B. We add another ns so we can observe it
p B         # Yes, B has received the event
run 10ns    # We expect another 10ns for the message to get to C
p C         # But wait. It's not there!
run 10ns    # Let's wait some more to see if it arrives
p C         # And it has!

# From here we may want to continue to debug to narrow down specifically what timestep the message did arrive.
# Ideally, this would clue us in that link latency might be off.
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

## Approach 2 -- run to termination and bisect path

[TODO]

Note: This would depend on knowing the expected path of the event.

## Thoughts and wishlist items

[TODO]