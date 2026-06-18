# outOfOrderReceipt

## Situation

E is intended to see `ev1` before `ev2`, but two events launched on different branches arrive in the opposite order because C starts at `3ns` while A starts at `5ns` (with all links at `1ns`).

Notes: Events are tagged by source (`A -> 1`, `C -> 2`), and nodes writes the received tag into its `value` field on each arrival, so you can watch `E.value` change in arrival order.

![outOfOrderReceipt flowchart](../story_flowcharts/outOfOrderReceipt.png)

## To try it out:

`sst --interactive-start outOfOrderReceipt.py`

-or-

`./doit outOfOrderReceipt`

## Approach 1 -- tracepoint

```
# The test changes `value` to the last event that was visited. Our expectation is
# to see E's value change from 0 (unset) to 1, to 2. Does that happen?
cd E
trace value changed : 5 5 : value : printStatus
run 12ns            # This is sufficiently long to see 'E' receive its messages.
printTrace 0
```

Let's now run this and observe the output from the SST debugger:

```
Entering interactive mode at time 0
Interactive start at 0
> cd E
> trace value changed : 5 5 : value : printStatus
Added watchpoint #0
> run 12ns
Entering interactive mode at time 12000
Ran clock for 12000 sim cycles
> printTrace 0
TriggerRecord:@cycle7000: samples lost = 0: E/value=1
buf[0] BE @5000 (-) E/value=0
buf[1] AE @5000 (!) E/value=2
buf[2] BE @7000 (+) E/value=2
buf[3] AE @7000 (+) E/value=1
```

## Thoughts and wishlist items

[TODO]