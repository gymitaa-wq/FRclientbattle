"""
Backfill Script: Extract Product Names from Accepted Proposals
Uses LLM to extract product names from existing simulation records where product_names is empty.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, SimulationResult
from project_caii_framework import callModel
import json
import re


def extract_products_from_proposal_llm(proposal_text: str) -> tuple[str, float]:
    """
    Use LLM to extract product names and total premium from proposal text.
    
    Args:
        proposal_text: The final proposal text
        
    Returns:
        Tuple of (product_names_string, total_monthly_premium)
    """
    
    if not proposal_text or len(proposal_text) < 50:
        return "", 0.0
    
    # Create extraction prompt
    prompt = f"""Extract insurance product names and total monthly premium from this proposal.

PROPOSAL:
{proposal_text[:3000]}

Return ONLY this JSON (no other text):
```json
{{
    "products": ["Term Life Insurance", "Disability Insurance"],
    "total_monthly": 245
}}
```

Rules:
- Extract product names as simple strings (e.g., "Term Life Insurance", "Whole Life Insurance")
- Extract MONTHLY premium total (not annual, not coverage amount)
- Return ONLY the JSON in the code block
- If no products found, return {{"products": [], "total_monthly": 0}}
"""
    
    try:
        # Call LLM
        response = callModel(prompt, model="gemini", max_tokens=500)
        
        # Extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: find any JSON object
            start = response.find('{')
            end = response.rfind('}')
            if start >= 0 and end > start:
                json_str = response[start:end+1]
            else:
                print(f"  ⚠️ No JSON found in LLM response")
                return "", 0.0
        
        # Parse JSON
        data = json.loads(json_str)
        products = data.get('products', [])
        total_monthly = data.get('total_monthly', 0)
        
        # Join product names
        product_names_str = "; ".join(products) if products else ""
        
        return product_names_str, float(total_monthly)
        
    except Exception as e:
        print(f"  ❌ LLM extraction failed: {e}")
        return "", 0.0


def backfill_product_names():
    """
    Backfill product_names for existing simulation records where it's empty.
    """
    
    db = SessionLocal()
    
    try:
        # Query simulations where deal_closed=True and product_names is empty
        print("🔍 Searching for simulations with missing product names...")
        
        simulations = db.query(SimulationResult).filter(
            SimulationResult.deal_closed == True,
            (SimulationResult.product_names == "") | (SimulationResult.product_names == None)
        ).all()
        
        print(f"📊 Found {len(simulations)} accepted deals with missing product names")
        
        if not simulations:
            print("✅ No records need backfilling!")
            return
        
        updated_count = 0
        failed_count = 0
        
        for i, sim in enumerate(simulations, 1):
            print(f"\n[{i}/{len(simulations)}] Processing Simulation #{sim.id}")
            print(f"  Client: {sim.client_id}, Age: {sim.age}, {sim.occupation}")
            
            # Get final proposal from iterations_data
            iterations = sim.iterations_data
            if not iterations or len(iterations) == 0:
                print("  ⚠️ No iterations data found")
                failed_count += 1
                continue
            
            final_iteration = iterations[-1]
            proposal_text = final_iteration.get('proposal', '')
            
            if not proposal_text:
                print("  ⚠️ No proposal text found")
                failed_count += 1
                continue
            
            print(f"  📄 Extracting from proposal ({len(proposal_text)} chars)...")
            
            # Extract using LLM
            product_names, total_monthly = extract_products_from_proposal_llm(proposal_text)
            
            if product_names:
                # Update the record
                sim.product_names = product_names
                if total_monthly > 0 and (sim.total_monthly_premium == 0 or sim.total_monthly_premium is None):
                    sim.total_monthly_premium = total_monthly
                
                db.commit()
                
                print(f"  ✅ Updated: {product_names}")
                print(f"  💰 Premium: ${total_monthly}/month")
                updated_count += 1
            else:
                print(f"  ⚠️ No products extracted")
                failed_count += 1
        
        print("\n" + "="*70)
        print("BACKFILL COMPLETE")
        print("="*70)
        print(f"✅ Successfully updated: {updated_count} records")
        print(f"⚠️ Failed/Skipped: {failed_count} records")
        print(f"📊 Total processed: {len(simulations)} records")
        
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("="*70)
    print("PRODUCT NAMES BACKFILL SCRIPT")
    print("="*70)
    print("\nThis script will:")
    print("1. Find accepted simulations with missing product names")
    print("2. Extract products from proposals using LLM")
    print("3. Update the database records")
    print("\nNote: This uses LLM calls and may take several minutes.\n")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    backfill_product_names()
    
    print("\n✅ Script complete!")
