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


using namespace SST;
using namespace SST::cyclical;

/***********************************************************************************/
// Since the classes are brief, this file has the implementation for all four
// basicSubComponentAPI subcomponents declared in basicSubComponent_subcomponent.h
/***********************************************************************************/

// basicSubComponentIncrement

basicSubComponentIncrement::basicSubComponentIncrement(ComponentId_t id, Params& params) :
    basicSubComponentAPI(id, params)
{
    amount = params.find<int>("amount",  1);
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
