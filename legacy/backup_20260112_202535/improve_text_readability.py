"""Add CSS to make text box text more solid and readable"""

with open('streamlit_streamlined.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the CSS section
old_css = '''# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4;}
    .sub-header {font-size: 1.5rem; color: #ff7f0e;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;}
</style>
""", unsafe_allow_html=True)'''

new_css = '''# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4;}
    .sub-header {font-size: 1.5rem; color: #ff7f0e;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;}
    
    /* Make text in text areas more solid and readable */
    textarea {
        color: #000000 !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    
    /* Make disabled text areas also readable */
    textarea:disabled {
        color: #1a1a1a !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #1a1a1a !important;
    }
    
    /* Improve overall text readability */
    .stTextArea textarea {
        color: #000000 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)'''

content = content.replace(old_css, new_css)

with open('streamlit_streamlined.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Enhanced text box readability!")
print("Text is now solid black with better contrast")
