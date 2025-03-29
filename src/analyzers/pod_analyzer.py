"""
Analyzer for pod health.
"""

from config.settings import THRESHOLDS, POD_ERROR_TYPES


def check_pod_errors(metrics, events):
    """
    Check for pod-level errors based on metrics and events.
    
    Args:
        metrics (dict): Pod metrics
        events (list): Pod-related events
        
    Returns:
        list: List of detected errors
    """
    errors = []
    
    # CPU Throttling
    cpu_throttle = metrics.get("cpu_throttling", 0)
    if cpu_throttle is not None and cpu_throttle > THRESHOLDS["pod"]["cpu_throttle"]:
        errors.append("CPU Throttling")
    
    # Check CPU usage
    cpu_usage = metrics.get("cpu_usage")
    if cpu_usage is not None and cpu_usage > THRESHOLDS["pod"]["cpu_usage"]:
        errors.append("High CPU Usage")
    
    # Check for issues in events
    for event in events:
        message = "".join(event.message) if event.message else ""
        
        if "OOMKilled" in message:
            errors.append("OOMKilled (Out of Memory)")
        if "Back-off" in message:
            errors.append("CrashLoopBackOff")
        if "ContainerCreating" in message or "Back-off pulling image" in message:
            errors.append("ContainerNotReady")
        if "FailedScheduling" in message:
            errors.append("PodUnschedulable")
        if "MemoryPressure" in message or "DiskPressure" in message:
            errors.append("NodePressure")
        if "ErrImagePull" in message or "ImagePullBackOff" in message:
            errors.append("ImagePullFailure")
    
    # Remove duplicates
    return list(set(errors))


def add_error_flags(pod_metrics, errors):
    """
    Add binary flags for each possible error type.
    
    Args:
        pod_metrics (dict): Pod metrics
        errors (list): Detected errors
        
    Returns:
        dict: Updated metrics with error flags
    """
    metrics_with_flags = pod_metrics.copy()
    
    for error_type in POD_ERROR_TYPES:
        metrics_with_flags[error_type] = 1 if error_type in errors else 0
        
    return metrics_with_flags