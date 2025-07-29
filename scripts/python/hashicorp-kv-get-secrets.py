import os
import hvac

# Initialize the Vault client
client = hvac.Client(
    url='http://kv.internal.com',  # URL of your Vault server
    token='token',  # Token for authentication
    verify=False  # Disable SSL verification
)

# Check if the client is authenticated
if not client.is_authenticated():
    print("Vault authentication failed")
    exit(1)

# Define the correct path for the secrets engine
secrets_engine_path = 'secrets'

# Example: List all secrets inside the secrets engine path
try:
    secrets = client.secrets.kv.v1.list_secrets(path=secrets_engine_path)
    print("All Secrets:")
    for secret in secrets['data']['keys']:
        print(secret)
except Exception as e:
    print("Error:", e)
