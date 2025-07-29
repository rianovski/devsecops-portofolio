import os
import json
import requests
import psycopg2
from requests.auth import HTTPBasicAuth

# === Azure DevOps settings ===
organization = "Default"
project = "Default"
pat = os.environ.get("AZURE_PAT") or "USER_PAT"

# === PostgreSQL settings ===
db_host = "localhost"
db_port = "5432"
db_name = "azure-db"
db_user = "postgres"
db_password = "password"

# === API Endpoint Settings ===
url_base = f"https://azure.devops.com/{organization}/{project}/_apis/release/releases"
api_version = "6.1-preview.8"
top = 100
continuation_token = None
page = 1
all_releases = []

print("🔄 Fetching paginated releases...")

while True:
    params = {
        "$top": top,
        "api-version": api_version
    }
    if continuation_token:
        params["continuationToken"] = continuation_token

    response = requests.get(url_base, auth=HTTPBasicAuth("", pat), params=params)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page {page}: {response.status_code} - {response.text}")
        break

    data = response.json()
    releases = data.get("value", [])
    continuation_token = response.headers.get("x-ms-continuationtoken")

    print(f"📄 Page {page}: Retrieved {len(releases)} releases")

    all_releases.extend(releases)
    page += 1

    if not continuation_token:
        break

print(f"✅ Total releases fetched: {len(all_releases)}")

# === Save to PostgreSQL ===
try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS releases (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT,
            reason TEXT,
            description TEXT,
            created_by TEXT,
            modified_by TEXT,
            created_on TIMESTAMP,
            modified_on TIMESTAMP,
            release_definition_id INTEGER,
            release_definition_name TEXT,
            release_definition_url TEXT,
            logs_url TEXT,
            web_url TEXT,
            keep_forever BOOLEAN,
            variables JSONB,
            properties JSONB,
            project_id TEXT,
            project_name TEXT,
            raw JSONB
        );
    """)

    # Insert or update each release
    for r in all_releases:
        print(f"   ✅ Processing release [{r.get('id')}] - {r.get('name')}")

        project_ref = r.get("projectReference", {})
        cursor.execute("""
            INSERT INTO releases (
                id, name, status, reason, description,
                created_by, modified_by,
                created_on, modified_on,
                release_definition_id, release_definition_name, release_definition_url,
                logs_url, web_url, keep_forever,
                variables, properties,
                project_id, project_name,
                raw
            ) VALUES (%s, %s, %s, %s, %s,
                      %s, %s,
                      %s, %s,
                      %s, %s, %s,
                      %s, %s, %s,
                      %s, %s,
                      %s, %s,
                      %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                status = EXCLUDED.status,
                reason = EXCLUDED.reason,
                description = EXCLUDED.description,
                modified_by = EXCLUDED.modified_by,
                modified_on = EXCLUDED.modified_on,
                release_definition_id = EXCLUDED.release_definition_id,
                release_definition_name = EXCLUDED.release_definition_name,
                release_definition_url = EXCLUDED.release_definition_url,
                logs_url = EXCLUDED.logs_url,
                web_url = EXCLUDED.web_url,
                keep_forever = EXCLUDED.keep_forever,
                variables = EXCLUDED.variables,
                properties = EXCLUDED.properties,
                project_id = EXCLUDED.project_id,
                project_name = EXCLUDED.project_name,
                raw = EXCLUDED.raw;
        """, (
            r.get("id"),
            r.get("name"),
            r.get("status"),
            r.get("reason"),
            r.get("description"),
            r.get("createdBy", {}).get("displayName"),
            r.get("modifiedBy", {}).get("displayName"),
            r.get("createdOn"),
            r.get("modifiedOn"),
            r.get("releaseDefinition", {}).get("id"),
            r.get("releaseDefinition", {}).get("name"),
            r.get("releaseDefinition", {}).get("url"),
            r.get("logsContainerUrl"),
            r.get("_links", {}).get("web", {}).get("href"),
            r.get("keepForever"),
            json.dumps(r.get("variables", {})),
            json.dumps(r.get("properties", {})),
            project_ref.get("id"),
            project_ref.get("name"),
            json.dumps(r)
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All release data saved successfully!")

except Exception as e:
    print("❌ Database error:", e)
