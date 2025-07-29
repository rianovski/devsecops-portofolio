# 📦 Custom Helm Charts

This folder contains Helm charts used in DevSecOps workflows:

- `grafana/`: Preconfigured dashboards, datasources, and AD integration
- `custom-agent-chart/`: Azure DevOps agent with resource limits, secrets, and taints

To install:
```bash
helm install my-agent ./custom-agent-chart
