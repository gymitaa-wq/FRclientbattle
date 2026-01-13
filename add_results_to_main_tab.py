"""Add results display to Generate & Run tab"""

with open('streamlit_streamlined.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section after "else: st.info..." and add results display
results_section = '''    else:
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

# ============================================================================'''

old_section = '''    else:
        st.info("👆 Click 'Generate Client Profile' to start")

# ============================================================================'''

content = content.replace(old_section, results_section)

with open('streamlit_streamlined.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added results display to Generate & Run tab")
print("Results will now show on the same page for easy demos!")
