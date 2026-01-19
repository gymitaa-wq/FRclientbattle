# Realistic Premium Calculator Integration Guide

## Overview

The premium calculator generates **realistic insurance premiums** based on:
- Client age
- Annual income
- Coverage needs
- Gender
- Health class

## Files Created

1. **`premium_calculator.py`** - Core calculator with actuarial formulas
2. **`profile_parser.py`** - Extracts client data and formats premiums

## How It Works

### Example Output

For a 34-year-old making $90k:

```
TERM LIFE (20-year, $900k coverage): $72.00/month
WHOLE LIFE ($450k coverage): $288.00/month  
DISABILITY INSURANCE (60% income): $101.25/month
TOTAL MONTHLY: $461.25
```

### Products Calculated

1. **Term Life** - 10, 20, 30 year options
2. **Whole Life** - With cash value projections (10, 20, 30 years)
3. **Disability Insurance** - Based on income percentage
4. **Annuity** - With accumulation and income projections
5. **Cash Buffer** - Short-term treasury allocation

## Integration into Framework

### Step 1: Import in `project_caii_framework.py`

Add at the top:
```python
from profile_parser import enhance_advisor_prompt_with_premiums
```

### Step 2: Update Advisor Proposal Node

In the `generate_advisor_proposal()` function, replace the advisor_prompt creation with:

```python
# Original prompt (keep the base structure)
base_advisor_prompt = f"""
You are an insurance advisor with 15+ years of experience...
[your existing prompt text]
"""

# Enhance with realistic premiums
advisor_prompt = enhance_advisor_prompt_with_premiums(
    base_advisor_prompt,
    persona_profile
)
```

This will:
1. Extract age, income, coverage needs from the profile
2. Calculate realistic premiums
3. Append detailed premium data to the prompt
4. LLM will use EXACT numbers instead of placeholders

### Step 3: Update Product Plan Generation

Similarly, for each product plan, you can get specific premium data:

```python
from profile_parser import extract_client_data_from_profile
from premium_calculator import calculate_premiums

# Extract client data
client_data = extract_client_data_from_profile(persona_profile)

# Calculate all premiums
premiums = calculate_premiums(
    age=client_data['age'],
    annual_income=client_data['annual_income'],
    coverage_amount=client_data['coverage_need'],
    gender=client_data['gender'],
    health_class=client_data['health_class']
)

# Use in prompts
term_20_premium = premiums['term_life_options']['20_year']['monthly_premium']
whole_life_premium = premiums['whole_life']['monthly_premium']
# etc.
```

## Testing

Test the calculator:
```bash
python premium_calculator.py
```

Test the parser:
```bash
python profile_parser.py
```

## Premium Calculation Details

### Term Life Formula
- Base rate per $1,000 coverage (varies by age)
- Adjustments for: term length, gender, health class
- Example: 35-year-old, $500k, 20-year = $60/month

### Whole Life Formula
- ~8x term life rates
- Includes cash value projections
- Example: 35-year-old, $250k = $240/month
- Cash value year 20: ~$59,541

### Disability Insurance
- Based on 60-70% of income
- $2.50 per $100 of monthly benefit
- Adjustments for: age, gender, benefit period, elimination period

### Realistic Ranges

| Age | Term 20yr ($500k) | Whole Life ($250k) | DI (60% of $90k) |
|-----|-------------------|--------------------| -----------------|
| 30  | $40-50/mo         | $200-220/mo        | $90-100/mo       |
| 35  | $60-70/mo         | $240-260/mo        | $100-110/mo      |
| 40  | $90-100/mo        | $360-380/mo        | $110-120/mo      |
| 45  | $150-170/mo       | $600-650/mo        | $130-145/mo      |
| 50  | $250-280/mo       | $1000-1100/mo      | $150-170/mo      |

## Benefits

✅ **No more placeholders** - Real numbers in every proposal  
✅ **Consistent pricing** - Based on actuarial principles  
✅ **Automatic extraction** - Pulls data from profile text  
✅ **Complete proposals** - All products calculated together  
✅ **Cash value projections** - 10, 20, 30 year whole life values  

## Next Steps

1. Integrate into `project_caii_framework.py` (advisor proposal node)
2. Test with different client profiles
3. Verify premium numbers look realistic
4. Adjust formulas if needed (currently conservative/mid-market rates)

The calculator uses industry-standard formulas and can be fine-tuned for specific company rate tables if needed.
