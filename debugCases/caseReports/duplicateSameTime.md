# duplicateSameTime

## Situation

B is expected to receive a given event once, but A injects it twice at setup.

![duplicateSameTime flowchart](../story_flowcharts/duplicateSameTime.png)


## To try it out:

`sst --interactive-start duplicateSameTime.py`

-or-

`./doit duplicateSameTime`

## Approach 1 -- trace sink and print source

```
# Let's watch how D.visited increments when we run the simulation to completion.
# We'll see that it has been updated twice on the same time step.
cd D
trace visited changed : 5 5 : visited : printTrace
run 10ns
printTrace 0

# - RESTART THE SIMULATION AND DEBUGGER -

# If we observe A at the start of simulation we can see it starts with two events setup
p A
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> cd D
> trace visited changed : 5 5 : visited : printTrace
Added watchpoint #0
> run 10ns
Entering interactive mode at time 10000
Ran clock for 10000 sim cycles
> printTrace 0
TriggerRecord:@cycle3000: samples lost = 0: D/visited=2
buf[0] BE @3000 (-) D/visited=0
buf[1] AE @3000 (!) D/visited=1
buf[2] BE @3000 (+) D/visited=1
buf[3] AE @3000 (+) D/visited=2
```

Similiarly, if we examine the originating end 

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
 visited = 2 (int)
```

## Thoughts and wishlist items

### Breaking on a component receiving on sending a number of messages

[TODO]

It would be nice if we could break if A sends > 1 message or if B receives more than 1.