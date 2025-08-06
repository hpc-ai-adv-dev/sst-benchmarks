CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
PARAMS=
PARAMS="-DENABLE_SSTCHECKPOINT"
# PARAMS="-DENABLE_SSTDBG"
# PARAMS="-DUSE_GETLINK_API"

SRCS=Simulator.cpp Ponger.cpp GlobalParams.cpp HyperPonger.cpp

all: libpingpong.so install

libpingpong.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	sst-register pingpong pingpong_LIBDIR=$(CURDIR)

clean:
	rm -rf tests/graphs libpingpong.so
	sst-register -u pingpong
	rm *.json *.tmp *.time *.out
