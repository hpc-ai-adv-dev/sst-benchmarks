#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include <cmath>
#include "Node.h"

Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id), additionalData(nullptr)
{
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
  

  int componentSize = params.find<int>("componentSize", 0);
  if (componentSize == 0) {
    additionalData = nullptr;
  } else {
    additionalData = (char*) malloc(componentSize * sizeof(char));
  }

  recvCount = 0;
  

  // Use SST's Mersenne RNG for proper checkpoint serialization
  rng = new SST::RNG::MersenneRNG(myId);

  int numLinks = (2*numRings+1) * (2*numRings+1);
  links = std::vector<SST::Link*>(numLinks);

  setupLinks<Node>();

  if (eventDensity < 0.0) {
    eventDensity = links.size();
  }

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
  registerClock(timeToRun, new SST::Clock::Handler2<Node, &Node::tick>(this));


  // movement functions
  movementFunctionCounter = 0;

  std::string movementFunctionStr = params.find<std::string>("movementFunction", "random");
  if (movementFunctionStr == "random") {
    movementFunctionType = RANDOM;
    movementFunction = std::bind(&Node::movementFunctionRandom, this);
  } else if (movementFunctionStr == "cyclic") {
    movementFunctionType = CYCLIC;
    movementFunction = std::bind(&Node::movementFunctionCyclic, this);
  } else {
    std::cerr << "Unrecognized movement function: " << movementFunctionStr << ", defaulting to random\n";
    movementFunctionType = RANDOM;
    movementFunction = std::bind(&Node::movementFunctionRandom, this);
  }
  
}

Node::~Node() {
  delete rng;
  if (additionalData != nullptr) {
    std::cerr << "Freeing additional data\n";
    free(additionalData);
  }
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
  
  if (counter <= 0.0) return;

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
  std::string msg = std::to_string(myRow) + "," + std::to_string(myCol) + " : " + std::to_string(links.size()) + "," + std::to_string(recvCount) + "\n";
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

  // Note: Using pointer API for compatibility with both SST 14.1.0 and 15.0.0
  // This generates a deprecation warning in SST 15.0.0 because the link->send API
  // is being changed to no longer accept the shared TimeConverter object.
  links[nextRecipientLinkId]->send(psDelay, ps, createEvent());
}

// Base class has no additional delay.
SST::SimTime_t Node::timestepIncrementFunction() {
  return 0;
}

size_t Node::movementFunctionRandom() {
  uint32_t random_val = rng->generateNextUInt32();
  return random_val % links.size();
}

size_t Node::movementFunctionCyclic() {
  int next = movementFunctionCounter;
  movementFunctionCounter = (movementFunctionCounter + 1) % links.size();
  return next;
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
    SST_SER(links);
    SST_SER(rowCount);
    SST_SER(colCount);
    SST_SER(eventDensity);
    SST_SER(timeToRun);
    SST_SER(smallPayload);
    SST_SER(largePayload);
    SST_SER(largeEventFraction);
    SST_SER(recvCount);
    SST_SER(movementFunctionType);
    SST_SER(movementFunctionCounter);

    // SST RNG has built-in serialization support
    SST_SER(rng);


    // If unpacking, make sure to restore the movementFunction pointer.
    if (ser.mode() == SST::Core::Serialization::serializer::UNPACK) {
      if (movementFunctionType == RANDOM) {
        movementFunction = std::bind(&Node::movementFunctionRandom, this);
      } else if (movementFunctionType == CYCLIC) {
        movementFunction = std::bind(&Node::movementFunctionCyclic, this);
      } else {
        std::cerr << "Unrecognized movement function type during deserialization, defaulting to random\n";
        movementFunction = std::bind(&Node::movementFunctionRandom, this);
      }
    }
}

void ExponentialNode::serialize_order(SST::Core::Serialization::serializer& ser) {
    // Serialize component state for checkpointing
    Node::serialize_order(ser);
    SST_SER(multiplier);
}

void UniformNode::serialize_order(SST::Core::Serialization::serializer& ser) {
    // Serialize component state for checkpointing
    Node::serialize_order(ser);
    SST_SER(min);
    SST_SER(max);
}
#endif
