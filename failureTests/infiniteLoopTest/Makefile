CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)

SRCS=Node.cpp

all: libinfiniteLoop.so install

libinfiniteLoop.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

install:
	sst-register infiniteLoop infiniteLoop_LIBDIR=$(CURDIR)

clean:
	rm -rf libinfiniteLoop.so
	sst-register -u infiniteLoop
	rm -r *.json *.tmp *.time *.out
