"""
Fix product extraction to skip "Not Recommended" products
"""

with open('streamlined_simulation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the Whole Life extraction section
old_whole_life = '''    # Whole Life - look for "premium" or "cost" specifically
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
        })'''

new_whole_life = '''    # Whole Life - look for "premium" or "cost" specifically
    # But skip if it says "Not Recommended"
    whole_section_match = re.search(
        r'###.*?Whole Life(.*?)(?:###|$)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if whole_section_match:
        whole_section = whole_section_match.group(1)
        # Check if it's not recommended
        if 'not recommended' not in whole_section.lower():
            whole_match = re.search(
                r'(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
                whole_section,
                re.IGNORECASE | re.DOTALL
            )
            if whole_match:
                premium_str = whole_match.group(1).replace(',', '')
                products.append({
                    'name': 'Whole Life Insurance',
                    'monthly_premium': whole_match.group(1),
                    'premium_value': int(premium_str)
                })'''

content = content.replace(old_whole_life, new_whole_life)

# Also update Term Life to check for "Not Recommended"
old_term_life = '''    # Term Life - look for "premium" or "cost" specifically, not "benefit"
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
        })'''

new_term_life = '''    # Term Life - look for "premium" or "cost" specifically, not "benefit"
    # But skip if it says "Not Recommended"
    term_section_match = re.search(
        r'###.*?Term Life(.*?)(?:###|$)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if term_section_match:
        term_section = term_section_match.group(1)
        # Check if it's not recommended
        if 'not recommended' not in term_section.lower():
            term_match = re.search(
                r'(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
                term_section,
                re.IGNORECASE | re.DOTALL
            )
            if term_match:
                premium_str = term_match.group(1).replace(',', '')
                products.append({
                    'name': 'Term Life Insurance',
                    'monthly_premium': term_match.group(1),
                    'premium_value': int(premium_str)
                })'''

content = content.replace(old_term_life, new_term_life)

# Also update Disability to check for "Not Recommended"
old_disability = '''    # Disability - look for "premium" or "cost", NOT "benefit"
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
        })'''

new_disability = '''    # Disability - look for "premium" or "cost", NOT "benefit"
    # But skip if it says "Not Recommended"
    di_section_match = re.search(
        r'###.*?Disability(.*?)(?:###|$)',
        recommendations_section,
        re.IGNORECASE | re.DOTALL
    )
    if di_section_match:
        di_section = di_section_match.group(1)
        # Check if it's not recommended
        if 'not recommended' not in di_section.lower():
            di_match = re.search(
                r'(?:premium|cost).*?\\$([0-9,]+).*?(?:month|mo)',
                di_section,
                re.IGNORECASE | re.DOTALL
            )
            if di_match:
                premium_str = di_match.group(1).replace(',', '')
                products.append({
                    'name': 'Disability Insurance',
                    'monthly_premium': di_match.group(1),
                    'premium_value': int(premium_str)
                })'''

content = content.replace(old_disability, new_disability)

with open('streamlined_simulation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed product extraction to skip 'Not Recommended' products!")
print("Now checks each product section for 'Not Recommended' before extracting")
