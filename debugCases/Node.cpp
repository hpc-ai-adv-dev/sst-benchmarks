#include <sst/core/sst_config.h>
#include <assert.h>
#include "Node.h"

#define NODE_STORY_LIST(X)                           \
  do {                                               \
    bool storyMatched = false;                       \
    X(wrongPath)                                     \
    X(infiniteLoop)                                  \
    X(unexpectedDisappear)                           \
    X(missedDeadline)                                \
    X(outOfOrderReceipt)                             \
    X(duplicateSepTimes)                             \
    X(duplicateSameTime)                             \
    X(badMerge)                                      \
    X(missingLink)                                   \
    X(wrongLink)                                     \
    X(unexpectedDuplicateLink)                       \
    X(directDeadlock)                                \
    X(indirectDeadlock)                              \
    X(detectWhenComponentBecomesInvalid)             \
    X(badInvariantBetweenStates)                     \
    X(componentsLoseParity)                          \
    X(divergedModels_A)                              \
    X(divergedModels_B)                              \
    X(componentCausesSegfault)                       \
    X(badInitialState)                               \
    X(badTerminatingState)                           \
    X(findFirstToComplete)                           \
    X(determineWhatNotComplete)                      \
    X(findEventHeavyComponent)                       \
    X(findSlowProcessingComponent)                   \
    X(findMemIntensiveComponent)                     \
    X(findMemIntensiveEvent)                         \
    X(findStarvedComponent)                          \
    if (!storyMatched) {                             \
      std::cout << "INVALID STORY" << std::endl;    \
      assert(false);                                 \
    }                                                \
  } while (0)


#define DISPATCH_STORY_SETUP(storyName)         \
  if (!storyMatched && story == #storyName) {    \
    setup_##storyName();                          \
    storyMatched = true;                          \
  }

#define DISPATCH_STORY_EVENT_HANDLER(storyName)  \
  if (!storyMatched && story == #storyName) {   \
    handleEvent_##storyName(ev);                \
    storyMatched = true;                        \
  }

Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  name   = params.find<std::string>("name",  "");
  story  = params.find<std::string>("story", "");
  visited = 0;
  setupLinks(params.find<int>("numLinks", 0));

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
}

Node::~Node() { }

void Node::setup() {
  NODE_STORY_LIST(DISPATCH_STORY_SETUP);
}

void Node::sendMessageIfNode(const std::string &nodeName) {
  if(name == nodeName) {
    visited++;
    auto ev = new SST::Interfaces::StringEvent("event");
    links[0]->send(ev);
  }
}

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
  sendMessageIfNode("A");
  sendMessageIfNode("C");
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

void Node::setup_badMerge() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_missingLink() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_wrongLink() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_unexpectedDuplicateLink() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_directDeadlock() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_indirectDeadlock() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_detectWhenComponentBecomesInvalid() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_badInvariantBetweenStates() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_componentsLoseParity() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_divergedModels_A() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_divergedModels_B() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_componentCausesSegfault() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_badInitialState() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_badTerminatingState() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findFirstToComplete() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_determineWhatNotComplete() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findEventHeavyComponent() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findSlowProcessingComponent() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findMemIntensiveComponent() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findMemIntensiveEvent() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::setup_findStarvedComponent() {
  std::cout << "Story not implemented" << std::endl;
  assert(false);
}

void Node::handleEvent(SST::Event* ev) {
  NODE_STORY_LIST(DISPATCH_STORY_EVENT_HANDLER);
}

void Node::handleEvent_wrongPath(SST::Event *ev) {
  visited++;
  if(name == "B") {
    // The artificial bug is here, we intend to send to link[1] (to C) but instead
    // send to link[2] (D)
    links[2]->send(ev);
  }
  if(name == "C") {
    std::cout << "GOAL!" << std::endl;
  }
}

void Node::handleEvent_infiniteLoop(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
  else if(name == "C") { links[0]->send(ev); }
  else if(name == "D") {
    std::cout << "GOAL!" << std::endl;
  }
}

void Node::handleEvent_unexpectedDisappear(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
}

void Node::handleEvent_missedDeadline(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
  else if(name == "C") { links[1]->send(ev); }
}

void Node::handleEvent_outOfOrderReceipt(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
  else if(name == "C") { links[0]->send(ev); }
  else if(name == "D") { links[1]->send(ev); }
}

void Node::handleEvent_duplicateSepTimes(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
  else if(name == "C") { links[1]->send(ev); }
}

void Node::handleEvent_duplicateSameTime(SST::Event *ev) {
  visited++;
       if(name == "A") { links[0]->send(ev); }
  else if(name == "B") { links[1]->send(ev); }
  else if(name == "C") { links[1]->send(ev); }
}

void Node::handleEvent_badMerge(SST::Event *ev) {
}

void Node::handleEvent_missingLink(SST::Event *ev) {
}

void Node::handleEvent_wrongLink(SST::Event *ev) {
}

void Node::handleEvent_unexpectedDuplicateLink(SST::Event *ev) {
}

void Node::handleEvent_directDeadlock(SST::Event *ev) {
}

void Node::handleEvent_indirectDeadlock(SST::Event *ev) {
}

void Node::handleEvent_detectWhenComponentBecomesInvalid(SST::Event *ev) {
}

void Node::handleEvent_badInvariantBetweenStates(SST::Event *ev) {
}

void Node::handleEvent_componentsLoseParity(SST::Event *ev) {
}

void Node::handleEvent_divergedModels_A(SST::Event *ev) {
}

void Node::handleEvent_divergedModels_B(SST::Event *ev) {
}

void Node::handleEvent_componentCausesSegfault(SST::Event *ev) {
}

void Node::handleEvent_badInitialState(SST::Event *ev) {
}

void Node::handleEvent_badTerminatingState(SST::Event *ev) {
}

void Node::handleEvent_findFirstToComplete(SST::Event *ev) {
}

void Node::handleEvent_determineWhatNotComplete(SST::Event *ev) {
}

void Node::handleEvent_findEventHeavyComponent(SST::Event *ev) {
}

void Node::handleEvent_findSlowProcessingComponent(SST::Event *ev) {
}

void Node::handleEvent_findMemIntensiveComponent(SST::Event *ev) {
}

void Node::handleEvent_findMemIntensiveEvent(SST::Event *ev) {
}

void Node::handleEvent_findStarvedComponent(SST::Event *ev) {
}

void Node::setupLinks(int numLinks) {
    links = std::vector<SST::Link*>(numLinks);

    // Configure ports named port0..portN. If configuration fails the
    // pointer will be nullptr.
    for (int i = 0; i < numLinks; i++) {
        std::string portName = "port" + std::to_string(i);

        auto* evHandler = new SST::Event::Handler2<
            Node, &Node::handleEvent>(this);
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
}

#undef DISPATCH_STORY_EVENT_HANDLER
#undef DISPATCH_STORY_SETUP
#undef NODE_STORY_LIST
