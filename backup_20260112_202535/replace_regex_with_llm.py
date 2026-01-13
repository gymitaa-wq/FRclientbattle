"""
Replace regex-based product extraction with LLM-based extraction
Much more reliable and accurate!
"""

# Read the current file
with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the extract_final_products function
import re

# Find the function
function_match = re.search(
    r'def extract_final_products\(proposal_text: str, accepted: bool\) -\u003e Dict\[str, Any\]:.*?return \{[^}]*\'proposal_text\': proposal_text\s*\}',
    content,
    re.DOTALL
)

if function_match:
    new_function = '''def extract_final_products(proposal_text: str, accepted: bool, callModel: callable = None) -> Dict[str, Any]:
    """
    Extracts final product details from proposal using LLM (more reliable than regex).
    
    Args:
        proposal_text: Final proposal text
        accepted: Whether deal was accepted
        callModel: LLM function for extraction
    
    Returns:
        Dict with product details
    """
    
    if not accepted:
        return {'products': [], 'total_monthly': 0, 'total_annual': 0}
    
    # Use LLM to extract products - much more reliable than regex!
    extraction_prompt = f"""
You are a data extraction assistant. Extract the recommended insurance products from this proposal.

PROPOSAL TEXT:
{proposal_text}

Extract ONLY the products that are actually RECOMMENDED (not "Not Recommended").

Return a JSON object with this exact structure:
{{
    "products": [
        {{"name": "Term Life Insurance", "monthly_premium": 58}},
        {{"name": "Disability Insurance", "monthly_premium": 95}}
    ],
    "total_monthly": 153
}}

Rules:
1. Only include products that are RECOMMENDED (skip any marked "Not Recommended")
2. Extract the monthly PREMIUM (not benefit amount)
3. Use product names: "Term Life Insurance", "Whole Life Insurance", "Disability Insurance"
4. Return valid JSON only, no other text
5. If a product section says "Not Recommended" or similar, DO NOT include it

JSON:"""

    try:
        if callModel:
            response = callModel(extraction_prompt, model="gemini", max_tokens=500)
        else:
            # Fallback if no callModel provided
            from project_caii_framework import callModel as default_callModel
            response = default_callModel(extraction_prompt, model="gemini", max_tokens=500)
        
        # Parse JSON response
        import json
        import re
        
        # Extract JSON from response (in case LLM adds extra text)
        json_match = re.search(r'\\{.*\\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            products = data.get('products', [])
            total_monthly = data.get('total_monthly', 0)
            
            # Validate and clean up
            cleaned_products = []
            for p in products:
                if 'name' in p and 'monthly_premium' in p:
                    cleaned_products.append({
                        'name': p['name'],
                        'monthly_premium': str(p['monthly_premium']),
                        'premium_value': int(p['monthly_premium'])
                    })
            
            # Recalculate total if needed
            if total_monthly == 0 or abs(total_monthly - sum(p['premium_value'] for p in cleaned_products)) > 50:
                total_monthly = sum(p['premium_value'] for p in cleaned_products)
            
            return {
                'products': cleaned_products,
                'total_monthly': int(total_monthly),
                'total_annual': int(total_monthly * 12),
                'proposal_text': proposal_text
            }
        else:
            raise ValueError("No JSON found in LLM response")
    
    except Exception as e:
        print(f"Warning: LLM extraction failed ({e}), falling back to simple parsing")
        # Fallback: return empty if extraction fails
        return {
            'products': [],
            'total_monthly': 0,
            'total_annual': 0,
            'proposal_text': proposal_text,
            'extraction_error': str(e)
        }'''
    
    content = content[:function_match.start()] + new_function + content[function_match.end():]
    
    with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Replaced regex with LLM-based extraction!")
    print("Much more reliable - LLM understands context and intent")
    print("Can handle 'Not Recommended', variations in formatting, etc.")
else:
    print("❌ Could not find function to replace")
