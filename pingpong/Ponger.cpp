#include <sst/core/sst_config.h>
#include "Ponger.h"
#include "GlobalParams.h"

class BallEvent : public SST::Event {
  public:
    int64_t ballId;

    BallEvent() : SST::Event(), ballId(0) { }
    BallEvent(int64_t ballId) : SST::Event(), ballId(ballId) { }

    void serialize_order(SST::Core::Serialization::serializer &ser) override {
      Event::serialize_order(ser);
      SST_SER(ballId);
    }
    ImplementSerializable(BallEvent);
};

static double artificialWorkValue = 1.1;
static double artificialWorkMultiplier = 1.23;
static void conductArtificialWork(int64_t count) {
  for(int64_t i = 0; i < count; i++) {
    artificialWorkValue *= artificialWorkMultiplier;
  }
}

Ponger::Ponger( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  ballsHeadingNorth = params.find<int64_t>("ballsHeadingNorth", 0);
  ballsHeadingSouth = params.find<int64_t>("ballsHeadingSouth", 0);
  ballsHeadingWest  = params.find<int64_t>("ballsHeadingWest",  0);
  ballsHeadingEast  = params.find<int64_t>("ballsHeadingEast",  0);

  northPort = configureLink("northPort", new SST::Event::Handler2<Ponger, &Ponger::handleNorthPort>(this));
  southPort = configureLink("southPort", new SST::Event::Handler2<Ponger, &Ponger::handleSouthPort>(this));
  westPort  = configureLink("westPort",  new SST::Event::Handler2<Ponger, &Ponger::handleWestPort>(this));
  eastPort  = configureLink("eastPort",  new SST::Event::Handler2<Ponger, &Ponger::handleEastPort>(this));

#ifdef ENABLE_SSTDBG
  dbg = new SSTDebug(getName(),"./");
#endif
}
#ifdef ENABLE_SSTCHECKPOINT
  Ponger::Ponger() { }
#endif

Ponger::~Ponger() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}

void Ponger::setup() {
  static int64_t nextBallId = 0;

  auto sendNTimes = [&](int n, SST::Link *link) {
    for(int i = 0; i < n; i++) {
      link->send(new BallEvent(nextBallId++));
    }
  };

  if(ballsHeadingNorth > 0) {
         if(isPortConnected("northPort")) { sendNTimes(ballsHeadingNorth, northPort); }
    else if(isPortConnected("southPort")) { sendNTimes(ballsHeadingNorth, southPort); }
  }

  if(ballsHeadingSouth > 0) {
         if(isPortConnected("southPort")) { sendNTimes(ballsHeadingSouth, southPort); }
    else if(isPortConnected("northPort")) { sendNTimes(ballsHeadingSouth, northPort); }
  }

  if(ballsHeadingWest > 0) {
         if(isPortConnected("westPort")) { sendNTimes(ballsHeadingWest, westPort); }
    else if(isPortConnected("eastPort")) { sendNTimes(ballsHeadingWest, eastPort); }
  }

  if(ballsHeadingEast > 0) {
         if(isPortConnected("eastPort")) { sendNTimes(ballsHeadingEast, eastPort); }
    else if(isPortConnected("westPort")) { sendNTimes(ballsHeadingEast, westPort); }
  }
}

void Ponger::finish() { }

bool Ponger::tick( SST::Cycle_t currentCycle ) {
  return false;
}

void Ponger::handlePort(
  BallEvent *ev, const char *dirString, const char *portName,
  SST::Link *portLink, const char *oppositePortName, SST::Link *oppositePortLink)
{
  int64_t ballId = ev->ballId;
  conductArtificialWork(gArtificialWork);

  if(gVerbose) {
    std::cout << std::setw(10) << getElapsedSimTime().toStringBestSI() << " | "
              << dirString << getName() << " ballid=" << ballId << std::endl;
  }

  if(isPortConnected(oppositePortName)) {
    oppositePortLink->send(new BallEvent(ballId));
  } else if(isPortConnected(portName)) {
    portLink->send(new BallEvent(ballId));
  }

  delete ev;
}

void Ponger::handleNorthPort(SST::Event *ev) {
  handlePort(dynamic_cast<BallEvent*>(ev), "vvvvvv ", "northPort", northPort, "southPort", southPort);
}

void Ponger::handleSouthPort(SST::Event *ev) {
  handlePort(dynamic_cast<BallEvent*>(ev), "^^^^^^ ", "southPort", southPort, "northPort", northPort);
}

void Ponger::handleWestPort(SST::Event *ev) {
  handlePort(dynamic_cast<BallEvent*>(ev), "-----> ", "westPort", westPort, "eastPort", eastPort);
}

void Ponger::handleEastPort(SST::Event *ev) {
  handlePort(dynamic_cast<BallEvent*>(ev), "<----- ", "eastPort", eastPort, "westPort", westPort);
}

#ifdef ENABLE_SSTDBG
void Ponger::printStatus(SST::Output& out){
  if(!dbg->dump(getCurrentSimCycle(),
     DARG(ballsHeadingNorth),
     DARG(ballsHeadingSouth),
     DARG(ballsHeadingWest),
     DARG(ballsHeadingEast)))
  {
    out.output("Debug dump failed!\n");
  }
}
#endif

#ifdef ENABLE_SSTCHECKPOINT
void Ponger::serialize_order(SST::Core::Serialization::serializer& ser) {
  SST::Component::serialize_order(ser);
  SST_SER(ballsHeadingNorth);
  SST_SER(ballsHeadingSouth);
  SST_SER(ballsHeadingWest);
  SST_SER(ballsHeadingEast);
  SST_SER(northPort);
  SST_SER(southPort);
  SST_SER(westPort);
  SST_SER(eastPort);

  #ifdef ENABLE_SSTDBG
    SST_SER(dbg);
  #endif
}
#endif
