#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "Node.h"


Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  std::cout << "Initializing node";
  numRings = params.find<int>("numRings", 1);
  numLinks = (numRings+1) * (numRings+1);
  links = std::vector<SST::Link*>();
  for (int i = 0; i < numLinks; ++i) {
    std::string portName = "port" + std::to_string(i);
    links[i] = configureLink(portName, new SST::Event::Handler<Node>(this, &Node::handleEvent));
  }

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
}

Node::~Node() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}

void Node::setup() {
  std::cout << "Node setup";
  for(int i = 0; i < links.size(); i++) {
    if (links[i] && links[i]->isConfigured()) {
      links[i]->send(new SST::Interfaces::StringEvent("Hello from Node!"));
    }
  }
}

void Node::finish() { }

bool Node::tick( SST::Cycle_t currentCycle ) {
  primaryComponentOKToEndSim();
  return false;
}

void Node::handleEvent(SST::Event *ev){
  std::cout << "Handling event from component\n";

  size_t nextRecipientLinkId = movementFunction();

  while (links.at(nextRecipientLinkId) == nullptr) {
    nextRecipientLinkId = (nextRecipientLinkId + 1) % links.size();
  }
  links[nextRecipientLinkId]->send(ev);
}

size_t Node::movementFunction() {
  // Implement your movement logic here
  // For now, just return a random link ID
  return rand() % links.size();
}
  
