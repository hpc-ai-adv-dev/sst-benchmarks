import sst

# Drives the DistTest component (tests/test_trafficgen_distributions.cpp),
# which runs statistical checks on TrafficGen's private Generator subclasses
# in its constructor and exits non-zero if any check fails.
sst.Component("disttest", "merlin_benchmark_test.disttest")
