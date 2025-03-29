"""
Collector for pod metrics.
"""

from core.prometheus import get_metric_value
from config.settings import POD_QUERIES


def collect_pod_metrics(pod_name, namespace, node_name):
    """
    Collect metrics for a specific pod.
    
    Args:
        pod_name (str): Name of the pod
        namespace (str): Namespace of the pod
        node_name (str): Node where the pod is running
        
    Returns:
        dict: Dictionary of pod metrics
    """
    pod_metrics = {
        "namespace": namespace,
        "pod": pod_name,
        "node": node_name
    }
    
    for metric_name, query_template in POD_QUERIES.items():
        query = query_template.replace("{pod}", pod_name)
        pod_metrics[metric_name] = get_metric_value(query)
        
    return pod_metrics


def collect_all_pods_metrics(pods):
    """
    Collect metrics for all pods.
    
    Args:
        pods (list): List of tuples (namespace, pod_name, node_name)
        
    Returns:
        dict: Dictionary mapping pod identifiers to their metrics
    """
    pod_data = {}
    
    for namespace, pod_name, node_name in pods:
        pod_key = f"{namespace}/{pod_name}"
        pod_data[pod_key] = collect_pod_metrics(pod_name, namespace, node_name)
        
    return pod_data