#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include <cmath>
#include "Node.h"




Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  //std::cout << "initializing node on rank " << getRank().rank << " and id " << id << "\n" << std::flush;
  numRings = params.find<int>("numRings");

  myCol = params.find<int>("j", -1);
  myRow = params.find<int>("i", -1);
  rowCount = params.find<int>("rowCount", -1);
  colCount = params.find<int>("colCount", -1);

  smallPayload = params.find<int>("smallPayload", -1);
  largePayload = params.find<int>("largePayload", -1);
  largeEventFraction = params.find<double>("largeEventFraction", -1.0);
  verbose = params.find<int>("verbose", 0);

  if (myCol == -1) {std::cerr << "WARNING: Failed to get myCol\n";}
  if (myRow == -1) {std::cerr << "WARNING: Failed to get myRow\n";}
  if (rowCount == -1) {std::cerr << "WARNING: Failed to get rowCount\n";}
  if (colCount == -1) {std::cerr << "WARNING: Failed to get colCount\n";}
  if (smallPayload == -1) {std::cerr << "WARNING: Failed to get small payload size\n";}
  if (largePayload == -1) {std::cerr << "WARNING: Failed to get large payload size\n";}
  if (largeEventFraction == -1) {std::cerr << "WARNING: Failed to get large event fraction\n";}

  myId = myRow * colCount + myCol;
  timeToRun = params.find<std::string>("timeToRun");
  eventDensity = params.find<double>("eventDensity");

  recvCount = 0;
  numLinks = (2*numRings+1) * (2*numRings+1);
  numLinks_for_rng = numLinks; // Store for RNG calculations

  // Use SST's Mersenne RNG for proper checkpoint serialization
  rng = new SST::RNG::MersenneRNG(myId);

  links = std::vector<SST::Link*>(numLinks);

  setupLinks<Node>();

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
  registerClock(timeToRun, new SST::Clock::Handler2<Node, &Node::tick>(this));
  //std::cout << "Done initalizing component " << id << " on rank " <<getRank().rank << "\n" << std::flush;
}

Node::~Node() {
  delete rng;
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}

void Node::setup() {
  double counter = eventDensity;

  while (counter >= 1.0) {
    auto ev = createEvent();
    auto recipient = movementFunction();
    while (links.at(recipient) == nullptr) {
      recipient = movementFunction();
    }
    links.at(recipient)->send(ev);
    counter -= 1.0;
  }

  // At this point, we have counter between 0 and 1.
  // Thus, every 1/counter components should get an extra event
  int period = 1.0 / counter;
  if (myId % period == 0) {
    auto ev = createEvent();
    auto recipient = movementFunction();
    while (links.at(recipient) == nullptr) {
      recipient = movementFunction();
    }
    links.at(recipient)->send(ev);
  }
}

void Node::finish() {
  //std::cout << "Component at " << myRow << "," << myCol << " processed " << recvCount << " messages\n";
  std::string msg = std::to_string(myRow) + "," + std::to_string(myCol) + ":" + std::to_string(recvCount) + "\n";
  if (verbose) {
    std::cerr << msg;
  }

}

bool Node::tick( SST::Cycle_t currentCycle ) {
  primaryComponentOKToEndSim();
  return false;
}

SST::Interfaces::StringEvent * Node::createEvent() {
  // Use SST RNG to generate uniform random [0,1) for comparison with largeEventFraction
  double random_val = rng->nextUniform();
  auto size = (random_val < largeEventFraction) ? largePayload : smallPayload;
  std::string str(size, 'a'); // Create a string of size 'size' filled with 'a'
  SST::Interfaces::StringEvent* ev = new SST::Interfaces::StringEvent(str);
  return ev;
}

void Node::handleEvent(SST::Event *ev){
  SST::Interfaces::StringEvent * payloadEv = dynamic_cast<SST::Interfaces::StringEvent*>(ev);
  delete ev;
  static auto ps = getTimeConverter("1ps");
#ifdef SSTDEBUG
  std::cout << "Handling event at component " << myRow << "," << myCol << " with timestamp " << ev->getDeliveryTime() << "\n";
#endif
  recvCount += 1;

  size_t nextRecipientLinkId = movementFunction();
  while (links.at(nextRecipientLinkId) == nullptr) {
    nextRecipientLinkId = movementFunction();
  }

  SST::SimTime_t psDelay = timestepIncrementFunction();
  links[nextRecipientLinkId]->send(psDelay, ps, createEvent());
}

size_t Node::movementFunction() {
  // Use SST RNG to generate uniform integer in range [0, numLinks-1]
  uint32_t random_val = rng->generateNextUInt32();
  return random_val % numLinks_for_rng;
}

// Base class has no additional delay.
SST::SimTime_t Node::timestepIncrementFunction() {
  return 0;
}


ExponentialNode::ExponentialNode(SST::ComponentId_t id, SST::Params& params )
  : Node(id, params) {
  multiplier = params.find<double>("multiplier");
  setupLinks<ExponentialNode>();
}


SST::SimTime_t ExponentialNode::timestepIncrementFunction() {
  // Use SST RNG for exponential distribution
  auto v = -1.0 * log(rng->nextUniform());
  // The 1000 is to convert to ps
  return v*multiplier*1000;
}

UniformNode::UniformNode(SST::ComponentId_t id, SST::Params& params )
  : Node(id, params) {
  min = params.find<double>("min");
  max = params.find<double>("max");
  setupLinks<UniformNode>();
}

SST::SimTime_t UniformNode::timestepIncrementFunction() {
  // Use SST RNG for uniform distribution
  auto v = rng->nextUniform();
  auto increment = min + (max - min) * v;
  // The 1000 is to convert to ps
  return increment * 1000;
}

#ifdef ENABLE_SSTCHECKPOINT
void Node::serialize_order(SST::Core::Serialization::serializer& ser) {
    // Serialize component state for checkpointing
    SST::Component::serialize_order(ser);
    SST_SER(myId);
    SST_SER(myRow);
    SST_SER(myCol);
    SST_SER(verbose);
    SST_SER(numRings);
    SST_SER(numLinks);
    SST_SER(numLinks_for_rng);
    SST_SER(rowCount);
    SST_SER(colCount);
    SST_SER(eventDensity);
    SST_SER(timeToRun);
    SST_SER(smallPayload);
    SST_SER(largePayload);
    SST_SER(largeEventFraction);
    SST_SER(recvCount);

    // SST RNG has built-in serialization support
    SST_SER(rng);
}
#endif