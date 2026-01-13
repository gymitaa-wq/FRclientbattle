"""Quick fix for email_history undefined error"""

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Add email_history = "" when using streamlined mode
content = content.replace(
    '        use_streamlined = True\r\n    else:',
    '        use_streamlined = True\r\n        email_history = ""  # Not used in streamlined mode\r\n    else:'
)

# Fix: Remove duplicate email_history assignments
# Find and clean up the else block
old_else_block = '''    else:
        use_streamlined = False

        email_history = st.text_area(
            "Email History (50 interactions)",
            value=SAMPLE_EMAIL_HISTORY,
            height=400,
            help="Sample email history provided for testing"
        )
        # Option to use sample data
        use_sample = st.checkbox("Use Sample Email History", value=True)
        if use_sample:
            email_history = st.text_area(
            "Email History (50 interactions)",
            value="",
            height=400,
            placeholder="Paste your email history here..."
        )
    
    # Character count
    char_count = len(email_history)
    st.caption(f"Character count: {char_count:,}")'''

new_else_block = '''    else:
        use_streamlined = False
        
        # Option to use sample data
        use_sample = st.checkbox("Use Sample Email History", value=True)
        
        if use_sample:
            email_history = st.text_area(
                "Email History (50 interactions)",
                value=SAMPLE_EMAIL_HISTORY,
                height=400,
                help="Sample email history provided for testing"
            )
        else:
            email_history = st.text_area(
                "Email History (50 interactions)",
                value="",
                height=400,
                placeholder="Paste your email history here..."
            )
        
        # Character count
        char_count = len(email_history)
        st.caption(f"Character count: {char_count:,}")'''

content = content.replace(old_else_block, new_else_block)

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed email_history variable error")
print("Streamlit should auto-reload")
