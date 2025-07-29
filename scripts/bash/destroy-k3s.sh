```bash
#!/bin/bash
# Destroy k3s cluster and remove all resources

echo "[*] Stopping k3s..."
systemctl stop k3s
k3s-uninstall.sh

echo "[*] Cleaning leftover resources..."
rm -rf /etc/rancher /var/lib/rancher