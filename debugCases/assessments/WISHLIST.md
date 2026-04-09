# wishlist

This document contains some general wishlist features I encountered while using the SST debugger but didn't seem tied to any specific story or class or stories.

## Allow inline comments in replay scripts

I would like to be able to put comments into debug scripts inline like this. Currently it looks like if I do this the debugger runs the simulation to completion:

```
run 2ns     # Skip past the expected event.
```

## Named tracepoints

When setting a tracepoint assign an identifier which I can use to refer to it later.
