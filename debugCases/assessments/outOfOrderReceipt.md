# outOfOrderReceipt

## Situation

E is intended to see `ev1` before `ev2`, but two events launched on different branches arrive in the opposite order because C starts at `3ns` while A starts at `5ns` (with all links at `1ns`).

![outOfOrderReceipt flowchart](../story_flowcharts/outOfOrderReceipt.png)


## To try it out:

`sst --interactive-start outOfOrderReceipt.py`

-or-

`./doit outOfOrderReceipt`

## Approach 1 -- tracepoint

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
TriggerRecord:@cycle4000: samples lost = 0: D/visited=2
buf[1] AC @1000 (-) D/visited=0
buf[2] BE @3000 (-) D/visited=0
buf[3] AE @3000 (!) D/visited=1
buf[4] BE @4000 (+) D/visited=1
buf[0] AE @4000 (+) D/visited=2
```

Similiarly, we can examine at the originating end.

```
Entering interactive mode at time 0
Interactive start at 0
> cd A
> trace visited changed : 5 5 : visited : printTrace
Added watchpoint #0
> run 10ns
Entering interactive mode at time 10000
Ran clock for 10000 sim cycles
> printTrace 0
TriggerRecord:@cycle1000: samples lost = 0: A/visited=2
buf[0] BC @1000 (-) A/visited=1
buf[1] AC @1000 (!) A/visited=2
```