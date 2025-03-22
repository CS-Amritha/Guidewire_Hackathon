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
            data.append({
                "timestamp": datetime.now().isoformat(),
                "namespace": namespace,
                "pod_name": pod_name,
                "cpu_usage_millicores": int(cpu.replace("m", "")),
                "memory_usage_mib": int(mem.replace("Mi", "")),
                "network_io_kbps": get_network_usage(pod_name, namespace), 
                "disk_io_kbps": get_disk_usage(pod_name, namespace),  
                "log_lines": get_log_lines(pod_name, namespace),
                "error_count": get_error_count(pod_name, namespace),
            })

    return pd.DataFrame(data)

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

# Function to throttle all high-resource-consuming trainable parameters
def throttle_resources(namespace, pod_name):
    print(f"[WARNING] Throttling {pod_name} in {namespace} due to high resource usage.")

    throttle_yaml = f"""
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
            cpu: "100m"
            memory: "128Mi"
          requests:
            cpu: "50m"
            memory: "64Mi"
    """
    
    with open("throttle.yaml", "w") as f:
        f.write(throttle_yaml)
    
    run_command("kubectl apply -f throttle.yaml")
    print(f"✅ {pod_name} successfully throttled.")

# Function to label and throttle based on trainable parameters
def label_and_throttle(df):
    for index, row in df.iterrows():
        cpu, mem, net, disk, error_count = row["cpu_usage_millicores"], row["memory_usage_mib"], row["network_io_kbps"], row["disk_io_kbps"], row["error_count"]

        # Labeling logic
        if error_count > 0:
            df.at[index, "performance_label"] = "alert"  # Alert if there are any errors in logs
        elif cpu > 400 or mem > 400 or net > 500 or disk > 500:
            df.at[index, "performance_label"] = "bad"   # Bad if resource usage exceeds thresholds
        else:
            df.at[index, "performance_label"] = "good"   # Good if everything is within limits

        # Throttle if performance is bad or alert
        if df.at[index, "performance_label"] in ["bad", "alert"]:
            print(f"[ALERT] {row['pod_name']} in {row['namespace']} is labeled as {df.at[index, 'performance_label']}.")
            throttle_resources(row["namespace"], row["pod_name"])

    return df

# Run monitoring & throttling loop
while True:
    print("[INFO] Collecting trainable model parameters...")

    df_params = get_trainable_params()
    
    if not df_params.empty:
        df_params = label_and_throttle(df_params)
        df_params.to_csv("trainable_params_dataset.csv", index=False)

    print("[INFO] Sleeping for 5 seconds before next check...")
    time.sleep(5)
