#include <sst/core/sst_config.h>
#include "Simulator.h"
#include "GlobalParams.h"
#include <string>

Simulator::Simulator(SST::ComponentId_t id, SST::Params& params)
  : SST::Component(id)
{
  timeToRun       = params.find<int64_t>("timeToRun",      100);
  gVerbose        = params.find<bool>   ("verbose",        false);
  gArtificialWork = params.find<int64_t>("artificialWork", 0);

  registerClock(std::to_string(timeToRun) + "ps", new SST::Clock::Handler2<Simulator, &Simulator::clockTick>(this));

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();

#ifdef ENABLE_SSTDBG
  dbg = new SSTDebug(getName(),"./");
#endif
}

Simulator::~Simulator() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}
#ifdef ENABLE_SSTCHECKPOINT
  Simulator::Simulator() { }
#endif

void Simulator::setup()  { }
void Simulator::finish() { }

bool Simulator::clockTick(SST::Cycle_t currentCycle) {
  primaryComponentOKToEndSim();
  return true;
}

#ifdef ENABLE_SSTDBG
void Simulator::printStatus(SST::Output& out){
  if(!dbg->dump(getCurrentSimCycle(), DARG(timeToRun))) {
    out.output("Debug dump failed!\n");
  }
}
#endif

#ifdef ENABLE_SSTCHECKPOINT
void Simulator::serialize_order(SST::Core::Serialization::serializer& ser) {
  SST::Component::serialize_order(ser);
  SST_SER(timeToRun);
  SST_SER(gVerbose);
  SST_SER(gArtificialWork);

  #ifdef ENABLE_SSTDBG
    SST_SER(dbg);
  #endif
}
#endif
