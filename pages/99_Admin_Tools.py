"""
Admin Tools Page
Provides administrative functions like database backfills
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, SimulationResult
from streamlined_simulation import extract_final_products
from project_caii_framework import callModel
import json

st.set_page_config(page_title="Admin Tools", page_icon="🔧", layout="wide")

st.title("🔧 Admin Tools")
st.markdown("---")

# Password protection
st.sidebar.header("🔐 Authentication")
admin_password = st.sidebar.text_input("Admin Password", type="password", key="admin_pw")

# Simple password check (you can change this)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

if admin_password != ADMIN_PASSWORD:
    st.warning("⚠️ Please enter the admin password in the sidebar to access these tools.")
    st.stop()

st.success("✅ Authenticated")

# Backfill Products Tool
st.header("🔄 Backfill Product Extraction")

st.markdown("""
This tool re-runs the product extraction logic on existing simulations to fix any that were affected by the bug.

**What it does:**
1. Finds all simulations where `deal_closed = True`
2. Re-extracts products from the final proposal using the **fixed logic**
3. Updates the database with corrected product data

**Safe to run:** The tool compares old vs new products and only updates if there are differences.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Options")
    specific_sim_id = st.number_input(
        "Specific Simulation ID (leave as 0 for all)",
        min_value=0,
        value=0,
        help="Enter a simulation ID to fix only that one, or 0 to fix all"
    )
    
    dry_run = st.checkbox(
        "Dry Run (Preview Only)",
        value=True,
        help="If checked, will show what would change without updating the database"
    )

with col2:
    st.subheader("Status")
    if 'backfill_running' not in st.session_state:
        st.session_state['backfill_running'] = False
    
    if st.session_state['backfill_running']:
        st.info("⏳ Backfill in progress...")
    else:
        st.success("✅ Ready to run")

# Run button
if st.button("🚀 Run Backfill", type="primary", disabled=st.session_state['backfill_running']):
    st.session_state['backfill_running'] = True
    
    # Results container
    results_container = st.container()
    
    with results_container:
        st.markdown("---")
        st.subheader("📊 Backfill Results")
        
        session = SessionLocal()
        
        try:
            # Get simulations that need fixing
            if specific_sim_id > 0:
                query = session.query(SimulationResult).filter(
                    SimulationResult.id == specific_sim_id,
                    SimulationResult.deal_closed == True
                )
                st.info(f"🎯 Targeting simulation ID: {specific_sim_id}")
            else:
                query = session.query(SimulationResult).filter(
                    SimulationResult.deal_closed == True
                ).order_by(SimulationResult.timestamp.desc())
                st.info("🎯 Targeting all accepted simulations")
            
            simulations = query.all()
            
            st.write(f"**Found {len(simulations)} accepted simulations to check**")
            
            if dry_run:
                st.warning("🔍 DRY RUN MODE - No changes will be made to the database")
            else:
                st.warning("⚠️ LIVE MODE - Database will be updated!")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            fixed_count = 0
            unchanged_count = 0
            error_count = 0
            
            changes_log = []
            
            for idx, sim in enumerate(simulations):
                progress = (idx + 1) / len(simulations)
                progress_bar.progress(progress)
                status_text.text(f"Processing {idx + 1}/{len(simulations)}: Simulation ID {sim.id}")
                
                # Get proposal text from iterations_data
                try:
                    iterations = sim.iterations_data if sim.iterations_data else []
                    if not iterations:
                        error_count += 1
                        changes_log.append({
                            'sim_id': sim.id,
                            'status': 'SKIP',
                            'reason': 'No iterations data'
                        })
                        continue
                    
                    last_iteration = iterations[-1]
                    proposal_text = last_iteration.get('proposal', '')
                    
                    if not proposal_text:
                        error_count += 1
                        changes_log.append({
                            'sim_id': sim.id,
                            'status': 'SKIP',
                            'reason': 'No proposal text'
                        })
                        continue
                    
                except Exception as e:
                    error_count += 1
                    changes_log.append({
                        'sim_id': sim.id,
                        'status': 'ERROR',
                        'reason': f'Error reading iterations: {e}'
                    })
                    continue
                
                # Get old products (handle both JSON string and already-parsed list)
                old_products_raw = sim.final_products_data
                if isinstance(old_products_raw, str):
                    try:
                        old_products = json.loads(old_products_raw) if old_products_raw else []
                    except:
                        old_products = []
                elif old_products_raw is None:
                    old_products = []
                else:
                    old_products = old_products_raw
                
                # Re-extract with fixed logic
                try:
                    result = extract_final_products(proposal_text, accepted=True, callModel=callModel)
                    new_products = result['products']
                except Exception as e:
                    error_count += 1
                    changes_log.append({
                        'sim_id': sim.id,
                        'status': 'ERROR',
                        'reason': f'Failed to extract: {e}'
                    })
                    continue
                
                # Compare old vs new (handle different data formats for old_products)
                try:
                    # If old_products is a list of dicts
                    if old_products and isinstance(old_products[0], dict):
                        old_product_names = sorted([p.get('name', '') for p in old_products])
                    # If old_products is a list of strings (legacy format)
                    elif old_products and isinstance(old_products[0], str):
                        old_product_names = sorted(old_products)
                    # Empty or unknown format
                    else:
                        old_product_names = []
                except (IndexError, TypeError, AttributeError) as e:
                    # Fallback for any parsing issues
                    old_product_names = []
                
                new_product_names = sorted([p.get('name', '') for p in new_products])
                
                if old_product_names != new_product_names:
                    fixed_count += 1
                    changes_log.append({
                        'sim_id': sim.id,
                        'status': 'CHANGED',
                        'old_products': old_product_names,
                        'new_products': new_product_names,
                        'old_count': len(old_products),
                        'new_count': len(new_products)
                    })
                    
                    if not dry_run:
                        # Update the simulation
                        sim.final_products_data = new_products
                        sim.total_monthly_premium = result['total_monthly']
                        sim.product_names = ', '.join([p['name'] for p in new_products])
                else:
                    unchanged_count += 1
                    if unchanged_count <= 10:  # Log first 10 unchanged
                        changes_log.append({
                            'sim_id': sim.id,
                            'status': 'OK',
                            'products': old_product_names
                        })
            
            # Commit if live mode
            if not dry_run and fixed_count > 0:
                session.commit()
                st.success(f"✅ Committed {fixed_count} updates to database")
            elif dry_run and fixed_count > 0:
                st.info(f"🔍 Would update {fixed_count} records (dry run)")
            else:
                st.success("✅ No updates needed - all records are correct")
            
            # Summary
            st.markdown("---")
            st.subheader("📈 Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Checked", len(simulations))
            with col2:
                st.metric("Fixed", fixed_count, delta=f"+{fixed_count}" if fixed_count > 0 else None)
            with col3:
                st.metric("Unchanged", unchanged_count)
            with col4:
                st.metric("Errors", error_count, delta=f"-{error_count}" if error_count > 0 else None)
            
            # Detailed changes log
            if changes_log:
                st.markdown("---")
                st.subheader("📋 Detailed Changes Log")
                
                # Filter options
                show_filter = st.multiselect(
                    "Show Status",
                    options=['CHANGED', 'OK', 'SKIP', 'ERROR'],
                    default=['CHANGED', 'ERROR']
                )
                
                for log_entry in changes_log:
                    if log_entry['status'] not in show_filter:
                        continue
                    
                    if log_entry['status'] == 'CHANGED':
                        with st.expander(f"🔄 Sim ID {log_entry['sim_id']} - CHANGED"):
                            st.write(f"**Old** ({log_entry['old_count']} products): {log_entry['old_products']}")
                            st.write(f"**New** ({log_entry['new_count']} products): {log_entry['new_products']}")
                    
                    elif log_entry['status'] == 'OK':
                        st.success(f"✅ Sim ID {log_entry['sim_id']} - No changes needed: {log_entry['products']}")
                    
                    elif log_entry['status'] == 'SKIP':
                        st.warning(f"⏭️ Sim ID {log_entry['sim_id']} - SKIPPED: {log_entry['reason']}")
                    
                    elif log_entry['status'] == 'ERROR':
                        st.error(f"❌ Sim ID {log_entry['sim_id']} - ERROR: {log_entry['reason']}")
            
        except Exception as e:
            st.error(f"❌ Fatal error during backfill: {e}")
            import traceback
            st.code(traceback.format_exc())
        
        finally:
            session.close()
            st.session_state['backfill_running'] = False
            status_text.text("✅ Complete!")

# Database Stats
st.markdown("---")
st.header("📊 Database Statistics")

session = SessionLocal()
try:
    total_sims = session.query(SimulationResult).count()
    accepted_sims = session.query(SimulationResult).filter(SimulationResult.deal_closed == True).count()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Simulations", total_sims)
    with col2:
        st.metric("Accepted Deals", accepted_sims)
    with col3:
        acceptance_rate = (accepted_sims / total_sims * 100) if total_sims > 0 else 0
        st.metric("Acceptance Rate", f"{acceptance_rate:.1f}%")
        
except Exception as e:
    st.error(f"Error fetching stats: {e}")
finally:
    session.close()
