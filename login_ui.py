"""
Login UI Component for Streamlit App
Provides authentication interface and session management
"""

import streamlit as st
from user_auth import user_manager
from google_oauth import google_auth


def handle_google_callback(query_params):
    """Handle Google OAuth callback"""
    try:
        # Get authorization code
        auth_code = query_params.get('code')
        if not auth_code:
            return
        
        # Build full callback URL
        state = query_params.get('state', '')
        redirect_uri = "http://localhost:8501"
        authorization_response = f"{redirect_uri}?code={auth_code}&state={state}"
        
        # Get user info
        user_info = google_auth.handle_callback(authorization_response, redirect_uri)
        
        if user_info:
            # Check if user exists
            google_id = user_info['google_id']
            username = user_manager.find_google_user(google_id)
            
            if not username:
                # Create new user
                username = user_manager.create_google_user(
                    email=user_info['email'],
                    name=user_info['name'],
                    google_id=google_id
                )
                st.success(f"Welcome! Account created for {user_info['name']}")
            else:
                st.success(f"Welcome back, {user_info['name']}!")
            
            # Log in the user
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_info = user_manager.get_user_info(username)
            
            # Clear query parameters
            st.query_params.clear()
            st.rerun()
    
    except Exception as e:
        st.error(f"Google login failed: {e}")


def show_login_page():
    """Display login/signup page"""
    
    st.markdown("""
    <style>
    .login-header {
        text-align: center;
        padding: 2rem 0;
        color: #1f77b4;
    }
    .login-box {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .google-btn {
        background-color: #4285f4;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-header">🎯 Insurance Simulation Platform</h1>', unsafe_allow_html=True)
    
    #Check for OAuth callback
    query_params = st.query_params
    if 'code' in query_params:
        handle_google_callback(query_params)
    
    # Create tabs for Login and Signup
    tab1, tab2 = st.tabs(["🔑 Login", "✨ Create Account"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        
        # Google Sign-In button
        if google_auth.is_configured():
            st.markdown("#### Quick Login")
            if st.button("🔐 Sign in with Google", use_container_width=True, type="secondary"):
                # Detect production vs local environment
                if 'STREAMLIT_SHARING_MODE' in os.environ:
                    redirect_uri = "https://frclientbattlev1.streamlit.app/"
                else:
                    redirect_uri = "http://localhost:8501"
                
                auth_url = google_auth.get_authorization_url(redirect_uri)
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
                st.info("Redirecting to Google...")
            
            st.markdown("---")
            st.markdown("#### Or login with username/password")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                elif user_manager.authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_info = user_manager.get_user_info(username)
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.info("💡 **Demo Account:** Username: `demo` | Password: `demo123`")
        
        # Show setup instructions if Google OAuth not configured
        if not google_auth.is_configured():
            with st.expander("ℹ️ Want to enable Google Sign-In?"):
                st.markdown("""
                **Google Sign-In is not configured.** To enable it:
                
                1. See `GOOGLE_OAUTH_SETUP.txt` in the project folder
                2. Follow the instructions to set up Google Cloud Console
                3. Replace `google_client_secrets.json` with your credentials
                4. Restart the app
                
                Google Sign-In allows one-click login without creating a password!
                """)
    
    with tab2:
        st.markdown("### Create New Account")
        
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username", placeholder="Enter desired username")
            new_fullname = st.text_input("Full Name", placeholder="Enter your full name (optional)")
            new_password = st.text_input("Choose Password", type="password", placeholder="Enter password")
            new_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            signup_button = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if signup_button:
                if not new_username or not new_password:
                    st.error("Please enter both username and password")
                elif len(new_username) < 3:
                    st.error("Username must be at least 3 characters")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif new_password != new_password_confirm:
                    st.error("Passwords do not match")
                elif user_manager.user_exists(new_username):
                    st.error("Username already exists. Please choose a different one.")
                else:
                    if user_manager.create_user(new_username, new_password, new_fullname):
                        st.success(f"Account created successfully! Welcome, {new_username}!")
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.session_state.user_info = user_manager.get_user_info(new_username)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Account creation failed. Please try again.")


def show_user_header():
    """Display logged-in user info in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Logged In")
        
        user_info = st.session_state.get('user_info', {})
        username = st.session_state.get('username', 'Unknown')
        full_name = user_info.get('full_name', '')
        
        if full_name:
            st.markdown(f"**{full_name}**")
            st.caption(f"@{username}")
        else:
            st.markdown(f"**@{username}**")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.session_state.clear()
            st.rerun()


def require_login():
    """
    Check if user is logged in. If not, show login page.
    
    Returns:
        True if user is logged in, False otherwise
    """
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login_page()
        return False
    
    return True


def get_current_username() -> str:
    """Get currently logged in username"""
    return st.session_state.get('username', 'anonymous')
