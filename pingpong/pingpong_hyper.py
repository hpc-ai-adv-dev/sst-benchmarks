# This version of ping pong is meant to be run using sst with
# --parallel-load=SINGLE.  For --random and --randomOverlap ball placement we
# put a (roughly) even number of randomly place balls in each rank. Excess
# balls are placed on the final rank.

import sst
import time, argparse, random

startTime = time.time()

parser = argparse.ArgumentParser(
  prog='SSTPingPong',
  description='Run a simulation consisting of several components arranged in a 1D or 2D grid that send messages back and forth')
parser.add_argument('--N',              type=int, default=2)
parser.add_argument('--timeToRun',      type=int, default=200)
parser.add_argument('--edgeDelay',      type=int, default=50)
parser.add_argument('--artificialWork', type=int, default=0)
parser.add_argument('--verbose',        default=False, action='store_true')
parser.add_argument('--dryRun',         type=int, default=-1)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--corners',         default=False, action='store_true')
group.add_argument('--random',          type=int, default=-1)
group.add_argument('--randomOverlap',   type=int, default=-1)
group.add_argument('--chanceHasBall',   type=float, default=-1)
group.add_argument('--wavefront',       default=False, action='store_true')
args = parser.parse_args()

# -----------------------------------------------------------------------------

N = args.N
nGrids = (N*N) * 100
nHlPerPt = 100

if args.dryRun == -1:
  myRank   = sst.getMyMPIRank()
  numRanks = sst.getMPIRankCount()
else:
  myRank   = 0
  numRanks = args.dryRun

# -----------------------------------------------------------------------------

pongers = {}
numGhostPongers = 0
numNumGhostComponents = 0

def oppositeDir(direction):
  opposites = {'north': 'south', 'south': 'north', 'west' : 'east', 'east' : 'west'}
  return opposites[direction]

def pongerId(g,i,j):
  return g * (N*N) + i * N + j;

def pongerLoc(someId):
  gridNum = int(someId / (N*N))
  xyId = int(someId % (N*N));
  i = int(xyId / N)
  j = int(xyId % N)
  return (gridNum,i,j)

def ponger(g,i,j):
  global pongers, numGhostPongers, numNumGhostComponents 

  me = pongerId(g,i,j)
  if me in pongers:
    return pongers[me]

  ponger = None
  if args.dryRun == -1:
    ponger = sst.Component("p%i" % (me), "pingpong.hyperPonger")
  else:
    ponger = 1 # dummy value
  pongerRank = int(g / gridsPerRank)
  if args.dryRun == -1:
    ponger.setRank(pongerRank)
    if pongerRank == myRank:
      if args.chanceHasBall == -1:
        ponger.addParams({"numBalls": 0})
      else:
        rval = random.randint(0,100)
        ponger.addParams({"numBalls": 1 if rval <= args.chanceHasBall else 0})
  pongers[me] = ponger;

  isGhostPonger = int(g/gridsPerRank) != myRank
  if isGhostPonger:
    numGhostPongers += 1
  else:
    numNumGhostComponents += 1

  if args.verbose:
    print(f"Make ponger ({g},{i},{j}) on {int(g / gridsPerRank)} {'*' if isGhostPonger else ' '}")
  return ponger

def hyperLink(g1,i1,j1, g2,i2,j2, port1Name, port2Name, isPass2=False):
  id1 = pongerId(g1,i1,j1)
  id2 = pongerId(g2,i2,j2)
  minId = min(id1,id2)
  maxId = max(id1,id2)

  ponger1 = ponger(g1,i1,j1)
  ponger2 = ponger(g2,i2,j2)

  if args.verbose:
    print("Connect %d (%d,%d,%d) %s -- %d (%d,%d,%d) %s" % (id1,g1,i1,j1,port1Name, id2,g2,i2,j2,port2Name))

  linkName = "l%s%d_%d" % ('' if not isPass2 else 'b', minId, maxId)
  if args.dryRun == -1:
    sst.Link(linkName).connect( (ponger1, port1Name, "%ips" % args.edgeDelay), (ponger2, port2Name, "%ips" % args.edgeDelay) )

def prevDivisor(x, y):
  while True:
    if x % y == 0:
      return y
    y -= 1

def nextDivisor(x, y):
  while True:
    if x % y == 0:
      return y
    y += 1

# -----------------------------------------------------------------------------

gridsPerRank = int(nGrids / numRanks)

if nGrids % numRanks != 0:
  print("nGrids (%d) not divisible by numRanks (%d) how about run with %d or %d?" %
        (nGrids, numRanks, prevDivisor(nGrids, numRanks), nextDivisor(nGrids, numRanks)))
  exit(1)

if myRank == 0:
  print("Simulating %d, %dx%d grids" % (nGrids, N, N))
  simulation = sst.Component("sim", "pingpong.simulator")
  simulation.addParams({"timeToRun"      : args.timeToRun,
                     "verbose"        : args.verbose,
                     "artificialWork" : args.artificialWork})
  simulation.setRank(0)

# Consider if we have 400 2x2 grids, we assign inter-grid connections as
# follows, where each * is a point in the 2x2 grid.  The number above each
# point we call the pass 1 links and the numbers bove and below we call pass 2.
#
#           GRID 0                   GRID 1
#   .--------------------,   .---------------------,
#   |                    |   |                     |
#   |   0-99     100-199 |   |  1-100     101-200  |
#   |    *          *    |   |    *          *     |
#   | 399-300    299-200 |   | 398-299    298-199  |
#   |                    |   |                     |   . . .
#   |                    |   |                     |
#   | 200-299    300-399 |   | 201-300   301-399,0 |
#   |    *          *    |   |    *          *     |
#   | 199-100     99-0   |   | 198-99    98-0,399  |
#   |                    |   |                     |
#   `--------------------'   `---------------------'

passVerbosity = 0  # Set to 1 to see debug output for pass 1 links, and 2 to see debug output for pass 2 links 

firstGridOnRank = myRank * gridsPerRank
for g in range(firstGridOnRank, (myRank+1) * gridsPerRank):
  pass1NextGrid = (nGrids - g) % nGrids
  pass2NextGrid = nGrids - g - 1

  if passVerbosity > 0:
    print("\n")
    print("GRID ", g)

  for i in range(0,N):
    for j in range(0,N):
      if args.verbose:
        print("\n *", end="")

      ponger(g,i,j)

      if i+1 < N:
        hyperLink(g,i,j, g,i+1,j, "port_s", "port_n")
      if j+1 < N:
        hyperLink(g,i,j, g,i,j+1, "port_e", "port_w")

      for x in range(0,nHlPerPt):
        if pass1NextGrid > g or pass1NextGrid < firstGridOnRank:
          hyperLink(g,i,j, pass1NextGrid,i,j, "port_%d" % (x), "port_%d" % (x))
          if passVerbosity == 1:
            print(pass1NextGrid, " ", end="")
        elif passVerbosity == 1:
          print("-", " ", end="")

        if pass2NextGrid > g or pass2NextGrid < firstGridOnRank:
          hyperLink(g,i,j, pass2NextGrid,i,j, "port_%d" % (x + 100), "port_%d" % (x + 100), True)
          if passVerbosity == 2:
            print(pass2NextGrid, " ", end="")
        elif passVerbosity == 2:
          print("-", " ", end="")

        pass1NextGrid = (pass1NextGrid + 1) % nGrids
        pass2NextGrid = (pass2NextGrid - 1) % nGrids

if(args.dryRun != -1):
  endTime = time.time()
  elapsedTime = endTime - startTime
  print("Elapsed time on rank %i is %f secs" % (myRank, elapsedTime))
  sys.exit(1)
