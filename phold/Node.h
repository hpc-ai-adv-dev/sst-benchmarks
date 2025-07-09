#ifndef _pholdNode_H
#define _pholdNode_H

#include <sst/core/component.h>
#include <sst/core/link.h>

#ifdef ENABLE_SSTDBG
#include <sst/dbg/SSTDebug.h>
#endif



class Node : public SST::Component {
  public:
    Node( SST::ComponentId_t id, SST::Params& params );
    ~Node();

    void setup() override;
    void finish() override;

    bool tick( SST::Cycle_t currentCycle );

    void handleEvent(SST::Event *ev);

    // Register the component
    SST_ELI_REGISTER_COMPONENT(
      Node,   // class
      "phold",   // element library
      "Node", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "component that takes balls from its neighbors and passes along. If there's no neighbor to pass to, bounce back",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "numRings", "number of rings to connect to", "1" }
    )

    SST_ELI_DOCUMENT_PORTS(
      {"port%d", "Ports to others", {}}
    )
    
    size_t movementFunction();
    


#ifdef ENABLE_SSTDBG
    void printStatus(SST::Output& out) override;
#endif
    std::vector<SST::Link*> links;
    int numRings;
    int numLinks;

#ifdef ENABLE_SSTDBG
    SSTDebug *dbg;
#endif
};


#endif
