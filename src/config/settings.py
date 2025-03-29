"""
Configuration settings for the Kubernetes monitoring application.
"""

# Kubernetes settings
K8S_CONTEXT = "kind-clusterbusters"

# Prometheus settings
PROMETHEUS_URL = "http://localhost:9090"

# Application settings
POLLING_INTERVAL = 5  # seconds

# Thresholds
THRESHOLDS = {
    "node": {
        "cpu_usage": 80,
        "memory_usage": 90,
        "disk_usage": 90
    },
    "pod": {
        "cpu_usage": 80,
        "cpu_throttle": 0.75
    }
}

# PromQL queries
POD_QUERIES = {
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

NODE_QUERIES = {
    # CPU Metrics
    "node_cpu_usage": '(sum(rate(node_cpu_seconds_total{mode!="idle", node="{node}"}[5m])) or vector(0)) * 100',
    "node_cpu_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="cpu"}) or vector(0)',
    "node_cpu_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="cpu"}) or vector(0)',
    "node_cpu_utilization_ratio": 'sum(rate(node_cpu_seconds_total{node="{node}", mode!="idle"}[5m])) / sum(kube_node_status_allocatable{node="{node}", resource="cpu"})',

    # Memory Metrics
    "node_memory_usage": '((1 - (sum(node_memory_MemAvailable_bytes) or vector(0)) / (sum(node_memory_MemTotal_bytes) or vector(1))) * 100)',
    "node_memory_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="memory"}) or vector(0)',
    "node_memory_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="memory"}) or vector(0)',
    "node_memory_utilization_ratio": '1 - (sum(node_memory_MemAvailable_bytes{node="{node}"}) / sum(node_memory_MemTotal_bytes{node="{node}"}))',

    # Disk Metrics
    "node_disk_usage": '(1 - sum(node_filesystem_avail_bytes{node="{node}"}) / sum(node_filesystem_size_bytes{node="{node}"})) * 100',
    "node_disk_capacity": 'sum(kube_node_status_capacity{node="{node}", resource="ephemeral-storage"}) or vector(0)',
    "node_disk_allocatable": 'sum(kube_node_status_allocatable{node="{node}", resource="ephemeral-storage"}) or vector(0)',
    "node_disk_utilization_ratio": '(sum(node_filesystem_size_bytes{node="{node}"}) - sum(node_filesystem_avail_bytes{node="{node}"})) / sum(node_filesystem_size_bytes{node="{node}"})',

    # Network Metrics
    "node_network_receive_bytes": 'sum(rate(node_network_receive_bytes_total{node="{node}"}[5m]))',
    "node_network_transmit_bytes": 'sum(rate(node_network_transmit_bytes_total{node="{node}"}[5m]))',
    "node_network_errors": 'sum(rate(node_network_receive_errs_total{node="{node}"}[5m])) or vector(0)',

    # Node Status & Conditions
    "node_ready": 'max(kube_node_status_condition{node="{node}", condition="Ready"})',
    "node_memory_pressure": 'max(kube_node_status_condition{node="{node}", condition="MemoryPressure"})',
    "node_disk_pressure": 'max(kube_node_status_condition{node="{node}", condition="DiskPressure"})',
    "node_pid_pressure": 'max(kube_node_status_condition{node="{node}", condition="PIDPressure"})',
    "node_unschedulable": 'max(kube_node_spec_unschedulable{node="{node}"})',

    # Node Age
    "node_age_seconds": 'time() - kube_node_created{node="{node}"}'
}

DEPLOYMENT_QUERIES = {
    # Replica Metrics
    "deployment_replicas": 'sum(kube_deployment_spec_replicas{deployment="{deployment}"})',
    "deployment_available_replicas": 'sum(kube_deployment_status_available_replicas{deployment="{deployment}"})',
    "deployment_unavailable_replicas": 'sum(kube_deployment_status_replicas_unavailable{deployment="{deployment}"})',
    "deployment_updated_replicas": 'sum(kube_deployment_status_updated_replicas{deployment="{deployment}"})',
    "deployment_mismatch_replicas": 'sum(kube_deployment_status_replicas{deployment="{deployment}"}) - sum(kube_deployment_spec_replicas{deployment="{deployment}"})',

    # CPU Metrics
    "deployment_cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{container!="", pod=~"{deployment}-.*"}[5m]))',
    "deployment_cpu_requests": 'sum(kube_pod_container_resource_requests_cpu_cores{pod=~"{deployment}-.*"})',
    "deployment_cpu_limits": 'sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"})',
    "deployment_cpu_utilization_ratio": 'sum(rate(container_cpu_usage_seconds_total{container!="", pod=~"{deployment}-.*"}[5m])) / clamp_min(sum(kube_pod_container_resource_limits_cpu_cores{pod=~"{deployment}-.*"}), 1)',

    # Memory Metrics
    "deployment_memory_usage": 'sum(container_memory_usage_bytes{container!="", pod=~"{deployment}-.*"})',
    "deployment_memory_requests": 'sum(kube_pod_container_resource_requests_memory_bytes{pod=~"{deployment}-.*"})',
    "deployment_memory_limits": 'sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"})',
    "deployment_memory_utilization_ratio": 'sum(container_memory_usage_bytes{container!="", pod=~"{deployment}-.*"}) / clamp_min(sum(kube_pod_container_resource_limits_memory_bytes{pod=~"{deployment}-.*"}), 1)',

    # Disk I/O Metrics
    "deployment_disk_read_bytes": 'sum(rate(container_fs_reads_bytes_total{pod=~"{deployment}-.*"}[5m]))',
    "deployment_disk_write_bytes": 'sum(rate(container_fs_writes_bytes_total{pod=~"{deployment}-.*"}[5m]))',

    # Resource Pressure Conditions
    "deployment_memory_pressure": 'max(kube_node_status_condition{condition="MemoryPressure", status="true", node=~".*"})',
    "deployment_disk_pressure": 'max(kube_node_status_condition{condition="DiskPressure", status="true", node=~".*"})',
    "deployment_pid_pressure": 'max(kube_node_status_condition{condition="PIDPressure", status="true", node=~".*"})',

    # Scheduling Issues
    "deployment_waiting_pods": 'sum(kube_pod_container_status_waiting{pod=~"{deployment}-.*"})',

    # Age and Availability
    "deployment_age_seconds": 'max(time() - kube_deployment_created{deployment="{deployment}"})',
    "deployment_unavailable_duration": 'sum(increase(kube_deployment_status_replicas_unavailable{deployment="{deployment}"}[5m]))',

    # Deployment Conditions
    "deployment_progressing": 'sum(kube_deployment_status_condition{deployment="{deployment}", condition="Progressing", status="true"}) > 0',
    "deployment_available": 'sum(kube_deployment_status_condition{deployment="{deployment}", condition="Available", status="true"}) > 0',
    "deployment_paused": 'max(kube_deployment_spec_paused{deployment="{deployment}"})',
}

# Error types
NODE_ERROR_TYPES = [
    'CPU Pressure', 'Memory Pressure', 'Disk Pressure', 
    'Network Unavailable', 'Node Not Ready', 'PID Pressure', 
    'Node Unschedulable'
]

POD_ERROR_TYPES = [
    "CPU Throttling", "High CPU Usage", "OOMKilled (Out of Memory)",
    "CrashLoopBackOff", "ContainerNotReady", "PodUnschedulable",
    "NodePressure", "ImagePullFailure" 
]

DEPLOYMENT_ERROR_TYPES = [
    'Replica Mismatch', 'Unavailable Pods', 'ImagePullFailure', 
    'CrashLoopBackOff', 'FailedScheduling', 'QuotaExceeded', 
    'ProgressDeadlineExceeded'
]