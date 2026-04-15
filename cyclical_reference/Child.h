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

#ifndef _BASIC_SUBCOMPONENT_SUBCOMPONENT_H
#define _BASIC_SUBCOMPONENT_SUBCOMPONENT_H

/*
 * This is an example of a simple subcomponent that can take a number and do a computation on it.
 * This file happens to have multiple classes declaring both the SubComponentAPI
 * as well as a few subcomponents that implement the API.
 *
 *  Classes:
 *      basicSubComponentAPI - inherits from SST::SubComponent. Defines the API for the compute units.
 *      basicSubComponentIncrement - inherits from basicSubComponentAPI. A compute unit that increments the input.
 *      basicSubComponentDecrement - inherits from basicSubComponentAPI. A compute unit that decrements the input.
 *      basicSubComponentMultiply - inherits from basicSubComponentAPI. A compute unit that multiplies the input.
 *      basicSubComponentDivide - inherits from basicSubComponentAPI. A compute unit that divides the input.
 *
 * See 'basicSubComponent_component.h' for more information on how the example simulation works
 */

#include <sst/core/subcomponent.h>
#include <sst/core/sst_config.h>

namespace SST {
namespace cyclical {

/*****************************************************************************************************/

class basicSubComponent_Component;


class basicSubComponentAPI : public SST::SubComponent
{
public:
    /*
     * Register this API with SST so that SST can match subcomponent slots to subcomponents
     */
    SST_ELI_REGISTER_SUBCOMPONENT_API(SST::cyclical::basicSubComponentAPI, basicSubComponent_Component*, std::string)

    basicSubComponentAPI(ComponentId_t id, Params& params, basicSubComponent_Component* parent, std::string link_name) : SubComponent(id) { }
    virtual ~basicSubComponentAPI() { }

    // These are the two functions described in the comment above
    virtual int compute( int num ) =0;
    virtual std::string compute( std::string comp) =0;

    // Serialization
    basicSubComponentAPI() {};
    ImplementVirtualSerializable(SST::cyclical::basicSubComponentAPI);
};

/*****************************************************************************************************/

/* SubComponent that does an 'increment' computation */
class basicSubComponentIncrement : public basicSubComponentAPI {
public:

    // Register this subcomponent with SST and tell SST that it implements the 'basicSubComponentAPI' API
    SST_ELI_REGISTER_SUBCOMPONENT(
            basicSubComponentIncrement,     // Class name
            "cyclical",         // Library name, the 'lib' in SST's lib.name format
            "basicSubComponentIncrement",   // Name used to refer to this subcomponent, the 'name' in SST's lib.name format
            SST_ELI_ELEMENT_VERSION(1,0,0), // A version number
            "SubComponent that increments a value", // Description
            SST::cyclical::basicSubComponentAPI // Fully qualified name of the API this subcomponent implements
                                                            // A subcomponent can implment an API from any library
            )

    // Other ELI macros as needed for parameters, ports, statistics, and subcomponent slots
    SST_ELI_DOCUMENT_PARAMS( { "amount", "Amount to increment by", "1" } )

    basicSubComponentIncrement(ComponentId_t id, Params& params, basicSubComponent_Component* parent, std::string link_name);
    ~basicSubComponentIncrement();

    int compute( int num) override;
    std::string compute( std::string comp ) override;

    // serialization
    basicSubComponentIncrement() : basicSubComponentAPI() {};
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ImplementSerializable(SST::cyclical::basicSubComponentIncrement);

private:
    int amount;
    basicSubComponent_Component * parent;
    std::string link_name;
    Link * link;
};


/*****************************************************************************************************/

} } /* Namspaces */

#endif /* _BASIC_SUBCOMPONENT_SUBCOMPONENT_H */
