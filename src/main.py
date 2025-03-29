"""
Main application entry point for Kubernetes monitoring.
"""

import time
import pandas as pd
from datetime import datetime

# Core components
from core.k8s_client import (
    initialize_k8s_client, get_k8s_pods, get_k8s_nodes, 
    get_k8s_deployments, get_k8s_events
)

# Utils
from utils.event_filter import (
    get_new_events, filter_events_for_node, filter_events_for_pod,
    filter_events_for_deployment
)

# Collectors
from collectors.node_collector import collect_all_nodes_metrics
from collectors.pod_collector import collect_all_pods_metrics
from collectors.deployment_collector import collect_all_deployments_metrics

# Analyzers
from analyzers.node_analyzer import check_node_errors, add_error_flags as add_node_error_flags
from analyzers.pod_analyzer import check_pod_errors, add_error_flags as add_pod_error_flags
from analyzers.deployment_analyzer import check_deployment_errors, add_error_flags as add_deployment_error_flags

# Storage
from storage.csv_exporter import CSVExporter

# Settings
from config.settings import POLLING_INTERVAL


def main():
    """Main application function."""
    print("Starting Kubernetes monitoring...")
    
    # Initialize Kubernetes client
    if not initialize_k8s_client():
        print("Failed to initialize Kubernetes client. Exiting.")
        return
    
    # Initialize CSV exporter
    exporter = CSVExporter()
    
    # Main monitoring loop
    while True:
        try:
            timestamp = pd.Timestamp.now()
            print(f"Collecting metrics at {timestamp}...")
            
            # Collect Kubernetes resources
            pods = get_k8s_pods()
            nodes = get_k8s_nodes()
            deployments = get_k8s_deployments()
            all_events = get_k8s_events()
            new_events = get_new_events(all_events)
            
            # Collect metrics for all resources
            node_metrics = collect_all_nodes_metrics(nodes)
            pod_metrics = collect_all_pods_metrics(pods)
            deployment_metrics = collect_all_deployments_metrics(deployments)
            
            # Process node metrics and add error flags
            for node_name, metrics in node_metrics.items():
                node_events = filter_events_for_node(new_events, node_name)
                errors = check_node_errors(metrics, node_events)
                node_metrics[node_name] = add_node_error_flags(metrics, errors)
            
            # Process deployment metrics and add error flags
            for deployment_key, metrics in deployment_metrics.items():
                namespace, deployment_name = deployment_key.split("/", 1)
                deployment_events = filter_events_for_deployment(new_events, namespace, deployment_name)
                errors = check_deployment_errors(metrics, deployment_events)
                deployment_metrics[deployment_key] = add_deployment_error_flags(metrics, errors)
            
            # Combine metrics for pods with their respective node and deployment
            combined_data = []
            
            for pod_key, pod_metric in pod_metrics.items():
                namespace, pod_name = pod_key.split("/", 1)
                node_name = pod_metric["node"]
                
                # Get related node metrics
                node_metric = node_metrics.get(node_name, {})
                
                # Find related deployment
                deployment_key = next(
                    (key for key in deployment_metrics
                    if key.startswith(f"{namespace}/") and pod_name.startswith(key.split("/", 1)[1])),
                    None
                )
                
                # Combine metrics
                combined_metric = {
                    "timestamp": timestamp,
                    **pod_metric
                }
                
                # Add node metrics
                combined_metric.update(node_metric)
                
                # Add deployment metrics or defaults
                if deployment_key:
                    combined_metric.update(deployment_metrics[deployment_key])
                    combined_metric["deployment"] = deployment_key
                else:
                    # Add default deployment metrics
                    combined_metric["deployment"] = "None"
                    for key in deployment_metrics.values() and next(iter(deployment_metrics.values()), {}):
                        combined_metric[key] = 0
                
                # Check pod errors and add flags
                pod_events = filter_events_for_pod(new_events, namespace, pod_name)
                pod_errors = check_pod_errors(pod_metric, pod_events)
                combined_metric = add_pod_error_flags(combined_metric, pod_errors)
                
                combined_data.append(combined_metric)
            
            # Save combined metrics to CSV
            csv_path = exporter.save_to_csv(combined_data)
            print(f"Metrics saved to {csv_path} at {timestamp}")
            
            # Wait for next polling interval
            time.sleep(POLLING_INTERVAL)
            
        except KeyboardInterrupt:
            print("Monitoring stopped by user.")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()