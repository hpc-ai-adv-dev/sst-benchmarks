Program to examine the behaviour of the SST debugger with load imbalance


This test exhibits load imbalance by having one node spawn more events than the
other node.

To run
------

1. In this directory, call `make`.  This will build the program and register it
with SST.

2. `sst loadImbalance.py --interactive-start=0` will run the program with the
SST debugger.

3. In the console, `r` will run the program.  If providing any argument to the
run command greater than 200 nanoseconds, there will be more output from the
"slower" node than the "faster", because it is processing strictly more events
each cycle (as a result of `FasterNode::handleEvent`)

4. The program should complete on its own after 1000 ns but if you used a
specific amount of time and want to end it earlier, you can call the `shutdown`
command
