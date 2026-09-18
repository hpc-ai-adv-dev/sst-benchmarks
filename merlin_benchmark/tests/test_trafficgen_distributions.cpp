// Statistical unit tests for the address/size/delay pattern generators used
// by TrafficGen (src/generators.h): UniformDist, NormalDist, DiscreteDist,
// ExponentialDist, and NearestNeighbor.
//
// These classes rely on symbols (e.g. SST::RNG::MersenneRNG, serialization/ELI
// registration) that only exist inside a running SST simulation binary
// (sstsim.x) -- there is no standalone linkable SST core library. So this
// test is packaged as its own tiny SST component
// ("merlin_benchmark_test.disttest") that runs all checks in its constructor
// and exits the process with a non-zero code if any check fails. See
// tests/README.md for build/run instructions.
//
// Since the outputs are randomized, these are statistical tests: each check
// uses a fixed seed for reproducibility and a tolerance wide enough to make
// spurious failures astronomically unlikely, but a false failure is still
// possible in principle.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <set>
#include <string>
#include <vector>

#include <sst/core/component.h>
#include <sst/core/sst_types.h>
#include <sst/core/params.h>
#include <sst/core/eli/elementinfo.h>

#include "generators.h"

namespace SST {
namespace MerlinBenchmark {

// Thin wrappers that construct each generator, seed it, and collect samples
// into a plain vector for statistical analysis below.
struct Sampler {

    static std::vector<int> sampleUniform(int min, int max, uint32_t seed, size_t n)
    {
        UniformDist gen(min, max);
        gen.seed(seed);
        std::vector<int> out;
        out.reserve(n);
        for ( size_t i = 0; i < n; i++ ) out.push_back(gen.getNextValue());
        return out;
    }

    static std::vector<int> sampleNormal(int min, int max, double mean, double stddev, uint32_t seed, size_t n)
    {
        NormalDist gen(min, max, mean, stddev);
        gen.seed(seed);
        std::vector<int> out;
        out.reserve(n);
        for ( size_t i = 0; i < n; i++ ) out.push_back(gen.getNextValue());
        return out;
    }

    static std::vector<int> sampleExponential(int lambda, uint32_t seed, size_t n)
    {
        ExponentialDist gen(lambda);
        gen.seed(seed);
        std::vector<int> out;
        out.reserve(n);
        for ( size_t i = 0; i < n; i++ ) out.push_back(gen.getNextValue());
        return out;
    }

    static std::vector<int> sampleDiscrete(int min, int max, int target, double targetProb, uint32_t seed, size_t n)
    {
        DiscreteDist gen(min, max, target, targetProb);
        gen.seed(seed);
        std::vector<int> out;
        out.reserve(n);
        for ( size_t i = 0; i < n; i++ ) out.push_back(gen.getNextValue());
        return out;
    }

    static std::vector<int> sampleNearestNeighbor(
        int id, int maxX, int maxY, int maxZ, int numNeighbors, uint32_t seed, size_t n)
    {
        // NearestNeighbor picks a neighbor slot uniformly and maps it to a
        // node id; give it a uniform index generator over [0, numNeighbors).
        auto*        dist = new UniformDist(0, numNeighbors - 1);
        NearestNeighbor gen(dist, id, maxX, maxY, maxZ, numNeighbors);
        gen.seed(seed);
        std::vector<int> out;
        out.reserve(n);
        for ( size_t i = 0; i < n; i++ ) out.push_back(gen.getNextValue());
        return out;
    }

    // Exposes the raw neighbor-id list for the given mesh coordinates so the
    // test can check that NearestNeighbor's output set is exactly correct.
    static std::vector<int> expectedNeighbors(int id, int maxX, int maxY, int maxZ, int numNeighbors)
    {
        int myX = id % maxX;
        int myY = (id / maxX) % maxY;
        int myZ = id / (maxX * maxY);

        std::vector<int> neighbors(numNeighbors);
        neighbors[0] = (((myX - 1) + maxX) % maxX) + myY * maxX + myZ * (maxX * maxY);
        neighbors[1] = ((myX + 1) % maxX) + myY * maxX + myZ * (maxX * maxY);
        neighbors[2] = myX + (((myY - 1) + maxY) % maxY) * maxX + myZ * (maxX * maxY);
        neighbors[3] = myX + (((myY + 1)) % maxY) * maxX + myZ * (maxX * maxY);
        neighbors[4] = myX + myY * maxX + (((myZ - 1) + maxZ) % maxZ) * (maxX * maxY);
        neighbors[5] = myX + myY * maxX + (((myZ + 1)) % maxZ) * (maxX * maxY);
        return neighbors;
    }
};

} // namespace MerlinBenchmark
} // namespace SST

using SST::MerlinBenchmark::Sampler;

namespace {

int  g_checks = 0;
int  g_failures = 0;

void expectTrue(bool cond, const std::string& msg)
{
    g_checks++;
    if ( !cond ) {
        g_failures++;
        printf("[FAIL] %s\n", msg.c_str());
    }
    else {
        printf("[ OK ] %s\n", msg.c_str());
    }
}

void expectNear(double actual, double expected, double tolerance, const std::string& msg)
{
    expectTrue(
        std::fabs(actual - expected) <= tolerance,
        msg + " (actual=" + std::to_string(actual) + ", expected=" + std::to_string(expected) +
            ", tol=" + std::to_string(tolerance) + ")");
}

double mean(const std::vector<int>& v)
{
    double sum = 0;
    for ( int x : v ) sum += x;
    return sum / v.size();
}

double stddev(const std::vector<int>& v, double m)
{
    double sq = 0;
    for ( int x : v ) sq += (x - m) * (x - m);
    return std::sqrt(sq / v.size());
}

// ---------------------------------------------------------------------
// UniformDist: verify all samples fall in the produced range and that
// each bin is hit with roughly equal frequency.
// ---------------------------------------------------------------------
void testUniformDist()
{
    printf("\n== UniformDist ==\n");
    const int    min = 0, max = 9; // dist_size = max-min+1 = 10 bins: [0..9]
    const size_t n   = 200000;

    auto samples = Sampler::sampleUniform(min, max, /*seed=*/12345, n);

    bool inRange = std::all_of(samples.begin(), samples.end(), [&](int v) { return v >= 0 && v <= (max - min); });
    expectTrue(inRange, "UniformDist: all samples within [0, max-min]");

    std::vector<size_t> counts(max - min + 1, 0);
    for ( int v : samples ) counts[v]++;

    double expectedFrac = 1.0 / counts.size();
    for ( size_t i = 0; i < counts.size(); i++ ) {
        double frac = (double)counts[i] / n;
        expectNear(frac, expectedFrac, 0.01, "UniformDist: bin " + std::to_string(i) + " frequency near uniform");
    }
}

// ---------------------------------------------------------------------
// NormalDist: verify sample mean/stddev converge near the requested
// parameters, and that the rejection-sampling bounds are respected.
// ---------------------------------------------------------------------
void testNormalDist()
{
    printf("\n== NormalDist ==\n");
    const int    min = 0, max = 200;
    const double reqMean = 100.0, reqStddev = 15.0;
    const size_t n        = 200000;

    auto samples = Sampler::sampleNormal(min, max, reqMean, reqStddev, /*seed=*/42, n);

    bool inRange = std::all_of(samples.begin(), samples.end(), [&](int v) { return v >= min && v < max; });
    expectTrue(inRange, "NormalDist: all samples within [min, max)");

    double m = mean(samples);
    double s = stddev(samples, m);
    // getNextValue() truncates the double sample via (int), which biases the
    // mean down by ~0.5 on average; account for that instead of comparing
    // directly to the requested mean.
    expectNear(m, reqMean - 0.5, 1.0, "NormalDist: sample mean close to requested mean (minus truncation bias)");
    expectNear(s, reqStddev, 1.0, "NormalDist: sample stddev close to requested stddev");
}

// ---------------------------------------------------------------------
// ExponentialDist: verify sample mean is close to the theoretical mean
// (1/lambda) of the underlying continuous exponential distribution.
// ---------------------------------------------------------------------
void testExponentialDist()
{
    printf("\n== ExponentialDist ==\n");
    // ExponentialDist's constructor takes an int lambda (production code
    // passes it a float that gets silently truncated -- e.g. any lambda < 1
    // becomes 0, which SSTExponentialDistribution can't handle). Use lambda=1,
    // the smallest value that avoids that truncation-to-zero pitfall.
    const int    lambda = 1;
    const size_t n      = 300000;

    auto samples = Sampler::sampleExponential(lambda, /*seed=*/99, n);

    bool nonNegative = std::all_of(samples.begin(), samples.end(), [](int v) { return v >= 0; });
    expectTrue(nonNegative, "ExponentialDist: all samples non-negative");

    // getNextValue() truncates the continuous Exp(lambda) draw via (int).
    // E[floor(X)] for X ~ Exp(lambda) has closed form 1/(e^lambda - 1).
    double theoreticalMean = 1.0 / (std::exp((double)lambda) - 1.0);
    double m               = mean(samples);
    expectNear(m, theoreticalMean, 0.02, "ExponentialDist: sample mean close to E[floor(X)] for X~Exp(lambda)");
}

// ---------------------------------------------------------------------
// DiscreteDist: verify the target bin is hit with ~targetProb frequency and
// the remaining probability mass is split evenly over the rest. Counts are
// tallied with a map (not a fixed-size vector indexed by v-min) because
// SSTDiscreteDistribution's cumulative-probability lookup can return a value
// one past the intended [min, max) span.
// ---------------------------------------------------------------------
void testDiscreteDist()
{
    printf("\n== DiscreteDist ==\n");
    const int    min = 0, max = 9;
    const int    target     = 3;
    const double targetProb = 0.5;
    const size_t n          = 200000;

    auto samples = Sampler::sampleDiscrete(min, max, target, targetProb, /*seed=*/7, n);

    bool inRange = std::all_of(samples.begin(), samples.end(), [&](int v) { return v >= min && v < max; });
    expectTrue(inRange, "DiscreteDist: all samples within [min, max)");

    std::map<int, size_t> counts;
    for ( int v : samples ) counts[v]++;

    double targetFrac = (double)counts[target] / n;
    expectNear(targetFrac, targetProb, 0.01, "DiscreteDist: target bin frequency close to targetProb");

    size_t numBins      = max - min;
    double dfltExpected = (1.0 - targetProb) / (numBins - 1);
    for ( int v = min; v < max; v++ ) {
        if ( v == target ) continue;
        double frac = (double)counts[v] / n;
        expectNear(frac, dfltExpected, 0.01, "DiscreteDist: non-target bin " + std::to_string(v) + " frequency close to default prob");
    }
}

// ---------------------------------------------------------------------
// NearestNeighbor: verify only the 6 expected torus neighbors are ever
// produced, and that each is chosen with roughly equal frequency.
// ---------------------------------------------------------------------
void testNearestNeighbor()
{
    printf("\n== NearestNeighbor ==\n");
    const int    maxX = 4, maxY = 4, maxZ = 4;
    const int    id            = 5; // arbitrary interior node
    const int    numNeighbors  = 6;
    const size_t n             = 200000;

    auto expected = Sampler::expectedNeighbors(id, maxX, maxY, maxZ, numNeighbors);
    auto samples  = Sampler::sampleNearestNeighbor(id, maxX, maxY, maxZ, numNeighbors, /*seed=*/2024, n);

    std::set<int> expectedSet(expected.begin(), expected.end());
    bool          onlyExpected =
        std::all_of(samples.begin(), samples.end(), [&](int v) { return expectedSet.count(v) > 0; });
    expectTrue(onlyExpected, "NearestNeighbor: every sample is one of the 6 torus neighbors");

    std::vector<size_t> counts(numNeighbors, 0);
    for ( int v : samples ) {
        for ( int i = 0; i < numNeighbors; i++ ) {
            if ( expected[i] == v ) counts[i]++;
        }
    }
    double expectedFrac = 1.0 / numNeighbors;
    for ( int i = 0; i < numNeighbors; i++ ) {
        double frac = (double)counts[i] / n;
        expectNear(frac, expectedFrac, 0.01, "NearestNeighbor: neighbor slot " + std::to_string(i) + " frequency near uniform");
    }
}

} // namespace

namespace SST {
namespace MerlinBenchmark {

// Minimal SST component that runs the statistical checks above once, at
// construction time, and reports pass/fail. No ports or links are used.
class DistTest : public Component {
public:
    SST_ELI_REGISTER_COMPONENT(
        DistTest,
        "merlin_benchmark_test",
        "disttest",
        SST_ELI_ELEMENT_VERSION(1, 0, 0),
        "Statistical verification of TrafficGen's Generator subclasses (see src/generators.h).",
        COMPONENT_CATEGORY_UNCATEGORIZED)

    SST_ELI_DOCUMENT_PARAMS()

    DistTest(ComponentId_t id, Params& params) : Component(id)
    {
        (void)params;

        testUniformDist();
        testNormalDist();
        testExponentialDist();
        testDiscreteDist();
        testNearestNeighbor();

        printf("\n%d/%d checks passed\n", g_checks - g_failures, g_checks);

        if ( g_failures != 0 ) {
            fflush(stdout);
            std::exit(1);
        }
    }
};

} // namespace MerlinBenchmark
} // namespace SST
