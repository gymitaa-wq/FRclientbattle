"""
Profile Parser and Premium Integration for Project CAII

Extracts client information from persona profile and calculates realistic premiums.
"""

import re
from typing import Dict, Optional
from premium_calculator import InsurancePremiumCalculator, calculate_premiums


def extract_client_data_from_profile(persona_profile: str) -> Dict:
    """
    Extracts key client data from the persona profile text.
    
    Args:
        persona_profile: The extracted client profile text
    
    Returns:
        Dict with age, income, assets, etc.
    """
    data = {
        'age': 35,  # defaults
        'annual_income': 90000,
        'coverage_need': 500000,
        'gender': 'M',
        'health_class': 'standard'
    }
    
    # Extract age
    age_match = re.search(r'(\d+)[\s-]year[\s-]old|age[:\s]+(\d+)', persona_profile, re.IGNORECASE)
    if age_match:
        data['age'] = int(age_match.group(1) or age_match.group(2))
    
    # Extract income
    income_patterns = [
        r'annual income[:\s]+\$?([\d,]+)',
        r'salary[:\s]+\$?([\d,]+)',
        r'makes[:\s]+\$?([\d,]+)',
        r'income[:\s]+\$?([\d,]+)'
    ]
    for pattern in income_patterns:
        income_match = re.search(pattern, persona_profile, re.IGNORECASE)
        if income_match:
            income_str = income_match.group(1).replace(',', '')
            data['annual_income'] = int(income_str)
            break
    
    # Estimate coverage need (typically 10-15x income, or based on mortgage/debts)
    mortgage_match = re.search(r'mortgage[:\s]+\$?([\d,]+)', persona_profile, re.IGNORECASE)
    if mortgage_match:
        mortgage = int(mortgage_match.group(1).replace(',', ''))
        # Coverage = mortgage + 5-10x income
        data['coverage_need'] = mortgage + (data['annual_income'] * 7)
    else:
        # Default to 10x income
        data['coverage_need'] = data['annual_income'] * 10
    
    # Round coverage to nearest $50k
    data['coverage_need'] = round(data['coverage_need'] / 50000) * 50000
    
    # Detect gender (if mentioned)
    if re.search(r'\bshe\b|\bher\b|\bwife\b|\bmother\b', persona_profile, re.IGNORECASE):
        data['gender'] = 'F'
    
    # Detect health class hints
    if re.search(r'excellent health|very healthy|athletic|runner|gym', persona_profile, re.IGNORECASE):
        data['health_class'] = 'preferred'
    elif re.search(r'health issues|medication|condition|diabetes|high blood pressure', persona_profile, re.IGNORECASE):
        data['health_class'] = 'substandard'
    
    return data


def format_premium_data_for_prompt(premiums: Dict) -> str:
    """
    Formats premium calculation results into a structured string for LLM prompts.
    
    Args:
        premiums: Output from calculate_premiums()
    
    Returns:
        Formatted string with all premium details
    """
    
    term_10 = premiums['term_life_options']['10_year']
    term_20 = premiums['term_life_options']['20_year']
    term_30 = premiums['term_life_options']['30_year']
    whole = premiums['whole_life']
    di = premiums['disability_insurance']
    annuity = premiums['annuity']
    buffer = premiums['cash_buffer']
    
    formatted = f"""
REALISTIC PREMIUM CALCULATIONS:

## TERM LIFE INSURANCE OPTIONS

### 10-Year Term
- Coverage: ${term_10['coverage_amount']:,}
- Monthly Premium: ${term_10['monthly_premium']:.2f}
- Annual Premium: ${term_10['annual_premium']:.2f}
- Total Cost Over Term: ${term_10['total_cost_over_term']:.2f}

### 20-Year Term (RECOMMENDED)
- Coverage: ${term_20['coverage_amount']:,}
- Monthly Premium: ${term_20['monthly_premium']:.2f}
- Annual Premium: ${term_20['annual_premium']:.2f}
- Total Cost Over Term: ${term_20['total_cost_over_term']:.2f}

### 30-Year Term
- Coverage: ${term_30['coverage_amount']:,}
- Monthly Premium: ${term_30['monthly_premium']:.2f}
- Annual Premium: ${term_30['annual_premium']:.2f}
- Total Cost Over Term: ${term_30['total_cost_over_term']:.2f}

## WHOLE LIFE INSURANCE

- Coverage: ${whole['coverage_amount']:,}
- Monthly Premium: ${whole['monthly_premium']:.2f}
- Annual Premium: ${whole['annual_premium']:.2f}
- Projected Cash Value (Year 10): ${whole['cash_value_year_10']:,}
- Projected Cash Value (Year 20): ${whole['cash_value_year_20']:,}
- Projected Cash Value (Year 30): ${whole['cash_value_year_30']:,}
- Guaranteed Death Benefit: ${whole['guaranteed_death_benefit']:,}

## DISABILITY INSURANCE

- Monthly Benefit: ${di['monthly_benefit']:,} ({di['coverage_percentage']}% of income)
- Annual Benefit: ${di['annual_benefit']:,}
- Monthly Premium: ${di['monthly_premium']:.2f}
- Annual Premium: ${di['annual_premium']:.2f}
- Benefit Period: {di['benefit_period'].replace('_', ' ').title()}
- Elimination Period: {di['elimination_period_days']} days

## ANNUITY STRATEGY

- Type: {annuity['annuity_type'].replace('_', ' ').title()}
- Initial Investment: ${annuity['initial_investment']:,}
- Deferral Period: {annuity['deferral_years']} years
- Projected Accumulation Value: ${annuity['projected_accumulation_value']:,}
- Guaranteed Annual Income (starting age {annuity['income_start_age']}): ${annuity['guaranteed_annual_income']:,}
- Guaranteed Monthly Income: ${annuity['guaranteed_monthly_income']:,}
- Assumed Growth Rate: {annuity['assumed_growth_rate']}

## CASH BUFFER STRATEGY

- Investment: {buffer['investment_type']}
- Allocation Amount: ${buffer['allocation_amount']:,}
- Current Yield: {buffer['current_yield']}
- Annual Income: ${buffer['annual_income']:,}
- Monthly Income: ${buffer['monthly_income']:.2f}
- Liquidity: {buffer['liquidity']}
- Risk Level: {buffer['risk_level']}

## TOTAL INVESTMENT SUMMARY

- Recommended Monthly Premium: ${premiums['total_monthly_investment']:.2f}
  (Term 20-year + Whole Life + Disability Insurance)
- Total Annual Investment: ${premiums['total_annual_investment']:.2f}

IMPORTANT: Use these EXACT numbers in your proposal. Do not use placeholders like [insert amount].
"""
    
    return formatted


def enhance_advisor_prompt_with_premiums(base_prompt: str, persona_profile: str) -> str:
    """
    Enhances the advisor proposal prompt with realistic premium calculations.
    
    Args:
        base_prompt: Original advisor prompt
        persona_profile: Extracted client profile
    
    Returns:
        Enhanced prompt with premium data
    """
    # Extract client data
    client_data = extract_client_data_from_profile(persona_profile)
    
    # Calculate premiums
    premiums = calculate_premiums(
        age=client_data['age'],
        annual_income=client_data['annual_income'],
        coverage_amount=client_data['coverage_need'],
        gender=client_data['gender'],
        health_class=client_data['health_class']
    )
    
    # Format premium data
    premium_text = format_premium_data_for_prompt(premiums)
    
    # Insert into prompt
    enhanced_prompt = base_prompt + "\n\n" + premium_text
    
    return enhanced_prompt


# Test
if __name__ == "__main__":
    sample_profile = """
    ## FINANCIAL STANDING
    - Estimated Annual Income: $90,000
    - Estimated Assets: $25,000 in 401k, $10,000 emergency fund
    - Estimated Liabilities/Debt: $450,000 mortgage, $15,000 student loans
    - Current Insurance Coverage: $180,000 (2x salary through employer)
    
    ## PSYCHOLOGY
    - Skepticism Level (1-10): 7
    - Communication Style: Analytical and research-heavy
    
    ## LEGACY NEEDS
    - Family Structure: Married, 1 child (6 months old)
    - Age: 34 years old
    """
    
    client_data = extract_client_data_from_profile(sample_profile)
    print("Extracted Client Data:")
    print(client_data)
    
    print("\n" + "="*80)
    print("Calculated Premiums:")
    print("="*80)
    
    premiums = calculate_premiums(
        age=client_data['age'],
        annual_income=client_data['annual_income'],
        coverage_amount=client_data['coverage_need'],
        gender=client_data['gender'],
        health_class=client_data['health_class']
    )
    print(format_premium_data_for_prompt(premiums))
