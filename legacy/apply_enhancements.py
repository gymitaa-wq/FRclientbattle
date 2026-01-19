"""
Auto-Patcher for Streamlit App
Adds: Random Profile Generator, CSV Export, History Tab
"""

import re

# Read current streamlit_app.py
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('streamlit_app_backup.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created: streamlit_app_backup.py")

# ============================================================================
# PATCH 1: Add imports after line 33
# ============================================================================

imports_to_add = """
# Import profile generator and CSV export
try:
    from profile_generator import generate_random_client_profile
    PROFILE_GENERATOR_AVAILABLE = True
except ImportError:
    PROFILE_GENERATOR_AVAILABLE = False

try:
    from csv_export import save_simulation_to_csv, load_simulation_history, get_history_stats
    import pandas as pd
    CSV_EXPORT_AVAILABLE = True
except ImportError:
    CSV_EXPORT_AVAILABLE = False
"""

# Find the line after IMPORT_ERROR
import_insert_point = content.find("IMPORT_ERROR = str(e)")
if import_insert_point != -1:
    # Find the end of that line
    next_newline = content.find("\n", import_insert_point)
    content = content[:next_newline+1] + imports_to_add + content[next_newline+1:]
    print("✓ Added imports")

# ============================================================================
# PATCH 2: Update tab creation to add History tab
# ============================================================================

old_tabs = 'tab1, tab2, tab3, tab4 = st.tabs([\n    "📧 Input & Run",\n    "📊 Results Dashboard",\n    "📄 Documents",\n    "🔬 Analysis"\n])'

new_tabs = '''tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📧 Input & Run",
    "📊 Results Dashboard",
    "📄 Documents",
    "🔬 Analysis",
    "📈 History"
])'''

content = content.replace(old_tabs, new_tabs)
print("✓ Updated tab creation")

# ============================================================================
# PATCH 3: Add profile generator button in Tab 1
# ============================================================================

# Find the Tab 1 section and add button before text area
tab1_marker = 'with tab1:\n    st.markdown("## 📧 Email History Input")'
if tab1_marker in content:
    button_code = '''with tab1:
    st.markdown("## 📧 Email History Input")
    
    st.info("Enter 50 unstructured email interactions that reveal the client's financial situation, psychology, and needs.")
    
    # Profile generation button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if PROFILE_GENERATOR_AVAILABLE:
            if st.button("🎲 Generate Random Profile", use_container_width=True, type="secondary"):
                new_profile = generate_random_client_profile()
                st.session_state['generated_profile'] = new_profile
                st.success("✅ New random client profile generated!")
                st.rerun()
    
    # Check if we have a generated profile
    if 'generated_profile' in st.session_state:
        use_generated = st.checkbox("Use Generated Profile", value=True)
    else:
        use_generated = False
    
    if use_generated and 'generated_profile' in st.session_state:
        email_history = st.text_area(
            "Email History (50 interactions)",
            value=st.session_state['generated_profile'],
            height=400,
            help="Randomly generated client profile"
        )
    else:'''
    
    # Replace the tab1 opening
    content = content.replace(tab1_marker, button_code)
    
    # Remove the old "Option to use sample data" section
    old_sample_section = '''    
    st.info("Enter 50 unstructured email interactions that reveal the client's financial situation, psychology, and needs.")
    
    # Option to use sample data
    use_sample = st.checkbox("Use Sample Email History", value=True)
    
    if use_sample:'''
    
    content = content.replace(old_sample_section, '')
    
    # Fix the else clause
    content = content.replace(
        '    else:\n        email_history = st.text_area(',
        '        # Option to use sample data\n        use_sample = st.checkbox("Use Sample Email History", value=True)\n        if use_sample:\n            email_history = st.text_area('
    )
    
    print("✓ Added profile generator button")

# ============================================================================
# PATCH 4: Add CSV export after simulation
# ============================================================================

csv_marker = '# Store result\n            st.session_state.simulation_state = result'
csv_code = '''# Store result
            st.session_state.simulation_state = result
            
            # Save to CSV history
            if CSV_EXPORT_AVAILABLE:
                try:
                    save_simulation_to_csv(result)
                    st.info("📊 Results saved to simulation_history.csv")
                except Exception as e:
                    st.warning(f"Could not save to CSV: {e}")'''

content = content.replace(csv_marker, csv_code)
print("✓ Added CSV export")

# ============================================================================
# PATCH 5: Add History tab content before footer
# ============================================================================

footer_marker = '# ============================================================================\n# FOOTER\n# ============================================================================'

history_tab = '''
# ============================================================================
# TAB 5: HISTORY
# ============================================================================

with tab5:
    st.markdown("## 📈 Simulation History")
    
    if CSV_EXPORT_AVAILABLE:
        df = load_simulation_history()
        
        if not df.empty:
            stats = get_history_stats()
            
            st.markdown("### 📊 Overall Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Simulations", stats['total_simulations'])
            with col2:
                st.metric("Conversion Rate", f"{stats['conversion_rate']:.1f}%")
            with col3:
                st.metric("Avg Friction Score", f"{stats['avg_friction_score']:.1f}")
            with col4:
                if 'latest_timestamp' in stats:
                    st.metric("Latest Run", stats['latest_timestamp'][:10])
            
            st.markdown("---")
            st.markdown("### 📋 Simulation History")
            st.dataframe(df, use_container_width=True, height=400)
            
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download History CSV",
                csv,
                "simulation_history.csv",
                "text/csv",
                use_container_width=True
            )
            
            if st.button("🗑️ Clear History", type="secondary"):
                import os
                if os.path.exists("simulation_history.csv"):
                    os.remove("simulation_history.csv")
                    st.success("History cleared!")
                    st.rerun()
        else:
            st.info("📭 No simulation history yet. Run some simulations to see data here.")
    else:
        st.error("❌ CSV export module not available")


'''

content = content.replace(footer_marker, history_tab + footer_marker)
print("✓ Added History tab")

# ============================================================================
# Write enhanced version
# ============================================================================

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ STREAMLIT APP ENHANCED SUCCESSFULLY!")
print("="*70)
print("\nChanges made:")
print("  ✓ Added profile generator imports")
print("  ✓ Added CSV export imports")
print("  ✓ Added 🎲 Generate Random Profile button")
print("  ✓ Added CSV history saving")
print("  ✓ Added History tab (5th tab)")
print("\nBackup saved to: streamlit_app_backup.py")
print("\nRestart Streamlit to see changes:")
print("  1. Stop current app (Ctrl+C)")
print("  2. Run: streamlit run streamlit_app.py")
print("="*70)
