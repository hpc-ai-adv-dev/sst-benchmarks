CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
PARAMS=
#PARAMS="-DENABLE_SSTCHECKPOINT"
#PARAMS="-DENABLE_SSTDBG"

SRCS=Node.cpp 

all: libdebugUseCases.so install

libdebugUseCases.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	sst-register debugUseCases debugUseCases_LIBDIR=$(CURDIR)

clean:
	rm -rf tests/graphs libdebugUseCases.so libdebugUseCases.so.dSYM
	sst-register -u debugUseCases
