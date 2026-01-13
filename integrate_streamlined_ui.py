"""
Streamlit UI Integration for Streamlined Simulation
Patches streamlit_app.py to use new profile-based workflow
"""

import re

# Read current streamlit_app.py
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('streamlit_app_before_streamlined.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created: streamlit_app_before_streamlined.py")

# Add new imports
import_section = """try:
    from csv_export import save_simulation_to_csv, load_simulation_history, get_history_stats
    import pandas as pd
    CSV_EXPORT_AVAILABLE = True
except ImportError:
    CSV_EXPORT_AVAILABLE = False

# Import enhanced simulation with refinement
try:
    from run_simulation_enhanced import run_simulation as run_simulation_enhanced
    REFINEMENT_AVAILABLE = True
except ImportError:
    REFINEMENT_AVAILABLE = False
    run_simulation_enhanced = None

# Import streamlined simulation (NEW)
try:
    from structured_profile_generator import generate_structured_client_profile, format_profile_for_display
    from run_streamlined_simulation import run_streamlined_simulation
    STREAMLINED_AVAILABLE = True
except ImportError:
    STREAMLINED_AVAILABLE = False
    run_streamlined_simulation = None"""

# Find and replace import section
old_import = re.search(r'try:\s+from csv_export.*?run_simulation_enhanced = None', content, re.DOTALL)
if old_import:
    content = content.replace(old_import.group(0), import_section)
    print("✓ Updated imports")

# Update profile generator button to use structured profiles
old_button = '''if PROFILE_GENERATOR_AVAILABLE:
            if st.button("🎲 Generate Random Profile", use_container_width=True, type="secondary"):
                new_profile = generate_random_client_profile()
                st.session_state['generated_profile'] = new_profile
                st.success("✅ New random client profile generated!")
                st.rerun()'''

new_button = '''if STREAMLINED_AVAILABLE:
            if st.button("🎲 Generate Random Client Profile", use_container_width=True, type="secondary"):
                # Generate structured profile
                profile_dict = generate_structured_client_profile()
                profile_text = format_profile_for_display(profile_dict)
                st.session_state['client_profile_dict'] = profile_dict
                st.session_state['client_profile_text'] = profile_text
                st.success("✅ New client profile generated!")
                st.rerun()'''

content = content.replace(old_button, new_button)
print("✓ Updated profile generator button")

# Replace email history text area with profile display
old_textarea_section = '''if 'generated_profile' in st.session_state:
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

new_textarea_section = '''# Display client profile if generated
    if 'client_profile_text' in st.session_state:
        st.markdown("### 👤 Client Profile")
        st.text_area(
            "Generated Profile",
            value=st.session_state['client_profile_text'],
            height=500,
            help="Structured client profile with comprehensive attributes",
            key="profile_display"
        )
        use_streamlined = True
    else:
        use_streamlined = False'''

content = content.replace(old_textarea_section, new_textarea_section)
print("✓ Updated profile display")

# Update simulation call
old_sim_section = '''# Use enhanced simulation if refinement enabled
                if REFINEMENT_AVAILABLE and enable_refinement:
                    result = run_simulation_enhanced(
                        email_history,
                        model=model_option,
                        enable_refinement=True,
                        max_iterations=max_iterations
                    )
                else:
                    result = run_simulation(email_history, model=model_option)'''

new_sim_section = '''# Use streamlined simulation if profile generated
                if use_streamlined and STREAMLINED_AVAILABLE:
                    result = run_streamlined_simulation(
                        profile=st.session_state['client_profile_dict'],
                        max_iterations=max_iterations,
                        enable_refinement=enable_refinement
                    )
                # Use enhanced simulation if refinement enabled
                elif REFINEMENT_AVAILABLE and enable_refinement:
                    result = run_simulation_enhanced(
                        email_history,
                        model=model_option,
                        enable_refinement=True,
                        max_iterations=max_iterations
                    )
                else:
                    result = run_simulation(email_history, model=model_option)'''

content = content.replace(old_sim_section, new_sim_section)
print("✓ Updated simulation call")

# Write updated file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ STREAMLIT APP UPDATED FOR STREAMLINED WORKFLOW!")
print("="*70)
print("\nChanges made:")
print("  ✓ Added streamlined simulation imports")
print("  ✓ Updated profile generator to use structured profiles")
print("  ✓ Replaced email history with profile display")
print("  ✓ Integrated streamlined simulation engine")
print("\nBackup saved to: streamlit_app_before_streamlined.py")
print("\nRestart Streamlit to see changes:")
print("  Ctrl+C to stop, then: streamlit run streamlit_app.py")
print("="*70)
