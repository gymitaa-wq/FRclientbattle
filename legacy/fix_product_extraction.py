"""
Improved product extraction - only extracts from final recommendations section
"""

with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the extract_final_products function with a smarter version
old_function = '''def extract_final_products(proposal_text: str, accepted: bool) -> Dict[str, Any]:
    """
    Extracts final product details from proposal.
    
    Args:
        proposal_text: Final proposal text
        accepted: Whether deal was accepted
    
    Returns:
        Dict with product details
    """
    
    if not accepted:
        return {'products': [], 'total_monthly': 0, 'total_annual': 0}
    
    # Simple extraction (could be enhanced with better parsing)
    products = []
    
    # Look for product sections
    import re
    
    # Term life
    term_match = re.search(r'Term Life.*?\\$([0-9,]+).*?month', proposal_text, re.IGNORECASE | re.DOTALL)
    if term_match:
        products.append({
            'name': 'Term Life Insurance',
            'monthly_premium': term_match.group(1)
        })
    
    # Whole life
    whole_match = re.search(r'Whole Life.*?\\$([0-9,]+).*?month', proposal_text, re.IGNORECASE | re.DOTALL)
    if whole_match:
        products.append({
            'name': 'Whole Life Insurance',
            'monthly_premium': whole_match.group(1)
        })
    
    # Disability
    di_match = re.search(r'Disability.*?\\$([0-9,]+).*?month', proposal_text, re.IGNORECASE | re.DOTALL)
    if di_match:
        products.append({
            'name': 'Disability Insurance',
            'monthly_premium': di_match.group(1)
        })
    
    # Total
    total_match = re.search(r'Total.*?Monthly.*?\\$([0-9,]+)', proposal_text, re.IGNORECASE | re.DOTALL)
    total_monthly = int(total_match.group(1).replace(',', '')) if total_match else 0
    
    return {
        'products': products,
        'total_monthly': total_monthly,
        'total_annual': total_monthly * 12,
        'proposal_text': proposal_text
    }'''

new_function = '''def extract_final_products(proposal_text: str, accepted: bool) -> Dict[str, Any]:
    """
    Extracts final product details from proposal - ONLY from recommendations section.
    
    Args:
        proposal_text: Final proposal text
        accepted: Whether deal was accepted
    
    Returns:
        Dict with product details
    """
    
    if not accepted:
        return {'products': [], 'total_monthly': 0, 'total_annual': 0}
    
    import re
    
    # Extract only the recommendations section (after "RECOMMENDED" or "REVISED RECOMMENDATIONS")
    # This avoids matching products mentioned in "what's changed" or comparison sections
    recommendations_match = re.search(
        r'(?:REVISED RECOMMENDATIONS|RECOMMENDED PRODUCTS)(.*?)(?:TOTAL INVESTMENT|ADDRESSING YOUR CONCERNS|VALUE PROPOSITION|$)',
        proposal_text,
        re.IGNORECASE | re.DOTALL
    )
    
    if recommendations_match:
        recommendations_section = recommendations_match.group(1)
    else:
        # Fallback: use entire text if section not found
        recommendations_section = proposal_text
    
    products = []
    
    # Look for product sections ONLY in recommendations
    # Term life - look for "### 1. Term Life" or similar
    term_match = re.search(
        r'###.*?Term Life.*?\\n.*?Monthly.*?\\$([0-9,]+)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if term_match:
        products.append({
            'name': 'Term Life Insurance',
            'monthly_premium': term_match.group(1)
        })
    
    # Whole life - look for "### 2. Whole Life" or similar
    whole_match = re.search(
        r'###.*?Whole Life.*?\\n.*?Monthly.*?\\$([0-9,]+)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if whole_match:
        products.append({
            'name': 'Whole Life Insurance',
            'monthly_premium': whole_match.group(1)
        })
    
    # Disability - look for "### 3. Disability" or similar  
    di_match = re.search(
        r'###.*?Disability.*?\\n.*?Monthly.*?\\$([0-9,]+)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if di_match:
        products.append({
            'name': 'Disability Insurance',
            'monthly_premium': di_match.group(1)
        })
    
    # Total - look in TOTAL INVESTMENT section
    total_match = re.search(r'TOTAL.*?Monthly.*?\\$([0-9,]+)', proposal_text, re.IGNORECASE | re.DOTALL)
    total_monthly = int(total_match.group(1).replace(',', '')) if total_match else 0
    
    return {
        'products': products,
        'total_monthly': total_monthly,
        'total_annual': total_monthly * 12,
        'proposal_text': proposal_text
    }'''

content = content.replace(old_function, new_function)

with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Improved product extraction!")
print("Now only extracts from final recommendations section")
print("Ignores products mentioned in comparison/history text")
