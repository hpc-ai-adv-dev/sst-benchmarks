import sst

node1 = sst.Component("node1", "infiniteLoop.Node")
node2 = sst.Component("node2", "infiniteLoop.Node")

node1.addParams({"payload": 0})
node2.addParams({"payload": 1})

# connect the nodes
link = sst.Link("link1")
link.connect((node1, "myPort", "1ns"), (node2, "myPort", "1ns"))
