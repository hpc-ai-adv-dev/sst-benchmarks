#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
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
  
  rng = std::mt19937(myId);
  uid = std::uniform_int_distribution<int>(0, numLinks-1);
  urd = std::uniform_real_distribution<double>(0.0,1.0);

  links = std::vector<SST::Link*>(numLinks);
  
  int componentSize = params.find<int>("componentSize", 0);
  if (componentSize == 0) {
    additionalData = nullptr;
  } else {
    additionalData = (char*) malloc(componentSize * sizeof(char));
  }

  setupLinks<Node>();

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
  registerClock(timeToRun, new SST::Clock::Handler<Node>(this, &Node::tick));
  //std::cout << "Done initalizing component " << id << " on rank " <<getRank().rank << "\n" << std::flush;
}

Node::~Node() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
  if (additionalData != nullptr) {
    free(additionalData);
  }
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
  auto size = (urd(rng) < largeEventFraction) ? largePayload : smallPayload;
  std::string str(size, 'a'); // Create a string of size 'size' filled with 'a'
  SST::Interfaces::StringEvent* ev = new SST::Interfaces::StringEvent(str);
  return ev;
}

void Node::handleEvent(SST::Event *ev){
  SST::Interfaces::StringEvent * payloadEv = dynamic_cast<SST::Interfaces::StringEvent*>(ev);
  delete ev;
  static SST::TimeConverter * ps = getTimeConverter("1ps");
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
  return uid(rng);
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
  auto v = -1.0 * log(urd(rng));
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
  auto v = urd(rng);
  auto increment = min + (max - min) * v;
  // The 1000 is to convert to ps
  return increment * 1000;
}