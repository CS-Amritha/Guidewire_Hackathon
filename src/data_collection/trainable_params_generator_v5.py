import requests
import pandas as pd
import time
import subprocess
import json
from kubernetes import client, config

config.load_kube_config(context="kind-my-cluster")
prometheus_url = "http://localhost:9090"
v1 = client.CoreV1Api()


def run_promql_query(query):
    response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": query})
    response.raise_for_status()
    return response.json().get("data", {}).get("result", [])

seen_event_uids = set()
def fetch_new_k8s_events():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    try:
        all_events = v1.list_event_for_all_namespaces(watch=False).items
        new_events = []
        for event in all_events:
            if event.metadata.uid not in seen_event_uids:
                seen_event_uids.add(event.metadata.uid)
                new_events.append(event)
        return new_events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []


def get_k8s_pods():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    return [(pod.metadata.namespace, pod.metadata.name, pod.spec.node_name) for pod in pods.items]

def get_k8s_nodes():
    v1 = client.CoreV1Api()
    nodes = v1.list_node(watch=False)
    return [node.metadata.name for node in nodes.items]

def get_k8s_deployments():
    v1 = client.AppsV1Api()
    deployments = v1.list_deployment_for_all_namespaces(watch=False)
    return [(deployment.metadata.namespace, deployment.metadata.name) for deployment in deployments.items]

def check_node_error(metrics, events):
   
    errors = []

    # CPU Pressure
    cpu_usage_threshold = 80  # Example threshold in percentage
    cpu_usage = metrics.get("node_cpu_usage")
    if cpu_usage is not None and cpu_usage > cpu_usage_threshold:
        errors.append("CPU Pressure")

    # Memory Pressure
    memory_usage_threshold = 90  # Threshold in percentage
    memory_usage = metrics.get("node_memory_usage")
    if memory_usage is not None and memory_usage > memory_usage_threshold:
        errors.append("Memory Pressure")
    if "MemoryPressure" in events:
        errors.append("Memory Pressure")

    # Disk Pressure
    disk_usage_threshold = 90
    if metrics.get("node_disk_pressure", 0) == 1:
        errors.append("Disk Pressure")
    if "DiskPressure" in events:
        errors.append("Disk Pressure")
    disk_usage = metrics.get("node_disk_usage")
    if disk_usage is not None and disk_usage > disk_usage_threshold:
        errors.append("Disk Pressure")

    # Network Unavailable
    if "NetworkUnavailable" in events:
        errors.append("Network Unavailable")

    # Node Not Ready
    if "NodeNotReady" in events:
        errors.append("Node Not Ready")

    # PID Pressure
    if "PIDPressure" in events:
        errors.append("PID Pressure")

    # Node Unschedulable (Taints or Conditions)
    if "Taint" in events or "node.kubernetes.io/unschedulable" in events:
        errors.append("Node Unschedulable")

    return errors

def check_pod_error(metrics, events):

    errors = []


    # CPU Throttling
    cpu_throttle_threshold = 0.75  # Example threshold in percentage
    if metrics.get("cpu_throttling", 0) > cpu_throttle_threshold:
        errors.append("CPU Throttling")

    # Check CPU usage
    cpu_usage_threshold = 80
    cpu_usage = metrics.get("cpu_usage")
    if cpu_usage is not None and cpu_usage > cpu_usage_threshold:
        errors.append("High CPU Usage")
  

    # OOMKilled (Out of Memory)
    if "OOMKilled" in events:
        errors.append("Out of Memory (OOMKilled)")

    # CrashLoopBackOff
    if "CrashLoopBackOff" in events:
        errors.append("CrashLoopBackOff")

    # ContainerNotReady
    if "ContainerCreating" in events or "Back-off pulling image" in events:
        errors.append("ContainerNotReady")

    # PodUnschedulable
    if "FailedScheduling" in events:
        errors.append("PodUnschedulable")

    # Node Pressure
    if "MemoryPressure" in events or "DiskPressure" in events:
        errors.append("NodePressure")

    # Image Pull Failure
    if "ErrImagePull" in events or "ImagePullBackOff" in events:
        errors.append("ImagePullFailure")

    return errors

def check_deployment_error(metrics, events):

    errors = []

    # Replica Mismatch (desired vs available replicas)
    desired_replicas = metrics.get("deployment_replicas", 0)
    available_replicas = metrics.get("deployment_available_replicas", 0)
    if desired_replicas != available_replicas:
        errors.append("Replica Mismatch")

    # Unavailable Pods (No ready pods available)
    if available_replicas == 0:
        errors.append("Unavailable Pods")

    # Image Pull Failure
    if "ErrImagePull" in events or "ImagePullBackOff" in events:
        errors.append("ImagePullFailure")

    # CrashLoopBackOff
    if "CrashLoopBackOff" in events:
        errors.append("CrashLoopBackOff")

    # Failed Scheduling (Pods cannot be scheduled)
    if "FailedScheduling" in events:
        errors.append("FailedScheduling")

    # Resource Quota Exceeded (Cannot deploy more pods)
    if "QuotaExceeded" in events:
        errors.append("QuotaExceeded")

    # Progress Deadline Exceeded (Deployment update taking too long)
    if "ProgressDeadlineExceeded" in events:
        errors.append("ProgressDeadlineExceeded")

    return errors

def filter_events_for_node(events, node_name):
    node_related_events = []
    for event in events:
        obj = event.involved_object
        if obj.kind == "Node" and obj.name == node_name:
            node_related_events.append(event)
    return node_related_events

def filter_events_for_deployment(events, namespace, deployment_name):
    deployment_related_events = []
    for event in events:
        obj = event.involved_object
        if (obj.kind == "Deployment" and
            obj.name == deployment_name and
            obj.namespace == namespace):
            deployment_related_events.append(event)
    return deployment_related_events
def filter_events_for_pod(events, namespace, pod_name):
    pod_related_events = []
    for event in events:
        obj = event.involved_object
        if (obj.kind == "Pod" and
            obj.name == pod_name and
            obj.namespace == namespace):
            pod_related_events.append(event)
    return pod_related_events




def main():
    prom_url = "http://localhost:9090"

    # PromQL queries
    pod_queries = {
       
        # CPU Metrics
        "cpu_usage": '((sum(rate(container_cpu_usage_seconds_total{pod="{pod}"}[5m])) or vector(0)) / (sum(kube_pod_container_resource_limits{pod="{pod}", resource="cpu"}) or sum(kube_node_status_allocatable{resource="cpu"}))) * 100',
        "cpu_limit": 'sum(kube_pod_container_resource_limits{pod="{pod}", resource="cpu"}) or vector(0)',
        "cpu_request": 'sum(kube_pod_container_resource_requests{pod="{pod}", resource="cpu"}) or vector(0)',
        "cpu_throttling": 'sum(rate(container_cpu_cfs_throttled_seconds_total{pod="{pod}"}[5m])) OR vector(0)',


        # Memory Metrics
        "memory_usage": 'sum(container_memory_usage_bytes{pod="{pod}"})',
        "memory_limit": 'sum(kube_pod_container_resource_limits{pod="{pod}", resource="memory"}) or vector(0)',
        "memory_request": 'sum(kube_pod_container_resource_requests{pod="{pod}", resource="memory"}) or vector(0)',
        "memory_rss": 'sum(container_memory_rss{pod="{pod}"})',

        # Network Metrics
        "network_receive_bytes": 'sum(rate(container_network_receive_bytes_total{pod="{pod}"}[5m]))',
        "network_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{pod="{pod}"}[5m]))',
        "network_errors": 'sum(rate(container_network_receive_errors_total{pod="{pod}"}[5m]))',

        # Pod Status & Restarts
        "restarts": 'sum(kube_pod_container_status_restarts_total{pod="{pod}"})',
        "oom_killed": 'sum(kube_pod_container_status_last_terminated_reason{pod="{pod}", reason="OOMKilled"}) or vector(0)',
        "pod_ready": 'max(kube_pod_status_ready{pod="{pod}"})',
        "pod_phase": 'kube_pod_status_phase{pod="{pod}"}',

        # Disk and I/O Metrics
        "disk_read_bytes": 'sum(rate(container_fs_reads_bytes_total{pod="{pod}"}[5m]))',
        "disk_write_bytes": 'sum(rate(container_fs_writes_bytes_total{pod="{pod}"}[5m]))',
        "disk_io_errors": 'sum(rate(container_fs_errors_total{pod="{pod}"}[5m])) or vector(0)',

        # Scheduling & Pending Metrics
        "pod_scheduled": 'max(kube_pod_status_scheduled{pod="{pod}"})',
        "pod_pending": 'max(kube_pod_status_phase{pod="{pod}", phase="Pending"})',
        "pod_unschedulable": 'max(kube_pod_status_unschedulable{pod="{pod}"}) or vector(0)',

        # Container State Metrics
        "container_running": 'max(kube_pod_container_status_running{pod="{pod}"})',
        "container_terminated": 'max(kube_pod_container_status_terminated{pod="{pod}"})',
        "container_waiting": 'max(kube_pod_container_status_waiting{pod="{pod}"})',
        
        # Pod Uptime and Lifecycle
        "pod_uptime_seconds": 'time() - kube_pod_start_time{pod="{pod}"}',

        # Resource Utilization Ratios
        "cpu_utilization_ratio": '(sum(rate(container_cpu_usage_seconds_total{pod="{pod}"}[5m])) or vector(0))/ (sum(kube_pod_container_resource_limits{pod="{pod}", resource="cpu"}) or vector(1))',
        "memory_utilization_ratio": '(sum(container_memory_usage_bytes{pod="{pod}"}) or vector(0)) / (sum(kube_pod_container_resource_limits{pod="{pod}" , resource="memory"}) or vector(1))',
    }
    node_queries = {
        # CPU Metrics
        "node_cpu_usage": '(sum(rate(node_cpu_seconds_total{mode!="idle", node="{node}"}[5m])) or vector(0)) * 100',
        "node_cpu_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="cpu"}) or vector(0)',
        "node_cpu_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="cpu"}) or vector(0)',
        "node_cpu_utilization_ratio": 'sum(rate(node_cpu_seconds_total{node="{node}", mode!="idle"}[5m])) / sum(kube_node_status_allocatable{node="{node}", resource="cpu"})',
        

        # Memory Metrics
        "node_memory_usage": '((1 - (sum(node_memory_MemAvailable_bytes) or vector(0)) / (sum(node_memory_MemTotal_bytes) or vector(1))) * 100)',
        "node_memory_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="memory"}) or vector(0)',
        "node_memory_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="memory"}) or vector(0)',
        "node_memory_utilization_ratio": '1 - (node_memory_MemAvailable_bytes{node="{node}"} / node_memory_MemTotal_bytes{node="{node}"})',
        "node_memory_pressure": 'max(kube_node_status_condition{node="{node}", condition="MemoryPressure", status="true"}) or vector(0)',

        # Disk Metrics
        "node_disk_read_bytes": 'sum(rate(node_disk_read_bytes_total{instance=~"{node}.*"}[5m])) or vector(0)',
        #"node_disk_usage": '100 * (1 - ((sum(node_filesystem_avail_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(0)) / (sum(node_filesystem_size_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(1))))',
        "node_disk_usage":'100 * (1 - ((sum(node_filesystem_avail_bytes{mountpoint="/"}) or vector(0)) / (sum(node_filesystem_size_bytes{mountpoint="/"}) or vector(1))))',

       #"node_disk_write_bytes": 'sum(rate(node_disk_written_bytes_total{instance=~"{node}.*"}[5m])) or vector(0)',
        "node_disk_write_bytes":'sum(rate(node_disk_written_bytes_total[5m])) or vector(0)',
        "node_disk_pressure": 'max(kube_node_status_condition{node="{node}", condition="DiskPressure", status="true"}) or vector(0)',
        "node_disk_capacity": 'sum(node_filesystem_size_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(0)',
        #"node_disk_available": 'sum(node_filesystem_avail_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(0)',
        "node_disk_utilization_ratio": '1 - ((sum(node_filesystem_avail_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(0)) / (sum(node_filesystem_size_bytes{instance=~"{node}.*", mountpoint="/"}) or vector(1)))',

        # Network Metrics
        "node_network_receive_bytes": 'sum(rate(node_network_receive_bytes_total{instance=~"{node}.*"}[5m])) or vector(0)',
        "node_network_transmit_bytes": 'sum(rate(node_network_transmit_bytes_total{instance=~"{node}.*"}[5m])) or vector(0)',
        "node_network_errors": 'sum(rate(node_network_receive_errs_total{instance=~"{node}.*"}[5m]) or vector(0)) + sum(rate(node_network_transmit_errs_total{instance=~"{node}.*"}[5m]) or vector(0))',

        # Node Conditions & Status
        "node_ready": 'max(kube_node_status_condition{node="{node}", condition="Ready", status="true"}) or vector(0)',
        "node_unschedulable": 'max(kube_node_spec_unschedulable{node="{node}"}) or vector(0)',
        "node_out_of_disk": 'max(kube_node_status_condition{node="{node}", condition="OutOfDisk", status="true"}) or vector(0)',

        # Pod Scheduling Metrics
        "node_pods_running": 'count(kube_pod_info{node="{node}"}) or vector(0)',
        "node_pods_allocatable": 'sum(kube_node_status_allocatable_pods{node="{node}"}) or vector(0)',
        "node_pods_usage_ratio": '((count(kube_pod_info{node="{node}"}) or vector(0)) / (sum(kube_node_status_allocatable_pods{node="{node}"}) or vector(1)))',

        # Node Uptime and Kubelet Health
        "node_uptime_seconds": '(time() - (node_boot_time_seconds{node="{node}"} or vector(0)))',
        "node_kubelet_healthy": 'max(kube_node_status_condition{node="{node}", condition="Ready", status="true"}) or vector(0)',

        # I/O and Filesystem Errors
        "node_disk_io_errors": 'sum(rate(node_disk_io_time_seconds_total{instance=~"{node}.*"}[5m])) or vector(0)',
        "node_inode_utilization_ratio": '1 - ((sum(node_filesystem_files_free{instance=~"{node}.*", mountpoint="/"}) or vector(0)) / (sum(node_filesystem_files{instance=~"{node}.*", mountpoint="/"}) or vector(1)))',

        # Temperature and Hardware
        #"node_hardware_temperature": 'sum(node_hwmon_temp_celsius{instance=~"{node}.*"}) or vector(0)',

        # Node Pressure Conditions
        "node_pid_pressure": 'max(kube_node_status_condition{node="{node}", condition="PIDPressure", status="true"}) or vector(0)',
    }
    deployment_queries = {
        # Replica Metrics
        "deployment_replicas": 'sum(kube_deployment_spec_replicas{deployment="{deployment}"}) or vector(0)',
        "deployment_available_replicas": 'sum(kube_deployment_status_available_replicas{deployment="{deployment}"}) or vector(0)',
        "deployment_unavailable_replicas": 'sum(kube_deployment_status_replicas_unavailable{deployment="{deployment}"}) or vector(0)',
        "deployment_updated_replicas": 'sum(kube_deployment_status_updated_replicas{deployment="{deployment}"}) or vector(0)',
        "deployment_mismatch_replicas": 'sum(kube_deployment_status_replicas{deployment="{deployment}"}) or vector(0) - sum(kube_deployment_spec_replicas{deployment="{deployment}"})  or vector(0)',

        # CPU Metrics
        "deployment_cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{container!="", pod=~"{deployment}-.*"}[5m])) or vector(0)',
        "deployment_cpu_requests": 'sum(kube_pod_container_resource_requests_cpu_cores{pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_cpu_limits": 'sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_cpu_utilization_ratio": 'sum(rate(container_cpu_usage_seconds_total{container!="", pod=~"{deployment}-.*"}[5m])) / clamp_min(sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"}), 1) or vector(0)',

        # Memory Metrics
        "deployment_memory_usage": 'sum(container_memory_usage_bytes{container!="", pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_memory_requests": 'sum(kube_pod_container_resource_requests_memory_bytes{pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_memory_limits": 'sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_memory_utilization_ratio": 'sum(container_memory_usage_bytes{container!="", pod=~"{deployment}-.*"}) / clamp_min(sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"}), 1) or vector(0)',

        # Pod Health Metrics
        "deployment_pod_restarts": 'sum(increase(kube_pod_container_status_restarts_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',
        "deployment_pod_crashloop_backoff": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason="CrashLoopBackOff"}) or vector(0)',
        "deployment_pod_oom_killed": 'sum(kube_pod_container_status_terminated_reason{pod=~"{deployment}-.*", reason="OOMKilled"}) or vector(0)',
        "deployment_pod_pending": 'sum(kube_pod_status_phase{pod=~"{deployment}-.*", phase="Pending"}) or vector(0)',
        "deployment_pod_failed": 'sum(kube_pod_status_phase{pod=~"{deployment}-.*", phase="Failed"}) or vector(0)',
        "deployment_pod_evicted": 'sum(kube_pod_status_reason{pod=~"{deployment}-.*", reason="Evicted"}) or vector(0)',

        # Network Metrics
        "deployment_network_receive_bytes": 'sum(rate(container_network_receive_bytes_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',
        "deployment_network_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',
        "deployment_network_errors": 'sum(rate(container_network_receive_errors_total{pod=~"{deployment}-.*"}[5m]) + rate(container_network_transmit_errors_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',

        # Disk I/O Metrics
        "deployment_disk_read_bytes": 'sum(rate(container_fs_reads_bytes_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',
        "deployment_disk_write_bytes": 'sum(rate(container_fs_writes_bytes_total{pod=~"{deployment}-.*"}[5m])) or vector(0)',

        # Resource Pressure Conditions
        "deployment_memory_pressure": 'max(kube_node_status_condition{condition="MemoryPressure", status="true", node=~".*"}) or vector(0)',
        "deployment_disk_pressure": 'max(kube_node_status_condition{condition="DiskPressure", status="true", node=~".*"}) or vector(0)',
        "deployment_pid_pressure": 'max(kube_node_status_condition{condition="PIDPressure", status="true", node=~".*"}) or vector(0)',

        # Scheduling Issues
        "deployment_unschedulable_pods": 'sum(kube_pod_status_unschedulable{pod=~"{deployment}-.*"}) or vector(0)',
        "deployment_waiting_pods": 'sum(kube_pod_container_status_waiting{pod=~"{deployment}-.*"}) or vector(0)',

        # Age and Availability
        "deployment_age_seconds": 'max(time() - kube_deployment_created{deployment="{deployment}"}) or vector(0)',
        "deployment_unavailable_duration": 'sum(increase(kube_deployment_status_replicas_unavailable{deployment="{deployment}"}[5m])) or vector(0)',

        # Deployment Conditions
        "deployment_progressing": 'sum(kube_deployment_status_condition{deployment="{deployment}", condition="Progressing", status="true"}) > 0 or vector(0)',
        "deployment_available": 'sum(kube_deployment_status_condition{deployment="{deployment}", condition="Available", status="true"}) > 0 or vector(0)',
        "deployment_paused": 'max(kube_deployment_spec_paused{deployment="{deployment}"}) or vector(0)',

        # Crash and Errors
        "deployment_image_pull_error": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason=~"ImagePullBackOff|ErrImagePull"}) or vector(0)',
        "deployment_create_container_error": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason="CreateContainerConfigError"}) or vector(0)',
        "deployment_node_not_ready": 'sum(kube_pod_status_reason{pod=~"{deployment}-.*", reason="NodeNotReady"}) or vector(0)',
    }

    data = []
    while True:
        timestamp = pd.Timestamp.now()

        pods = get_k8s_pods()
        events = fetch_new_k8s_events()
        nodes = get_k8s_nodes()
        deployments = get_k8s_deployments()

        node_data = {}
        deployment_data = {}

        for namespace, deployment_name in deployments:

            deployment_metrics = {}

            for metric_name, query in deployment_queries.items():
                
                query = query.replace("{deployment}", deployment_name)

             
                results = run_promql_query(query)

               
                deployment_metrics[metric_name] = float(results[0]['value'][1]) if results else None

            
            deployment_events = filter_events_for_deployment(events, namespace, deployment_name)

            if deployment_events:
                print(f"Found {len(deployment_events)} new events for deployment {namespace}/{deployment_name}")
            else:
                print(f"No new events for deployment {namespace}/{deployment_name}")

            derrors = check_deployment_error(deployment_metrics, deployment_events)

            for i in ['Replica Mismatch', 'Unavailable Pods', 'ImagePullFailure', 'CrashLoopBackOff', 'FailedScheduling', 'QuotaExceeded', 'ProgressDeadlineExceeded']:
                deployment_metrics[i] = 1 if i in derrors else 0

            deployment_data[f"{namespace}/{deployment_name}"] = deployment_metrics


            
        for node in nodes:
            node_metrics = {}

            
            for metric_name, query in node_queries.items():
                query = query.replace("{node}", node)
                results = run_promql_query(query)
                node_metrics[metric_name] = float(results[0]['value'][1]) if results else None

            
            node_events = filter_events_for_node(events, node)

            if node_events:
                print(f"Found {len(node_events)} new events for node {node}")
            else:
                print(f"No new events for node {node}")

            nerrors = check_node_error(node_metrics, node_events)

            for i in ['CPU Pressure', 'Memory Pressure', 'Disk Pressure', 'Network Unavailable', 'Node Not Ready', 'PID Pressure', 'Node Unschedulable']:
                node_metrics[i] = 1 if i in nerrors else 0

            node_data[node] = node_metrics



        pod_data = {}

        for namespace, pod_name, node in pods:

            pod_metrics = {
                "timestamp": timestamp,
                "namespace": namespace,
                "pod": pod_name,
                "node": node
            }

            for metric_name, query in pod_queries.items():
                query = query.replace("{pod}", pod_name)

                results = run_promql_query(query)
                pod_metrics[metric_name] = float(results[0]['value'][1]) if results else None

            # 🎯 Filter events specific to this pod
            pod_events = filter_events_for_pod(events, namespace, pod_name)

            if pod_events:
                print(f"Found {len(pod_events)} new events for pod {namespace}/{pod_name}")
            else:
                print(f"No new events for pod {namespace}/{pod_name}")

            # 🔍 Run error checks on pod metrics + events
            perrors = check_node_error(pod_metrics, pod_events)

            for i in [
                "CPU Throttling", "High CPU Usage", "OOMKilled (Out of Memory)",
                "CrashLoopBackOff", "ContainerNotReady", "PodUnschedulable",
                "NodePressure", "ImagePullFailure"  # (typo: should be ImagePullFailure)
            ]:
                pod_metrics[i] = 1 if i in perrors else 0

            # Store pod metrics
            pod_data[f"{namespace}/{pod_name}"] = pod_metrics

            # Optional: Merge deployment & node data
            deployment_key = next(
                (key for key in deployment_data
                if key.startswith(f"{namespace}/") and pod_name.startswith(key.split("/", 1)[1])),
                None
            )

            node_metrics = node_data.get(node, {})
            combined_metrics = {**pod_metrics, **node_metrics}

            if deployment_key:
                combined_metrics.update(deployment_data[deployment_key])
                combined_metrics["deployment"] = deployment_key

            else:
                temp = {}
                for i in deployment_data:
                    for key in deployment_data[i]:
                        temp[key] = 0
                    break
                combined_metrics.update(temp)
                combined_metrics["deployment"] = "None"

            data.append(combined_metrics)


        df = pd.DataFrame(data)
        df.to_csv("k8s_pod_metrics.csv", index=False)
        print("Added data to csv at ", timestamp)

        time.sleep(5)


if __name__ == "__main__":
    main()

