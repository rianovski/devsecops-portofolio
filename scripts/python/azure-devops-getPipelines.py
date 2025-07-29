import requests
import psycopg2
from requests.auth import HTTPBasicAuth

# Azure DevOps details
organization = "Default"
project = "Default"
pat = "USER_PAT"

# PostgreSQL database credentials
db_host = "localhost"
db_port = "5432"
db_name = "azure_pipeline"
db_user = "postgres"
db_password = "passwords"

# API URL
url = f"https://azure.devops.com/{organization}/{project}/_apis/pipelines?api-version=6.1-preview.1"

# Fetch pipeline data from Azure DevOps API
response = requests.get(url, auth=HTTPBasicAuth("", pat))

if response.status_code == 200:
    pipelines = response.json().get("value", [])
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, database=db_name, user=db_user, password=db_password
        )
        cursor = conn.cursor()

        # Insert pipelines into the database
        for pipeline in pipelines:
            id = pipeline.get("id")
            name = pipeline.get("name")
            url = pipeline.get("url")
            folder = pipeline.get("folder")

            cursor.execute(
                """
                INSERT INTO pipelines (id, name, url, folder)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (id, name, url, folder),
            )

        # Commit transaction and close connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Data inserted successfully!")

    except Exception as e:
        print("Database error:", e)

else:
    print(f"Error: {response.status_code}, {response.text}")
