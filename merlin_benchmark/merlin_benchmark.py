import sys
import sst
import argparse
import merlin_topologies


def parse_args():
    parser = argparse.ArgumentParser(
        description='SST Merlin benchmark. Configures and builds a mesh network with endpoints.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python merlin_mesh.py --mesh_shape 8x8 --mesh_local_ports 4
  python merlin_mesh.py --flit_size 16 --link_bw 8 --link_lat 2
        '''
    )

    parser = argparse.ArgumentParser(description='SST Merlin benchmark. Configures and builds a simulated network with endpoints over a configurable topology.')
    
    # Global simulation parameters
    global_args = parser.add_argument_group("Global Simulation Parameters")
    global_args.add_argument('--stop_at', '--stop-at', type=str, default='10us',
                            help='Simulation stop time (default: 10us). Determines how long the simulation runs before stopping.')
    global_args.add_argument('--verbose', type=int, default=None,
                        help='Optional SST program verbose level. If omitted, keep the existing SST verbose setting.')

    # Topology selection
    parser.add_argument("--topology", type=str, choices=["mesh", "dragonfly", "fattree"], default="mesh",
                        help="Select the network topology to use (default: mesh).")


    # Mesh topology arguments
    mesh_args = parser.add_argument_group("Mesh Topology Arguments")
    mesh_args.add_argument('--mesh_shape', '--shape', '--mesh-shape', dest='mesh_shape', default='4x4', 
                        help='Shape of the mesh topology in XxY format (default: 4x4). Example: 8x8 for 8x8 mesh.')
    mesh_args.add_argument('--mesh_width', type=str, default='2x2',
                        help='Width configuration for mesh routing. Specifies router connectivity in each direction (default: 2x2).')
    mesh_args.add_argument('--mesh_local_ports', type=int, default=2,
                        help='Number of local endpoints connected to each router in the mesh (default: 2).')

    # Dragonfly topology arguments
    dragonfly_args = parser.add_argument_group("DragonFly Topology Arguments")
    dragonfly_args.add_argument('--dragonfly_hosts_per_router', '--dragonfly_hosts-per-router', type=int, default=2,
                        help='Number of hosts (endpoints) connected to each router (default: 2).')
    dragonfly_args.add_argument('--dragonfly_routers_per_group', '--dragonfly_routers-per-group', type=int, default=4,
                        help='Number of routers in each group (default: 4).')
    dragonfly_args.add_argument('--dragonfly_intergroup_links', '--dragonfly_intergroup-links', type=int, default=1,
                        help='Number of links connecting each group to other groups (default: 1).')
    dragonfly_args.add_argument('--dragonfly_num_groups', '--dragonfly_num-groups', type=int, default=9,
                        help='Number of groups in the DragonFly topology (default: 9).') 
    dragonfly_args.add_argument('--dragonfly_algorithm', '--dragonfly-algorithm', type=str, default='minimal',
                        help='Routing algorithm to use (default: minimal). Options: minimal, adaptive-local')
    dragonfly_args.add_argument('--dragonfly_adaptive_threshold', '--dragonfly_adaptive-threshold', type=float, default=2.0,
                        help='Threshold for adaptive routing decisions (default: 2.0). Only used if algorithm is adaptive-local.')
    dragonfly_args.add_argument('--dragonfly_global_routing_mode', '--dragonfly_global-routing-mode', type=str, default='absolute',
                        help='Global routing mode for intergroup links (default: absolute). Options: absolute, relative')
  
    # FatTree topology arguments
    fattree_args = parser.add_argument_group("FatTree Topology Arguments")
    fattree_args.add_argument('--fattree_shape', type=str, default="4,4:4,4:8")


    # Network parameters - Link and buffer configuration
    network_args = parser.add_argument_group("Network Parameters")
    network_args.add_argument('--flit_size_bytes', '--flit_size', type=int, default=8,
                        help='Flit (flow control unit) size in bytes (default: 8B). Smaller values reduce latency but increase overhead.')
    network_args.add_argument('--link_bw_gbps', '--link_bw', type=int, default=4,
                        help='Link bandwidth in GB/s (default: 4GB/s). Affects network throughput.')
    network_args.add_argument('--link_lat_ns', '--link_lat', type=int, default=1,
                        help='Link latency in nanoseconds (default: 1ns). Delay for each hop through a link.')
    network_args.add_argument('--xbar_bw_gbps', '--xbar_bw', type=int, default=4,
                        help='Crossbar bandwidth in GB/s (default: 4GB/s). Bandwidth within each router.')
    

    # Endpoint and buffer parameters

    endpoint_args = parser.add_argument_group("Endpoint and Buffer Parameters")

    endpoint_args.add_argument('--tg-output-file-name', '--tg_output_file_name', type=str, default='',
                        help='Output file name for traffic generator logs. If empty, logs are printed to stdout.')
    endpoint_args.add_argument('--tg-input-latency', '--tg_input_latency', type=str, default='20ns',
                               help='Traffic generator input latency (e.g. 20ns).')
    endpoint_args.add_argument('--tg-output-latency', '--tg_output_latency', type=str, default='20ns',
                               help='Traffic generator output latency (e.g. 20ns).')
    endpoint_args.add_argument('--tg-input-buf-size', '--tg_input_buf_size', type=str, default='4kB',
                        help='Traffic generator input buffer size (e.g. 1kB).')
    endpoint_args.add_argument('--tg-output-buf-size', '--tg_output_buf_size', type=str, default='4kB',
                        help='Traffic generator output buffer size (e.g. 1kB).')


    # Traffic generator parameters
    endpoint_args.add_argument('--tg-num-vns', '--tg_num_vns', type=int, default=None,
                        help='Number of virtual networks requested by the traffic generator.')
    endpoint_args.add_argument('--tg-buffer-length', '--tg_buffer_length', type=str, default=None,
                        help='Traffic generator network interface buffer length (e.g. 1kB).')
    endpoint_args.add_argument('--tg-packets-to-send', '--tg_packets_to_send', type=int, default=None,
                        help='Number of packets each traffic generator endpoint should send.')
    endpoint_args.add_argument('--tg-packet-size', '--tg_packet_size', type=str, default=None,
                        help='Packet size with units (e.g. 64B, 512b).')
    endpoint_args.add_argument('--tg-delay-between-packets', '--tg_delay_between_packets', type=str, default=None,
                        help='Delay between packets with time units (e.g. 5ns).')
    endpoint_args.add_argument('--tg-message-rate', '--tg_message_rate', type=str, default=None,
                        help='Clock/message rate for traffic generation (e.g. 1GHz).')

    # Packet destination generator parameters
    endpoint_args.add_argument('--tg-packet-dest-pattern', '--tg_packet_dest_pattern', type=str, default=None,
                        choices=['NearestNeighbor', 'Uniform', 'HotSpot', 'Normal', 'Exponential', 'Binomial'],
                        help='Packet destination generation pattern.')
    endpoint_args.add_argument('--tg-packet-dest-seed', '--tg_packet_dest_seed', type=int, default=None,
                        help='RNG seed for PacketDest generator.')
    endpoint_args.add_argument('--tg-packet-dest-range-min', '--tg_packet_dest_range_min', type=int, default=None,
                        help='Minimum destination id for PacketDest generator.')
    endpoint_args.add_argument('--tg-packet-dest-range-max', '--tg_packet_dest_range_max', type=int, default=None,
                        help='Maximum destination id for PacketDest generator.')
    endpoint_args.add_argument('--tg-packet-dest-nearest-neighbor-size', '--tg_packet_dest_nearest_neighbor_size', type=str, default=None,
                        help='NearestNeighbor mesh shape for PacketDest in "x y z" format.')
    endpoint_args.add_argument('--tg-packet-dest-hotspot-target', '--tg_packet_dest_hotspot_target', type=int, default=None,
                        help='HotSpot target for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-hotspot-target-probability', '--tg_packet_dest_hotspot_target_probability', type=float, default=None,
                        help='HotSpot target probability for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-normal-mean', '--tg_packet_dest_normal_mean', type=float, default=None,
                        help='Normal distribution mean for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-normal-sigma', '--tg_packet_dest_normal_sigma', type=float, default=None,
                        help='Normal distribution sigma for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-binomial-mean', '--tg_packet_dest_binomial_mean', type=int, default=None,
                        help='Binomial mean/trials value for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-binomial-sigma', '--tg_packet_dest_binomial_sigma', type=float, default=None,
                        help='Binomial sigma/probability value for PacketDest.')
    endpoint_args.add_argument('--tg-packet-dest-exponential-lambda', '--tg_packet_dest_exponential_lambda', type=float, default=None,
                        help='Exponential lambda for PacketDest.')

    # Packet size generator parameters
    endpoint_args.add_argument('--tg-packet-size-pattern', '--tg_packet_size_pattern', type=str, default=None,
                        choices=['Uniform', 'HotSpot', 'Normal', 'Exponential', 'Binomial'],
                        help='Packet size generation pattern.')
    endpoint_args.add_argument('--tg-packet-size-seed', '--tg_packet_size_seed', type=int, default=None,
                        help='RNG seed for PacketSize generator.')
    endpoint_args.add_argument('--tg-packet-size-range-min', '--tg_packet_size_range_min', type=int, default=None,
                        help='Minimum packet size for PacketSize generator.')
    endpoint_args.add_argument('--tg-packet-size-range-max', '--tg_packet_size_range_max', type=int, default=None,
                        help='Maximum packet size for PacketSize generator.')
    endpoint_args.add_argument('--tg-packet-size-hotspot-target', '--tg_packet_size_hotspot_target', type=int, default=None,
                        help='HotSpot target for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-hotspot-target-probability', '--tg_packet_size_hotspot_target_probability', type=float, default=None,
                        help='HotSpot target probability for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-normal-mean', '--tg_packet_size_normal_mean', type=float, default=None,
                        help='Normal distribution mean for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-normal-sigma', '--tg_packet_size_normal_sigma', type=float, default=None,
                        help='Normal distribution sigma for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-binomial-mean', '--tg_packet_size_binomial_mean', type=int, default=None,
                        help='Binomial mean/trials value for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-binomial-sigma', '--tg_packet_size_binomial_sigma', type=float, default=None,
                        help='Binomial sigma/probability value for PacketSize.')
    endpoint_args.add_argument('--tg-packet-size-exponential-lambda', '--tg_packet_size_exponential_lambda', type=float, default=None,
                        help='Exponential lambda for PacketSize.')

    # Packet delay generator parameters
    endpoint_args.add_argument('--tg-packet-delay-pattern', '--tg_packet_delay_pattern', type=str, default=None,
                        choices=['Uniform', 'HotSpot', 'Normal', 'Exponential', 'Binomial'],
                        help='Packet delay generation pattern.')
    endpoint_args.add_argument('--tg-packet-delay-seed', '--tg_packet_delay_seed', type=int, default=None,
                        help='RNG seed for PacketDelay generator.')
    endpoint_args.add_argument('--tg-packet-delay-range-min', '--tg_packet_delay_range_min', type=int, default=None,
                        help='Minimum delay for PacketDelay generator.')
    endpoint_args.add_argument('--tg-packet-delay-range-max', '--tg_packet_delay_range_max', type=int, default=None,
                        help='Maximum delay for PacketDelay generator.')
    endpoint_args.add_argument('--tg-packet-delay-hotspot-target', '--tg_packet_delay_hotspot_target', type=int, default=None,
                        help='HotSpot target for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-hotspot-target-probability', '--tg_packet_delay_hotspot_target_probability', type=float, default=None,
                        help='HotSpot target probability for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-normal-mean', '--tg_packet_delay_normal_mean', type=float, default=None,
                        help='Normal distribution mean for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-normal-sigma', '--tg_packet_delay_normal_sigma', type=float, default=None,
                        help='Normal distribution sigma for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-binomial-mean', '--tg_packet_delay_binomial_mean', type=int, default=None,
                        help='Binomial mean/trials value for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-binomial-sigma', '--tg_packet_delay_binomial_sigma', type=float, default=None,
                        help='Binomial sigma/probability value for PacketDelay.')
    endpoint_args.add_argument('--tg-packet-delay-exponential-lambda', '--tg_packet_delay_exponential_lambda', type=float, default=None,
                        help='Exponential lambda for PacketDelay.')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    sst.setProgramOption("stop-at", args.stop_at)
    if args.verbose is not None:
        sst.setProgramOption("verbose", str(args.verbose))

    if args.topology == "mesh":
        topo = merlin_topologies.topoMesh()
        merlin_topologies._params['mesh.shape'] = args.mesh_shape
        merlin_topologies._params['mesh.width'] = args.mesh_width
        merlin_topologies._params['mesh.local_ports'] = args.mesh_local_ports
        merlin_topologies._params['num_dims'] = args.mesh_shape.count('x') + 1

    elif args.topology == "dragonfly":
        topo = merlin_topologies.topoDragonFly()
        merlin_topologies._params['dragonfly.hosts_per_router'] = str(args.dragonfly_hosts_per_router)
        merlin_topologies._params['dragonfly.routers_per_group'] = str(args.dragonfly_routers_per_group)
        merlin_topologies._params['dragonfly.intergroup_links'] = str(args.dragonfly_intergroup_links)
        merlin_topologies._params['dragonfly.num_groups'] = str(args.dragonfly_num_groups)
        merlin_topologies._params['dragonfly.algorithm'] = args.dragonfly_algorithm
        if args.dragonfly_algorithm == 'adaptive-local':
            merlin_topologies._params['dragonfly.adaptive_threshold'] = str(args.dragonfly_adaptive_threshold)
        if args.dragonfly_global_routing_mode == 'relative':
            topo.setRoutingModeRelative()
    elif args.topology == "fattree":
        topo = merlin_topologies.topoFatTree()
        merlin_topologies._params["fattree.shape"] = args.fattree_shape
    else:
        print(f"Error: Unknown topology '{args.topology}'")
        sys.exit(1)

    endPoint = merlin_topologies.TrafficGenerator()

    merlin_topologies._params["flit_size"] = f"{args.flit_size_bytes}B"
    merlin_topologies._params["link_bw"] = f"{args.link_bw_gbps}GB/s"
    merlin_topologies._params["link_lat"] = f"{args.link_lat_ns}ns"
    merlin_topologies._params["xbar_bw"] = f"{args.xbar_bw_gbps}GB/s"

    tg_arg_map = {
        "output_file_name": args.tg_output_file_name,
        "input_latency": args.tg_input_latency,
        "output_latency": args.tg_output_latency,
        "input_buf_size": args.tg_input_buf_size,
        "output_buf_size": args.tg_output_buf_size,
        "num_vns": args.tg_num_vns,
        "buffer_length": args.tg_buffer_length,
        "packets_to_send": args.tg_packets_to_send,
        "packet_size": args.tg_packet_size,
        "delay_between_packets": args.tg_delay_between_packets,
        "message_rate": args.tg_message_rate,
        "PacketDest.pattern": args.tg_packet_dest_pattern,
        "PacketDest.Seed": args.tg_packet_dest_seed,
        "PacketDest.RangeMin": args.tg_packet_dest_range_min,
        "PacketDest.RangeMax": args.tg_packet_dest_range_max,
        "PacketDest.NearestNeighbor.Size": args.tg_packet_dest_nearest_neighbor_size,
        "PacketDest.HotSpot.target": args.tg_packet_dest_hotspot_target,
        "PacketDest.HotSpot.targetProbability": args.tg_packet_dest_hotspot_target_probability,
        "PacketDest.Normal.Mean": args.tg_packet_dest_normal_mean,
        "PacketDest.Normal.Sigma": args.tg_packet_dest_normal_sigma,
        "PacketDest.Binomial.Mean": args.tg_packet_dest_binomial_mean,
        "PacketDest.Binomial.Sigma": args.tg_packet_dest_binomial_sigma,
        "PacketDest.Exponential.Lambda": args.tg_packet_dest_exponential_lambda,
        "PacketSize.pattern": args.tg_packet_size_pattern,
        "PacketSize.Seed": args.tg_packet_size_seed,
        "PacketSize.RangeMin": args.tg_packet_size_range_min,
        "PacketSize.RangeMax": args.tg_packet_size_range_max,
        "PacketSize.HotSpot.target": args.tg_packet_size_hotspot_target,
        "PacketSize.HotSpot.targetProbability": args.tg_packet_size_hotspot_target_probability,
        "PacketSize.Normal.Mean": args.tg_packet_size_normal_mean,
        "PacketSize.Normal.Sigma": args.tg_packet_size_normal_sigma,
        "PacketSize.Binomial.Mean": args.tg_packet_size_binomial_mean,
        "PacketSize.Binomial.Sigma": args.tg_packet_size_binomial_sigma,
        "PacketSize.Exponential.Lambda": args.tg_packet_size_exponential_lambda,
        "PacketDelay.pattern": args.tg_packet_delay_pattern,
        "PacketDelay.Seed": args.tg_packet_delay_seed,
        "PacketDelay.RangeMin": args.tg_packet_delay_range_min,
        "PacketDelay.RangeMax": args.tg_packet_delay_range_max,
        "PacketDelay.HotSpot.target": args.tg_packet_delay_hotspot_target,
        "PacketDelay.HotSpot.targetProbability": args.tg_packet_delay_hotspot_target_probability,
        "PacketDelay.Normal.Mean": args.tg_packet_delay_normal_mean,
        "PacketDelay.Normal.Sigma": args.tg_packet_delay_normal_sigma,
        "PacketDelay.Binomial.Mean": args.tg_packet_delay_binomial_mean,
        "PacketDelay.Binomial.Sigma": args.tg_packet_delay_binomial_sigma,
        "PacketDelay.Exponential.Lambda": args.tg_packet_delay_exponential_lambda,
    }

    for key, value in tg_arg_map.items():
        if value is not None:
            merlin_topologies._params[key] = value

    topo.prepParams()
    endPoint.prepParams()
    topo.setEndPoint(endPoint)
    topo.build_distributed()