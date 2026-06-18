# Wish List

This document contains some general wishlist features I encountered while using the SST debugger but didn't seem tied to any specific story or class or stories.

It also includes a [catalog of wishlist seen within the use case reports](#items-from-use-case-reports).

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

# Items from use case reports

- Apply validation function to all components ([badInitialState](badInitialState.md#thoughts-and-wishlist-items))
- Specify an invariant, break when invalid ([badInvariantBetweenComponents](badInvariantBetweenComponents.md#thoughts-and-wishlist-items))
- Stepping through individual events being processed ([badMerge](badMerge.md#thoughts-and-wishlist-items))
- Add a "run until termination without quitting" option ([badTerminatingState](badTerminatingState.md#thoughts-and-wishlist-items))
- Breaking on a component receiving on sending a number of messages ([broadcastStorm](broadcastStorm.md#thoughts-and-wishlist-items), [duplicateSameTime](duplicateSameTime.md#thoughts-and-wishlist-items))
- Keeping a log of when events were sent from a component over time would be useful ([broadcastStorm](broadcastStorm.md#thoughts-and-wishlist-items))
- Print component and event being processed upon failure ([componentCausesSegfault](componentCausesSegfault.md#thoughts-and-wishlist-items))
- Set a watch for when two components diverge ([componentsLoseParity](componentsLoseParity.md#thoughts-and-wishlist-items))
- Printing the validity state of all components would be useful ([detectWhenComponentBecomesInvalid](detectWhenComponentBecomesInvalid.md#thoughts-and-wishlist-items))
- Print completion state of a component ([determineWhatNotComplete](determineWhatNotComplete.md#thoughts-and-wishlist-items))
- A metadebugger to establish invariants between models ([divergedModels](divergedModels.md#thoughts-and-wishlist-items))
- Being able to break on receipt of an event would be useful ([duplicateSepTimes](duplicateSepTimes.md#thoughts-and-wishlist-items))
- Keep counters of events processed ([findEventHeavyComponent](findEventHeavyComponent.md#thoughts-and-wishlist-items), [findStarvedComponent](findStarvedComponent.md#thoughts-and-wishlist-items))
- Stop upon completion of a given (or any) component ([findFirstToComplete](findFirstToComplete.md#thoughts-and-wishlist-items))
- Have a way to query if any component has not processed events ([findStarvedComponent](findStarvedComponent.md#thoughts-and-wishlist-items))
- Have a way to query the component(s) that have processed the least (or most) events ([findStarvedComponent](findStarvedComponent.md#thoughts-and-wishlist-items))
- Being able to assess event lifetime would be useful ([infiniteLoop](infiniteLoop.md#thoughts-and-wishlist-items))
- Discovery of neighbors ([missingLink](missingLink.md#thoughts-and-wishlist-items), [unexpectedDuplicateLink](unexpectedDuplicateLink.md#thoughts-and-wishlist-items), [wrongLink](wrongLink.md#thoughts-and-wishlist-items), [wrongPath](wrongPath.md#thoughts-and-wishlist-items))
- Print the topology from within the debugger ([missingLink](missingLink.md#thoughts-and-wishlist-items))
- Break when event is deleted ([unexpectedDisappear](unexpectedDisappear.md#thoughts-and-wishlist-items))
- Emit the topology from within the debugger ([unexpectedDuplicateLink](unexpectedDuplicateLink.md#thoughts-and-wishlist-items), [wrongLink](wrongLink.md#thoughts-and-wishlist-items))
- A question: should the debugger break before or after events are processed? ([wrongPath](wrongPath.md#thoughts-and-wishlist-items))
- Pending event queue inspection ([wrongPath](wrongPath.md#thoughts-and-wishlist-items))
- Bulk queries across neighbors ([wrongPath](wrongPath.md#thoughts-and-wishlist-items))
- Bulk queries across tracepoints ([wrongPath](wrongPath.md#thoughts-and-wishlist-items))
- Event-centric debugging ([wrongPath](wrongPath.md#thoughts-and-wishlist-items))

NOTE: to update this table you can use the `update_wishlist_form_reports.pys` script.