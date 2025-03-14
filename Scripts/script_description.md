# **Script Documentation**

This file provides details about all scripts used in the project to generate data set.

---

## **1. `Generate_Dataset_v1.py`**
**Description:**  
- Collects **trainable model parameters** from Kubernetes.
- Monitors CPU, memory, network, and disk I/O.
- Saves data to a CSV file 

**Key Features:**

✔ Fetches real-time resource usage using `kubectl top pod`.  
✔ Extracts network and disk I/O from pod stats.  
✔ Saves logs for documentation and analysis.  


