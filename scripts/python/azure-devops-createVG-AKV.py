import requests
import base64
import json

# Azure DevOps Details
org_name = "Default"
shared_project_name = "Default"  # Project where the shared service connection is located
pat_token = "USER_PAT"

# Azure Key Vault Details
key_vault_name = "project-kv"

# API Base URLs
devops_base_url = f"https://azure.devops.com/{org_name}"
shared_project_url = f"{devops_base_url}/{shared_project_name}/_apis"

# Encode the PAT correctly
auth_header = base64.b64encode(f":{pat_token}".encode()).decode()

# Headers with authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_header}"
}


def get_service_connection():
    """Retrieve the Azure Key Vault Service Connection from the shared project."""
    url = f"{shared_project_url}/serviceendpoint/endpoints?api-version=6.1-preview.1"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        connections = response.json().get("value", [])
        for sc in connections:
            if sc["name"] == "Azure-KeyVault-Connection":
                print(f"Shared Service Connection '{sc['name']}' found: {sc['id']}")
                return sc["id"]
    print("No matching Shared Service Connection found. Exiting.")
    return None


def get_all_projects():
    """Retrieve all projects in the organization, handling pagination."""
    projects = []
    url = f"{devops_base_url}/_apis/projects?$top=1000&api-version=6.1-preview.1"
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            projects.extend(data.get("value", []))
            continuation_token = response.headers.get("X-MS-ContinuationToken")
            if continuation_token:
                url = f"{devops_base_url}/_apis/projects?$top=1000&api-version=6.1-preview.1&continuationToken={continuation_token}"
            else:
                break
        else:
            print(f"Failed to retrieve projects: {response.status_code} - {response.text}")
            break

    print(f"Total projects retrieved: {len(projects)}")
    return projects


def variable_group_exists(project_name):
    """Check if the Variable Group already exists in the given project."""
    url = f"{devops_base_url}/{project_name}/_apis/distributedtask/variablegroups?api-version=6.1-preview.1"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        for vg in response.json().get("value", []):
            if vg["name"] == "SSL":
                print(f"Variable Group 'SSL' already exists in project {project_name}. Skipping.")
                return True
    return False


def create_variable_group(service_endpoint_id, project_name):
    """Create Variable Group linked to the shared Service Connection."""
    url = f"{devops_base_url}/{project_name}/_apis/distributedtask/variablegroups?api-version=6.1-preview.1"

    payload = {
        "name": "SSL",
        "description": "Variable Group linked to Azure Key Vault",
        "type": "AzureKeyVault",
        "isShared": True,
        "providerData": {
            "serviceEndpointId": service_endpoint_id,
            "vault": key_vault_name,
        },
        "variables": {
            "crt": {"enabled": True, "isSecret": True},
            "key": {"enabled": True, "isSecret": True},
            "pem": {"enabled": True, "isSecret": True}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print(f"Variable group 'SSL' created successfully in project {project_name}!")
    else:
        print(f"Failed to create variable group in project {project_name}. Status: {response.status_code}")
        print(response.json())


if __name__ == "__main__":
    service_connection_id = get_service_connection()
    if not service_connection_id:
        exit(0)  # Exit if no matching Shared Service Connection

    projects = get_all_projects()
    if not projects:
        exit(0)  # Exit if no projects found

    for project in projects:
        project_name = project["name"]
        print(f"Processing project: {project_name}")

        if variable_group_exists(project_name):
            continue  # Skip if Variable Group already exists

        create_variable_group(service_connection_id, project_name)
