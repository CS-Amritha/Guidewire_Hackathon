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
            pod_metrics = collect_all_pods_metrics(pods)
            node_metrics = collect_all_nodes_metrics(nodes)
            deployment_metrics = collect_all_deployments_metrics(deployments)
            
            # Combine pod data
            combined_data_pods = []
            
            for pod_key, pod_metric in pod_metrics.items():
                namespace, pod_name = pod_key.split("/", 1)
                
                # Combine metrics for pod
                combined_metric = {
                    "timestamp": timestamp,
                    **pod_metric
                }
                
                # Check pod errors and add flags
                pod_events = filter_events_for_pod(new_events, namespace, pod_name)
                pod_errors = check_pod_errors(pod_metric, pod_events)
                combined_metric = add_pod_error_flags(combined_metric, pod_errors)
                
                combined_data_pods.append(combined_metric)
            
            # Combine node data
            combined_data_nodes = [{"timestamp": timestamp,  "node_name": node_name, **node_metrics[node_name]} for node_name in node_metrics]
            
            # Combine deployment data
            combined_data_deployments = [{"timestamp": timestamp, "node_name": deployment_metrics[deployment_key].get("node_name"), **deployment_metrics[deployment_key]} for deployment_key in deployment_metrics]
            
            # Save pod metrics to CSV (append mode)
            csv_pod_path = exporter.save_to_csv(combined_data_pods, filename="k8s_pod_metrics.csv")
            print(f"Pod metrics saved to {csv_pod_path} at {timestamp}")
            
            # Save node metrics to CSV (append mode)
            csv_node_path = exporter.save_to_csv(combined_data_nodes, filename="k8s_node_metrics.csv")
            print(f"Node metrics saved to {csv_node_path} at {timestamp}")
            
            # Save deployment metrics to CSV (append mode)
            csv_deployment_path = exporter.save_to_csv(combined_data_deployments, filename="k8s_deployment_metrics.csv")
            print(f"Deployment metrics saved to {csv_deployment_path} at {timestamp}\n")
            
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
