#!/usr/bin/env python3
"""
Compare topologies from SST JSON output files using NetworkX.
Supports both naming conventions:
  - Original: link_x_y_to_x_y
  - AHP: SubGridN.comp_x_y.portN__delay__SubGridM.comp_a_b.portM
"""

import json
import re
import sys
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


def parse_original_link_name(link_name: str) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """Parse link names like 'link_0_0_to_0_1' -> ((0,0), (0,1))"""
    match = re.match(r'link_(\d+)_(\d+)_to_(\d+)_(\d+)', link_name)
    if match:
        src = (int(match.group(1)), int(match.group(2)))
        dst = (int(match.group(3)), int(match.group(4)))
        return src, dst
    return None


def parse_ahp_link_name(link_name: str) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """Parse link names like 'SubGrid0.comp_0_0.port12__1ns__SubGrid0.comp_0_1.port11'"""
    # Pattern: SubGridN.comp_X_Y.portP__delay__SubGridM.comp_A_B.portQ
    match = re.match(
        r'SubGrid\d+\.comp_(\d+)_(\d+)\.port\d+__\d+\s*\w*__SubGrid\d+\.comp_(\d+)_(\d+)\.port\d+',
        link_name
    )
    if match:
        src = (int(match.group(1)), int(match.group(2)))
        dst = (int(match.group(3)), int(match.group(4)))
        return src, dst
    return None


def load_topology_from_json(json_path: str) -> nx.Graph:
    """Load a topology from an SST JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    G = nx.Graph()
    
    # Add nodes from components
    for comp in data.get('components', []):
        name = comp['name']
        # Extract coordinates from component name
        # Original: comp_x_y or AHP: SubGridN.comp_x_y
        match = re.search(r'comp_(\d+)_(\d+)', name)
        if match:
            node = (int(match.group(1)), int(match.group(2)))
            G.add_node(node, name=name)
    
    # Add edges from links
    for link in data.get('links', []):
        link_name = link.get('name', '')
        
        # Try original format first
        edge = parse_original_link_name(link_name)
        if edge is None:
            # Try AHP format
            edge = parse_ahp_link_name(link_name)
        
        if edge:
            src, dst = edge
            # Skip self-loops for cleaner visualization (optional)
            if src != dst:
                G.add_edge(src, dst, name=link_name)
    
    return G


def load_topology_from_multiple_json(json_paths: list[str]) -> nx.Graph:
    """Load and merge topologies from multiple JSON files (one per rank)."""
    G = nx.Graph()
    
    for json_path in json_paths:
        partial_G = load_topology_from_json(json_path)
        G = nx.compose(G, partial_G)
    
    return G


def compare_graphs(G1: nx.Graph, G2: nx.Graph, name1: str = "Graph1", name2: str = "Graph2"):
    """Compare two graphs and print differences."""
    print(f"\n{'='*60}")
    print(f"Comparison: {name1} vs {name2}")
    print(f"{'='*60}")
    
    # Node comparison
    nodes1 = set(G1.nodes())
    nodes2 = set(G2.nodes())
    
    print(f"\n{name1} nodes: {len(nodes1)}")
    print(f"{name2} nodes: {len(nodes2)}")
    
    only_in_1 = nodes1 - nodes2
    only_in_2 = nodes2 - nodes1
    common_nodes = nodes1 & nodes2
    
    if only_in_1:
        print(f"\nNodes only in {name1}: {sorted(only_in_1)}")
    if only_in_2:
        print(f"Nodes only in {name2}: {sorted(only_in_2)}")
    print(f"Common nodes: {len(common_nodes)}")
    
    # Edge comparison
    edges1 = set(frozenset(e) for e in G1.edges())
    edges2 = set(frozenset(e) for e in G2.edges())
    
    print(f"\n{name1} edges: {len(edges1)}")
    print(f"{name2} edges: {len(edges2)}")
    
    only_in_1_edges = edges1 - edges2
    only_in_2_edges = edges2 - edges1
    common_edges = edges1 & edges2
    
    if only_in_1_edges:
        print(f"\nEdges only in {name1} ({len(only_in_1_edges)}):")
        for e in sorted(only_in_1_edges, key=lambda x: tuple(sorted(x))):
            print(f"  {tuple(sorted(e))}")
    if only_in_2_edges:
        print(f"\nEdges only in {name2} ({len(only_in_2_edges)}):")
        for e in sorted(only_in_2_edges, key=lambda x: tuple(sorted(x))):
            print(f"  {tuple(sorted(e))}")
    
    print(f"\nCommon edges: {len(common_edges)}")
    
    # Degree comparison for common nodes
    print(f"\n{'='*60}")
    print("Degree comparison for common nodes:")
    print(f"{'='*60}")
    degree_diff = []
    for node in sorted(common_nodes):
        d1 = G1.degree(node)
        d2 = G2.degree(node)
        if d1 != d2:
            degree_diff.append((node, d1, d2))
    
    if degree_diff:
        print(f"{'Node':<12} {name1:<10} {name2:<10}")
        print("-" * 32)
        for node, d1, d2 in degree_diff:
            print(f"{str(node):<12} {d1:<10} {d2:<10}")
    else:
        print("All common nodes have the same degree in both graphs.")
    
    return nodes1 == nodes2 and edges1 == edges2


def visualize_topology(G: nx.Graph, title: str, ax=None, highlight_edges=None):
    """Visualize a topology graph."""
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Use grid positions based on node coordinates
    pos = {node: (node[1], -node[0]) for node in G.nodes()}
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue', 
                          node_size=500, alpha=0.9)
    
    # Draw edges
    if highlight_edges:
        # Draw normal edges
        normal_edges = [e for e in G.edges() if frozenset(e) not in highlight_edges]
        highlight_edge_list = [e for e in G.edges() if frozenset(e) in highlight_edges]
        
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=normal_edges,
                              edge_color='gray', alpha=0.5)
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=highlight_edge_list,
                              edge_color='red', width=2, alpha=0.8)
    else:
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', alpha=0.5)
    
    # Draw labels
    labels = {node: f"{node[0]},{node[1]}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8)
    
    ax.set_title(f"{title}\nNodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    ax.axis('off')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compare SST topologies from JSON files using NetworkX'
    )
    parser.add_argument('--og', nargs='+', required=True,
                       help='Original topology JSON files (e.g., og0.json og1.json ...)')
    parser.add_argument('--ahp', nargs='+', required=True,
                       help='AHP topology JSON files (e.g., ahp0.json ahp1.json ...)')
    parser.add_argument('--output', '-o', default='topology_comparison.png',
                       help='Output image file')
    parser.add_argument('--no-plot', action='store_true',
                       help='Skip plotting, just print comparison')
    
    args = parser.parse_args()
    
    # Load topologies
    print("Loading original topology...")
    G_og = load_topology_from_multiple_json(args.og)
    
    print("Loading AHP topology...")
    G_ahp = load_topology_from_multiple_json(args.ahp)
    
    # Compare
    are_equal = compare_graphs(G_og, G_ahp, "Original", "AHP")
    
    if are_equal:
        print("\n✓ Topologies are IDENTICAL")
    else:
        print("\n✗ Topologies are DIFFERENT")
    
    # Visualize
    if not args.no_plot:
        fig, axes = plt.subplots(1, 2, figsize=(20, 10))
        
        # Find edges unique to each graph for highlighting
        edges_og = set(frozenset(e) for e in G_og.edges())
        edges_ahp = set(frozenset(e) for e in G_ahp.edges())
        only_og = edges_og - edges_ahp
        only_ahp = edges_ahp - edges_og
        
        visualize_topology(G_og, "Original Topology", axes[0], highlight_edges=only_og)
        visualize_topology(G_ahp, "AHP Topology", axes[1], highlight_edges=only_ahp)
        
        plt.tight_layout()
        plt.savefig(args.output, dpi=150, bbox_inches='tight')
        print(f"\nSaved comparison plot to: {args.output}")
        plt.show()


if __name__ == '__main__':
    main()
