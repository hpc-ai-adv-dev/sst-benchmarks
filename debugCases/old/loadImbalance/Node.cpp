#include "Node.h"

FasterNode::FasterNode(SST::ComponentId_t id, SST::Params& params) : SST::Component(id) {
  payload = params.find<int64_t>("payload", 0);

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  myPort = configureLink("myPort", new SST::Event::Handler2<FasterNode,
                         &FasterNode::handleEvent>(this));

  auto* clkHandler =
    new SST::Clock::Handler2<FasterNode, &FasterNode::tick>(this);
  registerClock("1000ns", clkHandler);
}

FasterNode::~FasterNode() {

}

void FasterNode::setup() {
  myPort->send(new SST::Event());
}

void FasterNode::finish() {
  std::string msg = "faster component done\n";
  std::cout << msg;
}

bool FasterNode::tick(SST::Cycle_t /* currentCycle */)
{
  primaryComponentOKToEndSim();
  return false;
}

void FasterNode::handleEvent(SST::Event* ev) {
  std::cout << "Received event at timestamp " << ev->getDeliveryTime();
  std::cout << ", in faster node\n";
  delete ev;

  myPort->send(new SST::Event());
  myPort->send(new SST::Event());
}

void FasterNode::serialize_order(SST::Core::Serialization::serializer& ser) {
  // Serialize component state for checkpointing
  SST::Component::serialize_order(ser);
  SST_SER(payload);
}

SlowerNode::SlowerNode(SST::ComponentId_t id, SST::Params& params) : SST::Component(id) {
  payload = params.find<int64_t>("payload", 0);

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

  myPort = configureLink("myPort", new SST::Event::Handler2<SlowerNode,
                         &SlowerNode::handleEvent>(this));

  auto* clkHandler =
    new SST::Clock::Handler2<SlowerNode, &SlowerNode::tick>(this);
  registerClock("1000ns", clkHandler);
}

SlowerNode::~SlowerNode() {

}

void SlowerNode::setup() {
  myPort->send(new SST::Event());
}

void SlowerNode::finish() {
  std::string msg = "slower component done\n";
  std::cout << msg;
}

bool SlowerNode::tick(SST::Cycle_t /* currentCycle */)
{
  primaryComponentOKToEndSim();
  return false;
}

void SlowerNode::handleEvent(SST::Event* ev) {
  std::cout << "Received event at timestamp " << ev->getDeliveryTime();
  std::cout << ", in slower node " << "\n";
  delete ev;

  myPort->send(new SST::Event());
}

void SlowerNode::serialize_order(SST::Core::Serialization::serializer& ser) {
  // Serialize component state for checkpointing
  SST::Component::serialize_order(ser);
  SST_SER(payload);
}
