# 🚀 DevSecOps Portfolio by Moh. Ferian Fakhrul Zain

Welcome to my personal DevSecOps portfolio. This repository showcases my work in automating secure software delivery using modern DevOps tools and practices. It includes infrastructure setup, CI/CD pipelines, container security, GitOps, monitoring, and integrations across various stacks like Azure, Kubernetes, and Harbor.

---

## 🧩 Folder Structure

### 📄 about-me/
- `resume.md`: My professional profile and experience summary.

---

### 📚 articles/
- `cost-optimization.md`: Cost-saving automation strategies using Azure.
- `harbor-vs-dockerhub.md`: Comparison of Harbor and DockerHub registries.
- `secure-kubernetes.md`: Best practices to secure Kubernetes clusters.

---

### 📦 helm-charts/
Custom and public charts I’ve used or built for automation:
- `chart-museum/`: Chart Museum setup for private chart hosting.
- `custom-agent-chart/`: Helm chart for custom Azure DevOps agents.
- `grafana/`: Preconfigured Grafana chart with AD and dashboard provisioning.
- `n8n/`: Helm-based deployment of n8n automation.
- `nodered/`: Node-RED deployment via Helm.
- `postgresql-ha-cluster/`: HA PostgreSQL chart setup.

---

### 🚧 projects/
#### `01-k3s-aks-automation/`
- Bash script for installing and automating multi-node k3s and AKS clusters.
- Stateless deployment using `.env`.

#### `02-devsecops-pipeline/`
Full lifecycle DevSecOps pipeline components:
- 🛠 `Build/`, `Release/`
- 🔐 `SAST/`, `DAST/`, `SCA/`
- 📦 Reusable templates for `prod`, `qa`, and `utt` environments

#### `03-n8n-integration/`
- n8n flows integrated with Azure APIs and Microsoft Teams
- Automates reporting, cost alerts, and incident handling

---

### ⚙ scripts/
#### `azure-resource-automation/`
- Infrastructure scheduler in YAML to reduce Azure costs
- Includes ARM + Bicep-compatible templates

#### `bash/`
- `destroy-k3s.sh`: Safely remove k3s and clean up nodes
- `install-azure-devops-agent.sh`: Agent bootstrap script

#### `powershell/`
- `install-azure-devops-agent.ps1`: Windows-based agent deployment automation

#### `python/`
Python scripts to manage and automate Azure DevOps, HashiCorp Vault:
- Project, Repo, and Pipeline APIs
- Pricing API integration
- Secrets pull from Key Vault

---

## 🌐 Technologies & Tools

| Category       | Tools & Platforms                                    |
|----------------|------------------------------------------------------|
| ☁ Cloud        | Azure, AWS                                           |
| 📦 Containers  | Docker, Harbor, k3s, RKE, RKE2, AKS                  |
| 🔁 CI/CD       | Azure DevOps, GitHub Actions                         |
| 🛡 Security     | Trivy, SonarQube                                    |
| 📈 Monitoring  | Grafana, Loki, Prometheus                            |
| ⚙ Automation  | Bash, PowerShell, Python, Helm, Terraform, n8n       |

---

## 📫 Contact

- **Name**: Moh. Ferian Fakhrul Zain (Rian)
- **Email**: mferianfakhrulzain@gmail.com
- **LinkedIn**: [\[LinkedIn\]](https://www.linkedin.com/in/moh-ferian-fakhrul-zain/)
- **Location**: Jakarta, Indonesia
---

## 📜 License
This repository is licensed under the MIT License.