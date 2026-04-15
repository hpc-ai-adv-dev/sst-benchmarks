import sst

num_components = 10 

links = [] # List of link handlers
for x in range(num_components):
    link = sst.Link("link_" + str(x))
    links.append(link)


### Create the components and link
for x in range(num_components):
    component = sst.Component("component_" + str(x), "cyclical.basicSubComponent_comp")

    # Have all components start with some number between 0 and 5
    component.addParam("value", (x + 1) % 6)

    # Connect the components to each other in a ring
    component.addLink(links[x-1], "left", "10ns")
    component.addLink(links[x], "right", "10ns")