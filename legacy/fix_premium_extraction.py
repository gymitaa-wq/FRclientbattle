"""
Fix product extraction to get correct premiums and calculate total properly
"""

with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the extract_final_products function with improved version
old_function_start = "def extract_final_products(proposal_text: str, accepted: bool) -> Dict[str, Any]:"
old_function_end = "        'proposal_text': proposal_text\n    }"

# Find the function
import re
match = re.search(
    r'(def extract_final_products\(proposal_text: str, accepted: bool\) -\u003e Dict\[str, Any\]:.*?return \{.*?\'proposal_text\': proposal_text\s*\})',
    content,
    re.DOTALL
)

if match:
    new_function = '''def extract_final_products(proposal_text: str, accepted: bool) -> Dict[str, Any]:
    """
    Extracts final product details from proposal - looks for PREMIUM specifically.
    
    Args:
        proposal_text: Final proposal text
        accepted: Whether deal was accepted
    
    Returns:
        Dict with product details
    """
    
    if not accepted:
        return {'products': [], 'total_monthly': 0, 'total_annual': 0}
    
    import re
    
    # Extract only the recommendations section
    recommendations_match = re.search(
        r'(?:REVISED RECOMMENDATIONS|RECOMMENDED PRODUCTS)(.*?)(?:TOTAL INVESTMENT|ADDRESSING YOUR CONCERNS|VALUE PROPOSITION|$)',
        proposal_text,
        re.IGNORECASE | re.DOTALL
    )
    
    if recommendations_match:
        recommendations_section = recommendations_match.group(1)
    else:
        recommendations_section = proposal_text
    
    products = []
    
    # Term Life - look for "premium" or "cost" specifically, not "benefit"
    term_match = re.search(
        r'###.*?Term Life.*?(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if term_match:
        premium_str = term_match.group(1).replace(',', '')
        products.append({
            'name': 'Term Life Insurance',
            'monthly_premium': term_match.group(1),
            'premium_value': int(premium_str)
        })
    
    # Whole Life - look for "premium" or "cost" specifically
    whole_match = re.search(
        r'###.*?Whole Life.*?(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if whole_match:
        premium_str = whole_match.group(1).replace(',', '')
        products.append({
            'name': 'Whole Life Insurance',
            'monthly_premium': whole_match.group(1),
            'premium_value': int(premium_str)
        })
    
    # Disability - look for "premium" or "cost", NOT "benefit"
    # This is tricky because DI has both benefit amount and premium
    di_match = re.search(
        r'###.*?Disability.*?(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if di_match:
        premium_str = di_match.group(1).replace(',', '')
        products.append({
            'name': 'Disability Insurance',
            'monthly_premium': di_match.group(1),
            'premium_value': int(premium_str)
        })
    
    # Calculate total from extracted premiums
    total_monthly = sum(p.get('premium_value', 0) for p in products)
    
    # Also try to extract from TOTAL INVESTMENT section as backup
    total_match = re.search(r'TOTAL.*?Monthly.*?\\$([0-9,]+)', proposal_text, re.IGNORECASE | re.DOTALL)
    if total_match:
        total_from_text = int(total_match.group(1).replace(',', ''))
        # Use the total from text if it seems reasonable
        if abs(total_from_text - total_monthly) < 100:
            total_monthly = total_from_text
    
    return {
        'products': products,
        'total_monthly': total_monthly,
        'total_annual': total_monthly * 12,
        'proposal_text': proposal_text
    }'''
    
    content = content[:match.start()] + new_function + content[match.end():]
    
    with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed product extraction!")
    print("Now looks for 'premium' or 'cost' specifically")
    print("Calculates total by summing extracted premiums")
    print("Avoids confusing benefit amounts with premiums")
else:
    print("❌ Could not find function to replace")
