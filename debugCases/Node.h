// Declares a component (Node) and event type (UseCaseEvent) used the debug use
// case stories.  See README.md file in this directory for descriptions of each
// story.

#ifndef _node_H
#define _node_H

#include <sst/core/component.h>
#include <sst/core/link.h>
#include <sst/core/event.h>
#include <cstdlib>
#include <string>
#include <vector>

class UseCaseEvent : public SST::Event {
public:
  int value;
  void* payload;
  size_t payloadSize;

  UseCaseEvent() : SST::Event(), value(0), payload(nullptr), payloadSize(0) {}
  UseCaseEvent(int value) : SST::Event(), value(value), payload(nullptr), payloadSize(0) {}
  UseCaseEvent(int value, void* p, size_t size) : SST::Event(), value(value), payload(p), payloadSize(size) {}

  void serialize_order(SST::Core::Serialization::serializer &ser) override {
    SST::Event::serialize_order(ser);
    SST_SER(value);
  }

  ImplementSerializable(UseCaseEvent);
};

class Node : public SST::Component
{
  std::string name;
  int visited;
  int value;
  bool valid;
  void* payload;

  std::string story;
  std::vector<SST::Link*> links;

  public:
    SST_ELI_REGISTER_COMPONENT(
        Node,                             // Component class
        "debugUseCases",                  // Component library (for Python/library lookup)
        "Node",                           // Component name (for Python/library lookup)
        SST_ELI_ELEMENT_VERSION(1,0,0),   // Version of the component (not related to the SST version)
        "generic component",              // Description
        COMPONENT_CATEGORY_UNCATEGORIZED  // Category
    )

    Node(SST::ComponentId_t id, SST::Params& params);
    ~Node();

    void setup() override;

    void handleEvent(SST::Event *ev, int fromPort);

    void serialize_order(SST::Core::Serialization::serializer& ser) override;

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "name",     "", ""     },
     { "numLinks", "", "0"    },
     { "story",    "", "none" }
    )
    
    SST_ELI_DOCUMENT_PORTS({{"port%d", "Ports to others", {}}})

  private:
    void sendMessageIfNode(const std::string &nodeName, int value = 0);

    // --- Event Tracing ---
    void setup_wrongPath();
    void setup_infiniteLoop();
    void setup_unexpectedDisappear();
    void setup_missedDeadline();
    void setup_outOfOrderReceipt();
    void setup_duplicateSepTimes();
    void setup_duplicateSameTime();

    // --- Event Processing ---
    void setup_broadcastStorm();
    void setup_badMerge();

    // --- Incorrect Topology ---
    void setup_missingLink();
    void setup_wrongLink();
    void setup_unexpectedDuplicateLink();

    // --- Deadlock ---
    void setup_directDeadlock();
    void setup_indirectDeadlock();

    // --- Fault Detection And Attribution ---
    void setup_detectWhenComponentBecomesInvalid();
    void setup_badInvariantBetweenComponents();
    void setup_componentsLoseParity();
    void setup_divergedModels_A();
    void setup_divergedModels_B();
    void setup_componentCausesSegfault();
    void setup_badInitialState();
    void setup_badTerminatingState();
    void setup_findFirstToComplete();
    void setup_determineWhatNotComplete();

    // --- Load Imbalances ---
    void setup_findEventHeavyComponent();
    void setup_findSlowProcessingComponent();
    void setup_findMemHeavyComponent();
    void setup_findMemHeavyEvent();
    void setup_findStarvedComponent();

    bool clockTick_duplicateSepTimes(SST::Cycle_t currentCycle);
    bool clockTick_outOfOrderReceipt(SST::Cycle_t currentCycle);
    bool clockTick_detectWhenComponentBecomesInvalid(SST::Cycle_t currentCycle);
    bool clockTick_badInvariantBetweenComponents(SST::Cycle_t currentCycle);
    bool clockTick_componentsLoseParity(SST::Cycle_t currentCycle);
    bool clockTick_divergedModels_A(SST::Cycle_t currentCycle);
    bool clockTick_divergedModels_B(SST::Cycle_t currentCycle);
    bool clockTick_componentCausesSegfault(SST::Cycle_t currentCycle);
    bool clockTick_badTerminatingState(SST::Cycle_t currentCycle);
    bool clockTick_findFirstToComplete(SST::Cycle_t currentCycle);
    bool clockTick_determineWhatNotComplete(SST::Cycle_t currentCycle);
    bool clockTick_findEventHeavyComponent(SST::Cycle_t currentCycle);
    bool clockTick_findStarvedComponent(SST::Cycle_t currentCycle);

    // --- Event Tracing ---
    void handleEvent_wrongPath(SST::Event *ev, int fromPort);
    void handleEvent_infiniteLoop(SST::Event *ev, int fromPort);
    void handleEvent_unexpectedDisappear(SST::Event *ev, int fromPort);
    void handleEvent_missedDeadline(SST::Event *ev, int fromPort);
    void handleEvent_outOfOrderReceipt(SST::Event *ev, int fromPort);
    void handleEvent_duplicateSepTimes(SST::Event *ev, int fromPort);
    void handleEvent_duplicateSameTime(SST::Event *ev, int fromPort);

    // --- Event Processing ---
    void handleEvent_broadcastStorm(SST::Event *ev, int fromPort);
    void handleEvent_badMerge(SST::Event *ev, int fromPort);

    // --- Incorrect Topology ---
    void handleEvent_missingLink(SST::Event *ev, int fromPort);
    void handleEvent_wrongLink(SST::Event *ev, int fromPort);
    void handleEvent_unexpectedDuplicateLink(SST::Event *ev, int fromPort);

    // --- Deadlock ---
    void handleEvent_directDeadlock(SST::Event *ev, int fromPort);
    void handleEvent_indirectDeadlock(SST::Event *ev, int fromPort);

    // --- Fault Detection And Attribution ---
    void handleEvent_detectWhenComponentBecomesInvalid(SST::Event *ev, int fromPort);
    void handleEvent_badInvariantBetweenComponents(SST::Event *ev, int fromPort);
    void handleEvent_componentsLoseParity(SST::Event *ev, int fromPort);
    void handleEvent_divergedModels_A(SST::Event *ev, int fromPort);
    void handleEvent_divergedModels_B(SST::Event *ev, int fromPort);
    void handleEvent_componentCausesSegfault(SST::Event *ev, int fromPort);
    void handleEvent_badInitialState(SST::Event *ev, int fromPort);
    void handleEvent_badTerminatingState(SST::Event *ev, int fromPort);
    void handleEvent_findFirstToComplete(SST::Event *ev, int fromPort);
    void handleEvent_determineWhatNotComplete(SST::Event *ev, int fromPort);

    // --- Load Imbalances ---
    void handleEvent_findEventHeavyComponent(SST::Event *ev, int fromPort);
    void handleEvent_findSlowProcessingComponent(SST::Event *ev, int fromPort);
    void handleEvent_findMemHeavyComponent(SST::Event *ev, int fromPort);
    void handleEvent_findMemHeavyEvent(SST::Event *ev, int fromPort);
    void handleEvent_findStarvedComponent(SST::Event *ev, int fromPort);

    void setupLinks(int numLinks);
};

#endif
