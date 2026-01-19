"""
Streamlit App Enhancements Patch
Adds: Random Profile Generator Button, CSV Export, Premium Calculator Integration

This file contains the code snippets to add to streamlit_app.py
"""

# ============================================================================
# STEP 1: Add imports at the top (after existing imports, around line 20)
# ============================================================================

IMPORTS_TO_ADD = """
# Import profile generator and CSV export
try:
    from profile_generator import generate_random_client_profile
    PROFILE_GENERATOR_AVAILABLE = True
except ImportError:
    PROFILE_GENERATOR_AVAILABLE = False
    print("Warning: profile_generator not available")

try:
    from csv_export import save_simulation_to_csv, load_simulation_history, get_history_stats
    import pandas as pd
    CSV_EXPORT_AVAILABLE = True
except ImportError:
    CSV_EXPORT_AVAILABLE = False
    print("Warning: csv_export not available")

try:
    from profile_parser import enhance_advisor_prompt_with_premiums
    PREMIUM_CALC_AVAILABLE = True
except ImportError:
    PREMIUM_CALC_AVAILABLE = False
    print("Warning: premium_calculator not available")
"""

# ============================================================================
# STEP 2: Replace Tab 1 input section (around line 255-280)
# ============================================================================

TAB1_REPLACEMENT = """
with tab1:
    st.markdown("## 📧 Email History Input")
    
    st.info("Enter 50 unstructured email interactions that reveal the client's financial situation, psychology, and needs.")
    
    # Profile generation button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if PROFILE_GENERATOR_AVAILABLE:
            if st.button("🎲 Generate Random Profile", use_container_width=True, type="secondary"):
                # Generate new random profile
                new_profile = generate_random_client_profile()
                st.session_state['generated_profile'] = new_profile
                st.session_state['use_generated'] = True
                st.success("✅ New random client profile generated!")
                st.rerun()
        else:
            st.warning("Profile generator not available. Install profile_generator.py")
    
    # Profile source selection
    if 'generated_profile' in st.session_state and st.session_state.get('use_generated', False):
        profile_source = st.radio(
            "Profile Source:",
            ["Use Generated Profile", "Use Sample Data", "Enter Custom"],
            index=0,
            horizontal=True
        )
    else:
        profile_source = st.radio(
            "Profile Source:",
            ["Use Sample Data", "Enter Custom"],
            index=0,
            horizontal=True
        )
    
    # Display appropriate text area based on selection
    if profile_source == "Use Generated Profile" and 'generated_profile' in st.session_state:
        email_history = st.text_area(
            "Email History (50 interactions)",
            value=st.session_state['generated_profile'],
            height=400,
            help="Randomly generated client profile"
        )
    elif profile_source == "Use Sample Data":
        email_history = st.text_area(
            "Email History (50 interactions)",
            value=SAMPLE_EMAIL_HISTORY,
            height=400,
            help="Sample email history provided for testing"
        )
    else:  # Enter Custom
        email_history = st.text_area(
            "Email History (50 interactions)",
            value="",
            height=400,
            placeholder="Paste your email history here..."
        )
    
    # Character count
    char_count = len(email_history)
    st.caption(f"Character count: {char_count:,}")
"""

# ============================================================================
# STEP 3: Add CSV export after simulation completes (around line 323)
# ============================================================================

CSV_EXPORT_CODE = """
            # Store result
            st.session_state.simulation_state = result
            
            # Save to CSV history
            if CSV_EXPORT_AVAILABLE:
                try:
                    csv_path = save_simulation_to_csv(result)
                    st.info(f"📊 Results saved to {csv_path}")
                except Exception as e:
                    st.warning(f"Could not save to CSV: {e}")
"""

# ============================================================================
# STEP 4: Add History tab (modify tab creation around line 239)
# ============================================================================

HISTORY_TAB_CODE = """
# Main tabs - ADD "📈 History" to the list
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📧 Input & Run",
    "📊 Results Dashboard",
    "📄 Documents",
    "🔬 Analysis",
    "📈 History"  # NEW TAB
])

# ... existing tab code ...

# ============================================================================
# NEW: HISTORY TAB (add at the end, before footer)
# ============================================================================

with tab5:
    st.markdown("## 📈 Simulation History")
    
    if CSV_EXPORT_AVAILABLE:
        df = load_simulation_history()
        
        if not df.empty:
            # Statistics
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
                st.metric("Latest Run", stats.get('latest_timestamp', 'N/A')[:10])
            
            st.markdown("---")
            
            # Data table
            st.markdown("### 📋 Simulation History")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download History CSV",
                csv,
                "simulation_history.csv",
                "text/csv",
                use_container_width=True
            )
            
            # Clear history button
            if st.button("🗑️ Clear History", type="secondary"):
                import os
                if os.path.exists("simulation_history.csv"):
                    os.remove("simulation_history.csv")
                    st.success("History cleared!")
                    st.rerun()
        else:
            st.info("📭 No simulation history yet. Run some simulations to see data here.")
            st.markdown("""
            **What gets tracked:**
            - Timestamp of each simulation
            - Decision (CONVERT/REJECT)
            - Friction score
            - Model used
            - Number of products
            - Profile and outcome previews
            """)
    else:
        st.error("❌ CSV export module not available. Make sure csv_export.py is in the project directory.")
"""

# Print instructions
print("""
=============================================================================
STREAMLIT APP ENHANCEMENT INSTRUCTIONS
=============================================================================

To add the Random Profile Generator button and other features:

OPTION 1: Manual Integration (Recommended for learning)
--------------------------------------------------------
1. Open streamlit_app.py
2. Add the IMPORTS (Step 1) after line 20
3. Replace Tab 1 input section (Step 2) around line 255-280
4. Add CSV export code (Step 3) after line 323
5. Add History tab (Step 4) - modify tab creation and add new tab content

OPTION 2: Quick Integration Script
-----------------------------------
Run this Python script to automatically patch streamlit_app.py:

    python apply_enhancements.py

OPTION 3: Use Pre-Enhanced Version
-----------------------------------
I can create a complete streamlit_app_enhanced.py file with all features.
Then you can:
    1. Backup current: mv streamlit_app.py streamlit_app_backup.py
    2. Use enhanced: mv streamlit_app_enhanced.py streamlit_app.py
    3. Restart Streamlit

Which option would you like?
=============================================================================
""")
