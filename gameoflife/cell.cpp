#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "cell.h"

class GolEvent : public SST::Event {
  public:
    GolEvent() : SST::Event() { }

    void serialize_order(SST::Core::Serialization::serializer &ser) override {
      Event::serialize_order(ser);
    }
    ImplementSerializable(GolEvent);
};

Cell::Cell( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  isAlive = params.find<bool>("isAlive", false);
  aliveNeighbors = 0;

  registerClock("2s",   new SST::Clock::Handler<Cell>(this, &Cell::clockTick));

  nwPort = configureLink("nwPort", new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  nPort  = configureLink("nPort",  new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  nePort = configureLink("nePort", new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  wPort  = configureLink("wPort",  new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  ePort  = configureLink("ePort",  new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  swPort = configureLink("swPort", new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  sPort  = configureLink("sPort",  new SST::Event::Handler<Cell>(this, &Cell::handleEvent));
  sePort = configureLink("sePort", new SST::Event::Handler<Cell>(this, &Cell::handleEvent));

  if(id == 0) {
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
  }
}

Cell::~Cell() { }

void Cell::setup() {
  communicate();
}

void Cell::handleEvent(SST::Event *ev) {
  aliveNeighbors += 1;
  delete ev;
}

void Cell::update() {
  if(isAlive && (aliveNeighbors < 2 || aliveNeighbors > 3)) {
    isAlive = false;
  } else if(!isAlive && aliveNeighbors == 3) {
    isAlive = true;
  }
  aliveNeighbors = 0;
}

void Cell::communicate() {
  if(isAlive) {
    if(isPortConnected("nwPort")) { nwPort->send(new GolEvent()); }
    if(isPortConnected("nPort"))  { nPort->send(new GolEvent());  }
    if(isPortConnected("nePort")) { nePort->send(new GolEvent()); }
    if(isPortConnected("wPort"))  { wPort->send(new GolEvent());  }
    if(isPortConnected("ePort"))  { ePort->send(new GolEvent());  }
    if(isPortConnected("swPort")) { swPort->send(new GolEvent()); }
    if(isPortConnected("sPort"))  { sPort->send(new GolEvent());  }
    if(isPortConnected("sePort")) { sePort->send(new GolEvent()); }
  }
}

void Cell::report() {
  /*std::cout << (isAlive ? "#" : ".");
  if(getName().back() == '9') {
    std::cout << std::endl;
  }
  if(getName() == "cell_9_9") {
    std::cout << std::endl;
  }*/
}

bool Cell::clockTick(SST::Cycle_t currentCycle) {
  update();
  report();
  communicate();
  return false;
}

