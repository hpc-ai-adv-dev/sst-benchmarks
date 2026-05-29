import sys
import sst
import argparse
import realistic_benchmarks


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--mesh_shape', '--shape', '--mesh-shape', dest='mesh_shape', default='4x4', help='Shape of the mesh topology (e.g. 4x4)')
    parser.add_argument('--mesh_width', type=str, help='TODO', default='2x2')
    parser.add_argument('--mesh_local_ports', type=int, default=2, help='how many endpoints are connected to each router in the mesh')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    
    mesh_topo = realistic_benchmarks.topoMesh()
    endPoint = realistic_benchmarks.TestEndPoint()


    realistic_benchmarks._params['mesh.shape'] = args.mesh_shape
    realistic_benchmarks._params['mesh.width'] = args.mesh_width
    realistic_benchmarks._params['mesh.local_ports'] = args.mesh_local_ports
    realistic_benchmarks._params['num_dims'] = args.mesh_shape.count('x') + 1

    realistic_benchmarks._params["flit_size"] = "8B"
    realistic_benchmarks._params["link_bw"] = "4GB/s"
    realistic_benchmarks._params["link_lat"] = "20ns"
    realistic_benchmarks._params["xbar_bw"] = "4GB/s"
    realistic_benchmarks._params["input_latency"] = "20ns"
    realistic_benchmarks._params["output_latency"] = "20ns"
    realistic_benchmarks._params["input_buf_size"] = "4kB"
    realistic_benchmarks._params["output_buf_size"] = "4kB"

    mesh_topo.prepParams()
    endPoint.prepParams()
    mesh_topo.setEndPoint(endPoint)
    mesh_topo.build_take2()





