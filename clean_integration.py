"""
Clean integration - adds streamlined workflow without breaking existing
"""

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "Use Generated Profile" checkbox and add streamlined import
for i, line in enumerate(lines):
    # Add streamlined imports after refinement imports
    if 'run_simulation_enhanced = None' in line:
        lines.insert(i+1, '\n# Import streamlined simulation\n')
        lines.insert(i+2, 'try:\n')
        lines.insert(i+3, '    from structured_profile_generator import generate_structured_client_profile, format_profile_for_display\n')
        lines.insert(i+4, '    from run_streamlined_simulation import run_streamlined_simulation\n')
        lines.insert(i+5, '    STREAMLINED_AVAILABLE = True\n')
        lines.insert(i+6, 'except ImportError:\n')
        lines.insert(i+7, '    STREAMLINED_AVAILABLE = False\n')
        break

# Find profile generator button and update it
for i, line in enumerate(lines):
    if 'if st.button("🎲 Generate Random Profile"' in line:
        # Replace the button action
        j = i
        while j < len(lines) and 'st.rerun()' not in lines[j]:
            j += 1
        
        # Replace this section
        new_section = [
            '            if st.button("🎲 Generate Client Profile", use_container_width=True, type="secondary"):\n',
            '                if STREAMLINED_AVAILABLE:\n',
            '                    profile_dict = generate_structured_client_profile()\n',
            '                    profile_text = format_profile_for_display(profile_dict)\n',
            '                    st.session_state["client_profile_dict"] = profile_dict\n',
            '                    st.session_state["client_profile_text"] = profile_text\n',
            '                    st.success("✅ Client profile generated!")\n',
            '                else:\n',
            '                    from profile_generator import generate_random_client_profile\n',
            '                    new_profile = generate_random_client_profile()\n',
            '                    st.session_state["generated_profile"] = new_profile\n',
            '                    st.success("✅ Profile generated!")\n',
            '                st.rerun()\n'
        ]
        
        lines[i:j+1] = new_section
        break

# Add profile display before email history
for i, line in enumerate(lines):
    if '"Email History (50 interactions)"' in line and 'st.text_area' in line:
        # Add profile display before this
        profile_display = [
            '    # Display client profile if generated\n',
            '    if "client_profile_text" in st.session_state:\n',
            '        st.markdown("### 👤 Generated Client Profile")\n',
            '        st.text_area(\n',
            '            "Profile",\n',
            '            value=st.session_state["client_profile_text"],\n',
            '            height=400,\n',
            '            disabled=True,\n',
            '            key="profile_display"\n',
            '        )\n',
            '        st.markdown("---")\n',
            '    \n'
        ]
        lines[i:i] = profile_display
        break

# Update simulation call to use streamlined if profile exists
for i, line in enumerate(lines):
    if 'result = run_simulation_enhanced(' in line:
        # Add streamlined check before this
        streamlined_check = [
            '                # Use streamlined simulation if profile generated\n',
            '                if "client_profile_dict" in st.session_state and STREAMLINED_AVAILABLE:\n',
            '                    result = run_streamlined_simulation(\n',
            '                        profile=st.session_state["client_profile_dict"],\n',
            '                        max_iterations=max_iterations,\n',
            '                        enable_refinement=enable_refinement\n',
            '                    )\n',
            '                # Use enhanced simulation if refinement enabled\n',
            '                el'
        ]
        lines[i:i] = streamlined_check
        break

# Write updated file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Clean integration complete!")
print("Streamlit will auto-reload")
