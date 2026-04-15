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

/*
 * During construction this components parses its parameter, configures its links, and loads its compute unit subcomponent
 */
basicSubComponent_Component::basicSubComponent_Component(ComponentId_t id, Params& params) : Component(id) {

    // SST Output Object
    out = new Output("", 1, 0, Output::STDOUT);

    // Get the parameter, check if it was found or not and if not, return an error
    bool found;
    value = params.find<int>("value", 0, found);
    sst_assert(found, CALL_INFO, -1,
            "Error: The parameter 'value' is a required parameter and was not found in the input configuration\n");
    
    // Configure our links to call our event handler when an event arrives
    //leftLink = configureLink("left", new Event::Handler2<basicSubComponent_Component, &basicSubComponent_Component::handleEvent>(this));
    //rightLink = configureLink("right", new Event::Handler2<basicSubComponent_Component, &basicSubComponent_Component::handleEvent>(this));


    /****** Load a SubComponent in two steps ******/
    std::cout << "Loading subcomponents for component " << getName() << std::endl;
    // 1. Check with the input configuration to see if the user put a subcomponent in our subcomponent slot
    leftChild = loadAnonymousSubComponent<basicSubComponentAPI>("cyclical.basicSubComponentIncrement",
                "left_slot", 0, ComponentInfo::SHARE_PORTS, params, this, "left");
    rightChild = loadAnonymousSubComponent<basicSubComponentAPI>("cyclical.basicSubComponentIncrement",
                "right_slot", 0, ComponentInfo::SHARE_PORTS, params, this, "right");
    std::cout << "Finished loading subcomponents for component " << getName() << std::endl;
    /****** SubComponent loaded, almost done with construction ******/

    // Tell the simulation not to end until we're ready
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
}


/*
 * Destructor, clean up our output
 * We should not clean up our subcomponent - SST will do that
 */
basicSubComponent_Component::~basicSubComponent_Component()
{
    delete out;
}


/*
 * Setup function to send our event in preparation for simulation
 * Because the simulation has no clocks and SST will exit if no clocks and no events exist in the system,
 * we need to begin the simulation with an event.
 *
 * This function is called by SST on each component just prior to simulation start
 * It is *not* called on subcomponents automatically so we should manually call it on subcomponents that need it
 * Ours don't so we'll skip that step
 */
void basicSubComponent_Component::setup()
{ 
    // Create the event we'll send
    SST::Event* event = new SST::Interfaces::StringEvent("0");

    // Send our event
    leftChild->sendEvent(event);
}

/*
 * Event handling
 * If we get the event we sent, print the result and tell SST that we're OK if the simulation ends
 * If we get an event from someone else, pass it to our compute unit, update the event, and forward it to the left
 */

void basicSubComponent_Component::handleEvent(SST::Event* ev)
{
   out->output("Component %s received an event\n", getName().c_str());
}

void basicSubComponent_Component::continuePassing(SST::Event* ev) {
    std::cout << "Component " << getName() << " is passing the event along. Remaining value: " << this->value << std::endl;
    this->value -= 1;
    if (this->value <= 0) {
        registerReady();
    }
    leftChild->sendEvent(ev);
}

void basicSubComponent_Component::registerReady() {
    out->output("Component %s is ready to end simulation\n", getName().c_str());
    primaryComponentOKToEndSim();
}

/*
 * Default constructor
*/
basicSubComponent_Component::basicSubComponent_Component() : Component() {}

/*
 * Serialization function
*/
void basicSubComponent_Component::serialize_order(SST::Core::Serialization::serializer& ser) {
    Component::serialize_order(ser);

    SST_SER(out);
    SST_SER(value);

    SST_SER(leftLink);
    SST_SER(rightLink);

    SST_SER(leftChild);
    SST_SER(rightChild);
}
