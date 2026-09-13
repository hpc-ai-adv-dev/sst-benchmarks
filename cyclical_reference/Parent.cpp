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
#include "sst/core/sst_config.h"

#include "Child.h"
#include "Parent.h"
#include <sst/core/interfaces/stringEvent.h>
using namespace SST;
using namespace SST::cyclical;

ParentComponent::ParentComponent(ComponentId_t id, Params& params) : Component(id) {

    out = new Output("", 1, 0, Output::STDOUT);

    bool found;
    value = params.find<int>("value", 0, found);
    sst_assert(found, CALL_INFO, -1,
            "Error: The parameter 'value' is a required parameter and was not found "
            "in the input configuration\n");
    
    leftChild = loadAnonymousSubComponent<basicSubComponentAPI>("cyclical.basicSubComponent",
                "left_slot", 0, ComponentInfo::SHARE_PORTS, params, this, "left");
    rightChild = loadAnonymousSubComponent<basicSubComponentAPI>("cyclical.basicSubComponent",
                "right_slot", 0, ComponentInfo::SHARE_PORTS, params, this, "right");

    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
}


ParentComponent::~ParentComponent()
{
    delete out;
}

void ParentComponent::setup()
{ 
    // Create the event we'll send
    SST::Event* event = new SST::Interfaces::StringEvent("0");

    // Send our event through the left child.
    leftChild->sendEvent(event);
}

void ParentComponent::finish() {
    out->output("Component %s is finishing. Final value: %d\n",
         getName().c_str(), this->value);
    leftChild->finish();
    rightChild->finish();
}

void ParentComponent::computeAndSend(SST::Event* ev) {
    int event_value = std::stoi(dynamic_cast<SST::Interfaces::StringEvent*>(ev)->getString());

    out->output("Component %s is continuing to pass the event."
        "Remaining value: %d. Event value: %d\n", getName().c_str(), 
        this->value, event_value);

    this->value -= event_value;

    if (this->value <= 0) {
        out->output("Component %s is ready to end simulation\n", getName().c_str());
        primaryComponentOKToEndSim();
    }
    leftChild->sendEvent(ev);
}

ParentComponent::ParentComponent() : Component() {}


void ParentComponent::serialize_order(SST::Core::Serialization::serializer& ser) {
    Component::serialize_order(ser);

    SST_SER(out);
    SST_SER(value);

    SST_SER(leftChild);
    SST_SER(rightChild);
}
