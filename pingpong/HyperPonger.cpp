#include <sst/core/sst_config.h>
#include <sst/core/rng/marsaglia.h>
#include "HyperPonger.h"
#include "GlobalParams.h"

class BallEvent : public SST::Event {
  public:
    BallEvent() : SST::Event(), count(0) { }
    BallEvent(int64_t cnt) : SST::Event(), count(cnt) { }

    int64_t count;

    void serialize_order(SST::Core::Serialization::serializer &ser)  override {
      Event::serialize_order(ser);
      SST_SER(count);
    }

    // Register this event as serializable
    ImplementSerializable(BallEvent);
};

static double artificialWorkValue = 1.1;
static double artificialWorkMultiplier = 1.23;
static void conductArtificialWork(int64_t count) {
  for(int64_t i = 0; i < count; i++) {
    artificialWorkValue *= artificialWorkMultiplier;
  }
}

HyperPonger::HyperPonger( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  rng = new SST::RNG::MarsagliaRNG();
  initialBalls = params.find<int64_t>("numBalls", 0);

  SST::Link *n, *s, *w, *e;
  auto *evHandler = new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this);
  n = configureLink("port_n", evHandler);
  s = configureLink("port_s", evHandler);
  w = configureLink("port_w", evHandler);
  e = configureLink("port_e", evHandler);

  #ifndef USE_GETLINK_API
  linkN = n;
  linkS = s;
  linkW = w;
  linkE = e;

  for(int i = 0; i < NUM_LINKS; i++) {
    hyperLink[i] = configureLink("port_" + std::to_string(i),  evHandler);
  }
  #else
  for(int i = 0; i < NUM_LINKS; i++) {
    configureLink("port_" + std::to_string(i),  evHandler);
  }
  #endif
}

#ifdef ENABLE_SSTCHECKPOINT
  HyperPonger::HyperPonger() { }
#endif

HyperPonger::~HyperPonger() { }

void HyperPonger::setup() {
  for(int i = 0; i < initialBalls; i++) {
    sendOutRandomBall();
  }
}

void HyperPonger::finish() { }

bool HyperPonger::tick( SST::Cycle_t currentCycle ) {
  return false;
}

void HyperPonger::handleEvent(SST::Event *ev) {
  conductArtificialWork(gArtificialWork);
  sendOutRandomBall();
  delete ev;
}

void HyperPonger::sendOutRandomBall() {
  int rndNumber;
  rndNumber = (int)(rng->generateNextInt32());
  rndNumber = (rndNumber & 0x0000FFFF) ^ ((rndNumber & 0xFFFF0000) >> 16);
  rndNumber = abs((int)(rndNumber % 204));

  SST::Link *tgtLink = nullptr;
  if(rndNumber == 0) {
    #ifdef USE_GETLINK_API
    tgtLink = getLink("port_n");
    #else
    tgtLink = isPortConnected("port_n") ? linkN : nullptr;
    #endif

    if(tgtLink != nullptr) { tgtLink->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 1) {
    #ifdef USE_GETLINK_API
    tgtLink = getLink("port_s");
    #else
    tgtLink = isPortConnected("port_s") ? linkS : nullptr;
    #endif

    if(tgtLink != nullptr) { tgtLink->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 2) {
    #ifdef USE_GETLINK_API
    tgtLink = getLink("port_w");
    #else
    tgtLink = isPortConnected("port_w") ? linkW : nullptr;
    #endif

    if(tgtLink != nullptr) { tgtLink->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 3) {
    #ifdef USE_GETLINK_API
    tgtLink = getLink("port_e");
    #else
    tgtLink = isPortConnected("port_e") ? linkE : nullptr;
    #endif

    if(tgtLink != nullptr) { tgtLink->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber > 3)  {
    int hyperPort = rndNumber - 4;
    #ifdef USE_GETLINK_API
    tgtLink = getLink("port_" + std::to_string(hyperPort));
    #else
    tgtLink = isPortConnected("port_" + std::to_string(hyperPort)) ? hyperLink[hyperPort] : nullptr;
    #endif

    if(tgtLink != nullptr) {
      tgtLink->send(new BallEvent(1));
    } else {
      // we don't have self links back in this topology.
      #ifdef USE_GETLINK_API
      tgtLink = getLink("port_" + std::to_string((hyperPort+1) % NUM_LINKS));
      tgtLink->send(new BallEvent(1));
      #else
      hyperLink[(hyperPort+1) % NUM_LINKS]->send(new BallEvent(1));
      #endif
    }
  }
}

#ifdef ENABLE_SSTCHECKPOINT
void HyperPonger::serialize_order(SST::Core::Serialization::serializer& ser) {
  SST::Component::serialize_order(ser);
  SST_SER(initialBalls);
  SST_SER(rng);
  SST_SER(linkN);
  SST_SER(linkS);
  SST_SER(linkW);
  SST_SER(linkE);
  for (size_t i = 0; i < NUM_LINKS; i++) {
    SST_SER(hyperLink[i]);
  }
}
#endif
