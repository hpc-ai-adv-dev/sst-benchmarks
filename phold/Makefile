CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
PARAMS=-DENABLE_SSTCHECKPOINT
#PARAMS="-DENABLE_SSTDBG"

SRCS=Node.cpp

all: libphold.so install

libphold.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	sst-register phold phold_LIBDIR=$(CURDIR)

dataclean:
	 rm -rf *_dir *.out
	 rm -rf rank_*_thread_*

clean:
	rm -rf tests/graphs libphold.so
	sst-register -u phold
	rm -r *.json *.tmp *.time *.out

