CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)

SRCS=Node.cpp

all: libloadImbalance.so install

libloadImbalance.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

install:
	sst-register loadImbalance loadImbalance_LIBDIR=$(CURDIR)

clean:
	rm -rf libloadImbalance.so
	sst-register -u loadImbalance
	rm -r *.json *.tmp *.time *.out
