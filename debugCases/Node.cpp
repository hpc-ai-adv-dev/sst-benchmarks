// Implements the debug-use-case SST component behavior for all stories.  This
// file contains story setup logic, clock callbacks, and event handling used by
// the Node component declared in Node.h.  See README.md in this directory for
// descriptions of each story.

#include <sst/core/sst_config.h>
#include <sst/core/rng/mersenne.h>
#include <assert.h>
#include "Node.h"


// See https://en.wikipedia.org/wiki/X_macro to understand this pattern.  This
// is used by the DISPATCH_STORY_SETUP and DISPATCH_STORY_EVENT_HANDLER macros
// in setup() and handleEvent() to dispatch to the right story-specific setup or
// handleEvent function.  The alternative would be to use a long if-else chain
// in each function to do the dispatch.
#define NODE_STORY_LIST(X)               \
  do {                                   \
    bool storyMatched = false;           \
                                         \
    /* --- Event Tracing --- */          \
    X(wrongPath)                         \
    X(infiniteLoop)                      \
    X(unexpectedDisappear)               \
    X(missedDeadline)                    \
    X(outOfOrderReceipt)                 \
    X(duplicateSepTimes)                 \
    X(duplicateSameTime)                 \
                                         \
    /* --- Event Processing --- */       \
    X(broadcastStorm)                    \
    X(badMerge)                          \
                                         \
    /* --- Incorrect Topology --- */     \
    X(missingLink)                       \
    X(wrongLink)                         \
    X(unexpectedDuplicateLink)           \
                                         \
    /* --- Deadlock --- */               \
    X(directDeadlock)                    \
    X(indirectDeadlock)                  \
                                         \
    /* --- Fault Detection And Attribution --- */      \
    X(detectWhenComponentBecomesInvalid) \
    X(badInvariantBetweenComponents)     \
    X(componentsLoseParity)              \
    X(divergedModels_A)                  \
    X(divergedModels_B)                  \
    X(componentCausesSegfault)           \
    X(badInitialState)                   \
    X(badTerminatingState)               \
    X(findFirstToComplete)               \
    X(determineWhatNotComplete)          \
                                         \
    /* --- Load Imbalances --- */        \
    X(findEventHeavyComponent)           \
    X(findSlowProcessingComponent)       \
    X(findMemHeavyComponent)             \
    X(findMemHeavyEvent)                 \
    X(findStarvedComponent)              \
    if (!storyMatched) {                               \
      std::cout << "INVALID STORY" << std::endl;       \
      assert(false);                                   \
    }                                                  \
  } while (0);

// Macro intended to be passed to NODE_STORY_LIST in setup() to dispatch to the
// right setup function based on the current story.
#define DISPATCH_STORY_SETUP(storyName)         \
  if (!storyMatched && story == #storyName) {   \
    setup_##storyName();                        \
    storyMatched = true;                        \
  }

// Macro intended to be passed to NODE_STORY_LIST in handleEvent() to dispatch
// to the right event handler function based on the current story.
#define DISPATCH_STORY_EVENT_HANDLER(storyName) \
  if (!storyMatched && story == #storyName) {   \
    handleEvent_##storyName(ev, fromPort);      \
    storyMatched = true;                        \
  }

Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
  , name("")
  , visited(0)
  , value(0)
  , valid(true)
  , payload(nullptr)
  , story("")
  , links()
{
  name   = params.find<std::string>("name",  "");
  story  = params.find<std::string>("story", "");
  setupLinks(params.find<int>("numLinks", 0));

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
}

Node::~Node() {
  if(payload != nullptr) {
    free(payload);
  }
}

// ============================================================================
// Component Setup
// ============================================================================

void Node::setup() {
  NODE_STORY_LIST(DISPATCH_STORY_SETUP);
}

void Node::sendMessageIfNode(const std::string &nodeName, int value) {
  if(name == nodeName) {
    visited++;
    auto ev = new UseCaseEvent(value);
    links[0]->send(ev);
  }
}

// --- Event Tracing ---
void Node::setup_wrongPath() {
  sendMessageIfNode("A");
}

void Node::setup_infiniteLoop() {
  sendMessageIfNode("A");
}

void Node::setup_unexpectedDisappear() {
  sendMessageIfNode("A");
}

void Node::setup_missedDeadline() {
  sendMessageIfNode("A");
}

void Node::setup_outOfOrderReceipt() {
  if(name == "A" || name == "C") {
    auto clockHandler =
      new SST::Clock::Handler2<Node, &Node::clockTick_outOfOrderReceipt>(this);
    registerClock("1ns", clockHandler);
  }
}

bool Node::clockTick_outOfOrderReceipt(SST::Cycle_t currentCycle) {
  if((name == "A" && currentCycle >= 5) ||
     (name == "C" && currentCycle >= 3)) {
    visited++;
    links[0]->send(new UseCaseEvent());
  }

  return false;
}

void Node::setup_duplicateSepTimes() {
  sendMessageIfNode("A");
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_duplicateSepTimes>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_duplicateSepTimes(SST::Cycle_t currentCycle) {
  sendMessageIfNode("A");
  return true;
}

void Node::setup_duplicateSameTime() {
  sendMessageIfNode("A");
  sendMessageIfNode("A");
}

// --- Event Processing ---
void Node::setup_broadcastStorm() {
  if(name == "A") {
    for(int i = 0; i < 6; i++) {
      auto ev = new UseCaseEvent(0);
      links[i]->send(ev);
    }
  }
}

void Node::setup_badMerge() {
  sendMessageIfNode("A", 10);
  sendMessageIfNode("B", 2);
}

// --- Incorrect Topology ---
void Node::setup_missingLink() {
  // We don't simulate any behavior in the topology test cases.
}

void Node::setup_wrongLink() {
  // We don't simulate any behavior in the topology test cases.
}

void Node::setup_unexpectedDuplicateLink() {
  // We don't simulate any behavior in the topology test cases.
}

// --- Deadlock ---
void Node::setup_directDeadlock() {
  // Intentionally send nothing: A waits on B and B waits on A.
}

void Node::setup_indirectDeadlock() {
  // Intentionally send nothing: A waits on C, C waits on A, and B only relays.
}

// --- Fault Detection And Attribution ---
void Node::setup_detectWhenComponentBecomesInvalid() {
  if(name == "A") {
    auto clockHandler =
      new SST::Clock::Handler2<Node, &Node::clockTick_detectWhenComponentBecomesInvalid>(this);
    registerClock("40ns", clockHandler);
  }
}

bool Node::clockTick_detectWhenComponentBecomesInvalid(SST::Cycle_t currentCycle) {
  valid = false;
  return true;
}

void Node::setup_badInvariantBetweenComponents() {
  if(name == "B" || name == "C") {
    value = 10;
  }

  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_badInvariantBetweenComponents>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_badInvariantBetweenComponents(SST::Cycle_t currentCycle) {
  if(name == "A" || name == "B") {
    value++;
  } else if(name == "C") {
    int nextValue = value + 2;
    value = (nextValue == 30) ? 50 : nextValue;
  }
  return false;
}

void Node::setup_componentsLoseParity() {
  if(name == "A" || name == "B") {
    auto clockHandler =
      new SST::Clock::Handler2<Node, &Node::clockTick_componentsLoseParity>(this);
    registerClock("1ns", clockHandler);
  }
}

bool Node::clockTick_componentsLoseParity(SST::Cycle_t currentCycle) {
  if(currentCycle == 10) {
    value = 1;
  } else if(currentCycle == 20) {
    value = 4;
  } else if(currentCycle == 30) {
    value = 3;
  } else if(currentCycle == 40) {
    value = (name == "A") ? 5 : 7;
  }

  return false;
}

void Node::setup_divergedModels_A() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_divergedModels_A>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_divergedModels_A(SST::Cycle_t currentCycle) {
  if     (currentCycle == 10) { value = 1; }
  else if(currentCycle == 20) { value = 4; }
  else if(currentCycle == 30) { value = 3; }
  else if(currentCycle == 40) { value = 5; }   // The values diverge here!
  else if(currentCycle == 50) { value = 10; }
  return false;
}

void Node::setup_divergedModels_B() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_divergedModels_B>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_divergedModels_B(SST::Cycle_t currentCycle) {
  if     (currentCycle == 10) { value = 1; }
  else if(currentCycle == 20) { value = 4; }
  else if(currentCycle == 30) { value = 3; }
  else if(currentCycle == 40) { value = 7; }  // The values diverge here!
  else if(currentCycle == 50) { value = 10; }
  return false;
}

void Node::setup_componentCausesSegfault() {
  if(name == "C") {
    auto clockHandler =
      new SST::Clock::Handler2<Node, &Node::clockTick_componentCausesSegfault>(this);
    registerClock("1ns", clockHandler);
  }
}

bool Node::clockTick_componentCausesSegfault(SST::Cycle_t currentCycle) {
  if(currentCycle >= 50) {
    assert(false);
  }
  return false;
}

void Node::setup_badInitialState() {
  if(name == "A" || name == "B" || name == "D") {
    value = 1;
  } else if(name == "C") {
    value = 3;
  }
}

void Node::setup_badTerminatingState() {
  value = 1;
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_badTerminatingState>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_badTerminatingState(SST::Cycle_t currentCycle) {
  if(name == "C" && currentCycle == 500) {
    value = 3;
  }
  if(currentCycle >= 1000) {
    primaryComponentOKToEndSim();
    return true;
  }
  return false;
}

void Node::setup_findFirstToComplete() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_findFirstToComplete>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_findFirstToComplete(SST::Cycle_t currentCycle) {
  SST::Cycle_t completionTime;
  if     (name == "A") { completionTime = 750; }
  else if(name == "B") { completionTime = 300; }
  else if(name == "C") { completionTime = 492; }
  else                 { completionTime = 234; } // D is the fastest!

  if(currentCycle >= completionTime) {
    primaryComponentOKToEndSim();
    return true;
  }
  return false;
}

void Node::setup_determineWhatNotComplete() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_determineWhatNotComplete>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_determineWhatNotComplete(SST::Cycle_t currentCycle) {
  SST::Cycle_t completionTime;
  if     (name == "A") { completionTime = 100; }
  else if(name == "D") { completionTime = 230; }
  else if(name == "E") { completionTime = 340; }

  if(currentCycle >= completionTime) {
    primaryComponentOKToEndSim();
    return true;
  }
  return false;
}

// --- Load Imbalances ---
void Node::setup_findEventHeavyComponent() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_findEventHeavyComponent>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_findEventHeavyComponent(SST::Cycle_t currentCycle) {
  int quota;
  if     (name == "A") quota = 3;
  else if(name == "B") quota = 1;
  else if(name == "C") quota = 1;
  else if(name == "D") quota = 2;
  else { assert(false); }

  if(value < quota) {
    links[1]->send(new UseCaseEvent());
    value++;
  }

  return false;
}

void Node::setup_findSlowProcessingComponent() {
  links[0]->send(new UseCaseEvent());
}

void Node::setup_findMemHeavyComponent() {
  size_t bufferSize;
  if     (name == "A") bufferSize = 300;
  else if(name == "B") bufferSize = 1000000;
  else if(name == "C") bufferSize = 200;
  else if(name == "D") bufferSize = 700;
  else { assert(false); }

  payload = malloc(bufferSize);
}

void Node::setup_findMemHeavyEvent() {
  // Send event with payload to right neighbor
  size_t payloadSize;
  if     (name == "A") payloadSize = 1000000;  // A sends 1M to B
  else if(name == "B") payloadSize = 375;      // B sends 375 to C
  else if(name == "C") payloadSize = 412;      // C sends 412 to D
  else if(name == "D") payloadSize = 200;      // D sends 200 to A
  else { assert(false); }

  void* payloadBuffer = malloc(payloadSize);
  auto ev = new UseCaseEvent(0, payloadBuffer, payloadSize);
  links[1]->send(ev);  // Send to right neighbor
}

void Node::setup_findStarvedComponent() {
  auto clockHandler =
    new SST::Clock::Handler2<Node, &Node::clockTick_findStarvedComponent>(this);
  registerClock("1ns", clockHandler);
}

bool Node::clockTick_findStarvedComponent(SST::Cycle_t currentCycle) {
  int sendQuota;
  if     (name == "A") sendQuota = 3;
  else if(name == "B") sendQuota = 0;
  else if(name == "C") sendQuota = 2;
  else if(name == "D") sendQuota = 2;
  else { assert(false); }

  if(value < sendQuota) {
    links[1]->send(new UseCaseEvent());
    value++;
  }

  return false;
}

// ============================================================================
// Event Handling
// ============================================================================

void Node::handleEvent(SST::Event* ev, int fromPort) {
  NODE_STORY_LIST(DISPATCH_STORY_EVENT_HANDLER);
}

// --- Event Tracing ---
void Node::handleEvent_wrongPath(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

  if(name == "B") {
    // The artificial bug is here, we intend to send to link[1] (to C) but instead
    // send to link[2] (D)
    links[2]->send(ev);
    forwarded = true;
  }

  if(name == "C") {
    std::cout << "GOAL!" << std::endl;
  }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_infiniteLoop(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }
  else if(name == "C") { links[0]->send(ev); forwarded = true; }
  else if(name == "D") {
    std::cout << "GOAL!" << std::endl;
  }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_unexpectedDisappear(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_missedDeadline(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }
  else if(name == "C") { links[1]->send(ev); forwarded = true; }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_outOfOrderReceipt(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }
  else if(name == "C") { links[0]->send(ev); forwarded = true; }
  else if(name == "D") { links[1]->send(ev); forwarded = true; }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_duplicateSepTimes(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }
  else if(name == "C") { links[1]->send(ev); forwarded = true; }

  if(!forwarded) {
    delete ev;
  }
}

void Node::handleEvent_duplicateSameTime(SST::Event *ev, int fromPort) {
  visited++;
  bool forwarded = false;

       if(name == "A") { links[0]->send(ev); forwarded = true; }
  else if(name == "B") { links[1]->send(ev); forwarded = true; }
  else if(name == "C") { links[1]->send(ev); forwarded = true; }

  if(!forwarded) {
    delete ev;
  }
}

// --- Event Processing ---
void Node::handleEvent_broadcastStorm(SST::Event *ev, int fromPort) {
  visited++;
  delete ev;
}

void Node::handleEvent_badMerge(SST::Event *ev, int fromPort) {
  visited++;
  if(name == "C") {
    auto useCaseEvent = dynamic_cast<UseCaseEvent*>(ev);

    if(value == 0) {
      value = useCaseEvent->value;
    } else {
      // The bug is we were expected to do an add-reduction not a multiply reduction
      value *= useCaseEvent->value;
    }

    // Only send message out we've received two messages and merged them
    if(visited >= 2) {
      links[2]->send(new UseCaseEvent(value)); 
    }
  }

  if(name == "D") {
    auto useCaseEvent = dynamic_cast<UseCaseEvent*>(ev);
    value = useCaseEvent->value;
  }

  delete ev;
}

// --- Incorrect Topology ---
void Node::handleEvent_missingLink(SST::Event *ev, int fromPort) {
  // We don't simulate any behavior in the topology test cases.
}

void Node::handleEvent_wrongLink(SST::Event *ev, int fromPort) {
  // We don't simulate any behavior in the topology test cases.
}

void Node::handleEvent_unexpectedDuplicateLink(SST::Event *ev, int fromPort) {
  // We don't simulate any behavior in the topology test cases.
}

// --- Deadlock ---
void Node::handleEvent_directDeadlock(SST::Event *ev, int fromPort) {
  visited++;

  if(name == "A" || name == "B") {
    links[0]->send(new UseCaseEvent());
  }

  delete ev;
}

void Node::handleEvent_indirectDeadlock(SST::Event *ev, int fromPort) {
  visited++;

  if(name == "A" || name == "C") {
    // A expects to receive a message from C via B and to send a new message back.
    // and similiarly, C expects to receive a message from A via B and will send a new message back.
    auto ucev = dynamic_cast<UseCaseEvent*>(ev);
    links[0]->send(new UseCaseEvent(ucev->value+1));
    delete ev;
  } else if(name == "B") {
    // B relays A->C and C->A.
    if(fromPort == 0) {
      links[1]->send(ev);
    } else {
      assert(fromPort == 1);
      links[0]->send(ev);
    }
  }
}

// --- Fault Detection And Attribution ---
void Node::handleEvent_detectWhenComponentBecomesInvalid(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_badInvariantBetweenComponents(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_componentsLoseParity(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_divergedModels_A(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_divergedModels_B(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_componentCausesSegfault(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_badInitialState(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_badTerminatingState(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_findFirstToComplete(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_determineWhatNotComplete(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

// --- Load Imbalances ---
void Node::handleEvent_findEventHeavyComponent(SST::Event *ev, int fromPort) {
  delete ev;
}

void Node::handleEvent_findSlowProcessingComponent(SST::Event *ev, int fromPort) {
  static SST::RNG::MersenneRNG rng;
  volatile uint32_t result = 0;

  visited++;

  // Generate a bunch of busywork so that one component processes slower than the others.
  int iterations;
  if     (name == "A") iterations = 100;
  else if(name == "B") iterations = 1000000000; // B is the slow snail!
  else if(name == "C") iterations = 100;
  else if(name == "D") iterations = 100;
  else { assert(false); }

  for(int i = 0; i < iterations; i++) {
    result = rng.generateNextUInt32();
  }

  delete ev;
}

void Node::handleEvent_findMemHeavyComponent(SST::Event *ev, int fromPort) {
  // This story doesn't need to process any events.
}

void Node::handleEvent_findMemHeavyEvent(SST::Event *ev, int fromPort) {
  auto useCaseEvent = dynamic_cast<UseCaseEvent*>(ev);
  if(useCaseEvent && useCaseEvent->payload) {
    free(useCaseEvent->payload);
  }
  delete ev;
}

void Node::handleEvent_findStarvedComponent(SST::Event *ev, int fromPort) {
  visited++;
  delete ev;
}

void Node::setupLinks(int numLinks) {
    links = std::vector<SST::Link*>(numLinks);

    // Configure ports named port0..portN. If configuration fails the
    // pointer will be nullptr.
    for (int i = 0; i < numLinks; i++) {
        std::string portName = "port" + std::to_string(i);

        auto* evHandler = new SST::Event::Handler2<
            Node, &Node::handleEvent, int>(this, i);
        links[i] = configureLink(portName, evHandler);
        if (links[i] == nullptr) {
            // Link not configured; leave nullptr.
        } else {
            // Link configured.
        }
    }
}

void Node::serialize_order(SST::Core::Serialization::serializer& ser) {
    SST::Component::serialize_order(ser);
    SST_SER(name);
    SST_SER(visited);
    SST_SER(valid);
    SST_SER(value);
}

#undef DISPATCH_STORY_EVENT_HANDLER
#undef DISPATCH_STORY_SETUP
#undef NODE_STORY_LIST