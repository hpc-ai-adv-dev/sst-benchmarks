#ifndef _hyperPonger_H
#define _hyperPonger_H

#include <sst/core/component.h>
#include <sst/core/link.h>

class HyperPonger : public SST::Component {
  public:
    HyperPonger( SST::ComponentId_t id, SST::Params& params );
    ~HyperPonger();

    void setup() override;
    void finish() override;

    bool tick( SST::Cycle_t currentCycle );

    void handleEvent(SST::Event *ev);

    // Register the component
    SST_ELI_REGISTER_COMPONENT(
      HyperPonger,  // class
      "pingpong",   // element library
      "hyperPonger", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "component that takes balls from its neighbors and passes along. If there's no neighbor to pass to, bounce back",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "numBalls", "Balls currently on the component", "0" }
    )

    // Port name, description, event type
    SST_ELI_DOCUMENT_PORTS(
      { "port_n", "Port to north", {"pingpong.BallEvent"}},
      { "port_s", "Port to south", {"pingpong.BallEvent"}},
      { "port_w" , "Port to west", {"pingpong.BallEvent"}},
      { "port_e",  "Port to east", {"pingpong.BallEvent"}},
      { "port_%d",  "Nth port to neighboring grid",  {"pingpong.BallEvent"}}
    )

  #ifdef ENABLE_SSTCHECKPOINT
    // needed for serialization
    HyperPonger();
    // needed for serialization
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ImplementSerializable(HyperPonger)
  #endif

  private:
    void sendOutRandomBall();

    int64_t initialBalls;
    SST::RNG::MarsagliaRNG* rng;
    static const int NUM_LINKS = 200;

#ifndef USE_GETLINK_API
    SST::Link *linkN, *linkS, *linkW, *linkE;
    SST::Link *hyperLink[NUM_LINKS];
#endif
};

#endif
