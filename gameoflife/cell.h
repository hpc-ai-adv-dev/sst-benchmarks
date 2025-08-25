#ifndef _gol_cell_H
#define _gol_cell_H

#include <sst/core/component.h>
#include <sst/core/link.h>

class GolEvent;

class Cell : public SST::Component {
  public:
    Cell( SST::ComponentId_t id, SST::Params& params );
    ~Cell();

    // Register the component
    SST_ELI_REGISTER_COMPONENT(
      Cell,          // class
      "gol",         // element library
      "cell",        // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "game of life component",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "isAlive", "Indicates if space has a cell (is alive)", "true" }
    )

    // Port name, description, event type
    SST_ELI_DOCUMENT_PORTS(
      { "nwPort", "Northwest port", {"gameoflife.GolEvent"}},
      { "nPort",  "North port",     {"gameoflife.GolEvent"}},
      { "nePort", "Northeast port", {"gameoflife.GolEvent"}},
      { "wPort",  "West port",      {"gameoflife.GolEvent"}},
      { "ePort",  "East port",      {"gameoflife.GolEvent"}},
      { "swPort", "Southwest port", {"gameoflife.GolEvent"}},
      { "sPort",  "South port",     {"gameoflife.GolEvent"}},
      { "sePort", "Southeast port", {"gameoflife.GolEvent"}}
    )

    void setup() override;

  private:
    void update();
    void communicate();
    void report();
    void handleEvent(SST::Event *ev);
    bool clockTick(SST::Cycle_t currentCycle);

    bool isAlive;
    int aliveNeighbors;
    SST::Link *nwPort, *nPort, *nePort, *wPort, *ePort, *swPort, *sPort, *sePort;
};

#endif
