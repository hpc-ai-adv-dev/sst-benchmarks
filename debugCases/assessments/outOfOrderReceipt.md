# outOfOrderReceipt

## Situation

E is intended to see `ev1` before `ev2`, but two events launched on different branches arrive in the opposite order because C starts at `3ns` while A starts at `5ns` (with all links at `1ns`).

![outOfOrderReceipt flowchart](../story_flowcharts/outOfOrderReceipt.png)


## To try it out:

`sst --interactive-start outOfOrderReceipt.py`

-or-

`./doit outOfOrderReceipt`

## Approach 1 -- tracepoint

TODO: I'd like to modify this test to set the value on E when it receives an event so I can tell which event it receives.
Then I want to watch it change.