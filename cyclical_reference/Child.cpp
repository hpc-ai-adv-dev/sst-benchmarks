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

/***********************************************************************************/
// Since the classes are brief, this file has the implementation for all four
// basicSubComponentAPI subcomponents declared in basicSubComponent_subcomponent.h
/***********************************************************************************/

// basicSubComponentIncrement

basicSubComponentIncrement::basicSubComponentIncrement(ComponentId_t id, Params& params, basicSubComponent_Component* parent, std::string link_name) 
    : basicSubComponentAPI(id, params, parent, link_name), parent(parent), link_name(link_name)
{
    amount = params.find<int>("amount",  1);
    link = configureLink(link_name, new Event::Handler2<basicSubComponentIncrement, &basicSubComponentIncrement::handleEvent>(this));
        sst_assert(link, CALL_INFO, -1,
                "Error: SubComponent %s has an incorrectly configured link on port '%s'\n", getName().c_str(), link_name.c_str());
}

basicSubComponentIncrement::~basicSubComponentIncrement() { }

int basicSubComponentIncrement::compute( int num )
{
    return num + amount++;

}

std::string basicSubComponentIncrement::compute ( std::string comp )
{
    return "(" + comp + ")" + " + " + std::to_string(amount++);
}

void basicSubComponentIncrement::serialize_order(SST::Core::Serialization::serializer& ser) {
    SubComponent::serialize_order(ser);

    SST_SER(amount);
    SST_SER(link_name);
    SST_SER(parent);
    SST_SER(link);
}

void basicSubComponentIncrement::handleEvent(SST::Event* ev) {
    SST::Interfaces::StringEvent* payloadEv = 
        dynamic_cast<SST::Interfaces::StringEvent*>(ev);

    int received_value = std::stoi(payloadEv->getString());
    
    std::cout << "Received event with value " << received_value << " on link " << link_name << std::endl;
    std::cout << "Computing new value with amount " << amount << std::endl;
    std::cout << "Accessing parent: " << this->parent->value << std::endl;
    std::cout << "ACcessing link name: " << link_name << std::endl;
    std::cout << "Calling getName(): " << getName() << std::endl;
    std::cout << "Using paret->out" << std::endl;
    getSimulationOutput().output("string");
    std::cout << "used parent->out";
    getSimulationOutput().output("%s SubComponent of %s received event with value %d. Remaining on parent: %d. Subcomponent amount: %d\n", link_name.c_str(), getName().c_str(), received_value, this->parent->value, amount);
   
    int new_value = compute(received_value); // this will change this component's state

    
    SST::Interfaces::StringEvent* new_ev = new SST::Interfaces::StringEvent(std::to_string(new_value));
    delete ev;
    // print the address of the parent pointer
    std::cout << "Parent pointer address: " << parent << std::endl;
    parent->continuePassing(new_ev);
    
}

void basicSubComponentIncrement::sendEvent(SST::Event* ev) {
    std::cout << "Sending event with value " << dynamic_cast<SST::Interfaces::StringEvent*>(ev)->getString() << " on link " << link_name << std::endl;
    link->send(ev);
    std::cout << "Event sent with value " << dynamic_cast<SST::Interfaces::StringEvent*>(ev)->getString() << " on link " << link_name << std::endl;
}

void basicSubComponentIncrement::finish() {
    getSimulationOutput().output("%s SubComponent of %s is finishing. Final amount: %d\n", link_name.c_str(), getName().c_str(), amount);
}