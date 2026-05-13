# findMemHeavyEvent

## Situation

The goal is to spot an unusually large event; each node in a ring sends one rightward event with a payload buffer, and one of those messages is much larger than the others.

![findMemHeavyEvent flowchart](../story_flowcharts/findMemHeavyEvent.png)


## To try it out:

`sst --interactive-start findMemHeavyEvent.py`

-or-

`./doit findMemHeavyEvent`

## Approach 1 --

```
```

TODO:
- This seems even more difficult to do than the memory heavy component one. Ideally we'd want an event-centric view of debugging and a mechanism to query size.
- I suppose I could have the benchmark set 'value' based on the payload size, but it seems less than ideal.