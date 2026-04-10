# findStarvedComponent

## Situation

The intended pattern is that all components should receive work, but one does not; in the current ring with uneven send quotas, C receives no events while the others do.

![findStarvedComponent flowchart](../story_flowcharts/findStarvedComponent.png)


## To try it out:

'''
sst --interactive-start findStarvedComponent.py
'''

-or-

'''
./doit findStarvedComponent
'''

## Approach 1 --

```
```
