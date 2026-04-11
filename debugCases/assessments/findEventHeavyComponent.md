# findEventHeavyComponent

## Situation

The goal is to identify which component processes the most events; in this four-node ring each component sends to its neighbor to the right.

![findEventHeavyComponent flowchart](../story_flowcharts/findEventHeavyComponent.png)


## To try it out:

`sst --interactive-start findEventHeavyComponent.py`

-or-

`./doit findEventHeavyComponent`

## Approach 1 -- run to termination and print

```
run 100ns   # Run the simulation to termination
p A         # A.visited = 2
p B         # B.visited = 3, the most!
p C         # C.visited = 1
p D         # D.visited = 1
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> run 100ns
Entering interactive mode at time 100000
Ran clock for 100000 sim cycles
> p A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 3 (int)
 visited = 2 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 3 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 1 (int)
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 2 (int)
 visited = 1 (int)
```

TODO:
- The implementation arranges the nodes into a ring. Update the graphic to reflect this.