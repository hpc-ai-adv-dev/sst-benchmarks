# findStarvedComponent

## Situation

The intended pattern is that all components should receive work, but one does not; in the current ring with uneven send quotas, C receives no events while the others do.

![findStarvedComponent flowchart](../story_flowcharts/findStarvedComponent.png)


## To try it out:

`sst --interactive-start findStarvedComponent.py`

-or-

`./doit findStarvedComponent`

## Approach 1 -- Run to completion, examine visited counts

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
 value = 0 (int)
 visited = 3 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 2 (int)
 visited = 0 (int)
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 2 (int)
 visited = 2 (int)
```

TODO:
- Update illustrating to show ring topology
- Ideally we could run the simulation until end
- Would be annoying to have to query every component indivually. I really want some sort of query like "show me all components where visited == 0".