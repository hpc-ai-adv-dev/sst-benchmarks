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

#ifndef COMPONENTS_MERLIN_GENERATORS_GENERATORS_H
#define COMPONENTS_MERLIN_GENERATORS_GENERATORS_H

#include <algorithm>
#include <cstdlib>
#include <vector>

#include <sst/core/rng/mersenne.h>
#include <sst/core/rng/gaussian.h>
#include <sst/core/rng/discrete.h>
#include <sst/core/rng/expon.h>
#include <sst/core/rng/uniform.h>

#include <sst/core/output.h>
#include <sst/core/serialization/serializable.h>

// Address/size/delay pattern generators used by TrafficGen (see
// trafficgen.h). Kept in their own header, as ordinary namespace-scope
// classes (rather than nested private classes of TrafficGen), so they can be
// unit tested directly (see tests/test_trafficgen_distributions.cpp).
namespace SST {
namespace MerlinBenchmark {

class Generator : public SST::Core::Serialization::serializable {
public:
    Generator() = default;
    virtual ~Generator() {}
    virtual int getNextValue(void) = 0;
    virtual void seed(uint32_t val) = 0;
    void serialize_order(SST::Core::Serialization::serializer& ser) override {}
    ImplementVirtualSerializable(SST::MerlinBenchmark::Generator)
};

class NearestNeighbor : public Generator {
    Generator *dist = nullptr;
    int *neighbors = nullptr;
    int numNeighbors = 0;
public:
    NearestNeighbor() = default;
    NearestNeighbor(Generator *dist, int id, int maxX, int maxY, int maxZ, int numNeighbors) :
        dist(dist), numNeighbors(numNeighbors)
    {
        int myX = id % maxX;
        int myY = (id / maxX) % maxY;
        int myZ = id / (maxX*maxY);

        neighbors = new int[numNeighbors];
        switch (numNeighbors) {
        case 6: {
            neighbors[0] = (((myX-1) + maxX) % maxX) + myY*maxX                         + myZ*(maxX*maxY);
            neighbors[1] = ((myX+1) % maxX)          + myY*maxX                         + myZ*(maxX*maxY);
            neighbors[2] = myX                       + (((myY-1) + maxY) % maxY) * maxX + myZ*(maxX*maxY);
            neighbors[3] = myX                       + (((myY+1)) % maxY) * maxX        + myZ*(maxX*maxY);
            neighbors[4] = myX                       + myY*maxX                         + (((myZ-1) + maxZ) % maxZ) * (maxX*maxY);
            neighbors[5] = myX                       + myY*maxX                         + (((myZ+1)) % maxZ) * (maxX*maxY);
            break;
        }
        default:
            Output::getDefaultObject().fatal(CALL_INFO, -1, "Unsure how to deal with %d neighbors\n", numNeighbors);
        }
    }

    int getNextValue(void) override
    {
        int neighbor = dist->getNextValue();
        return neighbors[neighbor];
    }

    void seed(uint32_t val) override
    {
        dist->seed(val);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(dist);
        SST_SER(numNeighbors);
        SST_SER(SST::Core::Serialization::array(neighbors, numNeighbors));
    }
    ImplementSerializable(SST::MerlinBenchmark::NearestNeighbor)
};

class ExponentialDist : public Generator {
    SST::RNG::MersenneRNG* gen = nullptr;
    SSTExponentialDistribution* dist = nullptr;

public:
    ExponentialDist() = default;
    ExponentialDist(int lambda)
    {
        gen = new SST::RNG::MersenneRNG();
        dist = new SSTExponentialDistribution((double) lambda);
    }

    ~ExponentialDist() {
        delete dist;
        delete gen;
    }

    int getNextValue(void) override
    {
        return (int) dist->getNextDouble();
    }

    void seed(uint32_t val) override
    {
        delete gen;
        gen = new SST::RNG::MersenneRNG((unsigned int) val);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(gen);
        SST_SER(dist);
    }
    ImplementSerializable(SST::MerlinBenchmark::ExponentialDist)
};


class UniformDist : public Generator {
    SST::RNG::MersenneRNG* gen = nullptr;
    SSTUniformDistribution* dist = nullptr;

    int dist_size = 0;

public:
    UniformDist() = default;
    UniformDist(int min, int max)
    {
        gen = new SST::RNG::MersenneRNG();

        dist_size = std::max(1, max-min+1);
        dist = new SSTUniformDistribution(dist_size, gen);
    }

    ~UniformDist() {
        delete dist;
        delete gen;
    }

    int getNextValue(void) override
    {
        return (int) dist->getNextDouble();
    }

    void seed(uint32_t val) override
    {
        delete dist;
        delete gen;
        gen = new SST::RNG::MersenneRNG((unsigned int) val);
        dist = new SSTUniformDistribution(dist_size,gen);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(gen);
        SST_SER(dist);
        SST_SER(dist_size);
    }
    ImplementSerializable(SST::MerlinBenchmark::UniformDist)
};


class DiscreteDist : public Generator {
    SST::RNG::MersenneRNG* gen = nullptr;
    SSTDiscreteDistribution* dist = nullptr;
    int minValue = 0;
public:
    DiscreteDist() = default;
    DiscreteDist(int min, int max, int target, double targetProb) : minValue(min)
    {
        int size = std::max(max - min, 1);
        double dfltP = (1.0 - targetProb) / (size - 1);
        std::vector<double> probs(size);
        for ( int i = 0 ; i < size ; i++ ) {
            probs[i] = dfltP;
        }
        probs[target] = targetProb;

        gen = new SST::RNG::MersenneRNG();
        dist = new SSTDiscreteDistribution(&probs[0], size, gen);
    }

    ~DiscreteDist() {
        delete dist;
        delete gen;
    }

    int getNextValue(void) override
    {
        return ((int) dist->getNextDouble()) + minValue;
    }

    void seed(uint32_t val) override
    {
        gen = new SST::RNG::MersenneRNG((unsigned int) val);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(gen);
        SST_SER(dist);
        SST_SER(minValue);
    }
    ImplementSerializable(SST::MerlinBenchmark::DiscreteDist)
};

class NormalDist : public Generator {
    SSTGaussianDistribution* dist = nullptr;
    SST::RNG::MersenneRNG* gen = nullptr;

    int minValue = 0;
    int maxValue = 0;

public:
    NormalDist() = default;
    NormalDist(int min, int max, double mean, double stddev) : minValue(min), maxValue(max)
    {
        gen = new SST::RNG::MersenneRNG();
        dist = new SSTGaussianDistribution(mean, stddev);
    }

    ~NormalDist() {
        delete dist;
        delete gen;
    }

    int getNextValue(void)  override
    {
        double val = -1.0;
        while ((int)val >= maxValue || (int)val < minValue || val < 0){
            val = dist->getNextDouble();
        }
        return (int) val;
    }

    void seed(uint32_t val) override
    {
        gen = new SST::RNG::MersenneRNG((unsigned int) val);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(gen);
        SST_SER(dist);
        SST_SER(minValue);
        SST_SER(maxValue);
    }
    ImplementSerializable(SST::MerlinBenchmark::NormalDist)
};

class BinomialDist : public Generator {
    int minValue = 0;

public:
    BinomialDist() = default;
    BinomialDist(int min, int max, int trials, float probability) : minValue(min)
    {
        //SST::Merlin::merlin_abort.fatal(CALL_INFO, -1, "BinomialDist is not currently supported\n");
    }
    virtual int getNextValue(void) override
    {
        // return dist(gen) + minValue;
        return 0;
    }
    virtual void seed(uint32_t val) override
    {
        // gen.seed(val);
    }

    void serialize_order(SST::Core::Serialization::serializer& ser) override {
        Generator::serialize_order(ser);
        SST_SER(minValue);
    }
    ImplementSerializable(SST::MerlinBenchmark::BinomialDist)
};

} // namespace MerlinBenchmark
} // namespace SST

#endif // COMPONENTS_MERLIN_GENERATORS_GENERATORS_H
