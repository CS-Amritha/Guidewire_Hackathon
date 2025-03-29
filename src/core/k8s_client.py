"""
Kubernetes client for interacting with the cluster.
"""

from kubernetes import client, config
from config.settings import K8S_CONTEXT


def initialize_k8s_client():
    """Initialize the Kubernetes client with the configured context."""
    try:
        config.load_kube_config(context=K8S_CONTEXT)
        return True
    except Exception as e:
        print(f"Error initializing Kubernetes client: {e}")
        # Fallback to default context
        try:
            config.load_kube_config()
            return True
        except Exception as e:
            print(f"Error loading default Kubernetes config: {e}")
            return False


def get_k8s_pods():
    """
    Get all pods in the cluster.
    
    Returns:
        list: List of tuples containing (namespace, pod_name, node_name)
    """
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        return [(pod.metadata.namespace, pod.metadata.name, pod.spec.node_name) 
                for pod in pods.items]
    except Exception as e:
        print(f"Error getting pods: {e}")
        return []


def get_k8s_nodes():
    """
    Get all nodes in the cluster.
    
    Returns:
        list: List of node names
    """
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node(watch=False)
        return [node.metadata.name for node in nodes.items]
    except Exception as e:
        print(f"Error getting nodes: {e}")
        return []


def get_k8s_deployments():
    """
    Get all deployments in the cluster.
    
    Returns:
        list: List of tuples containing (namespace, deployment_name)
    """
    try:
        v1 = client.AppsV1Api()
        deployments = v1.list_deployment_for_all_namespaces(watch=False)
        return [(deployment.metadata.namespace, deployment.metadata.name) 
                for deployment in deployments.items]
    except Exception as e:
        print(f"Error getting deployments: {e}")
        return []


def get_k8s_events():
    """
    Get all events in the cluster.
    
    Returns:
        list: List of event objects
    """
    try:
        v1 = client.CoreV1Api()
        events = v1.list_event_for_all_namespaces(watch=False)
        return events.items
    except Exception as e:
        print(f"Error getting events: {e}")
        return []