import sst
import argparse, random

parser = argparse.ArgumentParser(
  prog='SSTPingPong',
  description='Run a simulation consisting of several components arranged in a 1D or 2D grid that send messages back and forth')
parser.add_argument('--N',              type=int, default=10)
parser.add_argument('--timeToRun',      type=int, default=200)
parser.add_argument('--numDims',        type=int, choices=[1,2], default=2)
parser.add_argument('--edgeDelay',      type=int, default=50)
parser.add_argument('--artificialWork', type=int, default=0)
parser.add_argument('--verbose',        default=False, action='store_true')
parser.add_argument('--seed',            type=int, default=-1)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--single',          default=False, action='store_true')
group.add_argument('--corners',         default=False, action='store_true')
group.add_argument('--random',          type=int, default=-1)
group.add_argument('--randomOverlap',   type=int, default=-1)
group.add_argument('--wavefront',       default=False, action='store_true')
args = parser.parse_args()

if args.seed != -1:
  random.seed(args.seed)

# -----------------------------------------------------------------------------

def oppositeDir(direction):
  opposites = {'north': 'south', 'south': 'north', 'west': 'east', 'east': 'west'}
  return opposites[direction]

numLinks = 0
def link(x, y, direction):
  global numLinks
  if args.verbose:
    print("connect ", x.getFullName(), direction, "--", y.getFullName(), oppositeDir(direction))
  sst.Link("link%i" % numLinks).connect( (x, "%sPort" % direction, "%ips" % args.edgeDelay), (y, "%sPort" % oppositeDir(direction), "%ips" % args.edgeDelay) )
  numLinks += 1

# -----------------------------------------------------------------------------

simulator = sst.Component("sim", "pingpong.simulator")
simulator.addParams({"timeToRun"      : args.timeToRun,
                   "verbose"        : args.verbose,
                   "artificialWork" : args.artificialWork})

pingPongers = {}
ballsHeadingNorthAt = {}
ballsHeadingSouthAt = {}
ballsHeadingWestAt  = {}
ballsHeadingEastAt  = {}

NW_PONGER = 0
NE_PONGER = args.N-1
SW_PONGER = args.N * (args.N-1)
SE_PONGER = (args.N * args.N) - 1

if args.single:
  if args.numDims == 1:
    ballsHeadingSouthAt[NW_PONGER] = 1
  elif args.numDims == 2:
    ballsHeadingEastAt[NW_PONGER] = 1
  else:
    print("Invalid configuration")
    exit(1)
elif args.corners:
  if args.numDims == 1:
    ballsHeadingEastAt[NW_PONGER] = 1
    ballsHeadingWestAt[NE_PONGER] = 1
  elif args.numDims > 1:
    ballsHeadingEastAt[NW_PONGER] = 1
    ballsHeadingWestAt[NE_PONGER] = 1
    ballsHeadingEastAt[SW_PONGER] = 1
    ballsHeadingWestAt[SE_PONGER] = 1
    ballsHeadingSouthAt[NW_PONGER] = 1
    ballsHeadingSouthAt[NE_PONGER] = 1
    ballsHeadingNorthAt[SW_PONGER] = 1
    ballsHeadingNorthAt[SE_PONGER] = 1
elif args.random != -1:
  sample = random.sample(range(args.N * args.N), min(args.N *args.N,args.random))
  for r in sample:
    direction = random.randint(0,3)
    if direction   == 0: ballsHeadingNorthAt[r] = 1
    elif direction == 1: ballsHeadingSouthAt[r] = 1
    elif direction == 2: ballsHeadingWestAt[r]  = 1
    elif direction == 3: ballsHeadingEastAt[r]  = 1
elif args.randomOverlap != -1:
  for _ in range(args.randomOverlap):
    r = random.randint(0, args.N * args.N - 1)
    direction = random.randint(0,3)
    if direction   == 0: ballsHeadingNorthAt[r] = ballsHeadingNorthAt.get(r,0) + 1
    elif direction == 1: ballsHeadingSouthAt[r] = ballsHeadingSouthAt.get(r,0) + 1
    elif direction == 2: ballsHeadingWestAt[r]  = ballsHeadingWestAt.get(r,0) + 1
    elif direction == 3: ballsHeadingEastAt[r]  = ballsHeadingEastAt.get(r,0) + 1
elif args.wavefront:
  for i in range(0,args.N):
     ballsHeadingSouthAt[i]                   = 1
     ballsHeadingEastAt[i*args.N]             = 1
     ballsHeadingWestAt[(i+1)*args.N-1]       = 1
     ballsHeadingNorthAt[args.N*(args.N-1)+i] = 1
else:
  print("Unknown ball placement configuration")
  exit(1)

if args.verbose:
  print("Initial balls --")
  for i in [0] if args.numDims == 1 else range(0,args.N):
    for j in range(0,args.N):
      me = i * args.N + j
      if me in ballsHeadingEastAt:  print("%5i %s" % (me, "east"))
      if me in ballsHeadingWestAt:  print("%5i %s" % (me, "west"))
      if me in ballsHeadingSouthAt: print("%5i %s" % (me, "south"))
      if me in ballsHeadingNorthAt: print("%5i %s" % (me, "north"))

for i in range(0,args.N):
  for j in [0] if args.numDims == 1 else range(0,args.N):
    me = i * args.N + j
    ponger = sst.Component("pong_%i_%i" % (i,j), "pingpong.ponger")
    ponger.addParams({
      "ballsHeadingNorth": ballsHeadingNorthAt.get(me, 0),
      "ballsHeadingSouth": ballsHeadingSouthAt.get(me, 0),
      "ballsHeadingWest":  ballsHeadingWestAt.get(me, 0),
      "ballsHeadingEast":  ballsHeadingEastAt.get(me, 0)})
    pingPongers[me] = ponger

# i = row, j = col, (0,0) = north west corner
for i in range(0,args.N):
  for j in [0] if args.numDims == 1 else range(0,args.N):
    me = i * args.N + j
    neighborS = me + args.N
    neighborE = me + 1

    connectS = i < args.N-1
    connectE = j < args.N-1 and args.numDims > 1

    if connectS:
      link(pingPongers[me], pingPongers[neighborS], "south")
    if connectE:
      link(pingPongers[me], pingPongers[neighborE], "east")

