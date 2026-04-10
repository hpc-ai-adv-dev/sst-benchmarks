# indirectDeadlock

## Situation

This is the same wait cycle as direct deadlock, but with B sitting between A and C as a relay, so the blocked endpoints are separated by an intermediate component.

![indirectDeadlock flowchart](../story_flowcharts/indirectDeadlock.png)


## To try it out:

'''
sst --interactive-start indirectDeadlock.py
'''

-or-

'''
./doit indirectDeadlock
'''

## Approach 1 --

```
```
