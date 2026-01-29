"""
Backfill script to re-extract products for simulations that were affected by the bug.

This script:
1. Finds all simulations where deal_status='accepted'
2. Re-runs extract_final_products on the proposal_text
3. Updates the database with the corrected product data

Run this after deploying the fix to production.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal, SimulationResult
from streamlined_simulation import extract_final_products
from project_caii_framework import callModel
import json

def backfill_product_extraction(dry_run=True, sim_id=None):
    """
    Re-extract products for accepted simulations.
    
    Args:
        dry_run: If True, only print what would be changed without updating database
        sim_id: Optional specific simulation ID to fix (otherwise fixes all)
    """
    session = SessionLocal()
    
    try:
        # Get simulations that need fixing (where deal was closed/accepted)
        if sim_id:
            query = session.query(SimulationResult).filter(
                SimulationResult.id == sim_id,
                SimulationResult.deal_closed == True
            )
        else:
            query = session.query(SimulationResult).filter(
                SimulationResult.deal_closed == True
            ).order_by(SimulationResult.timestamp.desc())
        
        simulations = query.all()
        
        print(f"\nFound {len(simulations)} accepted simulations to check")
        print("=" * 70)
        
        fixed_count = 0
        unchanged_count = 0
        
        for sim in simulations:
            # Get proposal text from iterations_data (last iteration)
            try:
                iterations = sim.iterations_data if sim.iterations_data else []
                if not iterations:
                    print(f"\n[SKIP] sim_id={sim.id}: No iterations data")
                    continue
                
                # Get the final proposal from last iteration
                last_iteration = iterations[-1]
                proposal_text = last_iteration.get('proposal', '')
                
                if not proposal_text:
                    print(f"\n[SKIP] sim_id={sim.id}: No proposal text in last iteration")
                    continue
                
            except Exception as e:
                print(f"\n[ERROR] sim_id={sim.id}: Error reading iterations - {e}")
                continue
            
            # Get old products
            old_products = sim.final_products_data or []
            
            # Re-extract with fixed logic
            try:
                result = extract_final_products(proposal_text, accepted=True, callModel=callModel)
                new_products = result['products']
            except Exception as e:
                print(f"\n[ERROR] sim_id={sim.id}: Failed to extract - {e}")
                continue
            
            # Compare old vs new
            old_product_names = sorted([p.get('name', '') for p in old_products])
            new_product_names = sorted([p.get('name', '') for p in new_products])
            
            if old_product_names != new_product_names:
                fixed_count += 1
                print(f"\n[CHANGE] sim_id={sim.id}")
                print(f"  OLD ({len(old_products)} products): {old_product_names}")
                print(f"  NEW ({len(new_products)} products): {new_product_names}")
                
                if not dry_run:
                    # Update the simulation
                    sim.final_products_data = new_products
                    sim.total_monthly_premium = result['total_monthly']
                    sim.product_names = ', '.join([p['name'] for p in new_products])
                    print(f"  → Marked for update")
            else:
                unchanged_count += 1
                if unchanged_count <= 5:  # Only print first few unchanged
                    print(f"[OK] sim_id={sim.id} - No changes needed")
        
        if not dry_run:
            session.commit()
            print(f"\n✓ Committed {fixed_count} updates to database")
        else:
            print(f"\n[DRY RUN] Would update {fixed_count} records")
        
        print(f"\nSummary:")
        print(f"  Fixed: {fixed_count}")
        print(f"  Unchanged: {unchanged_count}")
        print(f"  Total: {len(simulations)}")
        
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backfill product extraction for simulations")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating database")
    parser.add_argument("--sim-id", type=int, help="Fix specific simulation ID only")
    parser.add_argument("--live", action="store_true", help="Actually update the database")
    
    args = parser.parse_args()
    
    dry_run = not args.live  # Default to dry run unless --live is specified
    
    if args.live:
        print("\n⚠️  WARNING: Running in LIVE mode - will update database!")
        response = input("Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    else:
        print("\n[DRY RUN MODE] - No changes will be made to database")
        print("Use --live to actually update the database\n")
    
    backfill_product_extraction(dry_run=dry_run, sim_id=args.sim_id)
