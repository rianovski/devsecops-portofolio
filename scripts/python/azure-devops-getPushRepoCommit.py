import requests
import psycopg2
from requests.auth import HTTPBasicAuth

# Azure DevOps Server (TFS) config
collection = "Default"
project = "Default"
pat = "USER_PAT"
auth = HTTPBasicAuth("", pat)
base_url = f"https://azure.devops.com/{collection}/{project}/_apis"

# PostgreSQL config
db_host = "localhost"
db_port = "5432"
db_name = "azure-db"
db_user = "postgres"
db_password = "password"

def get_repositories():
    url = f"{base_url}/git/repositories?api-version=1.0"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

def get_branches(repo_id):
    url = f"{base_url}/git/repositories/{repo_id}/refs?filter=heads/&api-version=1.0"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

def get_commit_info(repo_id, commit_id):
    url = f"{base_url}/git/repositories/{repo_id}/commits/{commit_id}?api-version=1.0"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()

def insert_commit(conn, commit_data):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO git_push_event (
            commit_id, repo_name, branch_name, pushed_by,
            project_name, push_timestamp, push_url,
            commit_url, comment
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (commit_id) DO NOTHING;
        """,
        (
            commit_data["commit_id"],
            commit_data["repo_name"],
            commit_data["branch_name"],
            commit_data["pushed_by"],
            commit_data["project_name"],
            commit_data["push_timestamp"],
            commit_data["push_url"],
            commit_data["commit_url"],
            commit_data["comment"]
        )
    )
    conn.commit()
    cursor.close()

def main():
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, database=db_name, user=db_user, password=db_password
        )
    except Exception as e:
        print("Database connection error:", e)
        return

    try:
        repos = get_repositories()
        for repo in repos:
            print(f"\n📦 Repository: {repo['name']}")
            repo_id = repo["id"]
            push_url = repo.get("remoteUrl", "")
            branches = get_branches(repo_id)

            for branch in branches:
                branch_name = branch["name"].replace("refs/heads/", "")
                commit_id = branch["objectId"]
                commit_data = get_commit_info(repo_id, commit_id)

                pushed_by = commit_data.get("committer", {}).get("name", "")
                push_timestamp = commit_data.get("committer", {}).get("date", "")
                comment = commit_data.get("comment", "")
                commit_url = commit_data.get("url", "")

                commit_record = {
                    "commit_id": commit_id,
                    "repo_name": repo["name"],
                    "branch_name": branch_name,
                    "pushed_by": pushed_by,
                    "project_name": project,
                    "push_timestamp": push_timestamp,
                    "push_url": push_url,
                    "commit_url": commit_url,
                    "comment": comment,
                }

                insert_commit(conn, commit_record)
                print(f"   └─ ✅ {branch_name}: {commit_id}")

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
