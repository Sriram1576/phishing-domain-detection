import json
import logging
import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

import torch
try:
    import dgl
    DGL_AVAILABLE = True
except Exception as e:
    DGL_AVAILABLE = False
    logging.warning(f"DGL or PyTorch is not installed correctly. to_dgl_graph will not be available. ({e})")

logger = logging.getLogger(__name__)

class DomainGraphBuilder:
    """Builds a heterogeneous graph from domain, DNS, and feature data."""
    
    def __init__(self) -> None:
        """Initializes the DomainGraphBuilder."""
        self.graph: nx.Graph = nx.Graph()
        self.dgl_graph: Optional[Any] = None
        
        self.domain_to_idx: Dict[str, int] = {}
        self.ip_to_idx: Dict[str, int] = {}
        self.ns_to_idx: Dict[str, int] = {}
        
    def build_graph(self, domains_df: pd.DataFrame, dns_df: pd.DataFrame, features_df: pd.DataFrame) -> nx.Graph:
        """
        Builds a NetworkX graph with domain, IP, and nameserver nodes.
        
        Args:
            domains_df: DataFrame with 'domain' and 'label' columns.
            dns_df: DataFrame with 'domain', 'ip_addresses', 'nameservers', 'dns_status'.
            features_df: DataFrame with 'domain' and feature columns.
            
        Returns:
            The constructed NetworkX graph.
        """
        self.graph = nx.Graph()
        self.domain_to_idx.clear()
        self.ip_to_idx.clear()
        self.ns_to_idx.clear()
        
        # Merge dataframes
        df = domains_df.merge(dns_df, on='domain', how='left')
        df = df.merge(features_df, on='domain', how='left')
        
        for idx, row in df.iterrows():
            domain = row['domain']
            domain_id = f"d_{domain}"
            self.domain_to_idx[domain] = len(self.domain_to_idx)
            
            # Prepare domain node attributes
            attrs = row.to_dict()
            attrs['node_type'] = 'domain'
            self.graph.add_node(domain_id, **attrs)
            
            # Skip edge creation if DNS resolution failed, but node is added
            if row.get('dns_status') == 'failed':
                continue
                
            # Process IPs
            if pd.notna(row.get('ip_addresses')):
                try:
                    ips = json.loads(row['ip_addresses'])
                    for ip in ips:
                        ip_id = f"ip_{ip}"
                        if ip not in self.ip_to_idx:
                            self.ip_to_idx[ip] = len(self.ip_to_idx)
                            self.graph.add_node(ip_id, node_type='ip', ip_address=ip)
                        self.graph.add_edge(domain_id, ip_id, type='has_ip')
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse ip_addresses JSON for domain {domain}")
                    
            # Process Nameservers
            if pd.notna(row.get('nameservers')):
                try:
                    nameservers = json.loads(row['nameservers'])
                    for ns in nameservers:
                        ns_id = f"ns_{ns}"
                        if ns not in self.ns_to_idx:
                            self.ns_to_idx[ns] = len(self.ns_to_idx)
                            self.graph.add_node(ns_id, node_type='nameserver', nameserver=ns)
                        self.graph.add_edge(domain_id, ns_id, type='has_ns')
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse nameservers JSON for domain {domain}")

        stats = self.get_graph_stats()
        logger.info(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        logger.info(f"Graph stats: {stats}")
        
        return self.graph

    def to_dgl_graph(self, feature_cols: List[str]) -> Any:
        if not DGL_AVAILABLE:
            raise RuntimeError("DGL is not installed correctly. Cannot convert to DGL graph.")
            
        # Extract edges
        domain_has_ip_src, domain_has_ip_dst = [], []
        domain_has_ns_src, domain_has_ns_dst = [], []
        
        domain_nodes, ip_nodes, ns_nodes = [], [], []
        
        domain_features, domain_labels = [], []
        
        for n, data in self.graph.nodes(data=True):
            node_type = data.get('node_type')
            if node_type == 'domain':
                domain_nodes.append(n)
                feat = [float(data.get(col, 0.0)) for col in feature_cols]
                domain_features.append(feat)
                domain_labels.append(int(data.get('label', 0)))
            elif node_type == 'ip':
                ip_nodes.append(n)
            elif node_type == 'nameserver':
                ns_nodes.append(n)
                
        # Re-index to guarantee exact match with DGL node arrays (0..N-1)
        self.domain_to_idx = {self.graph.nodes[n].get('domain', n[2:] if n.startswith('d_') else n): i for i, n in enumerate(domain_nodes)}
        self.ip_to_idx = {self.graph.nodes[n].get('ip_address', n[3:] if n.startswith('ip_') else n): i for i, n in enumerate(ip_nodes)}
        self.ns_to_idx = {self.graph.nodes[n].get('nameserver', n[3:] if n.startswith('ns_') else n): i for i, n in enumerate(ns_nodes)}
                
        for u, v, data in self.graph.edges(data=True):
            rel = data.get('type')
            u_data = self.graph.nodes[u]
            v_data = self.graph.nodes[v]
            if rel == 'has_ip':
                if u_data.get('node_type') == 'domain':
                    d_name = u_data.get('domain', u[2:] if u.startswith('d_') else u)
                    ip_val = v_data.get('ip_address', v[3:] if v.startswith('ip_') else v)
                else:
                    d_name = v_data.get('domain', v[2:] if v.startswith('d_') else v)
                    ip_val = u_data.get('ip_address', u[3:] if u.startswith('ip_') else u)
                
                if d_name in self.domain_to_idx and ip_val in self.ip_to_idx:
                    domain_has_ip_src.append(self.domain_to_idx[d_name])
                    domain_has_ip_dst.append(self.ip_to_idx[ip_val])
            elif rel == 'has_ns':
                if u_data.get('node_type') == 'domain':
                    d_name = u_data.get('domain', u[2:] if u.startswith('d_') else u)
                    ns_val = v_data.get('nameserver', v[3:] if v.startswith('ns_') else v)
                else:
                    d_name = v_data.get('domain', v[2:] if v.startswith('d_') else v)
                    ns_val = u_data.get('nameserver', u[3:] if u.startswith('ns_') else u)
                
                if d_name in self.domain_to_idx and ns_val in self.ns_to_idx:
                    domain_has_ns_src.append(self.domain_to_idx[d_name])
                    domain_has_ns_dst.append(self.ns_to_idx[ns_val])
                
        # Create heterograph
        graph_data = {
            ('domain', 'has_ip', 'ip'): (torch.tensor(domain_has_ip_src, dtype=torch.int64), 
                                         torch.tensor(domain_has_ip_dst, dtype=torch.int64)),
            ('ip', 'ip_of', 'domain'): (torch.tensor(domain_has_ip_dst, dtype=torch.int64), 
                                        torch.tensor(domain_has_ip_src, dtype=torch.int64)),
            ('domain', 'has_ns', 'nameserver'): (torch.tensor(domain_has_ns_src, dtype=torch.int64), 
                                                 torch.tensor(domain_has_ns_dst, dtype=torch.int64)),
            ('nameserver', 'ns_of', 'domain'): (torch.tensor(domain_has_ns_dst, dtype=torch.int64), 
                                                torch.tensor(domain_has_ns_src, dtype=torch.int64)),
            # Self-loops for domain nodes
            ('domain', 'self', 'domain'): (torch.arange(len(domain_nodes), dtype=torch.int64), 
                                           torch.arange(len(domain_nodes), dtype=torch.int64))
        }
        
        # Ensure all node types are present even if isolated
        num_nodes_dict = {
            'domain': len(domain_nodes),
            'ip': len(ip_nodes),
            'nameserver': len(ns_nodes)
        }
        
        g = dgl.heterograph(graph_data, num_nodes_dict=num_nodes_dict)
        
        # Set node features and labels
        if len(domain_nodes) > 0:
            g.nodes['domain'].data['feat'] = torch.tensor(domain_features, dtype=torch.float32)
            g.nodes['domain'].data['label'] = torch.tensor(domain_labels, dtype=torch.int64)
            
        ip_degrees = np.zeros((len(ip_nodes), 1), dtype=np.float32)
        for d_dst in domain_has_ip_dst: ip_degrees[d_dst, 0] += 1
        if len(ip_nodes) > 0: g.nodes['ip'].data['feat'] = torch.tensor(ip_degrees, dtype=torch.float32)
            
        ns_degrees = np.zeros((len(ns_nodes), 1), dtype=np.float32)
        for d_dst in domain_has_ns_dst: ns_degrees[d_dst, 0] += 1
        if len(ns_nodes) > 0: g.nodes['nameserver'].data['feat'] = torch.tensor(ns_degrees, dtype=torch.float32)
            
        self.dgl_graph = g
        
        # Diagnostic: log edge counts per canonical edge type
        logger.info("DGL Heterograph Edge Counts:")
        for etype in g.canonical_etypes:
            logger.info("  %s: %d edges", etype, g.num_edges(etype))
        
        return g

    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Calculates and returns statistics about the NetworkX graph.
        
        Returns:
            Dictionary containing node and edge counts, and graph density.
        """
        num_domain = sum(1 for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'domain')
        num_ip = sum(1 for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'ip')
        num_ns = sum(1 for n, d in self.graph.nodes(data=True) if d.get('node_type') == 'nameserver')
        
        num_has_ip = sum(1 for u, v, d in self.graph.edges(data=True) if d.get('type') == 'has_ip')
        num_has_ns = sum(1 for u, v, d in self.graph.edges(data=True) if d.get('type') == 'has_ns')
        
        density = nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0.0
        
        return {
            'num_domain_nodes': num_domain,
            'num_ip_nodes': num_ip,
            'num_ns_nodes': num_ns,
            'num_has_ip_edges': num_has_ip,
            'num_has_ns_edges': num_has_ns,
            'density': density
        }
        
    def to_json(self, max_nodes: int = 200) -> Dict[str, Any]:
        """
        Converts a subgraph to JSON format for web dashboard visualization.
        
        Args:
            max_nodes: Maximum number of nodes to include.
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists.
        """
        if self.graph.number_of_nodes() > max_nodes:
            # Simple heuristic: take max_nodes from graph
            nodes = list(self.graph.nodes())[:max_nodes]
            subgraph = self.graph.subgraph(nodes)
        else:
            subgraph = self.graph
            
        result: Dict[str, Any] = {'nodes': [], 'edges': []}
        
        for n, data in subgraph.nodes(data=True):
            node_type = data.get('node_type', 'unknown')
            node_info = {
                'id': n,
                'type': node_type
            }
            if node_type == 'domain':
                node_info['label'] = data.get('label', 0)
                node_info['name'] = data.get('domain', n)
            elif node_type == 'ip':
                node_info['name'] = data.get('ip_address', n)
            elif node_type == 'nameserver':
                node_info['name'] = data.get('nameserver', n)
                
            result['nodes'].append(node_info)
            
        for u, v, data in subgraph.edges(data=True):
            result['edges'].append({
                'source': u,
                'target': v,
                'type': data.get('type', 'unknown')
            })
            
        return result

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    builder = DomainGraphBuilder()
    
    # Mock data
    domains_df = pd.DataFrame({
        'domain': ['example.com', 'phishing.com', 'test.org'],
        'label': [0, 1, 0]
    })
    
    dns_df = pd.DataFrame({
        'domain': ['example.com', 'phishing.com', 'test.org'],
        'ip_addresses': ['["192.168.1.1"]', '["192.168.1.1", "10.0.0.1"]', '[]'],
        'nameservers': ['["ns1.example.com"]', '["ns1.bad.com"]', '["ns1.test.org"]'],
        'dns_status': ['success', 'success', 'success']
    })
    
    features_df = pd.DataFrame({
        'domain': ['example.com', 'phishing.com', 'test.org'],
        'length': [11, 12, 8],
        'entropy': [3.5, 4.1, 2.8]
    })
    
    # Build graph
    G = builder.build_graph(domains_df, dns_df, features_df)
    
    print("Graph JSON snippet:")
    print(json.dumps(builder.to_json(max_nodes=5), indent=2))
    
    if DGL_AVAILABLE:
        dgl_g = builder.to_dgl_graph(['length', 'entropy'])
        print("DGL Heterograph:")
        print(dgl_g)
    else:
        print("DGL not available. Skipping DGL test.")
