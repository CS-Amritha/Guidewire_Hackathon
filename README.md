# Guidewire Hackathon - DevTrails 🚀


Problem Statement ❓ - Phase I
---
Kubernetes clusters can encounter failures such as pod crashes, resource bottlenecks, and network issues. The
challenge in Phase 1 is to build an AI/ML model capable of predicting these issues before they occur by analysing
historical and real-time cluster metrics.

**Key Challenges** ⚠️
- Node or pod failures
- Resource exhaustion (CPU, memory, disk)
- Network or connectivity issues
- Service disruptions based on logs and events
  
---
## Use Case ⚙️

<img src="images/biko.png" alt="Biko" width="200">

## Biko: The AI-Powered Kubernetes Octopus
Kubernetes clusters are like vast, ever changing oceans. Pods spin up, workloads shift, and resources fluctuate. But, unexpected disruptions can arise: pod crashes, resource exhaustion, or network failures.

Meet **Biko**, an AI-powered octopus designed to **monitor, predict, and respond** to Kubernetes issues before they escalate.

## Why Biko?

-  **Pods fail unpredictably**
-  **Resources—CPU, memory, disk—get overwhelmed**
-  **Network slowdowns impact performance**
-  **Service outages cause disruptions**

Traditional monitoring tools detect issues **after** they happen. Biko **anticipates and resolves them proactively.**

## How Biko Works 
Biko continuously tracks key metrics 
- CPU usage
- Memory consumption
- Network I/O
- Logs and system events

**Analyzes logs and metrics** to identify potential failures 
- Memory leaks
- Misconfigurations
- Out of Memory (OOM) errors
- Resource bottlenecks

Instead of vague alerts, Biko provides **clear, actionable suggestions** 

✅ "Increase memory limits by 20% to prevent a crash."

✅ "Scale replicas to handle increased traffic."

✅ "Restart the failing pod to restore stability."

Each recommendation includes a **confidence score** (eg: "90% sure this will fix the issue").

### 📩 Automated Notifications & Fixes
- Sends alerts via **Slack or email** with a summary of the issue, root cause, and suggested fix.
- Allows engineers to **apply fixes with a single click** or automatically resolve issues with approval.


## Example: Biko in Action
### Scenario: High Memory Usage Crash
1️⃣ **Biko detects abnormal memory usage** before users report downtime.

2️⃣ It **analyzes logs and metrics**, finding the memory limit is too low (512Mi).

3️⃣ Suggests increasing the limit to **1Gi with 90% confidence**.

4️⃣ Sends a **Slack alert** to the team with a detailed explanation.

5️⃣ With approval, Biko **automatically applies the fix, preventing further crashes.**

## Why Biko Stands Out
Detects and resolves issues **before** they escalate.

Keeps Kubernetes clusters **stable and optimized**.

Provides **data-driven, confidence-scored recommendations**.

Becomes **smarter with every incident.**

## Implementation Roadmap
| Phase | Deliverables |
|-------|-------------|
| 🚀 **1** | Data Collection (integrate with Kubernetes monitoring tools) |
| 📊 **2** | Feature Engineering (refine key metrics for prediction) |
| 🧠 **3** | AI Model Training (develop and test predictive models) |
| ⚙️ **4** | Fine-tuning & Deployment (optimize accuracy, enable automation) |
| 🔍 **5** | Continuous Monitoring & Scaling (learn from real-world incidents) |

### Biko: Your Kubernetes AI Co-Pilot
#### Biko **keeps your Kubernetes workloads running smoothly anticipating failures, preventing disruptions, and making smart decisions for you.**
---
Phase I Progress Bar 
---  
### 📌 Data Collection 
🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜  60%   

### 📌 ML Model 
🟩🟩🟩🟩🟩🟩⬜⬜⬜⬜  60% 

### 📌 Live Data Tracking  
🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜  40% 

Deliverables for Phase I
---


Problem Statement ❓ - Phase II
---
Once issues are predicted, the next step is to automate or recommend actions for remediation. The challenge in Phase
2 is to create an agent or system capable of responding to these predicted issues by suggesting or implementing actions
to mitigate potential failures in the Kubernetes cluster.

**Key Challenges** ⚠️
- Scaling pods when resource exhaustion is predicted
- Restarting or relocating pods when failures are forecasted
- Optimizing CPU or memory allocation when bottlenecks are detected


## Tech Stack & Tools 🛠️

  <p>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/grafana/grafana-original.svg" alt="Grafana" width="60"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/prometheus/prometheus-original.svg" alt="Prometheus" width="60"/>
    <img src="https://locust.io/static/img/logo.png" alt="Locust" width="170"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="60"/>
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/4b/Bash_Logo_Colored.svg" alt="Shell Scripts" width="60"/>
  </p>


## Meet The Team 👥

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/ADITHYA-NS">
          <img src="https://github.com/ADITHYA-NS.png" width="150" style="border-radius:10px;"><br>
          @ADITHYA-NS
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/Avi-Nair">
          <img src="https://github.com/Avi-Nair.png" width="150" style="border-radius:10px;"><br>
          @Avi-Nair
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/CS-Amritha">
          <img src="https://github.com/CS-Amritha.png" width="150" style="border-radius:10px;"><br>
          @CS_Amritha
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/Anaswara-Suresh">
          <img src="https://github.com/Anaswara-Suresh.png" width="150" style="border-radius:10px;"><br>
          @Anaswara-Suresh
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/R-Sruthi">
          <img src="https://github.com/R-Sruthi.png" width="150" style="border-radius:10px;"><br>
          @R-Sruthi
        </a>
      </td>
    </tr>
  </table>
</div>

