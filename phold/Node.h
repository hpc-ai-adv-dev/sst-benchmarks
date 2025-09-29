#ifndef _pholdNode_H
#define _pholdNode_H

#include <sst/core/component.h>
#include <sst/core/link.h>
#include <sst/core/sst_types.h>
#include <sst/core/serialization/serialize.h>
#include <sst/core/rng/mersenne.h>
#ifdef ENABLE_SSTDBG
#include <sst/dbg/SSTDebug.h>
#endif

enum MovementFunctionType {
  RANDOM = 0,
  CYCLIC = 1
};


class Node : public SST::Component {
  public:
    Node( SST::ComponentId_t id, SST::Params& params );
    ~Node();

    void setup() override;
    void finish() override;

    bool tick( SST::Cycle_t currentCycle );

    void handleEvent(SST::Event *ev);

    SST::Interfaces::StringEvent * createEvent();

    virtual SST::SimTime_t timestepIncrementFunction();

  #ifdef ENABLE_SSTCHECKPOINT
    // Serialization support for checkpointing/restart
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    // Default constructor for checkpointing - initialize critical members
    Node() : rng(nullptr), additionalData(nullptr) {}
  #endif

    // Register the component
    SST_ELI_REGISTER_COMPONENT(
      Node,   // class
      "phold",   // element library
      "Node", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "Base component for PHOLD benchmark. Each component sends messages to neighbors using the movement and timestep increment functions.",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "numRings", "number of rings to connect to", "1" },
     { "i", "My row index", "-1" },
     { "j", "My column index", "-1" },
     { "rowCount", "Total number of rows", "-1"},
     { "colCount", "Total number of columns", "-1"},
     { "timeToRun", "Time to run the simulation", "10ns" },
     { "eventDensity", "Number of events to start with per component", "0.1" },
     { "smallPayload", "Size of small event payloads in bytes", "8"},
     { "largePayload", "Size of large event payloads in bytes", "1024"},
     { "largeEventFraction", "Fraction of events that are large (default: 0.1)", "0.1"},
     { "verbose", "Whether or not to write the recvCount to file.", "0"},
     { "componentSize", "Additional size of components in bytes", "0"},
     { "movementFunction", "Movement function to use: random, or roundRobin", "random"}
    )

    SST_ELI_DOCUMENT_PORTS(
      {"port%d", "Ports to others", {}}
    )

    template<typename T>
    void setupLinks() {
      for (int i = 0; i < links.size(); i++) {
        std::string portName = "port" + std::to_string(i);
        auto *evHandler = new SST::Event::Handler2<Node, &Node::handleEvent>(this);
        links[i] = configureLink(portName, evHandler);
      }
      links.erase(std::remove(links.begin(), links.end(), nullptr), links.end());
    }

    int myId, myRow, myCol, verbose;
    std::vector<SST::Link*> links;
    int numRings, rowCount, colCount;
    double eventDensity;
    std::string timeToRun;
    int smallPayload, largePayload;
    float largeEventFraction;
    char* additionalData;

    int recvCount;

    // SST RNG system for proper checkpoint serialization
    SST::RNG::MersenneRNG* rng;

    // Movement function variables

    size_t movementFunctionRandom();
    size_t movementFunctionCyclic();

    // Needs to be an int so that serialization works, but we use the enum in code.
    int movementFunctionType;
    int movementFunctionCounter;
    std::function<size_t()> movementFunction;

  #ifdef ENABLE_SSTDBG
    void printStatus(SST::Output& out) override;
    SSTDebug *dbg;
  #endif

  #ifdef ENABLE_SSTCHECKPOINT
    ImplementSerializable(Node)
  #endif
};


class ExponentialNode : public Node {
  public:
  #ifdef ENABLE_SSTCHECKPOINT
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ExponentialNode() : Node() {}
  #endif
    ExponentialNode(SST::ComponentId_t id, SST::Params& params);
    SST::SimTime_t timestepIncrementFunction() override;

    SST_ELI_REGISTER_COMPONENT(
      ExponentialNode,   // class
      "phold",   // element library
      "ExponentialNode", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "PHOLD node that uses an exponential distribution for its timestep increment function.",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "multiplier", "Multiplier for exponential distribution, in ns", "1"}
    )

    double multiplier;

  #ifdef ENABLE_SSTCHECKPOINT
    ImplementSerializable(ExponentialNode)
  #endif
};


class UniformNode : public Node {
  public:
  #ifdef ENABLE_SSTCHECKPOINT
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    UniformNode() : Node() {}
  #endif
    UniformNode(SST::ComponentId_t id, SST::Params& params);
    SST::SimTime_t timestepIncrementFunction() override;

    SST_ELI_REGISTER_COMPONENT(
      UniformNode,   // class
      "phold",   // element library
      "UniformNode", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "PHOLD node that uses a uniform distribution for its timestep increment function.",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
      { "min", "Minimum value for uniform distribution, in ns, in addition to link delay", "0.0"},
      { "max", "Maximum value for uniform distribution, in ns, in addition to link delay", "1.0"}
    )

    double min, max;

  #ifdef ENABLE_SSTCHECKPOINT
    ImplementSerializable(UniformNode)
  #endif

};
#endif
