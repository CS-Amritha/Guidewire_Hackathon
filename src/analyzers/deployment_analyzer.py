"""
Analyzer for deployment health.
"""

from config.settings import DEPLOYMENT_ERROR_TYPES


def check_deployment_errors(metrics, events):
    """
    Check for deployment-level errors based on metrics and events.
    
    Args:
        metrics (dict): Deployment metrics
        events (list): Deployment-related events
        
    Returns:
        list: List of detected errors
    """
    errors = []
    
    # Replica Mismatch (desired vs available replicas)
    desired_replicas = metrics.get("deployment_replicas", 0)
    available_replicas = metrics.get("deployment_available_replicas", 0)
    
    if desired_replicas is not None and available_replicas is not None:
        if desired_replicas != available_replicas:
            errors.append("Replica Mismatch")
    
    # Unavailable Pods (No ready pods available)
    if available_replicas is not None and available_replicas == 0:
        errors.append("Unavailable Pods")
    
    # Check for issues in events
    for event in events:
        message = "".join(event.message) if event.message else ""
        
        if "ErrImagePull" in message or "ImagePullBackOff" in message:
            errors.append("ImagePullFailure")
        if "Back-off" in message:
            errors.append("CrashLoopBackOff")
        if "FailedScheduling" in message:
            errors.append("FailedScheduling")
        if "QuotaExceeded" in message:
            errors.append("QuotaExceeded")
        if "ProgressDeadlineExceeded" in message:
            errors.append("ProgressDeadlineExceeded")
    
    # Remove duplicates
    return list(set(errors))


def add_error_flags(deployment_metrics, errors):
    """
    Add binary flags for each possible error type.
    
    Args:
        deployment_metrics (dict): Deployment metrics
        errors (list): Detected errors
        
    Returns:
        dict: Updated metrics with error flags
    """
    metrics_with_flags = deployment_metrics.copy()
    
    for error_type in DEPLOYMENT_ERROR_TYPES:
        metrics_with_flags[f"deployment {error_type}"] = 1 if error_type in errors else 0
        
    return metrics_with_flags