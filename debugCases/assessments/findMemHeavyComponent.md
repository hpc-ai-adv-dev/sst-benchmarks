# findMemHeavyComponent

## Situation

The goal is to spot a component with unusually high memory usage; four unconnected components allocate different local buffer sizes, with B holding by far the largest payload.

![findMemHeavyComponent flowchart](../story_flowcharts/findMemHeavyComponent.png)


## To try it out:

`sst --interactive-start findMemHeavyComponent.py`

-or-

`./doit findMemHeavyComponent`

## Approach 1 --

```
```

TODO:
- I'm not sure how to approach this with the debugger. One could imagine the object having information that correlates with size that could be printed out.