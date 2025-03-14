# **Dataset Documentation**

This file describes all the datasets used in the project.

---

## **1. Dataset_v1.csv**
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

## **2. Dataset_v2.csv**

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

