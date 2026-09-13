// Copyright 2009-2025 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2025, NTESS
// All rights reserved.
//
// Portions are copyright of other developers:
// See the file CONTRIBUTORS.TXT in the top level directory
// of the distribution for more information.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.


// This include is ***REQUIRED***
// for ALL SST implementation files
#include <sst/core/sst_config.h>

#include "Child.h"
#include "Parent.h"

#include <sst/core/interfaces/stringEvent.h>

using namespace SST;
using namespace SST::cyclical;


basicSubComponent::basicSubComponent(ComponentId_t id, Params& params, ParentComponent* parent, std::string link_name) 
    : basicSubComponentAPI(id, params, parent, link_name), parent(parent), link_name(link_name)
{
    amount = params.find<int>("amount",  1);
    link = configureLink(link_name, 
        new Event::Handler2<basicSubComponent, &basicSubComponent::handleEvent>(this));
    sst_assert(link, CALL_INFO, -1,
        "Error: SubComponent %s has an incorrectly configured link on port '%s'\n", 
        getName().c_str(), link_name.c_str());
}

basicSubComponent::~basicSubComponent() { }

void basicSubComponent::handleEvent(SST::Event* ev) {
    SST::Interfaces::StringEvent* payloadEv = 
        dynamic_cast<SST::Interfaces::StringEvent*>(ev);

    int received_value = std::stoi(payloadEv->getString());
    
    getSimulationOutput().output(
        "%s SubComponent of %s received event with value %d. " 
        "Remaining on parent: %d. Subcomponent amount: %d\n", 
        link_name.c_str(), getName().c_str(), received_value, this->parent->value, amount);
   
    int new_value = received_value + amount++; // changes the state of the subcomponent

    SST::Interfaces::StringEvent* new_ev = new SST::Interfaces::StringEvent(std::to_string(new_value));
    
    delete ev;

    // Sends the newly created event up to the parent component, which will
    // then update its own state and send the event to the its neighbor
    parent->computeAndSend(new_ev);
}

void basicSubComponent::sendEvent(SST::Event* ev) {
    link->send(ev);
}

void basicSubComponent::finish() {
    getSimulationOutput().output(
        "%s SubComponent of %s is finishing. Final amount: %d\n", 
        link_name.c_str(), getName().c_str(), amount);
}


void basicSubComponent::serialize_order(SST::Core::Serialization::serializer& ser) {
    SubComponent::serialize_order(ser);
    SST_SER(amount);
    SST_SER(link_name);
    SST_SER(parent);
    SST_SER(link);
}