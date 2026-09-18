SST_CONFIG=$(shell which sst-config)
SST_REGISTER=$(shell which sst-register)

CXX=$(shell $(SST_CONFIG) --CXX)

CXXFLAGS=$(shell $(SST_CONFIG) --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell $(SST_CONFIG) --ELEMENT_LDFLAGS)
PARAMS="-DENABLE_SSTCHECKPOINT"

SRCDIR=src
SRCS=$(SRCDIR)/trafficgen.cc

# Install target directory for plugin .so/.dylib
# 1) explicit env override
# 2) auto-detect first -L path from sst-config --ELEMENT_LDFLAGS
# 3) repository-local fallback layout
SST_ELEMENT_LIBDIR ?= $(shell $(SST_CONFIG) --ELEMENT_LDFLAGS | tr ' ' '\n' | sed -n 's/^-L//p' | head -n1)
ifeq ($(strip $(SST_ELEMENT_LIBDIR)),)
SST_ELEMENT_LIBDIR := $(abspath ../../mysst/sst-elements/install/lib/sst-elements-library)
endif

all: check-env libmerlin_benchmark.so install

check-env:
	@if [ ! -x "$(SST_CONFIG)" ]; then \
		echo "Error: sst-config not found/executable: $(SST_CONFIG)"; \
		echo "Hint: export SST_CONFIG=/path/to/sst-config or SST_CORE_HOME=/path/to/sst-core/install"; \
		exit 1; \
	fi

print-config:
	@echo "SST_CONFIG=$(SST_CONFIG)"
	@echo "SST_REGISTER=$(SST_REGISTER)"
	@echo "SST_ELEMENT_LIBDIR=$(SST_ELEMENT_LIBDIR)"

libmerlin_benchmark.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install: libmerlin_benchmark.so
	$(SST_REGISTER) merlin_benchmark merlin_benchmark_LIBDIR=$(CURDIR)

# Statistical unit tests for the Generator subclasses in src/generators.h.
# Packaged as its own SST element/component (see tests/test_trafficgen_distributions.cpp)
# since the generators depend on SST core RNG symbols only available inside a
# running SST simulation.
libmerlin_benchmark_test.so: tests/test_trafficgen_distributions.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -I$(SRCDIR) -o $@ $^

test: libmerlin_benchmark_test.so
	$(SST_REGISTER) merlin_benchmark_test merlin_benchmark_test_LIBDIR=$(CURDIR)
	sst tests/test_trafficgen_distributions.py

clean:
	rm -rf libmerlin_benchmark.so libmerlin_benchmark_test.so
	rm -f $(SST_ELEMENT_LIBDIR)/libmerlin_benchmark.so
	@if [ -x "$(SST_REGISTER)" ]; then \
		$(SST_REGISTER) -u merlin_benchmark; \
		$(SST_REGISTER) -u merlin_benchmark_test; \
	fi
	rm -f *.json *.tmp *.time *.out *.csv
