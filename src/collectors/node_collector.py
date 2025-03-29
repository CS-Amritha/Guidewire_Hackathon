"""
Collector for node metrics.
"""

from core.prometheus import get_metric_value
from config.settings import NODE_QUERIES


def collect_node_metrics(node_name):
    """
    Collect metrics for a specific node.
    
    Args:
        node_name (str): Name of the node
        
    Returns:
        dict: Dictionary of node metrics
    """
    node_metrics = { "node_name": node_name}
    
    for metric_name, query_template in NODE_QUERIES.items():
        query = query_template.replace("{node}", node_name)
        node_metrics[metric_name] = get_metric_value(query)
        
    return node_metrics


def collect_all_nodes_metrics(nodes):
    """
    Collect metrics for all nodes.
    
    Args:
        nodes (list): List of node names
        
    Returns:
        dict: Dictionary mapping node names to their metrics
    """
    node_data = {}
    
    for node in nodes:
        node_data[node] = collect_node_metrics(node)
        
    return node_data