# findSlowProcessingComponent

## Situation

One component should be noticeably slower at processing than the others; all nodes send one event at startup to their right neighbor, but the event received by B takes much longer to process.

![findSlowProcessingComponent flowchart](../story_flowcharts/findSlowProcessingComponent.png)


## To try it out:

`sst --interactive-start findSlowProcessingComponent.py`

-or-

`./doit findSlowProcessingComponent`

## Approach 1 --

```
```

TODO:
- Update the image to show the ring topology.
- I'm unsure how to verify this. I'm not sure the debugger as it exists today can help with this.