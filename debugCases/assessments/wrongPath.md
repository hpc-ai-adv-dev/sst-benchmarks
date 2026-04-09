# wrongPath

## Situation

An event propagates throughout the model, its intended path is A -> B -> C, but B misroutes the event to D instead.

![wrongPath flowchart](../story_flowcharts/wrongPath.png)


## Approach 1 -- step by step

```
print A
run 2ns   # Need 2ns so first event gets processed, from now on we can step by 1ns
print B
run 1ns
print C
# Suprise, visited here is 0!
# Let's try the neighbor:
print D
# Oh there it is 
```

## Approach 2 -- set tracepoint on all components

```
cd A
trace visited changed : 5 5 : visited : printStatus
cd ..

cd B
trace visited changed : 5 5 : visited : printStatus
cd ..

cd C
trace visited changed : 5 5 : visited : printStatus
cd ..

cd D
trace visited changed : 5 5 : visited : printStatus
cd ..

run 4ns

printTrace 0
printTrace 1
printTrace 2
printTrace 3
```