import requests
from requests.auth import HTTPBasicAuth

# Azure DevOps Server (TFS) config
collection = "Default"
project = "Default"
pat = "USER_PAT"
auth = HTTPBasicAuth("", pat)

# Base URL
base_url = f"https://azure.devops.com/{collection}/{project}/_apis"

# Get repositories in specific project
def get_repositories():
    url = f"{base_url}/git/repositories?api-version=1.0"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

# Get branches from a specific repo
def get_branches(repo_id):
    url = f"{base_url}/git/repositories/{repo_id}/refs?filter=heads/&api-version=1.0"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

# Main function
def main():
    repos = get_repositories()
    if not repos:
        print("No repositories found.")
        return

    for repo in repos:
        print(f"\n📦 Repository: {repo['name']}")
        branches = get_branches(repo['id'])
        for branch in branches:
            branch_name = branch["name"].replace("refs/heads/", "")
            commit_id = branch["objectId"]
            print(f"   └─ 🟢 Branch: {branch_name} | 🔐 Commit ID: {commit_id}")

if __name__ == "__main__":
    main()
