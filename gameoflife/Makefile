CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)
# PARAMS=
#PARAMS="-DENABLE_SSTDBG"
PARAMS="-DENABLE_SSTCHECKPOINT"

SRCS=cell.cpp onDemandCell.cpp

all: libgol.so install

libgol.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(PARAMS) -o $@ $^

install:
	sst-register gol gol_LIBDIR=$(CURDIR)

clean:
	rm -f libgol.so
	sst-register -u libgol
