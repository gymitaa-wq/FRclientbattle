"""
Streamlit App - Streamlined Simulation Workflow
Clean standalone version with profile-based simulation
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure DB is initialized
try:
    from database import init_db
    init_db()
except Exception as e:
    print(f"DB Init Error: {e}")

# Import streamlined simulation components
try:
    from structured_profile_generator import generate_structured_client_profile, format_profile_for_display
    from run_streamlined_simulation import run_streamlined_simulation
    from database import save_simulation, load_history_df as load_simulation_history, get_stats as get_history_stats
    from login_ui import require_login, show_user_header, get_current_username
    import pandas as pd
    ALL_MODULES_LOADED = True
except ImportError as e:
    ALL_MODULES_LOADED = False
    IMPORT_ERROR = str(e)

# Page config
st.set_page_config(
    page_title="Insurance Simulation - Streamlined",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
""", unsafe_allow_html=True)

# Check if modules loaded
if not ALL_MODULES_LOADED:
    st.error(f"❌ Failed to load modules: {IMPORT_ERROR}")
    st.stop()

# ==============================================================================
# LOGIN GATE - Require authentication before showing app
# ==============================================================================
if not require_login():
    st.stop()

# ==============================================================================
# MAIN APP (Shown only after login)
# ==============================================================================

# Header
st.markdown('<p class="main-header">🎯 Insurance Simulation - Streamlined Workflow</p>', unsafe_allow_html=True)
st.markdown("**Profile-Based Simulation with Iteration Summaries & Deal Analysis**")

# Sidebar
with st.sidebar:
    # Show logged-in user info
    show_user_header()
    
    # Debug Info (Temporary)
    with st.expander("🛠️ Debug Env Vars (Render)", expanded=False):
        st.write("Checking Environment Keys:")
        env_keys = list(os.environ.keys())
        st.write(f"- GOOGLE_CLIENT_ID present: {'GOOGLE_CLIENT_ID' in os.environ}")
        if 'GOOGLE_CLIENT_ID' in os.environ:
             st.code(os.environ['GOOGLE_CLIENT_ID'][:10] + "...")
             
        st.write(f"- GOOGLE_CLIENT_SECRET present: {'GOOGLE_CLIENT_SECRET' in os.environ}")
        st.write(f"- STREAMLIT_SHARING_MODE: {os.environ.get('STREAMLIT_SHARING_MODE', 'Not Set')}")
        st.write(f"- GOOGLE_OAUTH_REDIRECT_URI: {os.environ.get('GOOGLE_OAUTH_REDIRECT_URI', 'Not Set')}")
    
    st.markdown("## ⚙️ Configuration")
    
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
    
    # Model selection
    st.markdown("### 🤖 AI Model")
    model_option = st.selectbox(
        "Select Model",
        ["Gemini 3.0 Flash (Latest)", "gemini-3.0-pro", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "claude", "gpt"],
        index=0,
        help="AI model for simulation. 'Gemini 3.0 Flash' is the latest public model released December 2025."
    )
    
    # Refinement settings
    st.markdown("### 🔄 Refinement Settings")
    enable_refinement = st.checkbox(
        "Enable Iterative Refinement",
        value=True,
        help="FR refines proposal if rejected"
    )
    
    if enable_refinement:
        max_iterations = st.slider(
            "Max Iterations",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum refinement attempts"
        )
    else:
        max_iterations = 0
    
    st.markdown("---")
    st.markdown("### 📊 My Statistics")
    
    try:
        current_user = get_current_username()
        stats = get_history_stats(current_user)
        st.metric("Total Simulations", stats['total_simulations'])
        st.metric("Conversion Rate", f"{stats['conversion_rate']:.1f}%")
        st.metric("Avg Friction", f"{stats['avg_friction_score']:.1f}")
    except:
        st.info("No history yet")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎲 Generate & Run",
    "📊 Results",
    "📄 Details",
    "📈 History",
    "🤖 Batch Mode",
    "⚔️ Battle Engine"
])

# ============================================================================
# FUNCTION: RENDER CUSTOMIZATION UI (Reusable)
# ============================================================================
def render_profile_customization_ui(key_prefix="run"):
    """Renders profile customization widgets and returns overrides dict."""
    with st.expander("📝 Profile Customization (Optional - Extreme Ranges)", expanded=False):
        st.caption("⚙️ Leave fields at default/zero to let AI randomize. Supports extreme cases!")
        
        # Reset callback
        def reset_customization():
            st.session_state[f"{key_prefix}_custom_age"] = 0
            st.session_state[f"{key_prefix}_custom_gender"] = "Random"
            st.session_state[f"{key_prefix}_custom_marital"] = "Random"
            st.session_state[f"{key_prefix}_custom_children"] = 0
            st.session_state[f"{key_prefix}_custom_income"] = 0
            st.session_state[f"{key_prefix}_custom_401k"] = -1
            st.session_state[f"{key_prefix}_custom_occupation"] = "Random"
            st.session_state[f"{key_prefix}_custom_skepticism"] = 0
            st.session_state[f"{key_prefix}_custom_risk"] = "Random"
            st.session_state[f"{key_prefix}_custom_smoker"] = "Random"
            st.session_state[f"{key_prefix}_custom_savings_total"] = -1
            st.session_state[f"{key_prefix}_custom_debt_total"] = -1
            st.session_state[f"{key_prefix}_custom_net_worth"] = 0
            st.session_state[f"{key_prefix}_custom_health_status"] = "Random"

        st.markdown("**👤 Demographics**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            custom_age = st.number_input("Age (0=Random)", 0, 100, key=f"{key_prefix}_custom_age", help="Range: 18-100")
        with col2:
            custom_gender = st.selectbox("Gender", ["Random", "Male", "Female"], key=f"{key_prefix}_custom_gender")
        with col3:
            custom_marital = st.selectbox("Marital Status", ["Random", "Single", "Married", "Divorced", "Widowed"], key=f"{key_prefix}_custom_marital")
        with col4:
            custom_children = st.number_input("Children (0=Random)", 0, 10, key=f"{key_prefix}_custom_children")
        
        st.markdown("**💼 Employment & Income**")
        col1, col2, col3 = st.columns(3)
        with col1:
            custom_occupation = st.selectbox("Occupation", ["Random", "Software Engineer", "Doctor", "Lawyer", "Teacher", "Sales Manager", "Business Owner", "Executive", "Entrepreneur", "Retired", "Unemployed"], key=f"{key_prefix}_custom_occupation")
        with col2:
            custom_income = st.number_input("Annual Income ($0=Random)", 0, 10000000, step=10000, key=f"{key_prefix}_custom_income")
        with col3:
            custom_net_worth = st.number_input("Net Worth ($0=Random)", -5000000, 50000000, step=50000, key=f"{key_prefix}_custom_net_worth", value=0)

        col1, col2, col3 = st.columns(3)
        with col1:
             custom_401k = st.number_input("401(k) Balance ($-1=Random)", -1, 5000000, step=10000, key=f"{key_prefix}_custom_401k")
        with col2:
            custom_savings_total = st.number_input("Total Liquid Savings ($-1=Random)", -1, 10000000, step=10000, key=f"{key_prefix}_custom_savings_total")
        with col3:
            custom_debt_total = st.number_input("Total Debt ($-1=Random)", -1, 10000000, step=10000, key=f"{key_prefix}_custom_debt_total")
        
        st.markdown("**🧠 Psychology & Health**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            custom_skepticism = st.slider("Skepticism", 0, 10, key=f"{key_prefix}_custom_skepticism")
        with col2:
            custom_risk = st.selectbox("Risk Tolerance", ["Random", "Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"], key=f"{key_prefix}_custom_risk")
        with col3:
            custom_health_status = st.selectbox("Health", ["Random", "Excellent", "Good", "Fair", "Poor", "Terminal"], key=f"{key_prefix}_custom_health_status")
        with col4:
            custom_smoker = st.selectbox("Smoker?", ["Random", "Yes", "No"], key=f"{key_prefix}_custom_smoker")
        
        st.button("🗑️ Reset All Customizations", on_click=reset_customization, type="secondary", key=f"{key_prefix}_reset_btn")
    
    # Build dictionary
    overrides = {}
    if custom_age > 0: overrides['age'] = custom_age
    if custom_gender != "Random": overrides['gender'] = custom_gender
    if custom_marital != "Random": overrides['marital_status'] = custom_marital
    if custom_children > 0: overrides['num_children'] = custom_children
    if custom_income > 0: overrides['annual_income'] = custom_income
    if custom_401k != -1: overrides['savings_401k'] = custom_401k
    if custom_occupation != "Random": overrides['occupation'] = custom_occupation
    if custom_skepticism > 0: overrides['skepticism_level'] = custom_skepticism
    if custom_risk != "Random": overrides['risk_tolerance'] = custom_risk.replace("Very ", "") if "Very " in custom_risk else custom_risk
    if custom_smoker != "Random": overrides['smoker'] = (custom_smoker == "Yes")
    if custom_net_worth != 0: overrides['net_worth'] = custom_net_worth
    if custom_savings_total != -1: overrides['total_assets'] = custom_savings_total
    if custom_debt_total != -1: overrides['total_debt'] = custom_debt_total
    if custom_health_status != "Random": overrides['health_status'] = custom_health_status
    
    return overrides

# ============================================================================
# TAB 1: GENERATE & RUN
# ============================================================================

with tab1:
    st.markdown("## 🎲 Client Profile Generation")
    
    # --- Profile Customization Controls (Refactored) ---
    overrides = render_profile_customization_ui(key_prefix="tab1")
    
    # Generate Profile Button
    if st.button("🎲 Generate Client Profile", type="primary"):
        with st.spinner("Generating detailed client profile..."):
            st.session_state['client_profile_dict'] = generate_structured_client_profile(overrides)
            st.session_state['client_profile_text'] = format_profile_for_display(st.session_state['client_profile_dict'])
            st.success("✅ Client profile generated!")
            st.rerun()

    # Display Profile
    if 'client_profile_text' in st.session_state:
        st.markdown("### 👤 Generated Client Profile")
        
        # Two column layout for profile display
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.text_area(
                "Profile Details",
                value=st.session_state['client_profile_text'],
                height=400,
                key=f"profile_{st.session_state['client_profile_dict']['profile_id']}"
            )
        
        with col2:
            # Quick stats
            profile = st.session_state['client_profile_dict']
            st.metric("Age", f"{profile['age']} years")
            st.metric("Income", f"${profile['total_household_income']:,}")
            st.metric("Coverage Gap", f"${profile['coverage_gap']:,}")
            st.metric("Skepticism", f"{profile['skepticism_level']}/10")
            
            st.markdown("---")
            
            # Model Selection
            model_option = st.selectbox(
                "Select AI Model for Simulation", 
                ["gemini-3.0-flash", "gemini-3.0-pro", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                index=0,
                help="Gemini 3.0 Flash is the latest public model from Google (December 2025)."
            )
            
            # Simulation controls
            max_iterations = st.number_input("Max Iterations", 1, 10, 5, help="Maximum conversation rounds")
            enable_refinement = st.checkbox("Enable Adaptive Refinement", value=True, help="AI learns from rejections")
            
            # Run Simulation Button
            if st.button("🚀 Run Simulation", use_container_width=True, type="primary"):
                with st.spinner("Running simulation... (this may take 2-3 minutes)"):
                    try:
                        result = run_streamlined_simulation(
                            profile=st.session_state['client_profile_dict'],
                            max_iterations=max_iterations,
                            enable_refinement=enable_refinement,
                            model_name=model_option
                        )
                        
                        st.session_state['simulation_result'] = result
                        
                        # Save to DB with username
                        try:
                            save_simulation(result, get_current_username())
                            st.toast("Simulation saved to history", icon="💾")
                        except Exception as e:
                            print(f"Error saving manual sim: {e}")
                        
                        st.success("✅ Simulation complete!")
                        st.rerun()
                        
                    except Exception as e:
                        error_msg = str(e)
                        if "Rate Limit" in error_msg:
                            st.error(f"🛑 {error_msg}")
                            st.warning("👉 Look at the sidebar on the left to enter your key!")
                        else:
                            st.error(f"❌ Simulation failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())
    else:
        st.info("👆 Click 'Generate Client Profile' to start")
    
    # ============================================================================
    # DISPLAY RESULTS ON SAME PAGE (for demos)
    # ============================================================================
    
    if 'simulation_result' in st.session_state:
        st.markdown("---")
        st.markdown("## 📊 Simulation Results")
        
        result = st.session_state['simulation_result']
        analysis = result['outcome_analysis']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = "✅ CLOSED" if result['deal_closed'] else "❌ NOT CLOSED"
            st.metric("Deal Status", status)
        
        with col2:
            st.metric("Total Iterations", result['total_iterations'])
        
        with col3:
            st.metric("Final Friction", f"{result['final_friction_score']:.1f}/100")
        
        with col4:
            if analysis.get('friction_reduction', 0) > 0:
                st.metric("Friction Reduction", f"{analysis['friction_reduction']:.1f} pts")
        
        st.markdown("---")
        
        # Iteration summaries
        st.markdown("### 🔄 Iteration Summary")
        
        for iter_data in result['iterations']:
            iteration = iter_data['iteration']
            accepted = iter_data['accepted']
            friction = iter_data['friction_score']
            status_emoji = "✅" if accepted else "❌"
            
            with st.expander(f"Iteration {iteration} {status_emoji} - Friction: {friction:.1f}/100", expanded=(iteration==result['total_iterations']-1)):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**FR Proposal (Summary):**")
                    st.text_area(
                        f"Proposal {iteration}",
                        value=iter_data['proposal'][:500] + "..." if len(iter_data['proposal']) > 500 else iter_data['proposal'],
                        height=150,
                        disabled=True,
                        key=f"main_proposal_{iteration}"
                    )
                
                with col2:
                    st.markdown("**Client Decision:**")
                    st.text_area(
                        f"Decision {iteration}",
                        value=iter_data['decision_text'][:500] + "..." if len(iter_data['decision_text']) > 500 else iter_data['decision_text'],
                        height=150,
                        disabled=True,
                        key=f"main_decision_{iteration}"
                    )
        
        st.markdown("---")
        
        # Deal outcome
        if result['deal_closed']:
            st.markdown("### 🎉 Deal Closed!")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Closure Reasons:**")
                for reason in analysis.get('closure_reasons', []):
                    st.markdown(f"- ✅ {reason}")
                
                if analysis.get('winning_factors'):
                    st.markdown("**Winning Factors:**")
                    for factor in analysis['winning_factors']:
                        st.markdown(f"- 🏆 {factor}")
            
            with col2:
                st.markdown("**💼 Final Products:**")
                products = result['final_products']
                if products.get('products'):
                    for product in products['products']:
                        st.markdown(f"• **{product['name']}**: ${product['monthly_premium']}/month")
                    
                    st.markdown(f"**Total**: ${products['total_monthly']:,}/month (${products['total_annual']:,}/year)")
                else:
                    st.info("See Details tab for full product information")
        
        else:
            st.markdown("### ❌ Deal Not Closed")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Rejection Reasons:**")
                for reason in analysis.get('rejection_reasons', []):
                    st.markdown(f"- ❌ {reason}")
            
            with col2:
                if analysis.get('remaining_concerns'):
                    st.markdown("**Remaining Concerns:**")
                    for concern in analysis['remaining_concerns'][:3]:
                        st.markdown(f"- ⚠️ {concern}")

# ============================================================================
# TAB 2: RESULTS
# ============================================================================

with tab2:
    if 'simulation_result' in st.session_state:
        result = st.session_state['simulation_result']
        analysis = result['outcome_analysis']
        
        st.markdown("## 📊 Simulation Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = "✅ CLOSED" if result['deal_closed'] else "❌ NOT CLOSED"
            st.metric("Deal Status", status)
        
        with col2:
            st.metric("Total Iterations", result['total_iterations'])
        
        with col3:
            st.metric("Final Friction", f"{result['final_friction_score']:.1f}/100")
        
        with col4:
            if analysis.get('friction_reduction', 0) > 0:
                st.metric("Friction Reduction", f"{analysis['friction_reduction']:.1f} pts")
        
        st.markdown("---")
        
        # Deal outcome analysis
        if result['deal_closed']:
            st.markdown("### 🎉 Deal Closed!")
            
            st.markdown("**Closure Reasons:**")
            for reason in analysis.get('closure_reasons', []):
                st.markdown(f"- ✅ {reason}")
            
            if analysis.get('winning_factors'):
                st.markdown("**Winning Factors:**")
                for factor in analysis['winning_factors']:
                    st.markdown(f"- 🏆 {factor}")
            
            # Final products
            st.markdown("---")
            st.markdown("### 💼 Final Products")
            
            products = result['final_products']
            if products.get('products'):
                for product in products['products']:
                    st.markdown(f"**{product['name']}**: ${product['monthly_premium']}/month")
                
                st.markdown(f"**Total Monthly**: ${products['total_monthly']:,}")
                st.markdown(f"**Total Annual**: ${products['total_annual']:,}")
            else:
                st.info("See proposal text for product details")
        
        else:
            st.markdown("### ❌ Deal Not Closed")
            
            st.markdown("**Rejection Reasons:**")
            for reason in analysis.get('rejection_reasons', []):
                st.markdown(f"- ❌ {reason}")
            
            if analysis.get('remaining_concerns'):
                st.markdown("**Remaining Concerns:**")
                for concern in analysis['remaining_concerns'][:3]:
                    st.markdown(f"- ⚠️ {concern}")
    
    else:
        st.info("No simulation results yet. Run a simulation in Tab 1.")

# ============================================================================
# TAB 3: DETAILS
# ============================================================================

with tab3:
    if 'simulation_result' in st.session_state:
        result = st.session_state['simulation_result']
        
        st.markdown("## 📄 Iteration Details")
        
        # Show each iteration
        for iter_data in result['iterations']:
            iteration = iter_data['iteration']
            accepted = iter_data['accepted']
            friction = iter_data['friction_score']
            
            status_emoji = "✅" if accepted else "❌"
            
            with st.expander(f"Iteration {iteration} {status_emoji} - Friction: {friction:.1f}/100", expanded=(iteration==0)):
                st.markdown(f"**Status**: {'ACCEPTED' if accepted else 'REJECTED'}")
                st.markdown(f"**Friction Score**: {friction:.1f}/100")
                
                st.markdown("---")
                st.markdown("**FR Proposal:**")
                st.text_area(
                    f"Proposal {iteration}",
                    value=iter_data['proposal'],
                    height=300,
                    disabled=True,
                    key=f"proposal_{iteration}"
                )
                
                st.markdown("**AI Critique:**")
                st.text_area(
                    f"Critique {iteration}",
                    value=iter_data['ai_critique'],
                    height=200,
                    disabled=True,
                    key=f"critique_{iteration}"
                )
                
                st.markdown("**Client Decision:**")
                st.text_area(
                    f"Decision {iteration}",
                    value=iter_data['decision_text'],
                    height=200,
                    disabled=True,
                    key=f"decision_{iteration}"
                )
    else:
        st.info("No simulation details yet. Run a simulation in Tab 1.")

# ============================================================================
# TAB 4: HISTORY
# ============================================================================

with tab4:
    st.markdown("## 📈 My Simulation History")
    
    current_user = get_current_username()
    st.caption(f"Viewing history for user: **`{current_user}`**")
    
    # Import new helper
    from database import get_simulation_details

    try:
        df = load_simulation_history(current_user)
        
        if not df.empty:
            # Statistics
            stats = get_history_stats(current_user)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Simulations", stats['total_simulations'])
            with col2:
                st.metric("Conversion Rate", f"{stats['conversion_rate']:.1f}%")
            with col3:
                st.metric("Avg Friction", f"{stats['avg_friction_score']:.1f}")
            with col4:
                if 'latest_timestamp' in stats:
                    st.metric("Latest Run", stats['latest_timestamp'][:10])
            
            st.markdown("---")
            
            # Interactive Data table
            st.markdown("### 📋 Click a row to see full conversation details")
            
            event = st.dataframe(
                df,
                use_container_width=True,
                height=400,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Show details if row selected
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                row_data = df.iloc[selected_index]
                sim_id = int(row_data['id'])
                
                details = get_simulation_details(sim_id)
                
                if details:
                    st.markdown("---")
                    st.markdown(f"## 💬 Full Conversation History (Sim ID: {sim_id})")
                    
                    iterations = details['iterations_data']
                    if iterations:
                        for i, iter_data in enumerate(iterations):
                            iter_num = iter_data.get('iteration', i)
                            with st.expander(f"🔄 Iteration {iter_num} - {iter_data.get('decision_text', '').splitlines()[0][:50]}...", expanded=True):
                                col_a, col_b = st.columns(2)
                                
                                with col_a:
                                    st.markdown("#### 🧑‍💼 Advisor Proposal")
                                    st.info(iter_data.get('proposal', 'No proposal data'))
                                
                                with col_b:
                                    st.markdown("#### 🤖 AI Critique")
                                    st.warning(iter_data.get('ai_critique', 'No critique data'))
                                
                                st.markdown("#### 🧑 Client Decision")
                                decision_color = "green" if iter_data.get('accepted') else "red"
                                st.markdown(f":{decision_color}[{iter_data.get('decision_text', 'No decision data')}]")
                    else:
                        st.warning("No detailed iteration data available for this simulation (legacy record).")
                
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download History CSV",
                csv,
                "simulation_history.csv",
                "text/csv",
                use_container_width=True
            )
            
            # Clear history
            if st.button("🗑️ Clear History", type="secondary"):
                import os
                if os.path.exists("simulation_history.csv"):
                    os.remove("simulation_history.csv")
                    st.success("History cleared!")
                    st.rerun()
        else:
            st.info("📭 No simulation history yet. Run some simulations to see data here.")
    
    except Exception as e:
        # Fallback to prevent app crash if History tab fails
        st.error(f"Error loading history: {e}")
        import traceback
        st.code(traceback.format_exc())

# ============================================================================
# TAB 5: BATCH MODE
# ============================================================================

with tab5:
    st.markdown("## 🤖 Automatic Batch Simulator")
    st.markdown("Run continuous simulations to generate dataset and test robustness.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        batch_size = st.number_input("Number of Simulations", min_value=1, max_value=50, value=10)
        
        start_batch = st.button("🚀 Start Automatic Batch", type="primary", use_container_width=True)
        
        st.info(f"Each simulation takes approx 1-3 minutes using **{model_option}**.")
    
    if start_batch:
        # Containers for live updates
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Data storage
        batch_results = []
        batch_df_placeholder = st.empty()
        
        # Stop button logic (place holder)
        stop_placeholder = st.empty()
        
        
        current_user = get_current_username()
        
        st.info(f"🚀 **Starting batch mode for user: `{current_user}`**")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        wins = 0
        total_friction = 0
        
        try:
            import time
            for i in range(batch_size):
                if i > 0:
                    time.sleep(5) # Rate limit buffer
                    
                sim_num = i + 1
                
                # Define callback for live updates
                def batch_status_callback(msg):
                    status_text.markdown(f"**Sim {sim_num}/{batch_size}:** {msg}")
                
                try:
                    # Run simulation
                    result = run_streamlined_simulation(
                        profile=None, # Random profile
                        max_iterations=max_iterations,
                        enable_refinement=enable_refinement,
                        model_name=model_option,
                        status_callback=batch_status_callback
                    )
                    
                    # Process result
                    is_closed = result['deal_closed']
                    friction = result['final_friction_score']
                    profile = result['profile']
                    
                    if is_closed:
                        wins += 1
                    total_friction += friction
                    
                    # Add to list
                    row = {
                        "Sim #": sim_num,
                        "Client ID": profile['profile_id'],
                        "Age": profile['age'],
                        "Income": f"${profile['total_household_income']:,}",
                        "Deal Closed": "✅ YES" if is_closed else "❌ NO",
                        "Friction": f"{friction:.1f}",
                        "Iterations": result['total_iterations']
                    }
                    batch_results.append(row)
                    
                    # Update table
                    df = pd.DataFrame(batch_results)
                    batch_df_placeholder.dataframe(df, use_container_width=True)
                    
                    # Update stats
                    with stats_col1:
                        st.metric("Completed", f"{sim_num}/{batch_size}")
                    with stats_col2:
                        win_rate = (wins / sim_num) * 100
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                    with stats_col3:
                        avg_fric = total_friction / sim_num
                        st.metric("Avg Friction", f"{avg_fric:.1f}")
                    
                    # Update progress
                    progress_bar.progress(sim_num / batch_size)
                    
                    # Save to DB immediately with explicit error handling
                    try:
                        sim_id = save_simulation(result, current_user)
                        st.toast(f"✅ Saved Sim #{sim_num} (ID: {sim_id}) for user '{current_user}'", icon="💾")
                        print(f"DEBUG: Saved batch run {sim_num} to DB with ID {sim_id} for user {current_user}")
                    except Exception as save_err:
                        st.error(f"❌ Failed to save Sim #{sim_num}: {save_err}")
                        print(f"ERROR: Failed to save batch sim {sim_num}: {save_err}")
                        import traceback
                        traceback.print_exc()
                    
                    
                except Exception as e:
                    st.error(f"Error in Simulation {sim_num}: {e}")
                    import traceback
                    traceback.print_exc()
            
            st.success(f"✅ Batch simulation complete! {batch_size} runs completed.")
            import time
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"Batch execution failed: {e}")



# Footer
st.markdown("---")
st.markdown("**Project CAII** - Multi-Agent Insurance Simulation | Streamlined Workflow")

# ============================================================================
# TAB 6: BATTLE ENGINE
# ============================================================================
with tab6:
    st.markdown("## ⚔️ Battle Engine: Digital Twin Stress Test")
    st.caption("The most rigorous stress-test. 1. Generate Hybrid Proposal -> 2. Ruthless AI Attack -> 3. Auto-Refined Defense.")

    # Customization UI
    battle_overrides = render_profile_customization_ui(key_prefix="battle")

    # Generate Profile
    if st.button("🎲 Generate Client Profile (Battle Mode)", type="primary", key="battle_gen_btn"):
        with st.spinner("Generating target profile..."):
            st.session_state.battle_profile = generate_structured_client_profile(battle_overrides)
            st.rerun()

    # Display Profile & Run Battle
    if 'battle_profile' in st.session_state:
        profile = st.session_state.battle_profile
        
        with st.expander("👤 Target Client Profile", expanded=False):
            st.text(format_profile_for_display(profile))
            
        st.info(f"Target Acquired: **{profile['profile_id']}** - {profile['age']}yo {profile['occupation']} (Skepticism: {profile['skepticism_level']}/10)")
        
        model_name = st.selectbox(
            "Select Adversary Model",
            ["gemini-3.0-flash", "gemini-3.0-pro"],
            key="battle_model",
            help="Using Gemini 3.0 models for maximum stress testing with latest AI capabilities."
        )

        if st.button("🔥 BEGIN STRESS TEST", type="primary", use_container_width=True):
            from battle_engine import run_battle_stress_test
            from project_caii_framework import callModel
            from database import save_battle_result
            
            status_container = st.empty()
            
            def update_status(msg):
                status_container.info(f"🚀 {msg}")
            
            try:
                # Run the battle
                results = run_battle_stress_test(
                    profile, 
                    callModel, 
                    model_name=model_name,
                    status_callback=update_status
                )
                
                status_container.success("✅ Stress Test Complete!")
                
                # Save to database
                try:
                    current_user = get_current_username()
                    battle_id = save_battle_result(
                        profile=profile,
                        stage1_proposal=results['stage_1_proposal'],
                        stage2_attack=results['stage_2_attack'],
                        stage3_defense=results['stage_3_refined'],
                        model_name=model_name,
                        username=current_user,
                        success=True,
                        error_message=None
                    )
                    st.toast(f"Battle #{battle_id} saved to history", icon="💾")
                except Exception as e:
                    print(f"Error saving battle result: {e}")
                    st.warning(f"Battle completed but failed to save: {e}")
                
                # Display Results
                st.markdown("### 1️⃣ The Proposal")
                with st.expander("📄 Stage 1: Hybrid Proposal (Whole Life + Term)", expanded=False):
                    st.markdown(results['stage_1_proposal'])
                
                st.markdown("### 2️⃣ The Attack")
                with st.expander("😈 Stage 2: AI Adversary 'Vulnerability Report'", expanded=True):
                    st.error(results['stage_2_attack'])  # Red box for attack
                
                st.markdown("### 3️⃣ The Defense")
                with st.expander("💎 Stage 3: Battle-Hardened Strategy (Pre-bunked)", expanded=True):
                    st.success(results['stage_3_refined']) # Green box for solution
                    
            except Exception as e:
                error_msg = str(e)
                status_container.error(f"Battle failed: {error_msg}")
                
                # Save failed battle
                try:
                    current_user = get_current_username()
                    save_battle_result(
                        profile=profile,
                        stage1_proposal="",
                        stage2_attack="",
                        stage3_defense="",
                        model_name=model_name,
                        username=current_user,
                        success=False,
                        error_message=error_msg
                    )
                except Exception as save_err:
                    print(f"Failed to save error battle: {save_err}")
                
                import traceback
                st.code(traceback.format_exc())
    
    # ============================================================================
    # BATTLE HISTORY SECTION
    # ============================================================================
    st.markdown("---")
    st.markdown("## 📜 Battle History")
    st.caption("Click any row to review the full 3-stage battle report")
    
    from database import load_battle_history_df, get_battle_details, get_battle_stats
    
    current_user = get_current_username()
    
    try:
        # Show stats
        battle_stats = get_battle_stats(current_user)
        if battle_stats['total_battles'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Battles", battle_stats['total_battles'])
            with col2:
                st.metric("Success Rate", f"{battle_stats['success_rate']:.1f}%")
            with col3:
                st.metric("Avg Skepticism", f"{battle_stats['avg_skepticism']:.1f}/10")
        
        # Load and display battle history
        battle_df = load_battle_history_df(current_user)
        
        if not battle_df.empty:
            st.markdown("### 🗂️ Click a row to view full battle details")
            
            event = st.dataframe(
                battle_df,
                use_container_width=True,
                height=300,
                on_select="rerun",
                selection_mode="single-row",
                hide_index=True
            )
            
            # Show details if row selected
            if len(event.selection.rows) > 0:
                selected_index = event.selection.rows[0]
                row_data = battle_df.iloc[selected_index]
                battle_id = int(row_data['id'])
                
                details = get_battle_details(battle_id)
                
                if details and details['success']:
                    st.markdown("---")
                    st.markdown(f"## ⚔️ Battle Report #{battle_id}")
                    
                    # Battle metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Client ID", details['client_id'])
                    with col2:
                        st.metric("Age", details['age'])
                    with col3:
                        st.metric("Skepticism", f"{details['skepticism_level']}/10")
                    with col4:
                        st.metric("Model", details['model_name'])
                    
                    # Three stages
                    st.markdown("### 1️⃣ Initial Proposal")
                    with st.expander("📄 View Stage 1: Hybrid Proposal", expanded=False):
                        st.markdown(details['stage1_proposal'])
                    
                    st.markdown("### 2️⃣ AI Attack")
                    with st.expander("😈 View Stage 2: Adversary Report", expanded=True):
                        st.error(details['stage2_attack'])
                    
                    st.markdown("### 3️⃣ Refined Defense")
                    with st.expander("💎 View Stage 3: Battle-Hardened Strategy", expanded=True):
                        st.success(details['stage3_defense'])
                elif details and not details['success']:
                    st.error(f"❌ Battle #{battle_id} failed with error: {details['error_message']}")
        else:
            st.info("📭 No battle history yet. Run a stress test above to begin!")
            
    except Exception as e:
        st.error(f"Error loading battle history: {e}")
        import traceback
        st.code(traceback.format_exc())
