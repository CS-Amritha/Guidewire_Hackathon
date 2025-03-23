# **Dataset Documentation**

This file describes all the datasets used in the project.

---

## **1. Dataset_1.csv**
**Description:**  
- Collected using `kubectl top pod` in minikube
- Contains **2,500** entries of pod resource utilization
- Helps analyze CPU, memory, network, and disk I/O usage

**Columns:**
| Column                  | Description |
|-------------------------|-------------|
| `timestamp`            | Timestamp of data collection |
| `namespace`            | Kubernetes namespace of the pod |
| `pod_name`             | Name of the pod |
| `cpu_usage_millicores` | CPU usage in millicores |
| `memory_usage_mib`     | Memory usage in MiB |
| `network_io_kbps`      | Network I/O in KB/s |
| `disk_io_kbps`         | Disk I/O in KB/s |


---

## **2. Dataset_2.csv**

**Description:**  
- A smaller, more focused dataset derived from Dataset_v1.csv.
- Contains few entries of pod resource utilization, logs, and error counts.
- Designed to help understand performance monitoring and throttling logic in detail.

**Columns:**
| Column                  | Description |
|-------------------------|-------------|
| `timestamp`            | Timestamp of data collection |
| `namespace`            | Kubernetes namespace of the pod |
| `pod_name`             | Name of the pod |
| `cpu_usage_millicores` | CPU usage in millicores |
| `memory_usage_mib`     | Memory usage in MiB |
| `network_io_kbps`      | Network I/O in KB/s |
| `disk_io_kbps`         | Disk I/O in KB/s |
| `log_lines`            | Last 10 log lines from the pod |
| `error_count`          | Number of errors in the pod logs |
| `performance_label`    | Performance label (`good`, `bad`, or `alert`) based on resource usage and error count |

---

### **Performance Labeling Logic**
The `performance_label` column is derived based on the following rules:
- **`alert`**: If there are any errors in the pod logs (`error_count > 0`).
- **`bad`**: If resource usage exceeds the following thresholds:
  - CPU > 400 millicores
  - Memory > 400 MiB
  - Network I/O > 500 KB/s
  - Disk I/O > 500 KB/s
- **`good`**: If all resource usage is within thresholds and there are no errors in the logs.

---

## **3. Dataset_3.csv**

**Description:**  
- Collected using Prometheus queries to gather detailed cluster and pod-level metrics.
- Contains **real-time metrics** for nodes, pods, deployments, statefulsets, services, and network performance.
- Helps monitor and analyze cluster health, resource usage, and failure conditions.

**Columns:**
| Column                          | Description |
|---------------------------------|-------------|
| `timestamp`                    | Timestamp of data collection |
| `pod`                          | Name of the pod |
| `node`                         | Node where the pod is running |
| `namespace`                    | Kubernetes namespace of the pod |
| `status`                       | Status label (`healthy`, `warning`, `high_risk`, `critical_failure`, etc.) |
| `node_cpu_usage`               | CPU usage on the node (as a fraction of total CPU) |
| `node_memory_usage`            | Memory usage on the node (as a fraction of total memory) |
| `node_disk_usage`              | Disk usage on the node (as a fraction of total disk) |
| `node_network_io`              | Network I/O on the node (bytes per second) |
| `node_process_count`           | Total number of processes running on the node |
| `node_load_average`            | Load average on the node (1-minute average) |
| `node_unavailable`             | Number of unavailable nodes |
| `pod_cpu_usage`                | CPU usage of the pod (as a fraction of total CPU) |
| `pod_memory_usage`             | Memory usage of the pod (in bytes) |
| `pod_disk_io`                  | Disk I/O of the pod (bytes per second) |
| `pod_network_io`               | Network I/O of the pod (bytes per second) |
| `pod_restarts_total`           | Total number of pod restarts |
| `pod_status`                   | Current status of the pod (e.g., Running, Failed) |
| `pod_eviction_count`           | Number of pod evictions |
| `deployment_failure_count`     | Number of deployment failures |
| `deployment_pod_scheduling_delay` | Pod scheduling delay for deployments (in seconds) |
| `service_error_rate`           | Error rate for services (as a fraction of total requests) |
| `service_latency`              | Latency for services (in seconds) |
| `network_packet_loss`          | Packet loss on the network (as a fraction of total packets) |
| `network_latency`              | Network latency (in seconds) |
| `network_connection_errors`    | Number of network connection errors |
| `event_pod_terminations`       | Number of pod terminations |
---

### **Performance Labeling Logic**
The `status` column is derived based on the following rules:
- **`critical_failure`**: Pod is in a failed state, has excessive restarts, or is evicted frequently.
- **`network_failure`**: High packet loss, latency, or connection errors.
- **`disk_pressure`**: Disk usage exceeds 90% or storage errors are detected.
- **`service_failure`**: High service error rate or latency.
- **`deployment_issue`**: Deployment failures or high pod scheduling delays.
- **`high_risk`**: High CPU, memory, or disk usage, or high node load.
- **`warning`**: Moderate resource usage or occasional restarts/evictions.
- **`idle`**: Low resource usage and no restarts.
- **`healthy`**: All metrics within acceptable thresholds.

---
## **4. Dataset_4.csv**

**Description:**  
This dataset contains detailed metrics and events collected from a Kubernetes cluster, focusing on pod performance, node health, and deployment status. 

---

## Columns

| **Column**                          | **Description**                                                                 |
|-------------------------------------|---------------------------------------------------------------------------------|
| `timestamp`                         | Timestamp of the metric collection.                                             |
| `namespace`                         | Kubernetes namespace where the pod is deployed.                                 |
| `pod`                               | Name of the Kubernetes pod.                                                    |
| `node`                              | Node on which the pod is running.                                              |
| `cpu_usage`                         | Current CPU usage of the pod (as a percentage of the limit).                    |
| `cpu_limit`                         | CPU limit allocated to the pod.                                                 |
| `cpu_request`                       | CPU requested by the pod.                                                       |
| `cpu_throttling`                    | CPU throttling experienced by the pod.                                          |
| `memory_usage`                      | Current memory usage of the pod (in bytes).                                     |
| `memory_limit`                      | Memory limit allocated to the pod.                                              |
| `memory_request`                    | Memory requested by the pod.                                                    |
| `memory_rss`                        | Resident Set Size (RSS) memory usage of the pod.                                |
| `network_receive_bytes`             | Network bytes received by the pod.                                              |
| `network_transmit_bytes`            | Network bytes transmitted by the pod.                                           |
| `network_errors`                    | Network errors encountered by the pod.                                          |
| `restarts`                          | Number of times the pod has restarted.                                          |
| `oom_killed`                        | Indicates if the pod was killed due to Out of Memory (OOM).                     |
| `pod_ready`                         | Indicates if the pod is in a ready state.                                       |
| `pod_phase`                         | Current phase of the pod (e.g., Running, Pending).                              |
| `disk_read_bytes`                   | Disk bytes read by the pod.                                                     |
| `disk_write_bytes`                  | Disk bytes written by the pod.                                                  |
| `disk_io_errors`                    | Disk I/O errors encountered by the pod.                                         |
| `pod_scheduled`                     | Indicates if the pod has been scheduled.                                        |
| `pod_pending`                       | Indicates if the pod is in a pending state.                                     |
| `pod_unschedulable`                 | Indicates if the pod is unschedulable.                                          |
| `container_running`                 | Indicates if the container is running.                                          |
| `container_terminated`              | Indicates if the container has terminated.                                      |
| `container_waiting`                 | Indicates if the container is in a waiting state.                               |
| `pod_uptime_seconds`                | Uptime of the pod in seconds.                                                   |
| `cpu_utilization_ratio`             | Ratio of CPU usage to CPU limit.                                                |
| `memory_utilization_ratio`          | Ratio of memory usage to memory limit.                                          |
| `CPU Throttling`                    | Indicates if the pod is experiencing CPU throttling.                            |
| `High CPU Usage`                    | Indicates if the pod has high CPU usage.                                        |
| `OOMKilled (Out of Memory)`         | Indicates if the pod was killed due to OOM.                                     |
| `CrashLoopBackOff`                  | Indicates if the pod is in a CrashLoopBackOff state.                            |
| `ContainerNotReady`                 | Indicates if the container is not ready.                                        |
| `PodUnschedulable`                  | Indicates if the pod is unschedulable.                                          |
| `NodePressure`                      | Indicates if the node is under resource pressure.                               |
| `ImagePullFailure`                  | Indicates if there was an image pull failure.                                   |
| `node_cpu_usage`                    | CPU usage of the node (as a percentage).                                        |
| `node_cpu_capacity`                 | Total CPU capacity of the node.                                                 |
| `node_cpu_allocatable`              | Allocatable CPU on the node.                                                    |
| `node_cpu_utilization_ratio`        | Ratio of CPU usage to CPU capacity on the node.                                 |
| `node_memory_usage`                 | Memory usage of the node (as a percentage).                                     |
| `node_memory_capacity`              | Total memory capacity of the node.                                              |
| `node_memory_allocatable`           | Allocatable memory on the node.                                                 |
| `node_memory_utilization_ratio`     | Ratio of memory usage to memory capacity on the node.                           |
| `node_memory_pressure`              | Indicates if the node is under memory pressure.                                 |
| `node_disk_read_bytes`              | Disk bytes read on the node.                                                    |
| `node_disk_usage`                   | Disk usage on the node (as a percentage).                                       |
| `node_disk_write_bytes`             | Disk bytes written on the node.                                                 |
| `node_disk_pressure`                | Indicates if the node is under disk pressure.                                   |
| `node_disk_capacity`                | Total disk capacity of the node.                                                |
| `node_disk_utilization_ratio`       | Ratio of disk usage to disk capacity on the node.                               |
| `node_network_receive_bytes`        | Network bytes received on the node.                                             |
| `node_network_transmit_bytes`       | Network bytes transmitted on the node.                                          |
| `node_network_errors`               | Network errors encountered on the node.                                         |
| `node_ready`                        | Indicates if the node is in a ready state.                                      |
| `node_unschedulable`                | Indicates if the node is unschedulable.                                         |
| `node_out_of_disk`                  | Indicates if the node is out of disk space.                                     |
| `node_pods_running`                 | Number of pods running on the node.                                             |
| `node_pods_allocatable`             | Number of allocatable pods on the node.                                         |
| `node_pods_usage_ratio`             | Ratio of running pods to allocatable pods on the node.                          |
| `node_uptime_seconds`               | Uptime of the node in seconds.                                                  |
| `node_kubelet_healthy`              | Indicates if the node's kubelet is healthy.                                     |
| `node_disk_io_errors`               | Disk I/O errors encountered on the node.                                        |
| `node_inode_utilization_ratio`      | Ratio of inode usage to inode capacity on the node.                             |
| `node_pid_pressure`                 | Indicates if the node is under PID pressure.                                    |
| `CPU Pressure`                      | Indicates if the node is under CPU pressure.                                    |
| `Memory Pressure`                   | Indicates if the node is under memory pressure.                                 |
| `Disk Pressure`                     | Indicates if the node is under disk pressure.                                   |
| `Network Unavailable`               | Indicates if the node's network is unavailable.                                 |
| `Node Not Ready`                    | Indicates if the node is not ready.                                             |
| `PID Pressure`                      | Indicates if the node is under PID pressure.                                    |
| `Node Unschedulable`                | Indicates if the node is unschedulable.                                         |
| `deployment_replicas`               | Desired number of replicas for the deployment.                                  |
| `deployment_available_replicas`     | Number of available replicas for the deployment.                                |
| `deployment_unavailable_replicas`   | Number of unavailable replicas for the deployment.                              |
| `deployment_updated_replicas`       | Number of updated replicas for the deployment.                                  |
| `deployment_mismatch_replicas`      | Difference between desired and available replicas.                              |
| `deployment_cpu_usage`              | CPU usage of the deployment.                                                    |
| `deployment_cpu_requests`           | CPU requested by the deployment.                                                |
| `deployment_cpu_limits`             | CPU limits for the deployment.                                                  |
| `deployment_cpu_utilization_ratio`  | Ratio of CPU usage to CPU limits for the deployment.                            |
| `deployment_memory_usage`           | Memory usage of the deployment.                                                 |
| `deployment_memory_requests`        | Memory requested by the deployment.                                             |
| `deployment_memory_limits`          | Memory limits for the deployment.                                               |
| `deployment_memory_utilization_ratio` | Ratio of memory usage to memory limits for the deployment.                    |
| `deployment_disk_read_bytes`        | Disk bytes read by the deployment.                                              |
| `deployment_disk_write_bytes`       | Disk bytes written by the deployment.                                           |
| `deployment_memory_pressure`        | Indicates if the deployment is under memory pressure.                           |
| `deployment_disk_pressure`          | Indicates if the deployment is under disk pressure.                             |
| `deployment_pid_pressure`           | Indicates if the deployment is under PID pressure.                              |
| `deployment_waiting_pods`           | Number of pods in a waiting state for the deployment.                           |
| `deployment_age_seconds`            | Age of the deployment in seconds.                                               |
| `deployment_unavailable_duration`   | Duration the deployment has been unavailable.                                   |
| `deployment_progressing`            | Indicates if the deployment is progressing.                                     |
| `deployment_available`              | Indicates if the deployment is available.                                       |
| `deployment_paused`                 | Indicates if the deployment is paused.                                          |
| `deployment Replica Mismatch`       | Indicates if there is a mismatch in desired and available replicas.             |
| `deployment Unavailable Pods`       | Indicates if there are unavailable pods in the deployment.                      |
| `deployment ImagePullFailure`       | Indicates if there was an image pull failure in the deployment.                 |
| `deployment CrashLoopBackOff`       | Indicates if any pod in the deployment is in a CrashLoopBackOff state.          |
| `deployment FailedScheduling`       | Indicates if any pod in the deployment failed to schedule.                      |
| `deployment QuotaExceeded`          | Indicates if the deployment exceeded resource quotas.                           |
| `deployment ProgressDeadlineExceeded` | Indicates if the deployment exceeded its progress deadline.                   |

---

### **Performance Labeling Logic**
The dataset includes binary indicators (0 or 1) for various performance issues, such as:
- **CPU Throttling**: Pod CPU usage exceeds the throttling threshold.
- **High CPU Usage**: Pod CPU usage exceeds the defined threshold (e.g., 80%).
- **OOMKilled**: Pod was terminated due to Out of Memory.
- **CrashLoopBackOff**: Pod is repeatedly crashing and restarting.
- **NodePressure**: Node is under resource pressure (CPU, memory, disk).
- **Replica Mismatch**: Mismatch between desired and available replicas in a deployment.
- **ImagePullFailure**: Failure to pull container images.



---
