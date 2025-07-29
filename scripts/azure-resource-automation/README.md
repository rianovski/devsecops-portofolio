# ⚙️ Azure Resource Automation

Scripts to turn on/off Azure VMs, SQL, and WebApps based on schedule to optimize cloud cost.

## 🧾 Features
- `.env`-based
- Support for resource groups or tags
- Logging to external API

## 🧪 Sample Script
```bash
az vm start --resource-group rg-cost --name vm-app1
