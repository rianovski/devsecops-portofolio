
```markdown
# 🔐 DevSecOps CI/CD Pipeline with Trivy + Horusec

## 💡 Objective
Secure the CI/CD pipeline by integrating static and container image analysis.

## 🔧 Tools
- Azure DevOps 
- Trivy
- Horusec

## 🚀 Features
- Pre-commit scan
- Pipeline stage for container image vulnerabilities
- SonarQube integration

## 🧪 Sample `trivy.yaml`
```yaml
- name: Trivy Scan
  run: trivy image your-image:latest