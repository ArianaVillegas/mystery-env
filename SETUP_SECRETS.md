# 🔐 Setup Streamlit Secrets for Google Cloud Firestore

## Local Development

Create `.streamlit/secrets.toml` with your Google Cloud service account information:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-private-key-content\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

## Copy from service-account-key.json

1. Open your `service-account-key.json` file
2. Copy each field to the corresponding entry in `secrets.toml`
3. **Important**: Make sure the `private_key` includes proper line breaks (`\n`)

## Streamlit Cloud Deployment

1. Go to your Streamlit Cloud app settings
2. Navigate to "Secrets" tab
3. Paste the same TOML content there

## Testing

After setting up secrets, restart your Streamlit app:
```bash
streamlit run app.py
```

The app should now connect to Firestore using the secrets configuration.
