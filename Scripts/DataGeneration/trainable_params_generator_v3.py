import subprocess
import pandas as pd
import time
from datetime import datetime
import os

# Function to execute shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stderr:
        print(f"[ERROR] Command failed: {command}\n{result.stderr}")
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

    total_io_kb = 0
    lines = result.split("\n")

    for line in lines:
        parts = line.split()
        if len(parts) > 13 and parts[5].isdigit() and parts[9].isdigit():
            sectors_read = int(parts[5])
            sectors_written = int(parts[9])
            total_io_kb += (sectors_read + sectors_written) * 512 / 1024  # Convert sectors to KB

    return total_io_kb if total_io_kb > 0 else 0  # Return 0 if no valid data

# Function to overload existing pods instead of creating new ones
def overload_existing_pod(namespace, pod_name):
    print(f"[MODIFY] Increasing resource limits for {pod_name} in {namespace}.")

    # Increase CPU and memory requests and limits
    patch_command = f"""
    kubectl patch pod {pod_name} -n {namespace} --type='json' -p='[
        {{"op": "replace", "path": "/spec/containers/0/resources/limits/cpu", "value": "1000m"}},
        {{"op": "replace", "path": "/spec/containers/0/resources/limits/memory", "value": "1Gi"}},
        {{"op": "replace", "path": "/spec/containers/0/resources/requests/cpu", "value": "500m"}},
        {{"op": "replace", "path": "/spec/containers/0/resources/requests/memory", "value": "512Mi"}}
    ]'
    """

    print("[DEBUG] Executing:", patch_command)
    patch_output = run_command(patch_command)
    print("[DEBUG] Patch Output:", patch_output)

    # Simulate CPU load within the pod
    load_command = f"kubectl exec -n {namespace} {pod_name} -- sh -c 'apt update && apt install -y stress && stress --cpu 2 --vm 1 --vm-bytes 256M'"
    print("[DEBUG] Executing Load:", load_command)
    load_output = run_command(load_command)
    print("[DEBUG] Load Output:", load_output)

    print(f"🔥 {pod_name} has increased resource limits and is being stressed.")

# Function to label and overload based on resource usage
def label_and_overload(df):
    df["performance_label"] = "Stable"  # Initialize column

    for index, row in df.iterrows():
        cpu, mem, net, disk = row["cpu_usage_millicores"], row["memory_usage_mib"], row["network_io_kbps"], row["disk_io_kbps"]

        if cpu > 400 or mem > 400 or net > 500 or disk > 500:
            print(f"[ALERT] {row['pod_name']} in {row['namespace']} is over threshold.")
            overload_existing_pod(row["namespace"], row["pod_name"])

            # Update the DataFrame correctly
            df.loc[index, "performance_label"] = "Overloaded"

    return df

# Run monitoring & overloading loop
while True:
    print("[INFO] Collecting trainable model parameters...")

    df_params = get_trainable_params()
    
    if not df_params.empty:
        df_params = label_and_overload(df_params)
        df_params.to_csv("trainable_params_dataset.csv", mode='a', index=False, header=not os.path.exists("trainable_params_dataset.csv"))

    print("[INFO] Sleeping for 5 seconds before next check...")
    time.sleep(5)
