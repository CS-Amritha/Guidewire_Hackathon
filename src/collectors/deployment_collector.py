"""
Collector for deployment metrics.
"""

from core.prometheus import get_metric_value
from config.settings import DEPLOYMENT_QUERIES


def collect_deployment_metrics(deployment_name, namespace):
    """
    Collect metrics for a specific deployment.
    
    Args:
        deployment_name (str): Name of the deployment
        namespace (str): Namespace of the deployment
        
    Returns:
        dict: Dictionary of deployment metrics
    """
    deployment_metrics = {
        "namespace": namespace,
        "deployment": deployment_name
    }
    
    for metric_name, query_template in DEPLOYMENT_QUERIES.items():
        query = query_template.replace("{deployment}", deployment_name)
        deployment_metrics[metric_name] = get_metric_value(query)
        
    return deployment_metrics


def collect_all_deployments_metrics(deployments):
    """
    Collect metrics for all deployments.
    
    Args:
        deployments (list): List of tuples (namespace, deployment_name)
        
    Returns:
        dict: Dictionary mapping deployment identifiers to their metrics
    """
    deployment_data = {}
    
    for namespace, deployment_name in deployments:
        deployment_key = f"{namespace}/{deployment_name}"
        deployment_data[deployment_key] = collect_deployment_metrics(deployment_name, namespace)
        
    return deployment_data