"""
Analyzer for node health.
"""

from config.settings import THRESHOLDS, NODE_ERROR_TYPES


def check_node_errors(metrics, events):
    """
    Check for node-level errors based on metrics and events.
    
    Args:
        metrics (dict): Node metrics
        events (list): Node-related events
        
    Returns:
        list: List of detected errors
    """
    errors = []
    
    # Check CPU Pressure
    cpu_usage = metrics.get("node_cpu_usage")
    if cpu_usage is not None and cpu_usage > THRESHOLDS["node"]["cpu_usage"]:
        errors.append("CPU Pressure")
    
    # Check Memory Pressure
    memory_usage = metrics.get("node_memory_usage")
    if memory_usage is not None and memory_usage > THRESHOLDS["node"]["memory_usage"]:
        errors.append("Memory Pressure")
    
    # Check Disk Pressure
    disk_usage = metrics.get("node_disk_usage")
    if disk_usage is not None and disk_usage > THRESHOLDS["node"]["disk_usage"]:
        errors.append("Disk Pressure")
    
    # Check Disk Pressure from metrics
    if metrics.get("node_disk_pressure", 0) == 1:
        errors.append("Disk Pressure")
    
    # Check for issues in events
    for event in events:
        message = "".join(event.message) if event.message else ""
        
        if "MemoryPressure" in message:
            errors.append("Memory Pressure")
        if "DiskPressure" in message:
            errors.append("Disk Pressure")
        if "NetworkUnavailable" in message:
            errors.append("Network Unavailable")
        if "NodeNotReady" in message:
            errors.append("Node Not Ready")
        if "PIDPressure" in message:
            errors.append("PID Pressure")
        if "Taint" in message or "node.kubernetes.io/unsche" in message:
            errors.append("Node Unschedulable")
    
    # Remove duplicates
    return list(set(errors))


def add_error_flags(node_metrics, errors):
    """
    Add binary flags for each possible error type.
    
    Args:
        node_metrics (dict): Node metrics
        errors (list): Detected errors
        
    Returns:
        dict: Updated metrics with error flags
    """
    metrics_with_flags = node_metrics.copy()
    
    for error_type in NODE_ERROR_TYPES:
        metrics_with_flags[error_type] = 1 if error_type in errors else 0
        
    return metrics_with_flags