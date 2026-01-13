# Google OAuth Configuration for Production Deployment
# Streamlit Cloud App: https://frclientbattlev1.streamlit.app/

## Part 1: Google Cloud Console Setup

### Step 1: Create/Select Project
1. Go to https://console.cloud.google.com/
2. Create a new project called "FRClientBattle" or use existing
3. Select the project from the dropdown

### Step 2: Enable Required APIs
1. Go to "APIs & Services" > "Library"
2. Search for "Google+ API" and click "Enable"
3. Also enable "People API" (recommended)

### Step 3: Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have Google Workspace)
3. Click "Create"
4. Fill in required fields:
   - App name: "FR Client Battle Simulation"
   - User support email: Your email
   - Developer contact: Your email
5. Click "Save and Continue"
6. Scopes: Keep default (or add email, profile, openid)
7. Test users: Add your email
8. Click "Save and Continue"

### Step 4: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **"Web application"**
4. Name: "FRClientBattle Web App"

5. **IMPORTANT - Add Authorized Redirect URIs:**
   For LOCAL development:
   - http://localhost:8501
   
   For PRODUCTION (Streamlit Cloud):
   - https://frclientbattlev1.streamlit.app/
   - https://frclientbattlev1.streamlit.app
   
   (Add both with and without trailing slash)

6. Click "Create"
7. **Download the credentials JSON file**

## Part 2: Configure Your Local App

### For Local Development:
1. Save the downloaded JSON as `google_client_secrets.json` in your project root
2. The app will automatically detect it
3. Restart Streamlit: The Google Sign-In button will appear

### For Production Deployment (Streamlit Cloud):
You have TWO options:

#### Option A: Use Streamlit Secrets (RECOMMENDED)
1. Go to your Streamlit Cloud dashboard
2. Select your app: frclientbattlev1.streamlit.app
3. Click "Settings" > "Secrets"
4. Add the following format:

```toml
[google_oauth]
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"
project_id = "your-project-id"
```

5. Update `google_oauth.py` to read from st.secrets instead of JSON file

#### Option B: Environment Variables
1. In Streamlit Cloud settings, add environment variables:
   - GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID"
   - GOOGLE_CLIENT_SECRET = "YOUR_SECRET"
2. Update code to read from os.environ

## Part 3: Update Code for Production

### Update google_oauth.py redirect URI:

```python
# In login_ui.py, update line ~102:
# OLD:
redirect_uri = "http://localhost:8501"

# NEW: Detect environment
import streamlit as st
if st.runtime.exists():
    # Production
    redirect_uri = "https://frclientbattlev1.streamlit.app/"
else:
    # Local
    redirect_uri = "http://localhost:8501"
```

### Update google_oauth.py for Streamlit Secrets:

```python
def __init__(self):
    # Try Streamlit secrets first (production)
    if 'google_oauth' in st.secrets:
        self.client_id = st.secrets.google_oauth.client_id
        self.client_secret = st.secrets.google_oauth.client_secret
        self.config_source = 'secrets'
    else:
        # Fall back to local file
        self.client_secrets_file = self._get_client_secrets_path()
        self.config_source = 'file'
    
    self.scopes = [...]
```

## Part 4: Security Checklist

✅ Added to .gitignore:
   - google_client_secrets.json
   - users.json
   - simulation_history.csv

✅ Never commit credentials to GitHub

✅ Use st.secrets for production

✅ Enable HTTPS-only in production (automatic on Streamlit Cloud)

## Part 5: Testing

### Test Locally:
1. Configure google_client_secrets.json
2. Run: streamlit run streamlit_streamlined.py
3. Click "Sign in with Google"
4. Should redirect to Google, then back

### Test Production:
1. Push code to GitHub
2. Configure Streamlit secrets
3. Deploy to https://frclientbattlev1.streamlit.app/
4. Test Google Sign-In button

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Add exact URL to Google Console authorized URIs
- Include both with/without trailing slash

**Error: "invalid_client"**
- Check client_id and client_secret are correct
- Verify using correct credentials file

**Error: "OAuth 2 MUST utilize https"**
- Local dev: Already fixed with OAUTHLIB_INSECURE_TRANSPORT=1
- Production: Streamlit Cloud uses HTTPS automatically

## Quick Start Commands

```bash
# Commit the fix
git add streamlit_app.py
git commit -m "fix: IndentationError in streamlit_app.py"
git push origin V1.1

# Streamlit Cloud will auto-deploy
```

## References
- Google Cloud Console: https://console.cloud.google.com/
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- OAuth 2.0 Setup: https://developers.google.com/identity/protocols/oauth2
