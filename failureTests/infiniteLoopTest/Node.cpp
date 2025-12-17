#include "Node.h"

Node::Node(SST::ComponentId_t id, SST::Params& params) : SST::Component(id) {
  payload = params.find<int64_t>("payload", 0);

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  myPort = configureLink("myPort", new SST::Event::Handler2<Node,
                         &Node::handleEvent>(this));

  auto* clkHandler =
    new SST::Clock::Handler2<Node, &Node::tick>(this);
  registerClock("1000ns", clkHandler);
}

Node::~Node() {

}

void Node::setup() {
  myPort->send(new SST::Event());
}

void Node::finish() {
  std::string msg = "component done with payload: " + std::to_string(payload) +
                    "\n";
  std::cout << msg;
}

bool Node::tick(SST::Cycle_t /* currentCycle */)
{
  // This would prevent the infinite loop, so leave it off for now
  //primaryComponentOKToEndSim();
  return false;
}

void Node::handleEvent(SST::Event* ev) {
  std::cout << "Received event at timestamp " << ev->getDeliveryTime();
  std::cout << ", payload was " << std::to_string(payload) << "\n";
  delete ev;

  myPort->send(new SST::Event());
}

void Node::serialize_order(SST::Core::Serialization::serializer& ser) {
  // Serialize component state for checkpointing
  SST::Component::serialize_order(ser);
  SST_SER(payload);
}
