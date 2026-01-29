"""
Test script to verify product extraction fix works correctly
"""
import sys
import os

# Add current directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import after env is loaded
from streamlined_simulation import extract_final_products
from project_caii_framework import callModel

# Test case: Revised proposal with "WHAT'S CHANGED" mentioning removed Whole Life
test_proposal = """
## ACKNOWLEDGMENT
Thank you for your feedback. I've revised my recommendations based on your concerns about cost and flexibility.

## WHAT'S CHANGED
- **Removed Whole Life Insurance** (was $200/month for $500,000 coverage)
- Switched to Term 20 for more affordable coverage
- Added Roth IRA for flexible retirement savings
- Kept Disability Insurance as recommended

## WHY THESE CHANGES
Based on your feedback about preferring lower premiums and more flexibility, I've restructured the plan to focus on term coverage and tax-advantaged savings.

## REVISED RECOMMENDATIONS

**1. Term 20 (Term Life Insurance)**
- Coverage Amount: $1,100,000
- Estimated Monthly Premium: $150
- Rationale: Provides 20 years of protection during your peak mortgage and dependency years.

**2. Disability Income Insurance (Own Occupation)**
- Monthly Benefit: $5,000
- Estimated Monthly Premium: $95
- Rationale: Protects your income if you become disabled.

**3. Roth IRA (Retirement/Flexibility)**
- Monthly Contribution: $100
- Rationale: Tax-free growth and flexible access to contributions.

## TOTAL INVESTMENT
- Monthly: $345
- Annual: $4,140

This provides comprehensive protection at a more affordable price point.
"""

print("="*70)
print("TESTING PRODUCT EXTRACTION FIX")
print("="*70)

print("\nTest Proposal includes:")
print("- WHAT'S CHANGED: Mentions 'Removed Whole Life Insurance'")
print("- REVISED RECOMMENDATIONS: Term 20, Disability, Roth IRA")
print("\nExpected: Should extract products from REVISED RECOMMENDATIONS only")
print("Should NOT extract Whole Life (it was removed)")

print("\n" + "="*70)
print("RUNNING EXTRACTION...")
print("="*70)

result = extract_final_products(test_proposal, accepted=True, callModel=callModel)

print("\n" + "="*70)
print("RESULTS")
print("="*70)

print(f"\nProducts extracted: {len(result['products'])}")
for product in result['products']:
    print(f"  - {product['name']}: ${product['monthly_premium']}/month")

print(f"\nTotal Monthly: ${result['total_monthly']}")
print(f"Total Annual: ${result['total_annual']}")

# Verification
product_names = [p['name'] for p in result['products']]

print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

has_whole_life = any('whole life' in name.lower() for name in product_names)
has_term = any('term' in name.lower() for name in product_names)
has_disability = any('disability' in name.lower() for name in product_names)
has_roth = any('roth' in name.lower() or 'ira' in name.lower() for name in product_names)

print(f"\n[PASS] Has Term Life: {has_term}")
print(f"[PASS] Has Disability: {has_disability}")
print(f"[PASS] Has Roth IRA: {has_roth}")
print(f"[FAIL] Has Whole Life (should be False): {has_whole_life}")

if has_whole_life:
    print("\n[X] FAILED: Whole Life was extracted (but it was removed!)")
    print("The fix is NOT working correctly!")
elif has_term and has_disability and has_roth:
    print("\n[OK] PASSED: Correct products extracted from REVISED RECOMMENDATIONS")
    print("The fix is working correctly!")
else:
    print("\n[?] PARTIAL: Some products missing, but Whole Life correctly not extracted")

print("\n" + "="*70)
