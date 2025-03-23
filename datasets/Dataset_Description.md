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
