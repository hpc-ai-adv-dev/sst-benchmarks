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
    return num + amount;
}

std::string basicSubComponentIncrement::compute ( std::string comp )
{
    return "(" + comp + ")" + " + " + std::to_string(amount);
}

void basicSubComponentIncrement::serialize_order(SST::Core::Serialization::serializer& ser) {
    SubComponent::serialize_order(ser);

    SST_SER(amount);
}

void basicSubComponentIncrement::handleEvent(SST::Event* ev) {
    SST::Interfaces::StringEvent* payloadEv = 
        dynamic_cast<SST::Interfaces::StringEvent*>(ev);

    int received_value = std::stoi(payloadEv->getString());
    std::cout << "Received event with value " << received_value << " on link " << link_name << std::endl;
    parent->out->output("SubComponent %s received event with received_value %d. Remaining: %d\n", getName().c_str(), received_value, this->parent->value);
   
    parent->continuePassing(ev);
    
}

void basicSubComponentIncrement::sendEvent(SST::Event* ev) {
    std::cout << "Sending event with value " << dynamic_cast<SST::Interfaces::StringEvent*>(ev)->getString() << " on link " << link_name << std::endl;
    link->send(ev);
    std::cout << "Event sent with value " << dynamic_cast<SST::Interfaces::StringEvent*>(ev)->getString() << " on link " << link_name << std::endl;
}