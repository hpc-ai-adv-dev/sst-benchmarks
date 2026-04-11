# wrongLink

## Situation

The intended topology is A -> B, but A is connected to C instead.

![wrongLink flowchart](../story_flowcharts/wrongLink.png)


## To try it out:

`sst --interactive-start wrongLink.py`

-or-

`./doit wrongLink`

## Approach 1 -- output DOT

I don't know of any real way to detect this using the SST debugger. You can, however, visualize the topology using SST directly:

```
sst --output-dot=missingLink.dot ./runStory.py -- wrongLink
dot -Tpng wrongLink.dot > wrongLink.png
```

![wrongLink topology visualization](./images/wrongLink.png)

In a real use case the situation there would likely be some other bug (like a misrouted message) that would lead the user to suspect there could be a topology issue.

## Thoughts and wishlist items

### Discovery of neighbors

This point was also mentioned in the wrongPath case.

### Emit the topology from within the debugger