Program to examine the behavior of the SST debugger with infinite loops


This test exhibits an infinite loop by failing to mark primary components as
okay to end the simulation.


To run
------

1. In this directory, call `make`.  This will build the program and register it
with SST.

2. `sst infiniteLoop.py --interactive-start=0` will run the program with the
SST debugger.

3. In the console, use `r 100ns` to run the program for a short while.  Do not
allow run to execute without a set time amount, as it will run forever in that
case.  Feel free to perform this step as much as you like.

4. The program will not complete on its own, so call the `shutdown` command when
you are finished.
