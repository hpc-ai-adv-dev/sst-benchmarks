#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "onDemandCell.h"

class GolEvent : public SST::Event {
  public:
    GolEvent() : SST::Event() { }

    void serialize_order(SST::Core::Serialization::serializer &ser) override {
      Event::serialize_order(ser);
    }
    ImplementSerializable(GolEvent);
};

OnDemandCell::OnDemandCell( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  isAlive = params.find<bool>("isAlive", false);
  aliveNeighbors = 0;

  clockOn = true;
  clockHandler = new SST::Clock::Handler2<OnDemandCell, &OnDemandCell::clockTick>(this);
  clockTc = registerClock("2s",   clockHandler);

  nwPort = configureLink("nwPort", new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  nPort  = configureLink("nPort",  new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  nePort = configureLink("nePort", new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  wPort  = configureLink("wPort",  new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  ePort  = configureLink("ePort",  new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  swPort = configureLink("swPort", new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  sPort  = configureLink("sPort",  new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));
  sePort = configureLink("sePort", new SST::Event::Handler2<OnDemandCell, &OnDemandCell::handleEvent>(this));

  if(id == 0) {
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
  }
}

OnDemandCell::~OnDemandCell() { }

void OnDemandCell::setup() {
  communicate();
}

void OnDemandCell::handleEvent(SST::Event *ev) {
 if(!clockOn) {
    clockOn = true;
    // TODO: reregisterClock changes in SST 15.0 to use a different signature
    //       that doesn't exist in SST 14.0, so we need to check the version
    //       and use the appropriate function, e.g.:
    // reregisterClock(*clockTc, clockHandler); // SST 15.0
    // reregisterClock(clockTc, clockHandler); // SST 14.0
    reregisterClock(clockTc, clockHandler);
  }
  aliveNeighbors += 1;
  delete ev;
}

void OnDemandCell::update() {
  if(isAlive && (aliveNeighbors < 2 || aliveNeighbors > 3)) {
    isAlive = false;
  } else if(!isAlive && aliveNeighbors == 3) {
    isAlive = true;
  }
  aliveNeighbors = 0;
}

void OnDemandCell::communicate() {
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

void OnDemandCell::report() {
  /*std::cout << (isAlive ? "#" : ".");
  if(getName().back() == '9') {
    std::cout << std::endl;
  }
  if(getName() == "cell_9_9") {
    std::cout << std::endl;
  }*/
}

bool OnDemandCell::clockTick(SST::Cycle_t currentCycle) {
  update();
  if(!isAlive && clockOn) {
    clockOn = false;
    // TODO: unregisterClock changes in SST 15.0 to use a different signature
    //       that doesn't exist in SST 14.0, so we need to check the version
    //       and use the appropriate function, e.g.:
    // unregisterClock(*clockTc, clockHandler); // SST 15.0
    // unregisterClock(clockTc, clockHandler); // SST 14.0
    unregisterClock(clockTc, clockHandler);
  }
  report();
  communicate();
  return false;
}

#ifdef ENABLE_SSTCHECKPOINT
void OnDemandCell::serialize_order(SST::Core::Serialization::serializer& ser) {
    SST::Component::serialize_order(ser);
    SST_SER(isAlive);
    SST_SER(clockOn);
    SST_SER(aliveNeighbors);
    SST_SER(nwPort);
    SST_SER(nPort);
    SST_SER(nePort);
    SST_SER(wPort);
    SST_SER(ePort);
    SST_SER(swPort);
    SST_SER(sPort);
    SST_SER(sePort);
}
#endif // ENABLE_SSTCHECKPOINT
