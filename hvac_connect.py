import hvac

# Configuration variables
VAULT_URL = 'https://vault.example.com'
ROLE_ID = 'your-approle-role-id'
SECRET_ID = 'your-approle-secret-id'
SECRET_PATH = 'secret/data/user-credentials'

def get_vault_client(vault_url, role_id, secret_id):
    """Authenticate with Vault using AppRole and return the client."""
    client = hvac.Client(url=vault_url)
    app_role_auth = client.auth.approle.login(role_id=role_id, secret_id=secret_id)
    if app_role_auth['auth']:
        print("Successfully authenticated to Vault")
    else:
        print("Failed to authenticate to Vault")
    return client

def retrieve_user_credentials(client, secret_path):
    """Retrieve user credentials from Vault."""
    read_response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return read_response['data']['data']

def main():
    # Step 1: Connect to Vault and authenticate using AppRole
    client = get_vault_client(VAULT_URL, ROLE_ID, SECRET_ID)
    
    # Step 2: Retrieve user credentials
    credentials = retrieve_user_credentials(client, SECRET_PATH)
    
    # Step 3: Print or use the retrieved credentials
    print(f"Retrieved credentials: {credentials}")

if __name__ == "__main__":
    main()
