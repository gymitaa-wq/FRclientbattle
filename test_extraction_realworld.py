"""
Test current product extraction with real-world example
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from streamlined_simulation import extract_final_products
from project_caii_framework import callModel

# Example from Simulation 132 - should extract Term 20 + Disability + Long-term Care
test_proposal = """
## MY RECOMMENDATIONS FOR YOUR FINANCIAL PROTECTION

Based on your profile - 45 years old, married with children, $140K household income - here's what I recommend:

### 1. **Term 20 Life Insurance** ($1,000,000 coverage)
- **Monthly Premium**: $85
- **Why**: Provides 20 years of protection during your peak earning years and while children are dependent
- **Coverage**: $1M ensures your family maintains their lifestyle if something happens to you

### 2. **Disability Insurance** (Own Occupation)
- **Monthly Benefit**: $4,500 
- **Monthly Premium**: $120
- **Why**: Protects 70% of your income if you become unable to work in your specific profession

### 3. **Long-Term Care Insurance**
- **Daily Benefit**: $200
- **Monthly Premium**: $95
- **Why**: At 45, locking in rates now saves thousands versus waiting until 55+

## TOTAL INVESTMENT
- **Monthly**: $300
- **Annual**: $3,600

This comprehensive plan protects your income, your family's future, and your retirement assets from catastrophic medical costs.
"""

print("="*70)
print("TESTING PRODUCT EXTRACTION - Real World Example")
print("="*70)

print("\nProposal contains:")
print("  - Term 20 Life Insurance: $85/month")
print("  - Disability Insurance: $120/month")
print("  - Long-Term Care Insurance: $95/month")

print("\nExpected: Should extract all 3 products")
print("="*70)

result = extract_final_products(test_proposal, accepted=True, callModel=callModel)

print("\n" + "="*70)
print("EXTRACTION RESULTS")
print("="*70)

print(f"\nProducts extracted: {len(result['products'])}")
for p in result['products']:
    print(f"  - {p['name']}: ${p['monthly_premium']}/month")

print(f"\nTotal Monthly: ${result['total_monthly']}")
print(f"Total Annual: ${result.get('total_annual', result['total_monthly'] * 12)}")

# Verify
product_names = [p['name'] for p in result['products']]
has_term = any('term' in name.lower() for name in product_names)
has_disability = any('disability' in name.lower() for name in product_names)
has_ltc = any('long' in name.lower() or 'care' in name.lower() for name in product_names)

print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

print(f"\n[{'PASS' if has_term else 'FAIL'}] Has Term Life Insurance: {has_term}")
print(f"[{'PASS' if has_disability else 'FAIL'}] Has Disability Insurance: {has_disability}")
print(f"[{'PASS' if has_ltc else 'FAIL'}] Has Long-Term Care: {has_ltc}")

if has_term and has_disability and has_ltc:
    print("\n[OK] All 3 products correctly extracted!")
    exit(0)
else:
    print("\n[FAIL] Missing products!")
    print(f"Extracted: {product_names}")
    exit(1)
