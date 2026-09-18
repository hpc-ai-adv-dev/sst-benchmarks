# Makefile for endpoint_generator component
# Part of merlin-benchmark suite

# Find SST installation
SST_CONFIG ?= sst-config
SST_ELEMENT_CXXFLAGS = $(shell $(SST_CONFIG) SSTCore ELEMENT_CXXFLAGS 2>/dev/null)
SST_ELEMENT_LDFLAGS = $(shell $(SST_CONFIG) SSTCore ELEMENT_LDFLAGS 2>/dev/null)
SST_LIBS = $(shell $(SST_CONFIG) SSTCore LIBS 2>/dev/null)

# Compiler and flags
CXX ?= g++
CXXFLAGS = -Wall -Wextra -O2 $(SST_ELEMENT_CXXFLAGS)
LDFLAGS = $(SST_ELEMENT_LDFLAGS) $(SST_LIBS)

# Include directory (included in SST_ELEMENT_CXXFLAGS)
INCLUDE = -I.

# Source and object files
SOURCES = endpoint_generator.cc
HEADERS = endpoint_generator.h
OBJECTS = $(SOURCES:.cc=.o)
TARGET = ../lib/libendpoint_generator.so

# Default target
all: $(TARGET)

# Build library
$(TARGET): $(OBJECTS)
	@mkdir -p ../lib
	$(CXX) $(LDFLAGS) -o $@ $(OBJECTS) $(SST_LDFLAGS)
	@echo "Built $@"

# Compile source files
%.o: %.cc $(HEADERS)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)
	@echo "Cleaned"

# Phony targets
.PHONY: all clean

