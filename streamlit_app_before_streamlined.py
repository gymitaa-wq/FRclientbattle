"""
Project CAII - Streamlit UI
Interactive visualization for the Multi-Agent Simulation Framework

This Streamlit app provides real-time visualization of the LangGraph workflow,
displaying each agent's output and generated documents.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to path to import the framework
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from project_caii_framework import (
        run_simulation,
        SimulationState,
        SAMPLE_EMAIL_HISTORY,
        create_simulation_graph,
        callModel
    )
    FRAMEWORK_LOADED = True
except ImportError as e:
    FRAMEWORK_LOADED = False
    IMPORT_ERROR = str(e)

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

# Import enhanced simulation with refinement
try:
    from run_simulation_enhanced import run_simulation as run_simulation_enhanced
    REFINEMENT_AVAILABLE = True
except ImportError:
    REFINEMENT_AVAILABLE = False
    run_simulation_enhanced = None


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Project CAII - Multi-Agent Simulation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    
    .node-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .product-card {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
    }
    
    .product-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2ca02c;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = None

if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False

if 'current_node' not in st.session_state:
    st.session_state.current_node = None


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Project+CAII", use_container_width=True)
    
    st.markdown("### ⚙️ Configuration")
    
    # Model selection
    model_option = st.selectbox(
        "Select LLM Model",
        ["gemini", "claude", "gpt"],
        index=0,
        help="Choose which AI model to use for the simulation"
    )
    
    # API Key configuration
    st.markdown("### 🔑 API Configuration")
    
    api_key_input = st.text_input(
        f"{model_option.upper()} API Key",
        type="password",
        help=f"Enter your {model_option.upper()} API key"
    )
    
    if api_key_input:
        if model_option == "gemini":
            os.environ["GOOGLE_API_KEY"] = api_key_input
        elif model_option == "claude":
            os.environ["ANTHROPIC_API_KEY"] = api_key_input
        elif model_option == "gpt":
            os.environ["OPENAI_API_KEY"] = api_key_input
    
    # Databricks configuration (optional)
    st.markdown("### 🧱 Databricks (Optional)")
    
    use_databricks = st.checkbox("Use Databricks Serving Endpoint")
    
    if use_databricks:
        databricks_endpoint = st.text_input("Databricks Endpoint URL")
        databricks_token = st.text_input("Databricks Token", type="password")
        
        if databricks_endpoint and databricks_token:
            os.environ["DATABRICKS_SERVING_ENDPOINT"] = databricks_endpoint
            os.environ["DATABRICKS_TOKEN"] = databricks_token
    
    # Iterative Refinement configuration
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
    st.markdown("### 📊 MLflow Tracking")
    
    mlflow_tracking = st.checkbox("Enable MLflow Tracking", value=True)
    
    if mlflow_tracking:
        experiment_name = st.text_input(
            "Experiment Name",
            value="Project_CAII",
            help="MLflow experiment name for tracking"
        )
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About Project CAII"):
        st.markdown("""
        **Project CAII** simulates the competitive cycle between Northwestern Mutual 
        advisors and public AI consultations.
        
        **Workflow:**
        1. Extract client profile from emails
        2. Simulate AI consultation
        3. Generate NM advisor proposal
        4. Create product plans
        5. AI critique of proposal
        6. Final client decision
        
        **Goal:** Develop AI-proof sales strategies
        """)


# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<div class="main-header">🤖 Project CAII - Multi-Agent Simulation Framework</div>', 
            unsafe_allow_html=True)

# Check if framework loaded
if not FRAMEWORK_LOADED:
    st.error(f"❌ Failed to load framework: {IMPORT_ERROR}")
    st.info("Please ensure all dependencies are installed: `pip install -r requirements.txt`")
    st.stop()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📧 Input & Run",
    "📊 Results Dashboard",
    "📄 Documents",
    "🔬 Analysis",
    "📈 History"
])


# ============================================================================
# TAB 1: INPUT & RUN
# ============================================================================

with tab1:
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
    else:

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
    st.caption(f"Character count: {char_count:,}")
    
    # Run simulation button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        run_button = st.button(
            "🚀 Run Simulation",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.simulation_running or not email_history
        )
    
    if run_button:
        st.session_state.simulation_running = True
        st.session_state.simulation_state = None
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Node progress containers
        node_containers = {
            "extract_profile": st.empty(),
            "ai_consultation": st.empty(),
            "advisor_proposal": st.empty(),
            "product_plans": st.empty(),
            "ai_scrutiny": st.empty(),
            "final_decision": st.empty()
        }
        
        try:
            # Update progress
            status_text.markdown("### 🔄 Running Simulation...")
            
            # Node 1: Extract Profile
            progress_bar.progress(10)
            node_containers["extract_profile"].markdown(
                '<div class="node-header">📋 Node 1: Extracting Client Profile</div>',
                unsafe_allow_html=True
            )
            
            # Run the simulation
            with st.spinner("Processing..."):
                # Use enhanced simulation if refinement enabled
                if REFINEMENT_AVAILABLE and enable_refinement:
                    result = run_simulation_enhanced(
                        email_history,
                        model=model_option,
                        enable_refinement=True,
                        max_iterations=max_iterations
                    )
                else:
                    result = run_simulation(email_history, model=model_option)
            
            # Store result
            st.session_state.simulation_state = result
            
            # Save to CSV history
            if CSV_EXPORT_AVAILABLE:
                try:
                    save_simulation_to_csv(result)
                    st.info("📊 Results saved to simulation_history.csv")
                except Exception as e:
                    st.warning(f"Could not save to CSV: {e}")
            
            # Complete
            progress_bar.progress(100)
            status_text.markdown("### ✅ Simulation Complete!")
            
            # Show success message
            st.success(f"""
            ✅ **Simulation completed successfully!**
            
            - Decision: **{'CONVERT' if result['metadata'].get('converted') else 'REJECT'}**
            - Friction Score: **{result['friction_score']:.1f}/100**
            - Products Generated: **{len(result['product_plans'])}**
            """)
            
            # Switch to results tab
            st.info("👉 Switch to the **Results Dashboard** tab to view detailed results.")
            
        except Exception as e:
            st.error(f"❌ Simulation failed: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
        
        finally:
            st.session_state.simulation_running = False


# ============================================================================
# TAB 2: RESULTS DASHBOARD
# ============================================================================

with tab2:
    st.markdown("## 📊 Simulation Results Dashboard")
    
    if st.session_state.simulation_state is None:
        st.warning("⚠️ No simulation results yet. Run a simulation in the **Input & Run** tab.")
    else:
        state = st.session_state.simulation_state
        
        # Key Metrics Row
        st.markdown("### 🎯 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{'✅' if state['metadata'].get('converted') else '❌'}</div>
                <div class="metric-label">Decision</div>
                <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                    {'CONVERT' if state['metadata'].get('converted') else 'REJECT'}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{state['friction_score']:.0f}</div>
                <div class="metric-label">Friction Score</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem; color: #666;">
                    out of 100
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(state['product_plans'])}</div>
                <div class="metric-label">Products</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem; color: #666;">
                    Generated
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            model_used = state['metadata'].get('model', 'Unknown')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🤖</div>
                <div class="metric-label">Model</div>
                <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                    {model_used.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Workflow Visualization
        st.markdown("### 🔄 Workflow Results")
        
        # Node 1: Client Profile
        with st.expander("📋 **Node 1: Client Profile Extraction**", expanded=False):
            st.markdown("**Extracted Profile:**")
            st.text_area("Profile", state['persona_profile'], height=300, key="profile_display")
            st.download_button(
                "📥 Download Profile",
                state['persona_profile'],
                file_name="client_profile.txt",
                mime="text/plain"
            )
        
        # Node 2: Initial AI Advice
        with st.expander("🤖 **Node 2: Initial AI Consultation**", expanded=False):
            st.markdown("**Public AI Advice (DIY Recommendations):**")
            st.text_area("AI Advice", state['initial_ai_advice'], height=300, key="ai_advice_display")
            st.download_button(
                "📥 Download AI Advice",
                state['initial_ai_advice'],
                file_name="initial_ai_advice.txt",
                mime="text/plain"
            )
        
        # Node 3: Advisor Proposal
        with st.expander("💼 **Node 3: NM Advisor Proposal**", expanded=False):
            st.markdown("**Northwestern Mutual Advisor Recommendation:**")
            st.text_area("Proposal", state['proposal_text'], height=300, key="proposal_display")
            st.download_button(
                "📥 Download Proposal",
                state['proposal_text'],
                file_name="nm_advisor_proposal.txt",
                mime="text/plain"
            )
        
        # Node 4: Product Plans
        with st.expander("📦 **Node 4: Individual Product Plans**", expanded=False):
            st.markdown(f"**{len(state['product_plans'])} Product Plans Generated:**")
            
            for product_key, product_plan in state['product_plans'].items():
                product_name = product_key.replace('_', ' ').title()
                
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">📄 {product_name}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.text_area(
                    f"{product_name} Plan",
                    product_plan,
                    height=200,
                    key=f"product_{product_key}_display"
                )
                
                st.download_button(
                    f"📥 Download {product_name}",
                    product_plan,
                    file_name=f"{product_key}_plan.txt",
                    mime="text/plain",
                    key=f"download_{product_key}"
                )
        
        # Node 5: AI Critique
        with st.expander("🔍 **Node 5: AI Scrutiny & Critique**", expanded=False):
            st.markdown("**Public AI's Critique of NM Proposal:**")
            st.text_area("Critique", state['ai_critique'], height=300, key="critique_display")
            st.download_button(
                "📥 Download Critique",
                state['ai_critique'],
                file_name="ai_critique.txt",
                mime="text/plain"
            )
        
        # Node 6: Final Decision
        with st.expander("⚖️ **Node 6: Final Client Decision**", expanded=True):
            st.markdown("**Client's Final Decision & Reasoning:**")
            st.text_area("Decision", state['outcome'], height=300, key="outcome_display")
            
            # Highlight decision
            if state['metadata'].get('converted'):
                st.success("✅ **DECISION: CONVERT** - Client accepted NM proposal")
            else:
                st.error("❌ **DECISION: REJECT** - Client declined NM proposal")
            
            st.download_button(
                "📥 Download Decision",
                state['outcome'],
                file_name="final_decision.txt",
                mime="text/plain"
            )


# ============================================================================
# TAB 3: DOCUMENTS
# ============================================================================

with tab3:
    st.markdown("## 📄 Generated Documents")
    
    if st.session_state.simulation_state is None:
        st.warning("⚠️ No documents yet. Run a simulation first.")
    else:
        state = st.session_state.simulation_state
        
        st.info("All documents generated during the simulation. These can be downloaded individually or as a package.")
        
        # Document selector
        doc_type = st.selectbox(
            "Select Document",
            [
                "Client Profile",
                "Initial AI Advice",
                "NM Advisor Proposal",
                "Term Life Plan",
                "Whole Life Plan",
                "Disability Insurance Plan",
                "Annuity Plan",
                "Cash Buffer Plan",
                "AI Critique",
                "Final Decision"
            ]
        )
        
        # Display selected document
        doc_mapping = {
            "Client Profile": state['persona_profile'],
            "Initial AI Advice": state['initial_ai_advice'],
            "NM Advisor Proposal": state['proposal_text'],
            "Term Life Plan": state['product_plans'].get('term_life', 'Not generated'),
            "Whole Life Plan": state['product_plans'].get('whole_life', 'Not generated'),
            "Disability Insurance Plan": state['product_plans'].get('disability', 'Not generated'),
            "Annuity Plan": state['product_plans'].get('annuity', 'Not generated'),
            "Cash Buffer Plan": state['product_plans'].get('cash_buffer', 'Not generated'),
            "AI Critique": state['ai_critique'],
            "Final Decision": state['outcome']
        }
        
        st.markdown(f"### {doc_type}")
        st.text_area("Document Content", doc_mapping[doc_type], height=500, key="doc_viewer")
        
        # Download button
        st.download_button(
            f"📥 Download {doc_type}",
            doc_mapping[doc_type],
            file_name=f"{doc_type.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )
        
        st.markdown("---")
        
        # Download all documents as JSON
        st.markdown("### 📦 Download All Documents")
        
        all_docs = {
            "metadata": state['metadata'],
            "friction_score": state['friction_score'],
            "client_profile": state['persona_profile'],
            "initial_ai_advice": state['initial_ai_advice'],
            "nm_proposal": state['proposal_text'],
            "product_plans": state['product_plans'],
            "ai_critique": state['ai_critique'],
            "final_decision": state['outcome']
        }
        
        st.download_button(
            "📥 Download All (JSON)",
            json.dumps(all_docs, indent=2),
            file_name=f"caii_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


# ============================================================================
# TAB 4: ANALYSIS
# ============================================================================

with tab4:
    st.markdown("## 🔬 Simulation Analysis")
    
    if st.session_state.simulation_state is None:
        st.warning("⚠️ No analysis available. Run a simulation first.")
    else:
        state = st.session_state.simulation_state
        
        # Friction Score Analysis
        st.markdown("### 📊 Friction Score Analysis")
        
        friction = state['friction_score']
        
        # Friction gauge
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create a visual gauge
            st.progress(friction / 100)
            
            if friction <= 20:
                interpretation = "🟢 **Low Friction** - High alignment between AI and NM advice"
                color = "success"
            elif friction <= 40:
                interpretation = "🟡 **Moderate-Low Friction** - Some tension, but clear winner"
                color = "info"
            elif friction <= 60:
                interpretation = "🟠 **Moderate Friction** - Significant conflict, difficult choice"
                color = "warning"
            elif friction <= 80:
                interpretation = "🔴 **High Friction** - Major conflict, very close decision"
                color = "warning"
            else:
                interpretation = "🔴 **Extreme Friction** - Severe conflict, almost a coin flip"
                color = "error"
            
            if color == "success":
                st.success(interpretation)
            elif color == "info":
                st.info(interpretation)
            elif color == "warning":
                st.warning(interpretation)
            else:
                st.error(interpretation)
        
        with col2:
            st.metric("Friction Score", f"{friction:.1f}/100")
        
        st.markdown("---")
        
        # Decision Analysis
        st.markdown("### ⚖️ Decision Breakdown")
        
        converted = state['metadata'].get('converted', False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Final Decision:**")
            if converted:
                st.success("✅ **CONVERT** - Accepted NM Proposal")
            else:
                st.error("❌ **REJECT** - Declined NM Proposal")
        
        with col2:
            st.markdown("**Conversion Rate:**")
            st.metric("This Simulation", "100%" if converted else "0%")
        
        st.markdown("---")
        
        # Timing Analysis
        st.markdown("### ⏱️ Execution Timeline")
        
        metadata = state['metadata']
        
        timeline_data = []
        
        if 'extraction_timestamp' in metadata:
            timeline_data.append(("Profile Extraction", metadata['extraction_timestamp']))
        if 'ai_consultation_timestamp' in metadata:
            timeline_data.append(("AI Consultation", metadata['ai_consultation_timestamp']))
        if 'advisor_proposal_timestamp' in metadata:
            timeline_data.append(("Advisor Proposal", metadata['advisor_proposal_timestamp']))
        if 'product_plans_timestamp' in metadata:
            timeline_data.append(("Product Plans", metadata['product_plans_timestamp']))
        if 'ai_critique_timestamp' in metadata:
            timeline_data.append(("AI Critique", metadata['ai_critique_timestamp']))
        if 'decision_timestamp' in metadata:
            timeline_data.append(("Final Decision", metadata['decision_timestamp']))
        
        for node_name, timestamp in timeline_data:
            st.text(f"✓ {node_name}: {timestamp}")
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("### 💡 Insights & Recommendations")
        
        if converted and friction < 40:
            st.info("""
            **Strong Conversion with Low Friction**
            
            This client profile shows high receptivity to professional guidance. The NM proposal 
            aligned well with the client's needs and successfully addressed AI-generated concerns.
            
            **Recommendation:** Use this profile as a template for similar client segments.
            """)
        elif converted and friction >= 40:
            st.warning("""
            **Conversion Despite High Friction**
            
            The client converted but experienced significant conflict. This suggests the NM proposal 
            had compelling elements that overcame AI-generated skepticism.
            
            **Recommendation:** Analyze which specific arguments won the client over. These are 
            your "AI-proof" value propositions.
            """)
        elif not converted and friction < 40:
            st.error("""
            **Rejection with Low Friction**
            
            The client rejected the proposal despite low conflict between AI and NM advice. This 
            suggests other factors (price, trust, timing) drove the decision.
            
            **Recommendation:** Focus on non-product factors like relationship building and timing.
            """)
        else:
            st.error("""
            **Rejection with High Friction**
            
            The AI-generated advice created significant doubt that the NM proposal couldn't overcome.
            
            **Recommendation:** Develop stronger counter-arguments to common AI objections. Focus on 
            value propositions that AI cannot replicate (personalization, ongoing support, holistic planning).
            """)



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


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>Project CAII</strong> - Multi-Agent Simulation Framework</p>
    <p>Northwestern Mutual | AI-Proof Sales Strategy Development</p>
    <p style="font-size: 0.9rem;">Powered by LangGraph + Google Gemini + MLflow</p>
</div>
""", unsafe_allow_html=True)
