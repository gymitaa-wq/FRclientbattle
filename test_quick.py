"""
Quick test: Verify product extraction is working correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from streamlined_simulation import extract_final_products
from project_caii_framework import callModel

# Test proposal with revision
test_proposal = """
## ACKNOWLEDGMENT
Thank you for your feedback. I've revised my recommendations.

## WHAT'S CHANGED
- **Removed Whole Life Insurance** (was $200/month for $500,000 coverage)

## REVISED RECOMMENDATIONS

**1. Term 20 (Term Life Insurance)**
- Coverage Amount: $1,100,000
- Estimated Monthly Premium: $150

**2. Disability Income Insurance**
- Monthly Benefit: $5,000
- Estimated Monthly Premium: $95

**3. Roth IRA**
- Monthly Contribution: $100

## TOTAL INVESTMENT
- Monthly: $345
"""

print("Testing product extraction fix...")
result = extract_final_products(test_proposal, accepted=True, callModel=callModel)

product_names = [p['name'] for p in result['products']]
has_whole_life = any('whole life' in name.lower() for name in product_names)

print(f"\nProducts found: {len(result['products'])}")
for p in result['products']:
    print(f"  - {p['name']}: ${p['monthly_premium']}/month")

print(f"\nHas Whole Life: {has_whole_life}")

if has_whole_life:
    print("\n[FAIL] Bug still exists - Whole Life was extracted despite being removed!")
    exit(1)
else:
    print("\n[PASS] Fix is working - Whole Life correctly NOT extracted!")
    exit(0)
