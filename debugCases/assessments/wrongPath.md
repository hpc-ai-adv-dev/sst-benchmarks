# wrongPath

## Situation

An event propagates throughout the model, its intended path is A -> B -> C, but B misroutes the event to D instead.  All links in the simulation have a 1ns latency.

![wrongPath flowchart](../story_flowcharts/wrongPath.png)

## To try it out:

`sst --interactive-start --stop-at 10ns wrongPath.py`

-or-

`./doit wrongPath`

## Summary

## Approach 1 -- step by step

In this approach we manually step through the simulation one nanosecond at a time, checking each component's `visited` counter after each step. We run 2ns initially to ensure the first event is fully processed, then step 1ns at a time, printing the state of A, B, C, and D in turn. When C's counter turns out to be 0 but D's is nonzero, we've identified the misrouted hop and so we print out D instead.

```
print A         # We see the event has been setup
run 2ns         # We need to wait 2ns before we can observe that component B has received it
print B         # Yep, we can see component B has received it
run 1ns         # Advance to the next timestep
print C         # Here we expect to see that C has received it, but it hasn't!
print D         # Instead we see it at component D
```

Let's run this, and observing the output:

```
Entering interactive mode at time 0
Interactive start at 0
```

At this point, let's assume I know that the event I want to trace starts at 'A'. I'll print it and note that when the simulation starts we have 'visited' already set. As the event propagates through the model it will increment 'visited' on each component. Although I don't do it in this example, if we wanted to we could print the others nodes in the simulation (e.g. print B; print C) and also observe that their 'visited' value are still 0.

```
> print A
A (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = A (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
```

Next we'll advance the simulation by 2ns and observe the state of A's neighbor, B.  This is necessary because although the event will be received by the next component on the next simulated nanosecond, the debugger stops before the event is processed. So we advance a second nanosecond before observing B:

```
> run 2ns
Entering interactive mode at time 2000
Ran clock for 2000 sim cycles
> print B
B (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = B (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
```

And indeed we see that `B.visited` is 1 as expected. We proceed another nanosecond and observe where we expect the message will be sent, which in this case is 'C'.

```
> run 1ns
Entering interactive mode at time 3000
Ran clock for 1000 sim cycles
> print C
C (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = C (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 0 (int)
```

But what is this? C.visited is 0!  This is our unexpected behavior, now observed by the debugger.

Given that C.visited wasn't set we'll check to see if the event was processed by one of B's neighbors instead. In this case we know B only has one other neighbor: D. So we print that out:

```
> print D
D (SST::Component)
 component_state_ = 3 (SST::BaseComponent::ComponentState)
 my_info_ ()
 my_info_ (SST::ComponentInfo*)
 name = D (std::string)
 valid = 1 (bool)
 value = 0 (int)
 visited = 1 (int)
```

And indeed we see `D.visited = 1`, showing where the event was misrouted to.

## Approach 2 -- tracepoints on all components

Rather than stepping manually, we set a tracepoint on the `visited` field of every component before the simulation runs. After running the full simulation we print each trace to see exactly when this field was modified, revealing that D was visited instead of C.

```
# We start by setting tracepoints on the 'visited' property of all components in the simulation
cd A
trace visited changed : 5 5 : visited : printStatus
cd ..
cd B
trace visited changed : 5 5 : visited : printStatus
cd ..
cd C
trace visited changed : 5 5 : visited : printStatus
cd ..
cd D
trace visited changed : 5 5 : visited : printStatus
cd ..

# Then we advance the simulation long enough that we could observe the misroute
run 4ns

# Finally we output all traces to see what really happened.
printTrace 0
printTrace 1
printTrace 2
printTrace 3
```

## Thoughts and wishlist items

### A question: should the debugger run until just before or just after events are processed?

In Approach 1, I observe that after SST's setup phase, component A has already been visited, which in this implementation is a side effect of creating the event. After a component receives the event it increments its `visited` property to 1. However, although the link latency between components A and B is 1ns, I have to run the simulation for 2ns in order to observe that component B has received the event.

This is because at timestep 1ns, although component B has received the event, it has not yet processed it. So in order to observe I have to advance the simulation by an additional 1ns. This raises a question: is this the desired behavior? Should the debugger process all pending events before stopping? If not, should there be a way to flush pending events without advancing simulation time?

Perhaps we could have a special `flushEvents` command:

```
> print A.value
A.value = 0 (int)

> run 1ns
> print A.value
A.value = 1 (int)

> flushEvents
```

Or alternatively, could we use `run 0ns` to accomplish this?


### Discovery of neighbors

In the first approach, I know the topology ahead of time, so after examining component 'A' I know that it makes sense to examine component 'B'.  After examinining component B I in turn examine component C, and failing that I know I should look at B's others neighbors, which in this case I knew was 'D'. 

In a real-world use case the topology might be more complicated.  It may be useful if the debugger had ways of examining the connectivity of a component.

```
> print A.neighbors
port0 -> B/ (SST::Component)

> print B.neighbors
port0 -> A
port1 -> C
port2 -> D
```

Similarly, imagine if component B were connected to several more neighbors. Manually printing the `visited` property under each might be tedious. Maybe there could be some syntax that would let me say "print the 'value' property in all my neighbors" in one shot:

```
> print B.neighbors/visited

A.visited = 1
C.visited = 0
D.visited = 1
```

### Event-centric debugging

The SST debugger is focused on a "component centric" view of the simulation.  It has features to examine and attach watchpoints to components, but for scenarios where the user is interested in monitoring the flow of a specific event throughout the simulation it might be better if the event itself were treated as a kind of "first class object" within the debugger.

Because of the lack of such an "event centric" view, in order to model this story I had the event perform a side effect of setting a visited counter on a component so that I could detect it.

Imagine being able to do something like the following to identify an event and then trace its path:

```
> print A.events

A (SST::Component)
  outgoing events:
    port0/UseCaseEvent_0000000

  incoming events:
    <none>

> trace UseCaseEvent_0000000
> run 4ns
> printTrace 0

@1000 UseCaseEvent_0000000 received by B/port0
@1000 UseCaseEvent_0000000 send out by B/port1
@2000 UseCaseEvent_0000000 received by B
```

Some additional thoughts:
- It's not clear how we would identify events in the debugger as unlike components, events don't necessarily have a name attached to them. Nevertheless, we could imagine coming up with some kind of artificial identifier, perhaps based on the event type name and when and where it was built? Or perhaps we could make it a hash of the event type and its properties?
