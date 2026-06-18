# badInitialState

## Situation

Four unconnected components are intended to initialize to the same state, but C starts with a different value than the others.

![badInitialState flowchart](../story_flowcharts/badInitialState.png)


## To try it out:

```
sst --interactive-start badInitialState.py
```

-or-

```
./doit badInitialState
```

## Approach 1 -- print on startup

It's pretty easy to just start things up and print the state of every componnet

```
# Print state of all components in the simulation:
p A
p B
p C     # x.value is not what we expect!
p D
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
 value = 1 (int)
 visited = 0 (int)
> p B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
> p C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 3 (int)
 visited = 0 (int)
> p D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 1 (int)
 visited = 0 (int)
```

## Thoughts and wishlist items

### Apply validation function to all components

[TODO]

Maybe a more ambitious ask. But it would nice if I could supply some kind of validation function and then ask to apply it to some set of components.