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

