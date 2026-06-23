import sys
import sst
import argparse
import realistic_benchmarks

def parse_args():
    parser = argparse.ArgumentParser(
        description='SST Merlin DragonFly topology benchmark. Configures and builds a DragonFly network with endpoints.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python merlin_dragonfly.py --hosts_per_router 2 --routers_per_group 4 --intergroup_links 1 --num_groups 9
  python merlin_dragonfly.py --link_bw 4GB/s --link_lat 20ns --flit_size 8B
        '''
    )

    # DragonFly topology arguments
    
    #sst.merlin._params["fattree.shape"] = "4,4:4,4:8"
    parser.add_argument('--fattree_shape', type=str, default="4,4:4,4:8")

    # Network parameters - Link and buffer configuration
    parser.add_argument('--flit_size_bytes', '--flit-size-bytes', '--flit_size', '--flit-size', type=int, default=8,
                        help='Flit (flow control unit) size in bytes (default: 8B). Smaller values reduce latency but increase overhead.')
    parser.add_argument('--link_bw_gbps', '--link-bw-gbps', '--link_bw', '--link-bw', type=int, default=4,
                        help='Link bandwidth in GB/s (default: 4GB/s). Affects network throughput.')
    parser.add_argument('--link_lat_ns', '--link-lat-ns', '--link_lat', '--link-lat', type=int, default=1,
                        help='Link latency in nanoseconds (default: 1ns). Delay for each hop through a link.')
    parser.add_argument('--xbar_bw_gbps', '--xbar-bw-gbps', '--xbar_bw', '--xbar-bw', type=int, default=4,
                        help='Crossbar bandwidth in GB/s (default: 4GB/s). Bandwidth within each router.')
    
    # Endpoint and buffer parameters
    parser.add_argument('--input_latency_ns', '--input-latency-ns', '--input_latency', '--input-latency', type=int, default=20,
                        help='Input latency in nanoseconds (default: 20ns). Processing time for incoming messages.')
    parser.add_argument('--output_latency_ns', '--output-latency-ns', '--output_latency', '--output-latency', type=int, default=20,
                        help='Output latency in nanoseconds (default: 20ns). Processing time for outgoing messages.')
    parser.add_argument('--input_buf_size_kb', '--input-buf-size-kb', '--input_buf_size', '--input-buf-size', type=int, default=4,
                        help='Input buffer size in kilobytes (default: 4kB). Buffering capacity for incoming traffic.')
    parser.add_argument('--output_buf_size_kb', '--output-buf-size-kb', '--output_buf_size', '--output-buf-size', type=int, default=4,
                        help='Output buffer size in kilobytes (default: 4kB). Buffering capacity for outgoing traffic.')

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()

    topo = realistic_benchmarks.topoFatTree()
    endPoint = realistic_benchmarks.TestEndPoint()

    realistic_benchmarks._params["fattree.shape"] = args.fattree_shape

    realistic_benchmarks._params["flit_size"] = f"{args.flit_size_bytes}B"
    realistic_benchmarks._params["link_bw"] = f"{args.link_bw_gbps}GB/s"
    realistic_benchmarks._params["link_lat"] = f"{args.link_lat_ns}ns"
    realistic_benchmarks._params["xbar_bw"] = f"{args.xbar_bw_gbps}GB/s"
    realistic_benchmarks._params["input_latency"] = f"{args.input_latency_ns}ns"
    realistic_benchmarks._params["output_latency"] = f"{args.output_latency_ns}ns"
    realistic_benchmarks._params["input_buf_size"] = f"{args.input_buf_size_kb}kB"
    realistic_benchmarks._params["output_buf_size"] = f"{args.output_buf_size_kb}kB"


    topo.prepParams()
    endPoint.prepParams()
    topo.setEndPoint(endPoint)
    topo.build_distributed()