# badMerge

## Situation

C receives values from A and B and should merge them correctly, but it multiplies `10 * 2` instead of performing the intended add-style merge before sending the result to D.

![badMerge flowchart](../story_flowcharts/badMerge.png)


## To try it out:

`sst --interactive-start badMerge.py`

-or-

`./doit badMerge`

## Approach 1 -- inspect component after merge

```
p A         # At startup we see A has an event
p B         # As does B
run 2ns     # We advance 2ns so C will receive and have processed the events
p C         # We see that 2 events have been processed but the result is unexpected
run 1ns     # If we advance again we can see what value gets to D
p D         # And it's still the bad merged value
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
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
> run 2ns
Entering interactive mode at time 2000
Ran clock for 2000 sim cycles
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 20 (int)
 visited = 2 (int)
> run 1ns
Entering interactive mode at time 3000
Ran clock for 1000 sim cycles
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 20 (int)
 visited = 1 (int)
```

NOTES:
- Ideally for this we would want to be able to examine the contents of incoming messages so we knew their values.
    - I should set value on startup on nodes A and B to show what they'll assign to the event. 
- We expect to see 10 + 2 instead of 10 * 2.