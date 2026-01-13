"""
Patch to add iterative refinement to Streamlit app
"""

import re

# Read streamlit_app.py
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('streamlit_app_before_refinement.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created: streamlit_app_before_refinement.py")

# Add import after CSV export
import_marker = "except ImportError:\n    CSV_EXPORT_AVAILABLE = False"
import_addition = """except ImportError:
    CSV_EXPORT_AVAILABLE = False

# Import enhanced simulation with refinement
try:
    from run_simulation_enhanced import run_simulation as run_simulation_enhanced
    REFINEMENT_AVAILABLE = True
except ImportError:
    REFINEMENT_AVAILABLE = False
    run_simulation_enhanced = None"""

content = content.replace(import_marker, import_addition)
print("✓ Added refinement import")

# Add UI controls in sidebar (find MLflow section and add before it)
sidebar_marker = '    # MLflow configuration\n    st.markdown("### 📊 MLflow Tracking")'
sidebar_addition = '''    # Iterative Refinement configuration
    st.markdown("### 🔄 Iterative Refinement")
    
    if REFINEMENT_AVAILABLE:
        enable_refinement = st.checkbox(
            "Enable Proposal Refinement",
            value=True,
            help="If client rejects, FR will refine proposal based on AI feedback"
        )
        
        if enable_refinement:
            max_iterations = st.slider(
                "Max Refinement Iterations",
                min_value=1,
                max_value=5,
                value=3,
                help="How many times FR can refine the proposal"
            )
        else:
            max_iterations = 0
    else:
        enable_refinement = False
        max_iterations = 0
        st.warning("Refinement module not available")
    
    st.markdown("---")
    
    # MLflow configuration
    st.markdown("### 📊 MLflow Tracking")'''

content = content.replace(sidebar_marker, sidebar_addition)
print("✓ Added refinement UI controls")

# Update simulation call to use enhanced version
old_sim_call = 'result = run_simulation(email_history, model=model_option)'
new_sim_call = '''# Use enhanced simulation if refinement enabled
                if REFINEMENT_AVAILABLE and enable_refinement:
                    result = run_simulation_enhanced(
                        email_history,
                        model=model_option,
                        enable_refinement=True,
                        max_iterations=max_iterations
                    )
                else:
                    result = run_simulation(email_history, model=model_option)'''

content = content.replace(old_sim_call, new_sim_call)
print("✓ Updated simulation call")

# Write updated file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ STREAMLIT APP UPDATED WITH ITERATIVE REFINEMENT!")
print("="*70)
print("\nChanges made:")
print("  ✓ Added refinement module import")
print("  ✓ Added refinement UI controls in sidebar")
print("  ✓ Updated simulation to use enhanced version")
print("\nBackup saved to: streamlit_app_before_refinement.py")
print("\nRestart Streamlit to see changes:")
print("  Ctrl+C to stop, then: streamlit run streamlit_app.py")
print("="*70)
