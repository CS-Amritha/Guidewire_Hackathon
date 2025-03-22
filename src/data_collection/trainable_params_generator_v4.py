import subprocess
import pandas as pd
import time
from datetime import datetime

# Function to execute shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Function to fetch all trainable model parameters from Kubernetes
def get_trainable_params():
    command = "kubectl top pod --no-headers --all-namespaces"
    output = run_command(command)

    data = []
    for line in output.split("\n"):
        if line:
            parts = line.split()
            namespace, pod_name, cpu, mem = parts[0], parts[1], parts[2], parts[3]
            
            # Fetch pod details to get resource limits and requests
            pod_details = get_pod_details(pod_name, namespace)
            
            # Fetch deployment metrics if the pod is part of a deployment
            deployment_metrics = get_deployment_metrics(pod_name, namespace)
            
            # Fetch event logs for the pod
            event_logs = get_event_logs(pod_name, namespace)
            
            data.append({
                "timestamp": datetime.now().isoformat(),
                "namespace": namespace,
                "pod_name": pod_name,
                "cpu_usage_millicores": int(cpu.replace("m", "")),
                "memory_usage_mib": int(mem.replace("Mi", "")),
                "cpu_limit_millicores": pod_details.get("cpu_limit", 0),
                "memory_limit_mib": pod_details.get("memory_limit", 0),
                "cpu_request_millicores": pod_details.get("cpu_request", 0),
                "memory_request_mib": pod_details.get("memory_request", 0),
                "network_io_kbps": get_network_usage(pod_name, namespace), 
                "disk_io_kbps": get_disk_usage(pod_name, namespace),  
                "log_lines": get_log_lines(pod_name, namespace),
                "error_count": get_error_count(pod_name, namespace),
                "restart_count": pod_details.get("restart_count", 0),
                "pod_status": pod_details.get("status", "unknown"),
                "node_name": pod_details.get("node_name", "unknown"),
                **deployment_metrics,  # Add deployment metrics
                "event_logs": event_logs,  # Add event logs
            })

    return pd.DataFrame(data)

# Function to fetch pod details (resource limits, requests, status, etc.)
def get_pod_details(pod_name, namespace):
    command = f"kubectl get pod -n {namespace} {pod_name} -o json"
    result = run_command(command)
    
    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch details for pod {pod_name}. Setting defaults.")
        return {}
    
    try:
        import json
        pod_info = json.loads(result)
        
        # Extract resource limits and requests
        containers = pod_info.get("spec", {}).get("containers", [])
        cpu_limit = 0
        memory_limit = 0
        cpu_request = 0
        memory_request = 0
        
        for container in containers:
            resources = container.get("resources", {})
            limits = resources.get("limits", {})
            requests = resources.get("requests", {})
            
            if limits.get("cpu"):
                cpu_limit += int(limits["cpu"].replace("m", ""))
            if limits.get("memory"):
                memory_limit += int(limits["memory"].replace("Mi", ""))
            if requests.get("cpu"):
                cpu_request += int(requests["cpu"].replace("m", ""))
            if requests.get("memory"):
                memory_request += int(requests["memory"].replace("Mi", ""))
        
        # Extract other pod details
        restart_count = pod_info.get("status", {}).get("containerStatuses", [{}])[0].get("restartCount", 0)
        pod_status = pod_info.get("status", {}).get("phase", "unknown")
        node_name = pod_info.get("spec", {}).get("nodeName", "unknown")
        
        return {
            "cpu_limit": cpu_limit,
            "memory_limit": memory_limit,
            "cpu_request": cpu_request,
            "memory_request": memory_request,
            "restart_count": restart_count,
            "pod_status": pod_status,
            "node_name": node_name,
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse pod details for {pod_name}: {e}")
        return {}

# Function to fetch deployment metrics
def get_deployment_metrics(pod_name, namespace):
    command = f"kubectl get deployments -n {namespace} -o json"
    result = run_command(command)
    
    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch deployment metrics for namespace {namespace}. Setting defaults.")
        return {}
    
    try:
        import json
        deployments = json.loads(result).get("items", [])
        
        for deployment in deployments:
            deployment_name = deployment.get("metadata", {}).get("name")
            selector = deployment.get("spec", {}).get("selector", {}).get("matchLabels", {})
            
            # Check if the pod belongs to this deployment
            if selector and selector.items() <= get_pod_labels(pod_name, namespace).items():
                return {
                    "deployment_name": deployment_name,
                    "replicas": deployment.get("spec", {}).get("replicas", 0),
                    "available_replicas": deployment.get("status", {}).get("availableReplicas", 0),
                    "deployment_status": deployment.get("status", {}).get("conditions", [{}])[0].get("type", "unknown"),
                }
        
        return {}  # Pod is not part of a deployment
    except Exception as e:
        print(f"[ERROR] Failed to parse deployment metrics for {pod_name}: {e}")
        return {}

# Function to fetch pod labels
def get_pod_labels(pod_name, namespace):
    command = f"kubectl get pod -n {namespace} {pod_name} -o jsonpath='{{.metadata.labels}}'"
    result = run_command(command)
    
    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch labels for pod {pod_name}. Setting defaults.")
        return {}
    
    try:
        import json
        return json.loads(result.replace("'", '"'))
    except Exception as e:
        print(f"[ERROR] Failed to parse labels for {pod_name}: {e}")
        return {}

# Function to fetch event logs for a pod
def get_event_logs(pod_name, namespace):
    command = f"kubectl get events -n {namespace} --field-selector involvedObject.name={pod_name} --sort-by=.lastTimestamp"
    result = run_command(command)
    
    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch event logs for pod {pod_name}. Setting to empty.")
        return ""
    
    return result

# Function to fetch Network I/O usage
def get_network_usage(pod_name, namespace):
    command = f"kubectl exec -n {namespace} {pod_name} -- cat /sys/class/net/eth0/statistics/tx_bytes"
    result = run_command(command)

    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch network I/O for {pod_name}. Setting to 0 KB/s.")
        return 0.0

    try:
        return int(result) / 1024  # Convert bytes to KB
    except ValueError:
        print(f"[ERROR] Unexpected network I/O output: '{result}' for {pod_name}. Setting to 0 KB/s.")
        return 0.0

# Function to fetch Disk I/O usage
def get_disk_usage(pod_name, namespace):
    command = f"kubectl exec -n {namespace} {pod_name} -- cat /proc/diskstats"
    result = run_command(command)

    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch disk I/O for {pod_name}. Setting to 0 KB/s.")
        return 0

    # Extract read/write bytes from /proc/diskstats
    total_io_kb = 0
    lines = result.split("\n")

    for line in lines:
        parts = line.split()
        if len(parts) > 13 and parts[5].isdigit() and parts[9].isdigit():
            sectors_read = int(parts[5])
            sectors_written = int(parts[9])
            total_io_kb += (sectors_read + sectors_written) * 512 / 1024  # Convert sectors to KB

    return total_io_kb if total_io_kb > 0 else 0  # Return 0 if no valid data

# Function to fetch log lines
def get_log_lines(pod_name, namespace):
    command = f"kubectl logs -n {namespace} {pod_name} --tail=10"
    result = run_command(command)

    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch logs for {pod_name}. Setting to empty.")
        return ""

    return result

# Function to fetch error count from logs
def get_error_count(pod_name, namespace):
    command = f"kubectl logs -n {namespace} {pod_name} | grep -i 'error' | wc -l"
    result = run_command(command)

    if not result.strip() or "failed" in result.lower():
        print(f"[WARNING] Could not fetch error count for {pod_name}. Setting to 0.")
        return 0

    try:
        return int(result)
    except ValueError:
        print(f"[ERROR] Unexpected error count output: '{result}' for {pod_name}. Setting to 0.")
        return 0

# Function to incrementally increase resource limits
def increment_resources(namespace, pod_name, cpu_limit, mem_limit):
    print(f"[INFO] Incrementing resources for {pod_name} in {namespace}: CPU={cpu_limit}m, Memory={mem_limit}Mi")

    increment_yaml = f """
    apiVersion: v1
    kind: Pod
    metadata:
      name: {pod_name}
      namespace: {namespace}
    spec:
      containers:
      - name: {pod_name}
        resources:
          limits:
            cpu: "{cpu_limit}m"
            memory: "{mem_limit}Mi"
          requests:
            cpu: "{int(cpu_limit / 2)}m"
            memory: "{int(mem_limit / 2)}Mi"""
    
    with open("increment.yaml", "w") as f:
        f.write(increment_yaml)
    
    run_command("kubectl apply -f increment.yaml")
    print(f"✅ {pod_name} resources incremented to CPU={cpu_limit}m, Memory={mem_limit}Mi.")

# Function to check if the pod is still running
def is_pod_running(namespace, pod_name):
    command = f"kubectl get pod -n {namespace} {pod_name} -o jsonpath='{{.status.phase}}'"
    result = run_command(command)
    return result.strip().lower() == "running"

# Function to label and increment resources based on trainable parameters
def label_and_increment(df):
    for index, row in df.iterrows():
        cpu, mem, net, disk, error_count = row["cpu_usage_millicores"], row["memory_usage_mib"], row["network_io_kbps"], row["disk_io_kbps"], row["error_count"]

        # Labeling logic
        if error_count > 0:
            df.at[index, "performance_label"] = "alert"  # Alert if there are any errors in logs
        elif cpu > 400 or mem > 400 or net > 500 or disk > 500:
            df.at[index, "performance_label"] = "bad"   # Bad if resource usage exceeds thresholds
        else:
            df.at[index, "performance_label"] = "good"   # Good if everything is within limits

        # Increment resources if performance is good
        if df.at[index, "performance_label"] == "good":
            current_cpu = int(row["cpu_usage_millicores"])
            current_mem = int(row["memory_usage_mib"])
            new_cpu = current_cpu + 100  # Increment CPU by 100m
            new_mem = current_mem + 128  # Increment memory by 128Mi

            increment_resources(row["namespace"], row["pod_name"], new_cpu, new_mem)

    return df

# Run monitoring & incremental resource increase loop
while True:
    print("[INFO] Collecting trainable model parameters...")

    df_params = get_trainable_params()
    
    if not df_params.empty:
        df_params = label_and_increment(df_params)
        df_params.to_csv("throttle_trainable_params_dataset.csv", index=False)

        # Check if any pod has failed
        for index, row in df_params.iterrows():
            if not is_pod_running(row["namespace"], row["pod_name"]):
                print(f"[ALERT] Pod {row['pod_name']} in {row['namespace']} has failed.")
                break  # Stop the loop if any pod fails

    print("[INFO] Sleeping for 5 seconds before next check...")
    time.sleep(5)
