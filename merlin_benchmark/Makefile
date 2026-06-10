CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
PARAMS="-DENABLE_SSTCHECKPOINT"

SRCDIR=src
SRCS=$(SRCDIR)/endpoint_generator.cc
SST_ELEMENT_LIBDIR=/Users/brandonneth/sst_workspace/sst-elements/install/lib/sst-elements-library

all: libmerlin_benchmark.so install

libmerlin_benchmark.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install: libmerlin_benchmark.so
	cp libmerlin_benchmark.so $(SST_ELEMENT_LIBDIR)/
	sst-register merlin_benchmark merlin_benchmark_LIBDIR=$(SST_ELEMENT_LIBDIR)

clean:
	rm -rf libmerlin_benchmark.so
	rm -f $(SST_ELEMENT_LIBDIR)/libmerlin_benchmark.so
	sst-register -u merlin_benchmark
	rm -f *.json *.tmp *.time *.out *.csv
