"""
Enhanced Structured Client Profile Generator
More realistic and reasonable financial profiles
"""

import random
from typing import Dict, Any
from datetime import datetime


def generate_structured_client_profile() -> Dict[str, Any]:
    """
    Generates a realistic structured client profile with comprehensive attributes.
    
    Returns:
        Dict with all client attributes
    """
    
    # Demographics
    age = random.randint(28, 58)
    gender = random.choice(['Male', 'Female'])
    marital_status = random.choice(['Single', 'Married', 'Married', 'Divorced'])
    
    # Age-appropriate children
    if age < 30:
        num_children = random.choice([0, 0, 0, 1])
    elif age < 40:
        num_children = random.choice([0, 1, 1, 2, 2])
    else:
        num_children = random.choice([0, 1, 2, 2, 3])
    
    # Employment & Income - age-correlated
    occupations_by_income = {
        'high': ['Software Engineer', 'Marketing Director', 'Operations Manager', 'Consultant', 'Project Manager'],
        'medium': ['Accountant', 'Business Analyst', 'Sales Manager', 'Nurse'],
        'lower': ['Teacher', 'Administrative Assistant', 'Customer Service Manager']
    }
    
    income_tier = random.choice(['high', 'high', 'medium', 'medium', 'lower'])
    occupation = random.choice(occupations_by_income[income_tier])
    
    # Income based on age and tier
    if income_tier == 'high':
        base_income = random.choice([110000, 125000, 150000, 180000])
    elif income_tier == 'medium':
        base_income = random.choice([65000, 75000, 85000, 95000])
    else:
        base_income = random.choice([45000, 55000, 65000])
    
    # Age adjustment (people earn more as they age)
    age_multiplier = 1.0 + ((age - 30) * 0.015)  # 1.5% increase per year after 30
    annual_income = int(base_income * age_multiplier)
    
    # Spouse income
    if marital_status == 'Married':
        spouse_income = random.choice([0, 45000, 55000, 65000, 75000, 85000])
    else:
        spouse_income = 0
    
    employment_years = min(random.randint(3, 20), age - 22)
    
    # Financial Situation - age and income correlated
    # 401k grows with age and income
    years_saving = max(0, age - 25)
    savings_401k = int(annual_income * 0.06 * years_saving * random.uniform(0.8, 1.5))
    savings_401k = max(10000, min(savings_401k, 500000))
    
    # Emergency fund: 3-6 months expenses
    monthly_expenses = int((annual_income + spouse_income) * 0.6 / 12)
    emergency_fund = random.randint(int(monthly_expenses * 2), int(monthly_expenses * 6))
    
    # Other investments grow with age and income
    if age > 40 and annual_income > 100000:
        other_investments = random.randint(30000, 150000)
    elif age > 35:
        other_investments = random.randint(10000, 60000)
    else:
        other_investments = random.randint(0, 30000)
    
    # Debts & Liabilities - realistic ratios
    has_mortgage = random.choice([True, True, False]) if age > 28 else random.choice([True, False])
    
    # Mortgage: 3-4x annual household income (realistic)
    if has_mortgage:
        household_income = annual_income + spouse_income
        mortgage_balance = int(household_income * random.uniform(2.5, 4.0))
        mortgage_balance = min(mortgage_balance, 800000)  # Cap at reasonable amount
        monthly_mortgage = int(mortgage_balance * 0.005)  # ~6% annual rate
    else:
        mortgage_balance = 0
        monthly_mortgage = 0
    
    # Student loans decrease with age
    if age < 35:
        student_loans = random.choice([0, 15000, 25000, 40000, 60000])
    elif age < 45:
        student_loans = random.choice([0, 0, 10000, 20000])
    else:
        student_loans = random.choice([0, 0, 0, 5000])
    
    # Car loans
    car_loans = random.choice([0, 0, 18000, 25000])
    
    # Credit card debt - reasonable amounts
    credit_card_debt = random.choice([0, 0, 3000, 5000, 8000])
    
    # Current Insurance
    employer_life_insurance = annual_income * 2  # Typical employer coverage
    has_personal_life_insurance = random.choice([True, False, False])
    personal_life_coverage = random.choice([0, 250000, 500000]) if has_personal_life_insurance else 0
    has_disability_insurance = random.choice([True, False, False])
    
    # Psychology & Behavior
    skepticism_level = random.randint(5, 9)  # Most people are somewhat skeptical
    risk_tolerance = random.choice(['Conservative', 'Moderate', 'Moderate', 'Aggressive'])
    decision_style = random.choice([
        'Analytical - needs data and research',
        'Emotional - family-focused',
        'Practical - cost-conscious',
        'Trusting - values expert advice',
        'Skeptical - questions everything'
    ])
    financial_literacy = random.choice(['Low', 'Medium', 'Medium', 'High'])
    
    # Needs & Goals - age appropriate
    if num_children > 0:
        primary_concern = random.choice([
            'Protecting family if I die',
            'Funding children\'s education',
            'Paying off mortgage if something happens'
        ])
    elif age > 50:
        primary_concern = random.choice([
            'Building retirement savings',
            'Estate planning and wealth transfer'
        ])
    else:
        primary_concern = random.choice([
            'Protecting family if I die',
            'Replacing income if disabled',
            'Building retirement savings'
        ])
    
    time_horizon = 'Long-term (15+ years)' if age < 45 else 'Medium-term (5-15 years)'
    
    # Health
    health_status = random.choice(['Excellent', 'Good', 'Good', 'Fair'])
    smoker = random.choice([True, False, False, False, False])  # ~20% smokers
    health_conditions = random.choice([
        'None', 'None', 'None',
        'Controlled high blood pressure',
        'Controlled diabetes',
        'Asthma'
    ])
    
    # Calculate derived values
    total_debt = mortgage_balance + student_loans + car_loans + credit_card_debt
    total_assets = savings_401k + emergency_fund + other_investments
    net_worth = total_assets - total_debt
    debt_to_income_ratio = (total_debt / annual_income) if annual_income > 0 else 0
    
    # Insurance needs calculation - realistic
    # Rule of thumb: 10x income or mortgage + 5x income, whichever is higher
    recommended_life_coverage = max(
        annual_income * 10,
        mortgage_balance + (annual_income * 5)
    )
    
    # But cap at reasonable amount
    recommended_life_coverage = min(recommended_life_coverage, 3000000)
    
    current_coverage_gap = recommended_life_coverage - (employer_life_insurance + personal_life_coverage)
    
    # Build profile
    profile = {
        # Demographics
        'age': age,
        'gender': gender,
        'marital_status': marital_status,
        'num_children': num_children,
        
        # Employment
        'occupation': occupation,
        'annual_income': annual_income,
        'spouse_income': spouse_income,
        'total_household_income': annual_income + spouse_income,
        'employment_years': employment_years,
        
        # Assets
        'savings_401k': savings_401k,
        'emergency_fund': emergency_fund,
        'other_investments': other_investments,
        'total_assets': total_assets,
        
        # Liabilities
        'has_mortgage': has_mortgage,
        'mortgage_balance': mortgage_balance,
        'monthly_mortgage': monthly_mortgage,
        'student_loans': student_loans,
        'car_loans': car_loans,
        'credit_card_debt': credit_card_debt,
        'total_debt': total_debt,
        
        # Financial Metrics
        'net_worth': net_worth,
        'debt_to_income_ratio': debt_to_income_ratio,
        
        # Current Insurance
        'employer_life_insurance': int(employer_life_insurance),
        'personal_life_coverage': personal_life_coverage,
        'total_current_coverage': int(employer_life_insurance + personal_life_coverage),
        'has_disability_insurance': has_disability_insurance,
        
        # Insurance Needs
        'recommended_life_coverage': int(recommended_life_coverage),
        'coverage_gap': int(current_coverage_gap),
        
        # Psychology
        'skepticism_level': skepticism_level,
        'risk_tolerance': risk_tolerance,
        'decision_style': decision_style,
        'financial_literacy': financial_literacy,
        
        # Goals & Needs
        'primary_concern': primary_concern,
        'time_horizon': time_horizon,
        
        # Health
        'health_status': health_status,
        'smoker': smoker,
        'health_conditions': health_conditions,
        
        # Metadata
        'generated_at': datetime.now().isoformat(),
        'profile_id': f"CLIENT_{random.randint(1000, 9999)}"
    }
    
    return profile


def format_profile_for_display(profile: Dict[str, Any]) -> str:
    """
    Formats profile dictionary into readable text for display.
    
    Args:
        profile: Client profile dictionary
    
    Returns:
        Formatted string for display
    """
    
    return f"""
═══════════════════════════════════════════════════════════════
CLIENT PROFILE: {profile['profile_id']}
═══════════════════════════════════════════════════════════════

👤 DEMOGRAPHICS
─────────────────────────────────────────────────────────────
Age:                {profile['age']} years old
Gender:             {profile['gender']}
Marital Status:     {profile['marital_status']}
Children:           {profile['num_children']}

💼 EMPLOYMENT & INCOME
─────────────────────────────────────────────────────────────
Occupation:         {profile['occupation']}
Annual Income:      ${profile['annual_income']:,}
Spouse Income:      ${profile['spouse_income']:,}
Total Household:    ${profile['total_household_income']:,}
Years Employed:     {profile['employment_years']} years

💰 FINANCIAL POSITION
─────────────────────────────────────────────────────────────
Assets:
  401(k):           ${profile['savings_401k']:,}
  Emergency Fund:   ${profile['emergency_fund']:,}
  Other Investments: ${profile['other_investments']:,}
  TOTAL ASSETS:     ${profile['total_assets']:,}

Liabilities:
  Mortgage:         ${profile['mortgage_balance']:,} (${profile['monthly_mortgage']:,}/mo)
  Student Loans:    ${profile['student_loans']:,}
  Car Loans:        ${profile['car_loans']:,}
  Credit Cards:     ${profile['credit_card_debt']:,}
  TOTAL DEBT:       ${profile['total_debt']:,}

Net Worth:          ${profile['net_worth']:,}
Debt-to-Income:     {profile['debt_to_income_ratio']:.1%}

🛡️ CURRENT INSURANCE
─────────────────────────────────────────────────────────────
Employer Life:      ${profile['employer_life_insurance']:,}
Personal Life:      ${profile['personal_life_coverage']:,}
Total Coverage:     ${profile['total_current_coverage']:,}
Disability:         {'Yes' if profile['has_disability_insurance'] else 'No'}

📊 INSURANCE NEEDS ANALYSIS
─────────────────────────────────────────────────────────────
Recommended Coverage: ${profile['recommended_life_coverage']:,}
Current Coverage:     ${profile['total_current_coverage']:,}
COVERAGE GAP:         ${profile['coverage_gap']:,}

🧠 PSYCHOLOGY & BEHAVIOR
─────────────────────────────────────────────────────────────
Skepticism Level:   {profile['skepticism_level']}/10
Risk Tolerance:     {profile['risk_tolerance']}
Decision Style:     {profile['decision_style']}
Financial Literacy: {profile['financial_literacy']}

🎯 GOALS & PRIORITIES
─────────────────────────────────────────────────────────────
Primary Concern:    {profile['primary_concern']}
Time Horizon:       {profile['time_horizon']}

🏥 HEALTH STATUS
─────────────────────────────────────────────────────────────
Overall Health:     {profile['health_status']}
Smoker:             {'Yes' if profile['smoker'] else 'No'}
Conditions:         {profile['health_conditions']}

═══════════════════════════════════════════════════════════════
Generated: {profile['generated_at'][:19]}
═══════════════════════════════════════════════════════════════
"""


def profile_to_prompt_context(profile: Dict[str, Any]) -> str:
    """
    Converts profile to context string for LLM prompts.
    
    Args:
        profile: Client profile dictionary
    
    Returns:
        Formatted context for prompts
    """
    
    family_desc = f"{profile['marital_status']}"
    if profile['num_children'] > 0:
        family_desc += f", {profile['num_children']} child{'ren' if profile['num_children'] > 1 else ''}"
    
    return f"""
CLIENT PROFILE SUMMARY:

Demographics: {profile['age']}-year-old {profile['gender']}, {family_desc}
Occupation: {profile['occupation']} ({profile['employment_years']} years)
Income: ${profile['annual_income']:,} annually (household: ${profile['total_household_income']:,})

Financial Position:
- Assets: ${profile['total_assets']:,} (401k: ${profile['savings_401k']:,}, Emergency: ${profile['emergency_fund']:,})
- Debt: ${profile['total_debt']:,} (Mortgage: ${profile['mortgage_balance']:,}, Student: ${profile['student_loans']:,})
- Net Worth: ${profile['net_worth']:,}

Current Insurance:
- Life Insurance: ${profile['total_current_coverage']:,} (Employer: ${profile['employer_life_insurance']:,}, Personal: ${profile['personal_life_coverage']:,})
- Disability: {'Yes' if profile['has_disability_insurance'] else 'No'}
- Coverage Gap: ${profile['coverage_gap']:,}

Psychology:
- Skepticism: {profile['skepticism_level']}/10
- Risk Tolerance: {profile['risk_tolerance']}
- Decision Style: {profile['decision_style']}
- Financial Literacy: {profile['financial_literacy']}

Primary Concern: {profile['primary_concern']}
Health: {profile['health_status']}, Smoker: {'Yes' if profile['smoker'] else 'No'}, Conditions: {profile['health_conditions']}
"""


# Test
if __name__ == "__main__":
    profile = generate_structured_client_profile()
    print(format_profile_for_display(profile))
    
    print("\n" + "="*70)
    print("PROMPT CONTEXT FORMAT:")
    print("="*70)
    print(profile_to_prompt_context(profile))
