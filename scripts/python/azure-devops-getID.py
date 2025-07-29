import requests
from requests.auth import HTTPBasicAuth

# Replace these values with your Azure DevOps organization, project, and PAT
organization = "Default"
project = "Default"
pat = "USER_PAT"

# API endpoint for getting project information
url = f"https://azure.devops.com/{organization}/{project}/_apis/projects/{project}?api-version=6.0"

# Request headers with PAT
headers = {
    'Authorization': f'Basic {pat}',
    'Content-Type': 'application/json'
}

# Make the API request
response = requests.get(url, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    project_info = response.json()

    # Extract and print the Project ID
    project_id = project_info.get('id')
    print(f"Project ID for {project} is: {project_id}")

else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code} - {response.text}")
