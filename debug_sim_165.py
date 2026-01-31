"""
Debug script to check simulation ID 165 product extraction
Fetches from database and re-runs extraction to compare
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

# Simulation ID to debug
SIM_ID = 165

print("="*70)
print(f"DEBUGGING SIMULATION ID {SIM_ID}")
print("="*70)

session = SessionLocal()

try:
    # Fetch simulation from database
    sim = session.query(SimulationResult).filter(SimulationResult.id == SIM_ID).first()
    
    if not sim:
        print(f"\n❌ Simulation ID {SIM_ID} not found in database")
        exit(1)
    
    print(f"\n✅ Found simulation ID {SIM_ID}")
    print(f"   Deal Closed: {sim.deal_closed}")
    print(f"   Username: {sim.username}")
    print(f"   Timestamp: {sim.timestamp}")
    
    # Show what's currently stored in database
    print(f"\n{'='*70}")
    print("CURRENTLY STORED IN DATABASE:")
    print(f"{'='*70}")
    print(f"Product Names (string): {sim.product_names}")
    print(f"Total Monthly Premium: ${sim.total_monthly_premium}")
    
    # Show final_products_data
    final_products_db = sim.final_products_data
    if isinstance(final_products_db, str):
        try:
            final_products_db = json.loads(final_products_db)
        except:
            pass
    
    if final_products_db and isinstance(final_products_db, dict):
        products_list = final_products_db.get('products', [])
        print(f"\nFinal Products Data ({len(products_list)} products):")
        for p in products_list:
            if isinstance(p, dict):
                print(f"  - {p.get('name', 'Unknown')}: ${p.get('monthly_premium', 0)}/month")
            else:
                print(f"  - {p}")
    
    # Get the final proposal text
    iterations = sim.iterations_data or []
    if not iterations:
        print(f"\n❌ No iterations data found")
        exit(1)
    
    last_iteration = iterations[-1]
    proposal_text = last_iteration.get('proposal', '')
    
    if not proposal_text:
        print(f"\n❌ No proposal text found in last iteration")
        exit(1)
    
    print(f"\n{'='*70}")
    print("FINAL PROPOSAL TEXT:")
    print(f"{'='*70}")
    print(proposal_text)
    
   # Re-run extraction with current logic
    print(f"\n{'='*70}")
    print("RE-RUNNING PRODUCT EXTRACTION (WITH FIXED LOGIC):")
    print(f"{'='*70}")
    
    result = extract_final_products(proposal_text, accepted=True, callModel=callModel)
    
    print(f"\nExtracted {len(result['products'])} products:")
    for p in result['products']:
        print(f"  - {p['name']}: ${p['monthly_premium']}/month")
    print(f"\nTotal Monthly: ${result['total_monthly']}")
    print(f"Total Annual: ${result.get('total_annual', result['total_monthly'] * 12)}")
    
    # Compare
    print(f"\n{'='*70}")
    print("COMPARISON:")
    print(f"{'='*70}")
    
    db_products = []
    if final_products_db and isinstance(final_products_db, dict):
        db_products_list = final_products_db.get('products', [])
        if db_products_list:
            if isinstance(db_products_list[0], dict):
                db_products = [p.get('name', '') for p in db_products_list]
            else:
                db_products = db_products_list
    
    new_products = [p['name'] for p in result['products']]
    
    print(f"\nStored in DB: {sorted(db_products)}")
    print(f"Should be:    {sorted(new_products)}")
    
    if sorted(db_products) == sorted(new_products):
        print(f"\n✅ MATCH - Database has correct products!")
    else:
        print(f"\n❌ MISMATCH - Database has wrong products!")
        print(f"\nMissing from DB: {set(new_products) - set(db_products)}")
        print(f"Extra in DB: {set(db_products) - set(new_products)}")
    
finally:
    session.close()
