import sst

node1 = sst.Component("node1", "loadImbalance.FasterNode")
node2 = sst.Component("node2", "loadImbalance.SlowerNode")

node1.addParams({"payload": 0})
node2.addParams({"payload": 1})

# connect the nodes
link = sst.Link("link1")
# note: using 100 ns so the program completes on its own, quickly
link.connect((node1, "myPort", "100ns"), (node2, "myPort", "100ns"))
