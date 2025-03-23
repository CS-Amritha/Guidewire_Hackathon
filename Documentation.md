# **Detailed Documentation for Phase 1:**

This document provides an in-depth account of the effort our team invested in Phase 1 of the project. The goal of this phase was to build a machine learning model capable of predicting failures in Kubernetes (K8s) clusters. Below, we break down our journey, highlighting the challenges, iterations, and deliverables of our work.

---

## **1. Understanding Kubernetes**

Before diving into the technical implementation, we recognized the importance of thoroughly understanding Kubernetes. This foundational knowledge was critical to ensuring we could effectively collect data and design models tailored to K8s environments.

### **Steps Taken:**
1. **Team Discussions and Research:**
   - Held multiple team discussions to align on Kubernetes basics.
   - Watched YouTube tutorials and read official Kubernetes documentation to understand its architecture, components, and workflows.

2. **Local Setup with Minikube:**
   - Installed Minikube to create a local Kubernetes cluster.
   - Practiced basic Kubernetes commands (`kubectl`) to interact with the cluster.
   - Deployed sample applications to understand pod lifecycle, resource allocation, and scaling.

3. **Exploring the Go Language:**
   - Since Kubernetes is written in Go, we explored the basics of Go to better understand Kubernetes' internal workings.
   - Reviewed Kubernetes source code to gain insights into its design and functionality.

4. **Multi-Node Multi-Cluster Setup:**
   - Explored options for setting up multi-node and multi-cluster environments on a local machine.
   - Evaluated tools like **Minikube**, **k3s**, and **Kind (Kubernetes IN Docker)**.
   - **Finalized on Kind:** Chose Kind for its lightweight nature, ease of setup, and ability to simulate multi-node and multi-cluster environments locally.

---

## **2. Data Collection**

Data collection was one of the most challenging and time-intensive phases of the project. We explored multiple approaches to gather relevant metrics and logs from Kubernetes clusters.

### **Approaches Explored:**
1. **Publicly Available Datasets:**
   - Searched for publicly available datasets on platforms like Google, Kaggle, and cloud providers (AWS, Azure).
   - Found limited datasets, and most were not specific to Kubernetes error logs.

2. **Simulating Data:**
   - Initially, we generated synthetic data using a basic Python script.
   - The synthetic data had unrealistically high accuracy and was not suitable for model training.

3. **Prometheus for Data Scraping:**
   - Installed Prometheus in Minikube to scrape metrics like CPU usage, memory usage, network I/O, and disk I/O.
   - Explored Prometheus Query Language (PromQL) to extract relevant metrics.
   - Wrote custom PromQL queries to capture specific metrics for pods, nodes, and deployments.

---

## **3. Script Development for Data Generation**

The data generation process involved multiple iterations of script development. Each version of the script was an improvement over the previous one, addressing limitations and adding new features to capture more comprehensive and realistic data.

### **Version 1: Basic Metrics Collection**
- **Objective:** Fetch basic metrics from Kubernetes clusters using `kubectl` commands.
- **Metrics Collected:**
  - Memory usage
  - Network I/O
  - CPU usage
  - Disk I/O usage
- **Labeling:** Labeled as `suboptimal` or `optimal` based on resource usage.
- **Throttling:** Used a YAML file to throttle resources (CPU, memory) to simulate resource exhaustion.
- **Limitations:**
  - The output dataset contained scraped metrics, but **labeling did not happen**.
  - Limited insights into pod health and errors.

### **Version 2: Adding Logs and Error Counts**
- **Objective:** Enhance the dataset by capturing logs and error counts for better error prediction.
- **New Additions:**
  - Log lines
  - Error counts
- **Labeling:** Pods were labeled as `good`, `bad`, or `alert` based on their health and resource usage.
- **Limitations:**
  - Captured log lines were not very insightful.
  - Lack of detailed error information to mitigate issues effectively.

### **Version 3: Expanded Metrics and Advanced Labeling**
- **Objective:** Capture a broader range of metrics and improve labeling accuracy.
- **New Additions:**
  - Additional metrics
  - Separate functions for modularity
- **Throttling:** Good pods were throttled to simulate bad behavior and create a balanced dataset.
- **Limitations:**
  - Limited system resources made it difficult to generate realistic errors.
  - Some metrics were not captured accurately due to parsing issues.

### **Version 4: Prometheus Integration and Event Handling**
- **Objective:** Use Prometheus queries to capture more detailed metrics and events.
- **New Additions:**
  - Prometheus queries for pods, nodes, and deployments.
  - Separate functions to parse events for pods, nodes, and deployments.
  - Error-checking conditions for labeling.
- **Key Improvements:**
  - Metrics and events were combined into a single dataset.
  - Node metrics were appended to all pods under that node.
  - Deployment metrics were appended to all pods related to that deployment.
- **Limitations:**
  - Some PromQL queries did not return values, leading to a sparse dataset.
  - Logical errors in error-checking conditions.
  - Event scraping and message parsing were not properly implemented.

### **Version 5: Final Refinement and Error Generation**
- **Objective:** Fix all issues in the previous version and fine-tune the script for accurate data generation.
- **Key Fixes:**
  - Resolved logical and syntactical issues in PromQL queries.
  - Ensured all functions returned expected values.
  - Properly implemented event scraping and message parsing.
- **Error Generation:**
  - Applied multiple YAML files to create specific errors (e.g., resource exhaustion, pod crashes).
  - Manually verified error messages and adjusted the script to match real-world scenarios.
  - Use of chaos mesh to create errors.
- **Output Dataset:**
  - Comprehensive dataset with accurate metrics, logs, events, and labels.
  - Balanced dataset with realistic error scenarios.

---

## **4. Machine Learning Model Design**

We explored multiple machine learning models to predict Kubernetes failures, focusing on **time-series forecasting** and **anomaly detection**.

### **Models Explored:**
1. **Facebook Prophet:**
   - Used for time-series forecasting of resource usage trends.
   - **Limitation:** Could not be trained on our dataset, so we did not proceed with it.

2. **Long Short-Term Memory (LSTM):**
   - An RNN model for time-series prediction.
   - **Issue:** Overfitting due to high accuracy on synthetic data.
   - Integrated Isolation Forest to identify unexpected spikes in resource usage.

3. **Gated Recurrent Unit (GRU):**
   - A lightweight alternative to LSTM.
   - Developed two versions:
     - **v1:** Had issues with null values during preprocessing.
     - **v2:** Fixed preprocessing issues and fine-tuned for better performance.
---
## **5. Additional Work**

### **Live Data Capture:**
- Installed PostgreSQL to store real-time metrics and logs.
- Developed a script to scrape live data from Kubernetes clusters and store it in the database.
- Separated data into three tables: `nodes`, `pods`, and `deployments`.

### **Use Case Development:**
- Defined a use case leveraging a **Large Language Model (LLM)** for automated incident response.
- Key features:
  1. Real-time monitoring of Kubernetes workloads.
  2. Root cause analysis (memory leaks, misconfigurations).
  3. Actionable recommendations with confidence scores.
  4. Notifications via Slack or email.
  5. Option to automatically apply recommended changes (with user approval).

---

## **6. Deliverables**

1. **Trained Machine Learning Model:**
   - A GRU-based model capable of predicting Kubernetes failures (e.g., node/pod failures, resource exhaustion, network issues).

2. **Codebase:**
   - Functional Python scripts for data collection, model training, and live data scraping.
   - Uploaded to GitHub for version control and collaboration.

3. **Documentation:**
   - This document provides a detailed explanation of our approach, key metrics, and model development process.
  
### **Learnings:**
1. **Importance of Realistic Data:**
   - Real-world data with proper labelling is critical for model performance.

2. **Iterative Development:**
   - Continuous improvement of scripts and models is essential.
   - Collaboration and regular code reviews helped identify and fix issues early.

3. **Integration with Kubernetes:**
   - Understanding Kubernetes internals and using tools like Prometheus and `kubectl` is crucial for effective data collection.
     
---
## **7. Next Steps**

1. **Refine Data Generation:**
   - Optimize the script to generate more realistic and diverse failure scenarios.
   - Improve labelling accuracy based on real-world error patterns.

2. **Enhance Model Performance:**
   - Train the GRU model on a larger and more diverse dataset.
   - Experiment with other anomaly detection techniques.

3. **Real-Time Prediction:**
   - Integrate the trained model with the live data capture pipeline.
   - Implement real-time failure prediction and alerting.

4. **Kubernetes Integration:**
   - Package the solution in Kubernetes for seamless deployment and scalability.




Phase 1 of the project laid a strong foundation for predicting Kubernetes failures. Over the course of 20 days, our team dedicated significant time and effort to understanding Kubernetes, developing a data generation pipeline, and exploring machine learning models. While challenges remain, the team is confident in the approach and excited to move forward with refining the solution in the subsequent phase.

---

**Date:** 23.03.2025


