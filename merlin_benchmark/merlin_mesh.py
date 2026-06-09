import sys
import sst
import argparse
import realistic_benchmarks


def parse_args():
    parser = argparse.ArgumentParser(
        description='SST Merlin mesh topology benchmark. Configures and builds a mesh network with endpoints.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python merlin_mesh.py --mesh_shape 8x8 --mesh_local_ports 4
  python merlin_mesh.py --flit_size 16 --link_bw 8 --link_lat 2
        '''
    )

    # Mesh topology arguments
    parser.add_argument('--mesh_shape', '--shape', '--mesh-shape', dest='mesh_shape', default='4x4', 
                        help='Shape of the mesh topology in XxY format (default: 4x4). Example: 8x8 for 8x8 mesh.')
    parser.add_argument('--mesh_width', type=str, default='2x2',
                        help='Width configuration for mesh routing. Specifies router connectivity in each direction (default: 2x2).')
    parser.add_argument('--mesh_local_ports', type=int, default=2,
                        help='Number of local endpoints connected to each router in the mesh (default: 2).')

    # Network parameters - Link and buffer configuration
    parser.add_argument('--flit_size_bytes', '--flit_size', type=int, default=8,
                        help='Flit (flow control unit) size in bytes (default: 8B). Smaller values reduce latency but increase overhead.')
    parser.add_argument('--link_bw_gbps', '--link_bw', type=int, default=4,
                        help='Link bandwidth in GB/s (default: 4GB/s). Affects network throughput.')
    parser.add_argument('--link_lat_ns', '--link_lat', type=int, default=1,
                        help='Link latency in nanoseconds (default: 1ns). Delay for each hop through a link.')
    parser.add_argument('--xbar_bw_gbps', '--xbar_bw', type=int, default=4,
                        help='Crossbar bandwidth in GB/s (default: 4GB/s). Bandwidth within each router.')
    
    # Endpoint and buffer parameters
    parser.add_argument('--input_latency_ns', '--input_latency', type=int, default=20,
                        help='Input latency in nanoseconds (default: 20ns). Processing time for incoming messages.')
    parser.add_argument('--output_latency_ns', '--output_latency', type=int, default=20,
                        help='Output latency in nanoseconds (default: 20ns). Processing time for outgoing messages.')
    parser.add_argument('--input_buf_size_kb', '--input_buf_size', type=int, default=4,
                        help='Input buffer size in kilobytes (default: 4kB). Buffering capacity for incoming traffic.')
    parser.add_argument('--output_buf_size_kb', '--output_buf_size', type=int, default=4,
                        help='Output buffer size in kilobytes (default: 4kB). Buffering capacity for outgoing traffic.')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    
    mesh_topo = realistic_benchmarks.topoMesh()
    endPoint = realistic_benchmarks.TestEndPoint()


    realistic_benchmarks._params['mesh.shape'] = args.mesh_shape
    realistic_benchmarks._params['mesh.width'] = args.mesh_width
    realistic_benchmarks._params['mesh.local_ports'] = args.mesh_local_ports
    realistic_benchmarks._params['num_dims'] = args.mesh_shape.count('x') + 1
    realistic_benchmarks._params["flit_size"] = f"{args.flit_size_bytes}B"
    realistic_benchmarks._params["link_bw"] = f"{args.link_bw_gbps}GB/s"
    realistic_benchmarks._params["link_lat"] = f"{args.link_lat_ns}ns"
    realistic_benchmarks._params["xbar_bw"] = f"{args.xbar_bw_gbps}GB/s"
    realistic_benchmarks._params["input_latency"] = f"{args.input_latency_ns}ns"
    realistic_benchmarks._params["output_latency"] = f"{args.output_latency_ns}ns"
    realistic_benchmarks._params["input_buf_size"] = f"{args.input_buf_size_kb}kB"
    realistic_benchmarks._params["output_buf_size"] = f"{args.output_buf_size_kb}kB"

    mesh_topo.prepParams()
    endPoint.prepParams()
    mesh_topo.setEndPoint(endPoint)
    mesh_topo.build()





