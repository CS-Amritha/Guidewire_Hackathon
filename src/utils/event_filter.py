"""
Utility functions for filtering Kubernetes events.
"""

# Store seen event UIDs to track new events
seen_event_uids = set()


def get_new_events(all_events):
    """
    Filter out events that have been seen before.
    
    Args:
        all_events (list): List of all current events
        
    Returns:
        list: List of new events not seen before
    """
    global seen_event_uids
    new_events = []
    
    for event in all_events:
        if event.metadata.uid not in seen_event_uids:
            seen_event_uids.add(event.metadata.uid)
            new_events.append(event)
            
    return new_events


def filter_events_for_node(events, node_name):
    """
    Filter events related to a specific node.
    
    Args:
        events (list): List of events
        node_name (str): Name of the node
        
    Returns:
        list: Filtered list of events related to the node
    """
    node_related_events = []
    for event in events:
        obj = event.involved_object
        if obj.kind == "Node" and obj.name == node_name:
            node_related_events.append(event)
    return node_related_events


def filter_events_for_pod(events, namespace, pod_name):
    """
    Filter events related to a specific pod.
    
    Args:
        events (list): List of events
        namespace (str): Namespace of the pod
        pod_name (str): Name of the pod
        
    Returns:
        list: Filtered list of events related to the pod
    """
    pod_related_events = []
    for event in events:
        obj = event.involved_object
        if (obj.kind == "Pod" and
            obj.name == pod_name and
            obj.namespace == namespace):
            pod_related_events.append(event)
    return pod_related_events


def filter_events_for_deployment(events, namespace, deployment_name):
    """
    Filter events related to a specific deployment.
    
    Args:
        events (list): List of events
        namespace (str): Namespace of the deployment
        deployment_name (str): Name of the deployment
        
    Returns:
        list: Filtered list of events related to the deployment
    """
    deployment_related_events = []
    for event in events:
        obj = event.involved_object
        if (obj.kind == "Deployment" and
            obj.name == deployment_name and
            obj.namespace == namespace):
            deployment_related_events.append(event)
    return deployment_related_events