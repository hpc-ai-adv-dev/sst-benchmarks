#ifndef _BASIC_SUBCOMPONENT_SUBCOMPONENT_H
#define _BASIC_SUBCOMPONENT_SUBCOMPONENT_H

#include <sst/core/subcomponent.h>
#include <sst/core/sst_config.h>

namespace SST {
namespace cyclical {

class ParentComponent;


class basicSubComponentAPI : public SST::SubComponent
{
public:
    /*
     * Register this API with SST so that SST can match subcomponent slots to subcomponents
     */
    SST_ELI_REGISTER_SUBCOMPONENT_API(SST::cyclical::basicSubComponentAPI, ParentComponent*, std::string)

    basicSubComponentAPI(ComponentId_t id, Params& params, ParentComponent* parent, std::string link_name) : SubComponent(id) { }
    virtual ~basicSubComponentAPI() { }

    virtual void handleEvent(SST::Event* ev) =0;
    virtual void sendEvent(SST::Event* ev) =0;
    virtual void finish() =0;

    // Serialization
    basicSubComponentAPI() {};
    ImplementVirtualSerializable(SST::cyclical::basicSubComponentAPI);
};

class basicSubComponent : public basicSubComponentAPI {
public:

    // Register this subcomponent with SST and tell SST that it implements the 'basicSubComponentAPI' API
    SST_ELI_REGISTER_SUBCOMPONENT(
            basicSubComponent,     // Class name
            "cyclical",         // Library name, the 'lib' in SST's lib.name format
            "basicSubComponent",   // Name used to refer to this subcomponent, the 'name' in SST's lib.name format
            SST_ELI_ELEMENT_VERSION(1,0,0), // A version number
            "SubComponent that increments a value", // Description
            SST::cyclical::basicSubComponentAPI // Fully qualified name of the API this subcomponent implements
            )

    // Other ELI macros as needed for parameters, ports, statistics, and subcomponent slots
    SST_ELI_DOCUMENT_PARAMS( { "amount", "Amount to increment by", "1" } )

    basicSubComponent(ComponentId_t id, Params& params, ParentComponent* parent, std::string link_name);
    ~basicSubComponent();

    void handleEvent(SST::Event* ev) override;
    void sendEvent(SST::Event* ev) override;
    virtual void finish() override;

    // serialization
    basicSubComponent() : basicSubComponentAPI(), amount(0), parent(nullptr), link_name(""), link(nullptr) {};
    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ImplementSerializable(SST::cyclical::basicSubComponent);

private:
    int amount;
    ParentComponent * parent;
    std::string link_name;
    Link * link;

};

} } /* Namspaces */

#endif /* _BASIC_SUBCOMPONENT_SUBCOMPONENT_H */
