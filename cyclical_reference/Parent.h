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

#ifndef _ParentComponent_H
#define _ParentComponent_H

/*
 * This example demonstrates the use of subcomponents.
 *
 * Concepts covered:
 *  - ELI macros for defining subcomponent slots
 *  - Loading a user vs anonymous subcomponent
 *  - Declaring a subcomponent api
 *  - Defining subcomponents
 *
 *
 *  This file defines a Component with a SubComponent slot.
 *
 *
 *  The simulation works this way:
 *      - The components are connected in a ring
 *      - Each component has a "compute" SubComponent that controls what kind of computation it does
 *      - Each component sends one message around the ring which contains an integer and a string describing the computation
 *      - When a component receives a message, it has its "compute" SubComponent operate on the integer
 *          and then forwards the integer to its neighbor. It also updates the string to describe what it did.
 *      - When a component receives the message it sent, it prints the string and the result
 *      - Whan all components have received the messages they sent, the simulation ends
 */

#include <sst/core/component.h>
#include <sst/core/link.h>

// Include file for the SubComponent API we'll use
#include "Child.h"

namespace SST {
namespace cyclical {


class ParentComponent : public SST::Component
{
public:

    SST_ELI_REGISTER_COMPONENT(
        ParentComponent,        // Component class
        "cyclical",             // Component library (for Python/library lookup)
        "basicSubComponent_comp",           // Component name (for Python/library lookup)
        SST_ELI_ELEMENT_VERSION(1,0,0),     // Version of the component (not related to SST version)
        "Basic: Using subcomponents",       // Description
        COMPONENT_CATEGORY_UNCATEGORIZED    // Category
    )

    SST_ELI_DOCUMENT_PARAMS(
        { "value",      "Integer starting value for this component. Counts down throughout the simulation.", NULL }
    )

    SST_ELI_DOCUMENT_PORTS(
            {"left", "Link to left neighbor"},
            {"right", "Link to right neighbor"}
    )

    SST_ELI_DOCUMENT_STATISTICS()

    // This Macro informs SST that this Component can load a SubComponent.
    // Parameter 1: Name of the location for the subcomponent
    // Parameter 2: Description of the purpose/use/etc. of the slot
    // Parameter 3: The API the subcomponent slot will use
    SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS(
            { "left_slot",
            "The compute unit that this component will use to operate on events",
            "SST::cyclical::basicSubComponentAPI" },
            { "right_slot",
            "The compute unit that this component will use to operate on events",
            "SST::cyclical::basicSubComponentAPI" }
            )

    ParentComponent(SST::ComponentId_t id, SST::Params& params);
    ~ParentComponent();

    virtual void setup() override;

    virtual void finish() override;

    /*
        Decreases our counter field by the value of the event and passes 
        the event along to the next component. Importantly, this does not 
        call send itself. It passes that on to one of the components.
    */
    void computeAndSend(SST::Event* ev);


    ParentComponent();
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ImplementSerializable(SST::cyclical::ParentComponent)

public:
    SST::Output* out;

    int value;

    SST::cyclical::basicSubComponentAPI* leftChild;
    SST::cyclical::basicSubComponentAPI* rightChild;

};

} // namespace cyclical
} // namespace SST

#endif /* _ParentComponent_H */
