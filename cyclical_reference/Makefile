CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
PARAMS=-DENABLE_SSTCHECKPOINT
#PARAMS="-DENABLE_SSTDBG"

SRCS=Parent.cpp Child.cpp

all: libcyclical.so install

libcyclical.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	sst-register cyclical cyclical_LIBDIR=$(CURDIR)

dataclean:
	 rm -rf *_dir *.out
	 rm -rf rank_*_thread_*

clean:
	rm -rf tests/graphs libcyclical.so
	sst-register -u cyclical
	rm -r *.json *.tmp *.time *.out

