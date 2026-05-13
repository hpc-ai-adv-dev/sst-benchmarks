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
# Let's watch A.valid and see when it becomes invalid
cd A
watch valid changed
run
```

Let's now run this and observe the output from the SST debugger:

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

## Thoughts and wishlist items

### Printing the validity state of all components would be useful

[TODO]