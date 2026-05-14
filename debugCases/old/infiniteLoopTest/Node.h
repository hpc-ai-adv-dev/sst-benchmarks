#include <sst/core/component.h>
#include <sst/core/link.h>
#include <sst/core/serialization/serialize.h>

class Node : public SST::Component {
 public:
  Node(SST::ComponentId_t id, SST::Params& params);
  Node(); // Needed for serialization
  ~Node();

  void setup() override;
  void finish() override;

  bool tick(SST::Cycle_t currentCycle);

  void handleEvent(SST::Event* ev);

  // Register the component
  SST_ELI_REGISTER_COMPONENT(
      Node,             // class
      "infiniteLoop",   // element library
      "Node",           // component
      SST_ELI_ELEMENT_VERSION(1, 0, 0),
      "Component that passes a message on to its neighbors.",
      COMPONENT_CATEGORY_UNCATEGORIZED)

  // Parameter name, description, default value
  SST_ELI_DOCUMENT_PARAMS(
      {"payload", "value to pass to neighbor", "0"})

  // Port name, description, event type
  SST_ELI_DOCUMENT_PORTS({{"myPort", "Port to other component", {}}})

  SST::Link *myPort;

  int payload;

  // needed for serialization
  void serialize_order(SST::Core::Serialization::serializer& ser) override;
  ImplementSerializable(Node)

};
