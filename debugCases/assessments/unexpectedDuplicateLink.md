# unexpectedDuplicateLink

## Situation

A and B are linked twice instead of once.

![unexpectedDuplicateLink flowchart](../story_flowcharts/unexpectedDuplicateLink.png)


## To try it out:

`sst --interactive-start unexpectedDuplicateLink.py`

-or-

`./doit unexpectedDuplicateLink`

## Approach 1 --

I don't know of any real way to detect this using the SST debugger. You can, however, visualize the topology using SST directly:

```
sst --output-dot=missingLink.dot ./runStory.py -- unexpectedDuplicateLink
dot -Tpng unexpectedDuplicateLink.dot > unexpectedDuplicateLink.png
```

In a real use case the situation there would likely be some other bug (like a misrouted message) that would lead the user to suspect there could be a topology issue.