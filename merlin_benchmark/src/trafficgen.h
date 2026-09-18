// -*- mode: c++ -*-

// Copyright 2009-2026 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2026, NTESS
// All rights reserved.
//
// Portions are copyright of other developers:
// See the file CONTRIBUTORS.TXT in the top level directory
// of the distribution for more information.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.


#ifndef COMPONENTS_MERLIN_GENERATORS_TRAFFICEGEN_H
#define COMPONENTS_MERLIN_GENERATORS_TRAFFICEGEN_H

#include <cstdlib>

#include <sst/core/rng/mersenne.h>
#include <sst/core/rng/gaussian.h>
#include <sst/core/rng/discrete.h>
#include <sst/core/rng/expon.h>
#include <sst/core/rng/uniform.h>

#include <sst/core/component.h>
#include <sst/core/event.h>
#include <sst/core/link.h>
#include <sst/core/timeConverter.h>
#include <sst/core/output.h>
#include <sst/core/interfaces/simpleNetwork.h>

#include <sst/core/serialization/serializable.h>

#include "generators.h"


#define ENABLE_FINISH_HACK 0

namespace SST {
namespace MerlinBenchmark {

class TrafficGen : public Component {

public:

    SST_ELI_REGISTER_COMPONENT(
        TrafficGen,
        "merlin_benchmark",
        "trafficgen",
        SST_ELI_ELEMENT_VERSION(1,0,0),
        "Forked Merlin traffic generator for benchmark experimentation.",
        COMPONENT_CATEGORY_NETWORK)

    SST_ELI_DOCUMENT_PARAMS(
        {"verbose",                               "Verbose logging level for out.verbose calls (0 disables current level-5 messages).","0"},
        {"id",                                    "Network ID of endpoint."},
        {"num_peers",                             "Total number of endpoints in network."},
        {"num_vns",                               "Number of requested virtual networks."},
        {"link_bw",                               "Bandwidth of the router link specified in either b/s or B/s (can include SI prefix)."},
        {"topology",                              "Name of the topology subcomponent that should be loaded to control routing."},
        {"buffer_length",                         "Length of input and output buffers.","1kB"},
        {"packets_to_send",                       "Number of packets to send in the test.","1000"},
        {"packet_size",                           "Packet size specified in either b or B (can include SI prefix).","5"},
        {"delay_between_packets",                 "","0"},
        {"message_rate",                          "","1GHz"},
        {"PacketDest.pattern",                    "Address pattern to be used (NearestNeighbor, Uniform, HotSpot, Normal, Binomial)",NULL},
        {"PacketDest.Seed",                       "Sets the seed of the RNG", "11" },
        {"PacketDest.RangeMax",                   "Minumum address to send packets.","0"},
        {"PacketDest.RangeMin",                   "Maximum address to send packets.","INT_MAX"},
        {"PacketDest.NearestNeighbor.Size",       "For Nearest Neighbors, the 3D size \"x y z\" of the mesh", ""},
        {"PacketDest.HotSpot.target",             "For HotSpot, which node is the target", ""},
        {"PacketDest.HotSpot.targetProbability",  "For HotSpot, with what probability is the target targeted", ""},
        {"PacketDest.Normal.Mean",                "In a normal distribution, the mean", ""},
        {"PacketDest.Normal.Sigma",               "In a normal distribution, the mean variance", ""},
        {"PacketDest.Binomial.Mean",              "In a binomial distribution, the mean", ""},
        {"PacketDest.Binomial.Sigma",             "In a binomial distribution, the variance", ""},
        {"PacketSize.pattern",                    "Address pattern to be used (Uniform, HotSpot, Normal, Binomial)",NULL},
        {"PacketSize.Seed",                       "Sets the seed of the RNG", "11" },
        {"PacketSize.RangeMax",                   "Minumum size of packets.","0"},
        {"PacketSize.RangeMin",                   "Maximum size of packets.","INT_MAX"},
        {"PacketSize.HotSpot.target",             "For HotSpot, the target packet size", ""},
        {"PacketSize.HotSpot.targetProbability",  "For HotSpot, with what probability is the target targeted", ""},
        {"PacketSize.Normal.Mean",                "In a normal distribution, the mean", ""},
        {"PacketSize.Normal.Sigma",               "In a normal distribution, the mean variance", "1.0"},
        {"PacketSize.Binomial.Mean",              "In a binomial distribution, the mean", ""},
        {"PacketSize.Binomial.Sigma",             "In a binomial distribution, the variance", "0.5"},
        {"PacketDelay.pattern",                   "Address pattern to be used (Uniform, HotSpot, Normal, Binomial)",NULL},
        {"PacketDelay.Seed",                      "Sets the seed of the RNG", "11" },
        {"PacketDelay.RangeMax",                  "Minumum delay between packets.","0"},
        {"PacketDelay.RangeMin",                  "Maximum delay between packets.","INT_MAX"},
        {"PacketDelay.HotSpot.target",            "For HotSpot, the target packet delay", ""},
        {"PacketDelay.HotSpot.targetProbability", "For HotSpot, with what probability is the target targeted", ""},
        {"PacketDelay.Normal.Mean",               "In a normal distribution, the mean", ""},
        {"PacketDelay.Normal.Sigma",              "In a normal distribution, the mean variance", "1.0"},
        {"PacketDelay.Binomial.Mean",             "In a binomial distribution, the mean", ""},
        {"PacketDelay.Binomial.Sigma",            "In a binomial distribution, the variance", "0.5"}
    )

    SST_ELI_DOCUMENT_PORTS(
        {"rtr",  "Port that hooks up to router.", { "merlin.RtrEvent", "merlin.credit_event" } }
    )


    SST_ELI_DOCUMENT_SUBCOMPONENT_SLOTS(
        {"networkIF", "Network interface", "SST::Interfaces::SimpleNetwork" }
    )

    SST_ELI_IS_CHECKPOINTABLE()


private:

#if ENABLE_FINISH_HACK
    static int count;
    static int received;
    static int min_lat;
    static int max_lat;
    static int mean_sum;
#endif

    enum AddressMode { SEQUENTIAL, FATTREE_IP };

    AddressMode addressMode = SEQUENTIAL;

    int id = 0;
    int ft_loading = 0;
    int ft_radix = 0;
    int num_peers = 0;
    int num_vns = 0;
//    int last_vc;

    uint64_t packets_sent = 0;
    uint64_t packets_recd = 0;

    bool done = false;

    SST::Interfaces::SimpleNetwork* link_control = nullptr;
    SST::Interfaces::SimpleNetwork::HandlerBase* send_notify_functor = nullptr;
    Clock::HandlerBase* clock_functor = nullptr;
    TimeConverter clock_tc;

    int base_packet_size = 0;
    uint64_t packets_to_send = 0;

    int base_packet_delay = 0;
    int packet_delay = 0;

    Generator *packetDestGen = nullptr;
    Generator *packetSizeGen = nullptr;
    Generator *packetDelayGen = nullptr;

public:
    TrafficGen(ComponentId_t cid, Params& params);
    TrafficGen() = default;
    ~TrafficGen();

    void serialize_order(SST::Core::Serialization::serializer& ser) override;
    ImplementSerializable(SST::MerlinBenchmark::TrafficGen)

    void init(unsigned int phase) override;
    void setup() override;
    void finish() override;


private:
    static Output out;
    static bool   out_initialized;

    Generator* buildGenerator(const std::string &prefix, Params& params);
    bool clock_handler(Cycle_t cycle);
    int fattree_ID_to_IP(int id);
    int IP_to_fattree_ID(int id);
    bool handle_receives(int vn);
    bool send_notify(int vn);

protected:
    int getPacketDest(void);
    int getPacketSize(void);
    int getDelayNextPacket(void);

};

} //namespace MerlinBenchmark
} //namespace SST

#endif
