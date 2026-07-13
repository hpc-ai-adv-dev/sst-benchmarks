SST_CONFIG ?= $(shell command -v sst-config 2>/dev/null)
SST_REGISTER ?= $(shell command -v sst-register 2>/dev/null)

# Optional user-provided roots (more portable than hard-coded absolute paths)
SST_CORE_HOME ?=
SST_ELEMENTS_HOME ?=

# Derive tools from explicit roots if requested.
ifeq ($(strip $(SST_CONFIG)),)
ifneq ($(strip $(SST_CORE_HOME)),)
SST_CONFIG := $(SST_CORE_HOME)/bin/sst-config
endif
endif

ifeq ($(strip $(SST_REGISTER)),)
ifneq ($(strip $(SST_CORE_HOME)),)
SST_REGISTER := $(SST_CORE_HOME)/bin/sst-register
endif
endif

# Repository-local fallback layout:
# sst-benchmarks/merlin_benchmark -> ../../sst-core/install/bin/sst-config
ifeq ($(strip $(SST_CONFIG)),)
SST_CONFIG := $(abspath ../../sst-core/install/bin/sst-config)
endif

ifeq ($(strip $(SST_REGISTER)),)
SST_REGISTER := $(abspath ../../sst-core/install/bin/sst-register)
endif

CXX=$(shell $(SST_CONFIG) --CXX)

# Needed for extending source-only SST elements components (e.g., merlin trafficgen headers).
SST_ELEMENTS_SRC ?=
ifeq ($(strip $(SST_ELEMENTS_SRC)),)
ifneq ($(strip $(SST_ELEMENTS_HOME)),)
SST_ELEMENTS_SRC := $(SST_ELEMENTS_HOME)/src
else
SST_ELEMENTS_SRC := $(abspath ../../sst-elements/src)
endif
endif

CXXFLAGS=$(shell $(SST_CONFIG) --ELEMENT_CXXFLAGS) -I$(SST_ELEMENTS_SRC) -g
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
SST_ELEMENT_LIBDIR := $(abspath ../../sst-elements/install/lib/sst-elements-library)
endif

all: check-env libmerlin_benchmark.so install

check-env:
	@if [ ! -x "$(SST_CONFIG)" ]; then \
		echo "Error: sst-config not found/executable: $(SST_CONFIG)"; \
		echo "Hint: export SST_CONFIG=/path/to/sst-config or SST_CORE_HOME=/path/to/sst-core/install"; \
		exit 1; \
	fi
	@if [ ! -d "$(SST_ELEMENTS_SRC)" ]; then \
		echo "Error: SST elements source dir not found: $(SST_ELEMENTS_SRC)"; \
		echo "Hint: export SST_ELEMENTS_SRC=/path/to/sst-elements/src or SST_ELEMENTS_HOME=/path/to/sst-elements"; \
		exit 1; \
	fi

print-config:
	@echo "SST_CONFIG=$(SST_CONFIG)"
	@echo "SST_REGISTER=$(SST_REGISTER)"
	@echo "SST_ELEMENTS_SRC=$(SST_ELEMENTS_SRC)"
	@echo "SST_ELEMENT_LIBDIR=$(SST_ELEMENT_LIBDIR)"

libmerlin_benchmark.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install: libmerlin_benchmark.so
	cp libmerlin_benchmark.so $(SST_ELEMENT_LIBDIR)/
	@if [ -x "$(SST_REGISTER)" ]; then \
		$(SST_REGISTER) merlin_benchmark merlin_benchmark_LIBDIR=$(SST_ELEMENT_LIBDIR); \
	else \
		echo "Skipping registration: sst-register not found"; \
	fi

clean:
	rm -rf libmerlin_benchmark.so
	rm -f $(SST_ELEMENT_LIBDIR)/libmerlin_benchmark.so
	@if [ -x "$(SST_REGISTER)" ]; then \
		$(SST_REGISTER) -u merlin_benchmark; \
	fi
	rm -f *.json *.tmp *.time *.out *.csv
