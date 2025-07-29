import requests
import base64
import json

# Azure DevOps Details
org_name = "Default"
pat_token = "USER_PAT"

# API Base URL
devops_base_url = f"https://azure.devops.com/{org_name}"

# Encode the PAT correctly
auth_header = base64.b64encode(f":{pat_token}".encode()).decode()

# Headers with authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_header}"
}

def get_all_projects():
    """Retrieve all projects with pagination, requesting 1000 at a time."""
    projects = []
    url = f"{devops_base_url}/_apis/projects?$top=1000&api-version=6.1-preview.1"
    page = 1  # Track pagination

    while url:
        print(f"\n🔹 Fetching page {page}...")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            projects.extend(data.get("value", []))

            continuation_token = response.headers.get("X-MS-ContinuationToken")
            if continuation_token:
                url = f"{devops_base_url}/_apis/projects?$top=1000&api-version=6.1-preview.1&continuationToken={continuation_token}"
                page += 1
            else:
                url = None  # No more pages, stop loop
        else:
            print(f"❌ Failed to retrieve projects: {response.status_code}")
            break  # Stop if there's an error

    print(f"\n✅ Total projects retrieved: {len(projects)}")
    return projects

# Run function
projects = get_all_projects()

# Print retrieved project names
for project in projects:
    print(f"📌 Project: {project['name']}")
