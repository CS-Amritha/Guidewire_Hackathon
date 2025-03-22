import requests
import pandas as pd
import time
import subprocess
import json
from kubernetes import client, config
import sqlite3  # For SQLite database

# Load Kubernetes configuration
config.load_kube_config(context="kind-chaos-cluster")
prometheus_url = "http://localhost:9090"
v1 = client.CoreV1Api()

# Database setup
DATABASE_NAME = "k8s_metrics.db"

import sqlite3  # Add this import for SQLite

# Initialize the SQLite database
def initialize_db():
    """Initialize the SQLite database and create tables for pods, nodes, and deployments."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create the pods table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pods (
            timestamp TEXT,
            namespace TEXT,
            pod_name TEXT,
            node_name TEXT,
            cpu_usage REAL,
            cpu_limit REAL,
            cpu_request REAL,
            cpu_throttling REAL,
            memory_usage REAL,
            memory_limit REAL,
            memory_request REAL,
            memory_rss REAL,
            network_receive_bytes REAL,
            network_transmit_bytes REAL,
            network_errors REAL,
            restarts INTEGER,
            oom_killed INTEGER,
            pod_ready INTEGER,
            pod_phase TEXT,
            disk_read_bytes REAL,
            disk_write_bytes REAL,
            disk_io_errors REAL,
            pod_scheduled INTEGER,
            pod_pending INTEGER,
            pod_unschedulable INTEGER,
            container_running INTEGER,
            container_terminated INTEGER,
            container_waiting INTEGER,
            pod_uptime_seconds REAL,
            cpu_utilization_ratio REAL,
            memory_utilization_ratio REAL
        )
    ''')

    # Create the nodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            timestamp TEXT,
            node_name TEXT,
            node_cpu_usage REAL,
            node_cpu_capacity REAL,
            node_cpu_allocatable REAL,
            node_cpu_utilization_ratio REAL,
            node_memory_usage REAL,
            node_memory_capacity REAL,
            node_memory_allocatable REAL,
            node_memory_utilization_ratio REAL,
            node_memory_pressure INTEGER,
            node_disk_read_bytes REAL,
            node_disk_write_bytes REAL,
            node_disk_pressure INTEGER,
            node_disk_capacity REAL,
            node_disk_available REAL,
            node_disk_utilization_ratio REAL,
            node_network_receive_bytes REAL,
            node_network_transmit_bytes REAL,
            node_network_errors REAL,
            node_ready INTEGER,
            node_unschedulable INTEGER,
            node_out_of_disk INTEGER,
            node_pods_running INTEGER,
            node_pods_allocatable INTEGER,
            node_pods_usage_ratio REAL,
            node_uptime_seconds REAL,
            node_kubelet_healthy INTEGER,
            node_disk_io_errors REAL,
            node_inode_utilization_ratio REAL,
            node_hardware_temperature REAL,
            node_pid_pressure INTEGER
        )
    ''')

    # Create the deployments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            timestamp TEXT,
            namespace TEXT,
            deployment_name TEXT,
            deployment_replicas INTEGER,
            deployment_available_replicas INTEGER,
            deployment_unavailable_replicas INTEGER,
            deployment_updated_replicas INTEGER,
            deployment_mismatch_replicas INTEGER,
            deployment_cpu_usage REAL,
            deployment_cpu_requests REAL,
            deployment_cpu_limits REAL,
            deployment_cpu_utilization_ratio REAL,
            deployment_memory_usage REAL,
            deployment_memory_requests REAL,
            deployment_memory_limits REAL,
            deployment_memory_utilization_ratio REAL,
            deployment_pod_restarts INTEGER,
            deployment_pod_crashloop_backoff INTEGER,
            deployment_pod_oom_killed INTEGER,
            deployment_pod_terminated INTEGER,
            deployment_pod_pending INTEGER,
            deployment_pod_failed INTEGER,
            deployment_pod_evicted INTEGER,
            deployment_network_receive_bytes REAL,
            deployment_network_transmit_bytes REAL,
            deployment_network_errors REAL,
            deployment_disk_read_bytes REAL,
            deployment_disk_write_bytes REAL,
            deployment_memory_pressure INTEGER,
            deployment_disk_pressure INTEGER,
            deployment_pid_pressure INTEGER,
            deployment_unschedulable_pods INTEGER,
            deployment_waiting_pods INTEGER,
            deployment_backoff_limit_exceeded INTEGER,
            deployment_age_seconds REAL,
            deployment_unavailable_duration REAL,
            deployment_progressing INTEGER,
            deployment_available INTEGER,
            deployment_paused INTEGER,
            deployment_replica_set_mismatch INTEGER,
            deployment_rollout_in_progress INTEGER,
            deployment_image_pull_error INTEGER,
            deployment_create_container_error INTEGER,
            deployment_node_not_ready INTEGER,
            deployment_pod_unscheduled INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# Insert pod metrics into the database
def insert_pod_metrics(metrics):
    """Insert pod metrics into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pods (
            timestamp, namespace, pod_name, node_name, cpu_usage, cpu_limit, cpu_request, cpu_throttling,
            memory_usage, memory_limit, memory_request, memory_rss, network_receive_bytes, network_transmit_bytes,
            network_errors, restarts, oom_killed, pod_ready, pod_phase, disk_read_bytes, disk_write_bytes,
            disk_io_errors, pod_scheduled, pod_pending, pod_unschedulable, container_running, container_terminated,
            container_waiting, pod_uptime_seconds, cpu_utilization_ratio, memory_utilization_ratio
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metrics["timestamp"],
        metrics["namespace"],
        metrics["pod"],
        metrics["node"],
        metrics.get("cpu_usage", None),
        metrics.get("cpu_limit", None),
        metrics.get("cpu_request", None),
        metrics.get("cpu_throttling", None),
        metrics.get("memory_usage", None),
        metrics.get("memory_limit", None),
        metrics.get("memory_request", None),
        metrics.get("memory_rss", None),
        metrics.get("network_receive_bytes", None),
        metrics.get("network_transmit_bytes", None),
        metrics.get("network_errors", None),
        metrics.get("restarts", None),
        metrics.get("oom_killed", None),
        metrics.get("pod_ready", None),
        metrics.get("pod_phase", None),
        metrics.get("disk_read_bytes", None),
        metrics.get("disk_write_bytes", None),
        metrics.get("disk_io_errors", None),
        metrics.get("pod_scheduled", None),
        metrics.get("pod_pending", None),
        metrics.get("pod_unschedulable", None),
        metrics.get("container_running", None),
        metrics.get("container_terminated", None),
        metrics.get("container_waiting", None),
        metrics.get("pod_uptime_seconds", None),
        metrics.get("cpu_utilization_ratio", None),
        metrics.get("memory_utilization_ratio", None)
    ))
    conn.commit()
    conn.close()

# Insert node metrics into the database
def insert_node_metrics(metrics):
    """Insert node metrics into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nodes (
            timestamp, node_name, node_cpu_usage, node_cpu_capacity, node_cpu_allocatable,
            node_cpu_utilization_ratio, node_memory_usage, node_memory_capacity,
            node_memory_allocatable, node_memory_utilization_ratio, node_memory_pressure,
            node_disk_read_bytes, node_disk_write_bytes, node_disk_pressure,
            node_disk_capacity, node_disk_available, node_disk_utilization_ratio,
            node_network_receive_bytes, node_network_transmit_bytes, node_network_errors,
            node_ready, node_unschedulable, node_out_of_disk, node_pods_running,
            node_pods_allocatable, node_pods_usage_ratio, node_uptime_seconds,
            node_kubelet_healthy, node_disk_io_errors, node_inode_utilization_ratio,
            node_hardware_temperature, node_pid_pressure
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metrics["timestamp"],
        metrics["node_name"],
        metrics.get("node_cpu_usage", None),
        metrics.get("node_cpu_capacity", None),
        metrics.get("node_cpu_allocatable", None),
        metrics.get("node_cpu_utilization_ratio", None),
        metrics.get("node_memory_usage", None),
        metrics.get("node_memory_capacity", None),
        metrics.get("node_memory_allocatable", None),
        metrics.get("node_memory_utilization_ratio", None),
        metrics.get("node_memory_pressure", None),
        metrics.get("node_disk_read_bytes", None),
        metrics.get("node_disk_write_bytes", None),
        metrics.get("node_disk_pressure", None),
        metrics.get("node_disk_capacity", None),
        metrics.get("node_disk_available", None),
        metrics.get("node_disk_utilization_ratio", None),
        metrics.get("node_network_receive_bytes", None),
        metrics.get("node_network_transmit_bytes", None),
        metrics.get("node_network_errors", None),
        metrics.get("node_ready", None),
        metrics.get("node_unschedulable", None),
        metrics.get("node_out_of_disk", None),
        metrics.get("node_pods_running", None),
        metrics.get("node_pods_allocatable", None),
        metrics.get("node_pods_usage_ratio", None),
        metrics.get("node_uptime_seconds", None),
        metrics.get("node_kubelet_healthy", None),
        metrics.get("node_disk_io_errors", None),
        metrics.get("node_inode_utilization_ratio", None),
        metrics.get("node_hardware_temperature", None),
        metrics.get("node_pid_pressure", None)
    ))
    conn.commit()
    conn.close()

# Insert deployment metrics into the database
def insert_deployment_metrics(metrics):
    """Insert deployment metrics into the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deployments (
            timestamp, namespace, deployment_name, deployment_replicas, deployment_available_replicas,
            deployment_unavailable_replicas, deployment_updated_replicas, deployment_mismatch_replicas,
            deployment_cpu_usage, deployment_cpu_requests, deployment_cpu_limits, deployment_cpu_utilization_ratio,
            deployment_memory_usage, deployment_memory_requests, deployment_memory_limits, deployment_memory_utilization_ratio,
            deployment_pod_restarts, deployment_pod_crashloop_backoff, deployment_pod_oom_killed, deployment_pod_terminated,
            deployment_pod_pending, deployment_pod_failed, deployment_pod_evicted, deployment_network_receive_bytes,
            deployment_network_transmit_bytes, deployment_network_errors, deployment_disk_read_bytes, deployment_disk_write_bytes,
            deployment_memory_pressure, deployment_disk_pressure, deployment_pid_pressure, deployment_unschedulable_pods,
            deployment_waiting_pods, deployment_backoff_limit_exceeded, deployment_age_seconds, deployment_unavailable_duration,
            deployment_progressing, deployment_available, deployment_paused, deployment_replica_set_mismatch,
            deployment_rollout_in_progress, deployment_image_pull_error, deployment_create_container_error,
            deployment_node_not_ready, deployment_pod_unscheduled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metrics["timestamp"],
        metrics["namespace"],
        metrics["deployment_name"],
        metrics.get("deployment_replicas", None),
        metrics.get("deployment_available_replicas", None),
        metrics.get("deployment_unavailable_replicas", None),
        metrics.get("deployment_updated_replicas", None),
        metrics.get("deployment_mismatch_replicas", None),
        metrics.get("deployment_cpu_usage", None),
        metrics.get("deployment_cpu_requests", None),
        metrics.get("deployment_cpu_limits", None),
        metrics.get("deployment_cpu_utilization_ratio", None),
        metrics.get("deployment_memory_usage", None),
        metrics.get("deployment_memory_requests", None),
        metrics.get("deployment_memory_limits", None),
        metrics.get("deployment_memory_utilization_ratio", None),
        metrics.get("deployment_pod_restarts", None),
        metrics.get("deployment_pod_crashloop_backoff", None),
        metrics.get("deployment_pod_oom_killed", None),
        metrics.get("deployment_pod_terminated", None),
        metrics.get("deployment_pod_pending", None),
        metrics.get("deployment_pod_failed", None),
        metrics.get("deployment_pod_evicted", None),
        metrics.get("deployment_network_receive_bytes", None),
        metrics.get("deployment_network_transmit_bytes", None),
        metrics.get("deployment_network_errors", None),
        metrics.get("deployment_disk_read_bytes", None),
        metrics.get("deployment_disk_write_bytes", None),
        metrics.get("deployment_memory_pressure", None),
        metrics.get("deployment_disk_pressure", None),
        metrics.get("deployment_pid_pressure", None),
        metrics.get("deployment_unschedulable_pods", None),
        metrics.get("deployment_waiting_pods", None),
        metrics.get("deployment_backoff_limit_exceeded", None),
        metrics.get("deployment_age_seconds", None),
        metrics.get("deployment_unavailable_duration", None),
        metrics.get("deployment_progressing", None),
        metrics.get("deployment_available", None),
        metrics.get("deployment_paused", None),
        metrics.get("deployment_replica_set_mismatch", None),
        metrics.get("deployment_rollout_in_progress", None),
        metrics.get("deployment_image_pull_error", None),
        metrics.get("deployment_create_container_error", None),
        metrics.get("deployment_node_not_ready", None),
        metrics.get("deployment_pod_unscheduled", None)
    ))
    conn.commit()
    conn.close()


def run_promql_query(query):
    """Run a PromQL query and return the result."""
    response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": query})
    response.raise_for_status()
    return response.json().get("data", {}).get("result", [])

def get_k8s_pods():
    """Get all pods in the cluster."""
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    return [(pod.metadata.namespace, pod.metadata.name, pod.spec.node_name) for pod in pods.items]

def get_k8s_nodes():
    """Get all nodes in the cluster."""
    v1 = client.CoreV1Api()
    nodes = v1.list_node(watch=False)
    return [node.metadata.name for node in nodes.items]

def get_k8s_deployments():
    """Get all deployments in the cluster."""
    v1 = client.AppsV1Api()
    deployments = v1.list_deployment_for_all_namespaces(watch=False)
    return [(deployment.metadata.namespace, deployment.metadata.name) for deployment in deployments.items]

def main():
    # Initialize the database
    initialize_db()

    pod_queries = {
        # CPU Metrics
        "cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{pod="{pod}"}[5m]))',
        "cpu_limit": 'sum(kube_pod_container_resource_limits{pod="{pod}", resource="cpu"})',
        "cpu_request": 'sum(kube_pod_container_resource_requests{pod="{pod}", resource="cpu"})',
        "cpu_throttling": 'sum(rate(container_cpu_cfs_throttled_seconds_total{pod="{pod}"}[5m]))',

        # Memory Metrics
        "memory_usage": 'sum(container_memory_usage_bytes{pod="{pod}"})',
        "memory_limit": 'sum(kube_pod_container_resource_limits{pod="{pod}", resource="memory"})',
        "memory_request": 'sum(kube_pod_container_resource_requests{pod="{pod}", resource="memory"})',
        "memory_rss": 'sum(container_memory_rss{pod="{pod}"})',

        # Network Metrics
        "network_receive_bytes": 'sum(rate(container_network_receive_bytes_total{pod="{pod}"}[5m]))',
        "network_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{pod="{pod}"}[5m]))',
        "network_errors": 'sum(rate(container_network_receive_errors_total{pod="{pod}"}[5m]))',

        # Pod Status & Restarts
        "restarts": 'sum(kube_pod_container_status_restarts_total{pod="{pod}"})',
        "oom_killed": 'sum(kube_pod_container_status_last_terminated_reason{pod="{pod}", reason="OOMKilled"})',
        "pod_ready": 'max(kube_pod_status_ready{pod="{pod}"})',
        "pod_phase": 'kube_pod_status_phase{pod="{pod}"}',

        # Disk and I/O Metrics
        "disk_read_bytes": 'sum(rate(container_fs_reads_bytes_total{pod="{pod}"}[5m]))',
        "disk_write_bytes": 'sum(rate(container_fs_writes_bytes_total{pod="{pod}"}[5m]))',
        "disk_io_errors": 'sum(rate(container_fs_errors_total{pod="{pod}"}[5m]))',

        # Scheduling & Pending Metrics
        "pod_scheduled": 'max(kube_pod_status_scheduled{pod="{pod}"})',
        "pod_pending": 'max(kube_pod_status_phase{pod="{pod}", phase="Pending"})',
        "pod_unschedulable": 'max(kube_pod_status_unschedulable{pod="{pod}"})',

        # Container State Metrics
        "container_running": 'max(kube_pod_container_status_running{pod="{pod}"})',
        "container_terminated": 'max(kube_pod_container_status_terminated{pod="{pod}"})',
        "container_waiting": 'max(kube_pod_container_status_waiting{pod="{pod}"})',
        
        # Pod Uptime and Lifecycle
        "pod_uptime_seconds": 'time() - kube_pod_start_time{pod="{pod}"}',

        # Resource Utilization Ratios
        "cpu_utilization_ratio": 'sum(rate(container_cpu_usage_seconds_total{pod="{pod}"}[5m])) / sum(kube_pod_container_resource_limits{pod="{pod}", resource="cpu"})',
        "memory_utilization_ratio": 'sum(container_memory_usage_bytes{pod="{pod}"}) / sum(kube_pod_container_resource_limits{pod="{pod}", resource="memory"})',
    }
    node_queries = {
        # CPU Metrics
        "node_cpu_usage": 'sum(rate(node_cpu_seconds_total{node="{node}", mode!="idle"}[5m]))',
        "node_cpu_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="cpu"})',
        "node_cpu_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="cpu"})',
        "node_cpu_utilization_ratio": 'sum(rate(node_cpu_seconds_total{node="{node}", mode!="idle"}[5m])) / sum(kube_node_status_allocatable{node="{node}", resource="cpu"})',

        # Memory Metrics
        "node_memory_usage": 'sum(node_memory_MemTotal_bytes{node="{node}"} - node_memory_MemAvailable_bytes{node="{node}"})',
        "node_memory_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="memory"})',
        "node_memory_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="memory"})',
        "node_memory_utilization_ratio": '1 - (node_memory_MemAvailable_bytes{node="{node}"} / node_memory_MemTotal_bytes{node="{node}"})',
        "node_memory_pressure": 'max(kube_node_status_condition{node="{node}", condition="MemoryPressure", status="true"})',

        # Disk Metrics
        "node_disk_read_bytes": 'sum(rate(node_disk_read_bytes_total{instance="{node}"}[5m]))',
        "node_disk_write_bytes": 'sum(rate(node_disk_written_bytes_total{instance="{node}"}[5m]))',
        "node_disk_pressure": 'max(kube_node_status_condition{node="{node}", condition="DiskPressure", status="true"})',
        "node_disk_capacity": 'sum(node_filesystem_size_bytes{node="{node}", mountpoint="/"})',
        "node_disk_available": 'sum(node_filesystem_avail_bytes{node="{node}", mountpoint="/"})',
        "node_disk_utilization_ratio": '1 - (node_filesystem_avail_bytes{node="{node}", mountpoint="/"} / node_filesystem_size_bytes{node="{node}", mountpoint="/"})',

        # Network Metrics
        "node_network_receive_bytes": 'sum(rate(node_network_receive_bytes_total{node="{node}"}[5m]))',
        "node_network_transmit_bytes": 'sum(rate(node_network_transmit_bytes_total{node="{node}"}[5m]))',
        "node_network_errors": 'sum(rate(node_network_receive_errs_total{node="{node}"}[5m]) + rate(node_network_transmit_errs_total{node="{node}"}[5m]))',

        # Node Conditions & Status
        "node_ready": 'max(kube_node_status_condition{node="{node}", condition="Ready", status="true"})',
        "node_unschedulable": 'max(kube_node_spec_unschedulable{node="{node}"})',
        "node_out_of_disk": 'max(kube_node_status_condition{node="{node}", condition="OutOfDisk", status="true"})',

        # Pod Scheduling Metrics
        "node_pods_running": 'count(kube_pod_info{node="{node}"})',
        "node_pods_allocatable": 'sum(kube_node_status_allocatable_pods{node="{node}"})',
        "node_pods_usage_ratio": 'count(kube_pod_info{node="{node}"}) / sum(kube_node_status_allocatable_pods{node="{node}"})',

        # Node Uptime and Kubelet Health
        "node_uptime_seconds": 'time() - node_boot_time_seconds{node="{node}"}',
        "node_kubelet_healthy": 'max(kube_node_status_condition{node="{node}", condition="Ready", status="true"})',

        # I/O and Filesystem Errors
        "node_disk_io_errors": 'sum(rate(node_disk_io_time_seconds_total{instance="{node}"}[5m]))',
        "node_inode_utilization_ratio": '1 - (node_filesystem_files_free{node="{node}", mountpoint="/"} / node_filesystem_files{node="{node}", mountpoint="/"})',

        # Temperature and Hardware
        "node_hardware_temperature": 'node_hwmon_temp_celsius{node="{node}"}',

        # Node Pressure Conditions
        "node_pid_pressure": 'max(kube_node_status_condition{node="{node}", condition="PIDPressure", status="true"})',
    }
    deployment_queries = {
        # Replica Metrics
        "deployment_replicas": 'sum(kube_deployment_spec_replicas{deployment="{deployment}"})',
        "deployment_available_replicas": 'sum(kube_deployment_status_available_replicas{deployment="{deployment}"})',
        "deployment_unavailable_replicas": 'sum(kube_deployment_status_replicas_unavailable{deployment="{deployment}"})',
        "deployment_updated_replicas": 'sum(kube_deployment_status_updated_replicas{deployment="{deployment}"})',
        "deployment_mismatch_replicas": 'sum(kube_deployment_status_replicas{deployment="{deployment}"}) - sum(kube_deployment_spec_replicas{deployment="{deployment}"})',

        # CPU Metrics
        "deployment_cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{pod=~"{deployment}-.*"}[5m]))',
        "deployment_cpu_requests": 'sum(kube_pod_container_resource_requests_cpu_cores{pod=~"{deployment}-.*"})',
        "deployment_cpu_limits": 'sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"})',
        "deployment_cpu_utilization_ratio": 'sum(rate(container_cpu_usage_seconds_total{pod=~"{deployment}-.*"}[5m])) / sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"})',

        # Memory Metrics
        "deployment_memory_usage": 'sum(container_memory_usage_bytes{pod=~"{deployment}-.*"})',
        "deployment_memory_requests": 'sum(kube_pod_container_resource_requests_memory_bytes{pod=~"{deployment}-.*"})',
        "deployment_memory_limits": 'sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"})',
        "deployment_memory_utilization_ratio": 'sum(container_memory_usage_bytes{pod=~"{deployment}-.*"}) / sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"})',

        # Pod Health Metrics
        "deployment_pod_restarts": 'sum(increase(kube_pod_container_status_restarts_total{pod=~"{deployment}-.*"}[5m]))',
        "deployment_pod_crashloop_backoff": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason="CrashLoopBackOff"})',
        "deployment_pod_oom_killed": 'sum(kube_pod_container_status_terminated_reason{pod=~"{deployment}-.*", reason="OOMKilled"})',
        "deployment_pod_terminated": 'sum(kube_pod_container_status_terminated_reason{pod=~"{deployment}-.*"})',
        "deployment_pod_pending": 'sum(kube_pod_status_phase{pod=~"{deployment}-.*", phase="Pending"})',
        "deployment_pod_failed": 'sum(kube_pod_status_phase{pod=~"{deployment}-.*", phase="Failed"})',
        "deployment_pod_evicted": 'sum(kube_pod_status_reason{pod=~"{deployment}-.*", reason="Evicted"})',

        # Network Metrics
        "deployment_network_receive_bytes": 'sum(rate(container_network_receive_bytes_total{pod=~"{deployment}-.*"}[5m]))',
        "deployment_network_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{pod=~"{deployment}-.*"}[5m]))',
        "deployment_network_errors": 'sum(rate(container_network_receive_errors_total{pod=~"{deployment}-.*"}[5m]) + rate(container_network_transmit_errors_total{pod=~"{deployment}-.*"}[5m]))',

        # Disk I/O Metrics
        "deployment_disk_read_bytes": 'sum(rate(container_fs_reads_bytes_total{pod=~"{deployment}-.*"}[5m]))',
        "deployment_disk_write_bytes": 'sum(rate(container_fs_writes_bytes_total{pod=~"{deployment}-.*"}[5m]))',

        # Resource Pressure Conditions
        "deployment_memory_pressure": 'max(kube_node_status_condition{condition="MemoryPressure", status="true"})',
        "deployment_disk_pressure": 'max(kube_node_status_condition{condition="DiskPressure", status="true"})',
        "deployment_pid_pressure": 'max(kube_node_status_condition{condition="PIDPressure", status="true"})',

        # Scheduling Issues
        "deployment_unschedulable_pods": 'sum(kube_pod_status_unschedulable{pod=~"{deployment}-.*"})',
        "deployment_waiting_pods": 'sum(kube_pod_container_status_waiting{pod=~"{deployment}-.*"})',
        "deployment_backoff_limit_exceeded": 'sum(kube_job_status_failed{job_name=~"{deployment}-.*"})',

        # Age and Availability
        "deployment_age_seconds": 'max(time() - kube_deployment_created{deployment="{deployment}"})',
        "deployment_unavailable_duration": 'sum(increase(kube_deployment_status_replicas_unavailable{deployment="{deployment}"}[5m]))',

        # Deployment Conditions
        "deployment_progressing": 'max(kube_deployment_status_condition{deployment="{deployment}", condition="Progressing", status="true"})',
        "deployment_available": 'max(kube_deployment_status_condition{deployment="{deployment}", condition="Available", status="true"})',
        "deployment_paused": 'max(kube_deployment_spec_paused{deployment="{deployment}"})',

        # Replicaset and Rollout
        "deployment_replica_set_mismatch": 'count(kube_replicaset_status_ready_replicas{deployment="{deployment}"} != kube_deployment_spec_replicas{deployment="{deployment}"})',
        "deployment_rollout_in_progress": 'max(kube_deployment_status_condition{deployment="{deployment}", condition="Progressing", status="true"})',

        # Crash and Errors
        "deployment_image_pull_error": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason="ImagePullBackOff"})',
        "deployment_create_container_error": 'sum(kube_pod_container_status_waiting_reason{pod=~"{deployment}-.*", reason="CreateContainerConfigError"})',
        "deployment_node_not_ready": 'sum(kube_pod_status_reason{pod=~"{deployment}-.*", reason="NodeNotReady"})',
        "deployment_pod_unscheduled": 'sum(kube_pod_status_unschedulable{pod=~"{deployment}-.*"})',
    }

    while True:
        timestamp = pd.Timestamp.now().isoformat()


        # Collect pod metrics
        pods = get_k8s_pods()
        for namespace, pod_name, node in pods:
            pod_metrics = {"timestamp": timestamp, "namespace": namespace, "pod": pod_name, "node": node}
            for metric_name, query in pod_queries.items():
                query = query.replace("{pod}", pod_name)
                results = run_promql_query(query)
                if results:
                    pod_metrics[metric_name] = float(results[0]['value'][1])
                else:
                    pod_metrics[metric_name] = None
            insert_pod_metrics(pod_metrics)

        # Collect node metrics
        nodes = get_k8s_nodes()
        for node in nodes:
            node_metrics = {"timestamp": timestamp, "node_name": node}
            for metric_name, query in node_queries.items():
                query = query.replace("{node}", node)
                results = run_promql_query(query)
                if results:
                    node_metrics[metric_name] = float(results[0]['value'][1])
                else:
                    node_metrics[metric_name] = None
            insert_node_metrics(node_metrics)

        # Collect deployment metrics
        deployments = get_k8s_deployments()
        for namespace, deployment_name in deployments:
            deployment_metrics = {"timestamp": timestamp, "namespace": namespace, "deployment_name": deployment_name}
            for metric_name, query in deployment_queries.items():
                query = query.replace("{deployment}", deployment_name)
                results = run_promql_query(query)
                if results:
                    deployment_metrics[metric_name] = float(results[0]['value'][1])
                else:
                    deployment_metrics[metric_name] = None
            insert_deployment_metrics(deployment_metrics)

        print(f"Metrics collected and stored in database at {timestamp}")
        time.sleep(5)

if __name__ == "__main__":
    main()
