# directDeadlock

## Situation

A waits for an event from B while B waits for an event from A, so neither side ever makes progress.

![directDeadlock flowchart](../story_flowcharts/directDeadlock.png)


## To try it out:

'''
sst --interactive-start directDeadlock.py
'''

-or-

'''
./doit directDeadlock
'''

## Approach 1 --

```
```
