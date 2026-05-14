# determineWhatNotComplete

## Situation

The goal is to find components that never mark complete when the simulation ought to be done; here A, D, and E finish, while B and C never do.

![determineWhatNotComplete flowchart](../story_flowcharts/determineWhatNotComplete.png)


## To try it out:

`sst --interactive-start determineWhatNotComplete.py`

-or-

`./doit determineWhatNotComplete`

## Approach 1 --

```
```

## Thoughts and wishlist items

### Print completion state of a component

TODO:
- I'm unsure how to do this with the debugger. I guess just run to when I would expect completion and then have some way to examine what components have flagged themselves complete.