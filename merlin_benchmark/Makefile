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

clean:
	rm -rf libmerlin_benchmark.so
	rm -f $(SST_ELEMENT_LIBDIR)/libmerlin_benchmark.so
	@if [ -x "$(SST_REGISTER)" ]; then \
		$(SST_REGISTER) -u merlin_benchmark; \
	fi
	rm -f *.json *.tmp *.time *.out *.csv
