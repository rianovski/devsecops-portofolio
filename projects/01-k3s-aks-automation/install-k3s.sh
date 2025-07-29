#!/bin/bash

# Define variables
INSTALL_K3S_EXEC="https://get.k3s.io"
KUBECONFIG_PATH="$HOME/.kube/config"
CONTEXT_NAME="devsecops-k3s"
CLUSTER_NAME="devsecops-k3s"
K3S_USER="devsecops-k3s"
REGISTRIES_YAML_PATH="/etc/rancher/k3s/registries.yaml"
CERT_PATH="/opt/DigiCert"

# CA, cert, and key files
CA_CERT=$(cat << 'EOF'
-----BEGIN CERTIFICATE-----
CERT
-----END CERTIFICATE-----
EOF
)

CERT=$(cat << 'EOF'
-----BEGIN CERTIFICATE-----
CERT
-----END CERTIFICATE-----
EOF
)

KEY=$(cat << 'EOF'
-----BEGIN RSA PRIVATE KEY-----
KEY
-----END RSA PRIVATE KEY-----
EOF
)

# Install k3s
sudo curl -sfL $INSTALL_K3S_EXEC | sh -

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Error: k3s installation failed."
    exit 1
fi

# Wait for k3s to be ready
sleep 10

# Retrieve server IP dynamically
ACTIVE_INTERFACE=$(sudo ip route get 1 | awk '{print $5}')
SERVER_IP=$(sudo ip a show dev $ACTIVE_INTERFACE | awk '/inet /{gsub(/\/.*/, "", $2); print $2}')

# Create directory for Cert
sudo mkdir -p $CERT_PATH

# Create directory for config
sudo mkdir -p $HOME/.kube/

# Save CA to a file
sudo echo "$CA_CERT" > $CERT_PATH/DigiCertCA.crt

# Save cert to a file
sudo echo "$CERT" > $CERT_PATH/wildcard_astra_co_id.cert

# Save key to a file
sudo echo "$KEY" > $CERT_PATH/wildcard_astra_co_id.key

# Check if the context already exists
if sudo kubectl config get-contexts $CONTEXT_NAME > /dev/null 2>&1; then
    echo "Context '$CONTEXT_NAME' already exists."
    if sudo kubectl config get-contexts default > /dev/null 2>&1; then
        sudo kubectl config delete-context default
        echo "Default context deleted."
    fi
else
    # Create the context
    sudo kubectl config set-context $CONTEXT_NAME --cluster=$CLUSTER_NAME --user=$K3S_USER
    echo "Context '$CONTEXT_NAME' created."
    if sudo kubectl config get-contexts default > /dev/null 2>&1; then
        sudo kubectl config delete-context default
        echo "Default context deleted."
    fi
fi

# Set the current context to "devsecops-k3s" and update the kubeconfig file
sudo kubectl config use-context $CONTEXT_NAME

# Copy kubeconfig
sudo cp -f /etc/rancher/k3s/k3s.yaml ~/.kube/config

# Update kubeconfig file to use the correct server address
sudo sed -i "s/127.0.0.1/$SERVER_IP/g" $KUBECONFIG_PATH
sudo sed -i "s/default/$CONTEXT_NAME/g" $KUBECONFIG_PATH

# Create registries.yaml
echo "mirrors:
  harbor.com:
    endpoint:
      - \"https://harbor.com\"
configs:
  \"harbor.com\":
    auth:
      username: admin
      password: password
    tls:
      cert_file: $CERT_PATH/wildcard_astra_co_id.cert
      key_file:  $CERT_PATH/wildcard_astra_co_id.key
      ca_file:   $CERT_PATH/DigiCertCA.crt" | sudo tee $REGISTRIES_YAML_PATH > /dev/null

# Restart after creating registries.yaml
sudo systemctl restart k3s

# Get node token for installing node
NODE_TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)

echo "k3s installation successful!"
echo "Kubeconfig file saved to: $KUBECONFIG_PATH"
echo "Current context set to: $CONTEXT_NAME"
echo "registries.yaml file created at: $REGISTRIES_YAML_PATH"

# Option to view kubeconfig
read -p "Do you want to view the kubeconfig? (y/n): " -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\nContents of the kubeconfig file:\n"
    sudo cat $KUBECONFIG_PATH
    echo -e "\n"
fi

# Option to add node
read -p "Do you want to add a node? (y/n): " -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n"
    echo "Your node-token for installing a node: $NODE_TOKEN"
    echo "To install the node, run the following command:"
    echo "curl -sfL https://get.k3s.io | K3S_URL=https://$SERVER_IP:6443 K3S_TOKEN=$NODE_TOKEN sh -"
    echo -e "\n"
fi
