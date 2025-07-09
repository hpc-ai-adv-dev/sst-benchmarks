import sst
import argparse
import numpy 


parser = argparse.ArgumentParser(
  prog='PHOLD',
  description='Run a simulation of the PHOLD benchmark.')

parser.add_argument('--N', type=int, default=10, help='Height of grid (number of rows)')
parser.add_argument('--M', type=int, default=10, help='Width of grid (number of columns)')
parser.add_argument('--timeToRun', type=int, default=1000, help='ns to run the simulation')
args = parser.parse_args()
N = args.N  # Number of rows
M = args.M  # Number of columns
timeToRun = args.timeToRun  # Time to run the simulation
numRings = 1

comps = []
# Create M by N grid
for i in range(N):
  row = []
  for j in range(M):
    comp = sst.Component(f"comp_{i}_{j}", "phold.Node")
    comp.addParams({
      "numRings": 1
    })
    row.append(comp)
  comps.append(row)


def grid_idx(i,j):
  return i * M + j

# calculates the port index for a component at (i,j) that connects to a component at (i2, j2)
def port_num(i,j, i2, j2, num_rings):
  side_length = (num_rings * 2 + 1)
  di = i-i2
  dj = j-j2
  ip = num_rings - di
  jp = num_rings - dj
  return ip * side_length + jp


def connect_upward(i,j,num_rings):
  my_shifted_idx = ((num_rings*2 + 1) ** 2 - 1) // 2
  high_shifted_idx = (num_rings*2 + 1) ** 2 - 1
  for neighbor_shifted_idx  in range(my_shifted_idx, high_shifted_idx + 1):

    my_shifted_i = my_shifted_idx // (num_rings * 2 + 1)
    my_shifted_j = my_shifted_idx % (num_rings * 2 + 1)

    neighbor_shifted_i = neighbor_shifted_idx // (num_rings * 2 + 1)
    neighbor_shifted_j = neighbor_shifted_idx % (num_rings * 2 + 1)

    neighbor_i = i + neighbor_shifted_i - my_shifted_i
    neighbor_j = j + neighbor_shifted_j - my_shifted_j

    if neighbor_i < 0 or neighbor_i >= N or neighbor_j < 0 or neighbor_j >= M:
      continue
    print("Component at (%d, %d) connects to neighbor at (%d, %d)" % (i, j, neighbor_i, neighbor_j))
    port1 = port_num(i,j,neighbor_i,neighbor_j,num_rings)
    port2 = port_num(neighbor_i,neighbor_j,i,j,num_rings)
    link = sst.Link("link_%d_%d_to_%d_%d" % (i, j, neighbor_i, neighbor_j))
    link.connect((comps[i][j], f"port{port1}", "1ns"), (comps[neighbor_i][neighbor_j], f"port{port2}", "1ns"))



# Connect components
for i in range(N):
  for j in range(M):
    
    my_idx = grid_idx(i,j)
    connect_upward(i,j,numRings)
    #print_indices(i,j,numRings)
                               
      


  

print("Done with setup")