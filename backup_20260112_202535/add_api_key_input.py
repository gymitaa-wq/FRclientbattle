"""Add API key input to sidebar"""

with open('streamlit_streamlined.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add API key input section after the configuration header
api_key_section = '''    st.markdown("## ⚙️ Configuration")
    
    # API Key input
    st.markdown("### 🔑 API Key")
    gemini_api_key = st.text_input(
        "Gemini API Key (optional)",
        type="password",
        help="Enter your Gemini API key. If left empty, will use key from .env file",
        placeholder="AIza..."
    )
    
    # Set API key in environment if provided
    if gemini_api_key:
        import os
        os.environ['GOOGLE_API_KEY'] = gemini_api_key
        st.success("✅ Using custom API key")
    else:
        st.info("ℹ️ Using API key from .env")
    
    st.markdown("---")
    
    # Model selection'''

old_section = '''    st.markdown("## ⚙️ Configuration")
    
    # Model selection'''

content = content.replace(old_section, api_key_section)

with open('streamlit_streamlined.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added API key input to sidebar")
print("Streamlit will auto-reload")
