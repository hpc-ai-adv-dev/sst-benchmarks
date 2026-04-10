# wishlist

This document contains some general wishlist features I encountered while using the SST debugger but didn't seem tied to any specific story or class or stories.

## Allow inline comments in replay scripts

I would like to be able to put comments into debug scripts inline like this. Currently it looks like if I do this the debugger runs the simulation to completion:

```
run 2ns     # Skip past the expected event.
```

## Named tracepoints

When setting a tracepoint assign an identifier which I can use to refer to it later.

## Have a way to restart the simulation

When debugging I often found myself in a situation where I want to go back in time; perhaps insights at gained during timestep 'x' of the simulation motivate me to want to stop and inspect at time 'x - y'.  Reversing the simulation would be ideal, be asbent that being able to restart without having to exit the debugger would be helpful.  Having to exit the debugger just adds extra steps and may be particularly inconvenient if exiting implies releases shared resources that would have to then be reallocated once again on the system's job queue (e.g. slurm).

## Have a way to say run the simulation and break just before completion

It can be useful to observe the final state of a simulation by simply using `run` will cause the debugger to exit upon completion. It would be nice if there was a way to pause and examine the final state before terminating.

## More succinct trace format when I just want to observe when a variable changes

A common use case I have is to trace a single variable when it changes. Could we make the syntax to do this more verbose.
TODO: Elaborate on this wish some more.
