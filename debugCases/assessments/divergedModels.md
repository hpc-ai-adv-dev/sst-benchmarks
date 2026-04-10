# divergedModels

## Situation

This story pair compares two models that are intended to retain parity throughout execution, but at timestamp 40 they diverge: `divergedModels_A` uses value 5 while `divergedModels_B` uses value 7.

![divergedModels flowchart](../story_flowcharts/divergedModels.png)


## To try it out:

```
sst --interactive-start divergedModels_A.py
sst --interactive-start divergedModels_B.py
```

-or-

```
./doit divergedModels_A
./doit divergedModels_B
```

## Approach 1 --

```
```
