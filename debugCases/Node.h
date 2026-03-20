#ifndef _node_H
#define _node_H

#include <sst/core/component.h>
#include <sst/core/link.h>
#include <sst/core/interfaces/stringEvent.h>
#include <string>
#include <vector>

class Node : public SST::Component
{
  std::vector<SST::Link*> links;
  std::string name;
  std::string story;
  int visited;

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

    void handleEvent(SST::Event *ev);

    void serialize_order(SST::Core::Serialization::serializer& ser) override;

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "name",     "", ""     },
     { "numLinks", "", "0"    },
     { "story",    "", "none" }
    )
    
    SST_ELI_DOCUMENT_PORTS({{"port%d", "Ports to others", {}}})

  private:
    void sendMessageIfNode(const std::string &nodeName);

    void setup_wrongPath();
    void setup_infiniteLoop();
    void setup_unexpectedDisappear();
    void setup_missedDeadline();
    void setup_outOfOrderReceipt();
    void setup_duplicateSepTimes();
    void setup_duplicateSameTime();
    void setup_badMerge();
    void setup_missingLink();
    void setup_wrongLink();
    void setup_unexpectedDuplicateLink();
    void setup_directDeadlock();
    void setup_indirectDeadlock();
    void setup_detectWhenComponentBecomesInvalid();
    void setup_badInvariantBetweenStates();
    void setup_componentsLoseParity();
    void setup_divergedModels_A();
    void setup_divergedModels_B();
    void setup_componentCausesSegfault();
    void setup_badInitialState();
    void setup_badTerminatingState();
    void setup_findFirstToComplete();
    void setup_determineWhatNotComplete();
    void setup_findEventHeavyComponent();
    void setup_findSlowProcessingComponent();
    void setup_findMemIntensiveComponent();
    void setup_findMemIntensiveEvent();
    void setup_findStarvedComponent();

    bool clockTick_duplicateSepTimes(SST::Cycle_t currentCycle);

    void handleEvent_wrongPath(SST::Event *ev);
    void handleEvent_infiniteLoop(SST::Event *ev);
    void handleEvent_unexpectedDisappear(SST::Event *ev);
    void handleEvent_missedDeadline(SST::Event *ev);
    void handleEvent_outOfOrderReceipt(SST::Event *ev);
    void handleEvent_duplicateSepTimes(SST::Event *ev);
    void handleEvent_duplicateSameTime(SST::Event *ev);
    void handleEvent_badMerge(SST::Event *ev);
    void handleEvent_missingLink(SST::Event *ev);
    void handleEvent_wrongLink(SST::Event *ev);
    void handleEvent_unexpectedDuplicateLink(SST::Event *ev);
    void handleEvent_directDeadlock(SST::Event *ev);
    void handleEvent_indirectDeadlock(SST::Event *ev);
    void handleEvent_detectWhenComponentBecomesInvalid(SST::Event *ev);
    void handleEvent_badInvariantBetweenStates(SST::Event *ev);
    void handleEvent_componentsLoseParity(SST::Event *ev);
    void handleEvent_divergedModels_A(SST::Event *ev);
    void handleEvent_divergedModels_B(SST::Event *ev);
    void handleEvent_componentCausesSegfault(SST::Event *ev);
    void handleEvent_badInitialState(SST::Event *ev);
    void handleEvent_badTerminatingState(SST::Event *ev);
    void handleEvent_findFirstToComplete(SST::Event *ev);
    void handleEvent_determineWhatNotComplete(SST::Event *ev);
    void handleEvent_findEventHeavyComponent(SST::Event *ev);
    void handleEvent_findSlowProcessingComponent(SST::Event *ev);
    void handleEvent_findMemIntensiveComponent(SST::Event *ev);
    void handleEvent_findMemIntensiveEvent(SST::Event *ev);
    void handleEvent_findStarvedComponent(SST::Event *ev);

    void setupLinks(int numLinks);
};

#endif
