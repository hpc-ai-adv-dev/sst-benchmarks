# findFirstToComplete

## Situation

The goal is to determine which component finishes first; the completion order is D first, then B, then C, then A.

![findFirstToComplete flowchart](../story_flowcharts/findFirstToComplete.png)


## To try it out:

`sst --interactive-start findFirstToComplete.py`

-or-

`./doit findFirstToComplete`

## Approach 1 --

```
```


## Thoughts and wishlist items

### Stop upon completion of a given (or any) component

[TODO]

I'm unsure how to do this with the debugger. Ideally there would be a kind of "stop upon completion of this component" watchpoint. We could have completion tied to some side-effect that we could set up a watch point on.