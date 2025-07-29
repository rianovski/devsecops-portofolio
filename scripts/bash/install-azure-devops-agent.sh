#!/bin/bash

# GitHub repository information
USERNAME="microsoft"
REPO="azure-pipelines-agent"

# Run a command with sudo without a password prompt
echo "Prompt password:"
sudo -S echo "Thanks for providing your password!"

# Number of agents to install (default to 3 if not provided as an argument) - run this script with ./agents.sh 1
num_agents=${1:-3}

# Action to perform (install or remove, default is install if not provided as an argument) - run this script with ./agents.sh 1 install or ./agents.sh 1 remove
action=${2:-"install"}

# Base directory for agent installation
base_dir="vsts-agent"

# Define the VSTS agent version
agent_version=$(get_latest_version)

# Define the VSTS agent pool
agent_pool="Agent-Azure"

# URL for VSTS agent package
agent_package_url="http://internal-repo.co.id/vsts-agent-linux-x64-latest.tar.gz"

# Authentication token
auth_token="AZURE_PAT"

echo "$action $num_agents agents for agent pool = $agent_pool"
echo "Latest VSTS agent version: latest"

# ---------------------------------------------------------------------------------------------------------------------------------

# Function to get the latest release version from GitHub
get_latest_version() {
    local version=$(curl -s "https://api.github.com/repos/$USERNAME/$REPO/releases/latest" | grep -oP '"tag_name": "\K(.*?)(?=")')
    echo "$version" | sed 's/^v//'
}

# Function to configure and start VSTS agent
configure_and_start_agent() {
    local agent_dir="$1"
    local agent_name="$2"

    # Check if directory already exists, remove if it does
    if [ -d "$agent_dir" ]; then
        echo "Agent directory $agent_dir already exists. Skipping installation..."
        return
    fi

    # Create directory
    mkdir -p "$agent_dir"

    # Move the downloaded package to the agent directory
    cp "vsts-agent-linux-x64-latest.tar.gz" "$agent_dir/"

    # Change into the extracted directory
    cd "$agent_dir"

    # Extract the VSTS agent package
    tar xzf "vsts-agent-linux-x64-latest.tar.gz"

    # Configure the VSTS agent
    ./config.sh --unattended \
      --agent "$agent_name" \
      --url "https://azure.devops.com" \
      --auth PAT \
      --token "$auth_token" \
      --pool "$agent_pool" \
      --work "_work" \
      --replace \
      --acceptTeeEula

    # Check the exit code of the config.sh command
    if [ $? -ne 0 ]; then
        echo "Error: ./config.sh command failed. Exiting script."
        exit 1
    fi

    # Install and start the VSTS agent as a service
    sudo ./svc.sh install && sudo ./svc.sh start

    # Move back to the original directory
    cd ..
}

# Check if the VSTS agent package file already exists
if [ ! -f "vsts-agent-linux-x64-latest.tar.gz" ]; then
    # Download the VSTS agent package if it doesn't exist
    wget "$agent_package_url"
fi

# Loop to install or remove agents
for ((i=1; i<=$num_agents; i++)); do
    unset {http,ftp,https}_proxy
    agent_dir="$base_dir-$i"
    agent_name="$(hostname)-$i"

    if [ "$action" == "install" ]; then
        configure_and_start_agent "$agent_dir" "$agent_name"
        echo "Success installing agent $agent_name"
    elif [ "$action" == "remove" ]; then
        # Check if directory exists, remove if it does
        if [ -d "$agent_dir" ]; then
            echo "Removing agent in $agent_dir..."
            cd "$agent_dir"
            sudo ./svc.sh stop
            sudo ./svc.sh uninstall
            ./config.sh remove --auth PAT --token "$auth_token"
            
            # Check the exit code of the remove command
            if [ $? -ne 0 ]; then
                echo "Error: ./config.sh remove command failed. Exiting script."
                exit 1
            fi

            cd ..
            rm -rf "$agent_dir"
        else
            echo "Agent directory $agent_dir does not exist. Skipping removal..."
        fi
    else
        echo "Invalid action. Use 'install' or 'remove'."
        exit 1
    fi
done
