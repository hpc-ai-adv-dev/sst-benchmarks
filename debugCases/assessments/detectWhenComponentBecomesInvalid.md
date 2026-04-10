# detectWhenComponentBecomesInvalid

## Situation

A starts valid and then flips its `valid` flag to false on a 40ns clock tick, modeling a component whose state becomes invalid during execution.

![detectWhenComponentBecomesInvalid flowchart](../story_flowcharts/detectWhenComponentBecomesInvalid.png)


## To try it out:

`sst --interactive-start detectWhenComponentBecomesInvalid.py`

-or-

`./doit detectWhenComponentBecomesInvalid`

## Approach 1 -- watchpoint

```
Entering interactive mode at time 0
Interactive start at 0
> cd A
> watch valid changed
Added watchpoint #0
> run
Entering interactive mode at time 40000
  WP0: AC : A/valid ...
```
