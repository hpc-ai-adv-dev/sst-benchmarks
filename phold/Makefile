CXX=$(shell PATH=/lus/bnchlu1/rezaii/sst/14.1.0/bin:$PATH sst-config --CXX)
CXXFLAGS=$(shell PATH=/lus/bnchlu1/rezaii/sst/14.1.0/bin:$PATH sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell PATH=/lus/bnchlu1/rezaii/sst/14.1.0/bin:$PATH sst-config --ELEMENT_LDFLAGS)
PARAMS=
#PARAMS="-DENABLE_SSTDBG"

SRCS=Node.cpp

all: libphold.so install

libphold.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	PATH=/lus/bnchlu1/rezaii/sst/14.1.0/bin:$PATH sst-register phold phold_LIBDIR=$(CURDIR)

dataclean:
	 rm -rf *_dir *.out
	 rm -rf rank_*_thread_*

clean:
	rm -rf tests/graphs libphold.so
	sst-register -u phold
	rm -r *.json *.tmp *.time *.out

