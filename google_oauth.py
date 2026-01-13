"""
Google OAuth Integration for Streamlit
Handles Google Sign-In authentication flow
"""

import os
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pathlib
from typing import Optional, Dict, Any

# Allow OAuth over HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class GoogleAuthManager:
    """Manages Google OAuth authentication"""
    
    def __init__(self):
        self.client_secrets_file = self._get_client_secrets_path()
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
    def _get_client_secrets_path(self) -> str:
        """Get path to client_secrets.json file"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'google_client_secrets.json')
    
    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured with real credentials"""
        if not os.path.exists(self.client_secrets_file):
            return False
        
        try:
            with open(self.client_secrets_file, 'r') as f:
                config = json.load(f)
            
            # Check if it's still the template (has placeholder values)
            client_id = config.get('web', {}).get('client_id', '')
            client_secret = config.get('web', {}).get('client_secret', '')
            
            # If contains placeholder text, not configured
            if 'YOUR_CLIENT_ID' in client_id or 'YOUR_CLIENT_SECRET' in client_secret:
                return False
            
            # If empty, not configured
            if not client_id or not client_secret:
                return False
            
            return True
            
        except:
            return False
    
    def create_flow(self, redirect_uri: str) -> Flow:
        """Create OAuth flow"""
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        return flow
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get Google authorization URL
        
        Args:
            redirect_uri: Callback URL for OAuth
            
        Returns:
            Authorization URL to redirect user to
        """
        flow = self.create_flow(redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store state in session for verification
        st.session_state.oauth_state = state
        
        return authorization_url
    
    def handle_callback(self, authorization_response: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """
        Handle OAuth callback and fetch user info
        
        Args:
            authorization_response: Full callback URL with code
            redirect_uri: Same redirect URI used for authorization
            
        Returns:
            User info dict or None if failed
        """
        try:
            flow = self.create_flow(redirect_uri)
            flow.fetch_token(authorization_response=authorization_response)
            
            credentials = flow.credentials
            
            # Get user info
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'google_id': user_info.get('id')
            }
            
        except Exception as e:
            st.error(f"OAuth callback failed: {e}")
            return None


# Global instance
google_auth = GoogleAuthManager()


def create_client_secrets_template():
    """Create a template client_secrets.json file with instructions"""
    template = {
        "web": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost:8501"]
        }
    }
    
    instructions = """
# Google OAuth Configuration Instructions

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Add authorized redirect URIs:
     - http://localhost:8501
     - http://localhost:8501/oauth/callback
5. Download the credentials JSON file
6. Replace the contents of google_client_secrets.json with your downloaded credentials
7. Restart the Streamlit app

IMPORTANT: Keep this file secret and never commit to version control!
Add google_client_secrets.json to your .gitignore file.
"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_file = os.path.join(script_dir, 'google_client_secrets.json')
    instructions_file = os.path.join(script_dir, 'GOOGLE_OAUTH_SETUP.txt')
    
    # Create template file if it doesn't exist
    if not os.path.exists(secrets_file):
        with open(secrets_file, 'w') as f:
            json.dump(template, f, indent=2)
    
    # Create instructions file
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    return secrets_file, instructions_file


if __name__ == "__main__":
    # Create template files
    secrets_file, instructions_file = create_client_secrets_template()
    print(f"✅ Created template: {secrets_file}")
    print(f"✅ Created instructions: {instructions_file}")
    print("\nPlease follow the instructions to configure Google OAuth.")
