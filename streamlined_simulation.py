"""
Streamlined Simulation Engine
Works directly from structured client profiles (no email history)
Generates iteration summaries and detailed deal analysis
"""

from typing import Dict, Any, List
from datetime import datetime
from structured_profile_generator import profile_to_prompt_context
from premium_calculator import InsurancePremiumCalculator
from product_catalog import get_product_catalog_text


def simulate_fr_client_interaction(
    profile: Dict[str, Any],
    iteration: int,
    previous_proposal: str = None,
    previous_critique: str = None,
    callModel: callable = None,
    model_name: str = "gemini",
    status_callback: callable = None
) -> Dict[str, Any]:
    """
    Simulates FR-client interaction for one iteration.
    
    Args:
        profile: Client profile dictionary
        iteration: Iteration number (0 = initial)
        previous_proposal: Previous proposal if refinement
        previous_critique: Previous AI critique if refinement
        callModel: LLM function
    
    Returns:
        Dict with proposal, critique, decision, and interaction summary
    """
    
    profile_context = profile_to_prompt_context(profile)
    product_catalog = get_product_catalog_text()
    
    # Calculate realistic premiums
    calculator = InsurancePremiumCalculator(
        age=profile['age'],
        gender='M' if profile['gender'] == 'Male' else 'F',
        health_class='preferred' if profile['health_status'] == 'Excellent' else 'standard'
    )
    
    # Generate FR proposal
    if status_callback:
        status_callback(f"Generating proposal (Iteration {iteration})...")
        
    if iteration == 0:
        # Initial proposal
        proposal_prompt = f"""
You are an experienced Northwestern Mutual insurance advisor meeting with a new client.

{product_catalog}

IMPORTANT: You MUST recommend products ONLY from the above Northwestern Mutual portfolio. Do not suggest generic products.

{profile_context}

Create a comprehensive insurance proposal that addresses their needs.

PROPOSAL STRUCTURE:

## EXECUTIVE SUMMARY
Brief overview of recommendations and total investment.

## RECOMMENDED PRODUCTS

Select 3-6 products from the catalog that best fit THIS CLIENT'S specific situation:

**For young families (age <40 with children):**
- Consider: Term Life (10/20), Disability Income, 529 College Savings

**For mid-career professionals (age 40-55):**
- Consider: Whole Life (65 Life/90 Life), Custom UL, Overhead Expense, Advisory Account

**For pre-retirees/retirees (age 55+):**
- Consider: Deferred Income Annuity, Long-Term Care, Accelerated Care Benefit, SPIA

**For high net worth clients (income >$250K or assets >$1M):**
- Consider: Survivorship Whole Life, Variable UL, Private Client Services, Index Annuity

**For business owners:**
- Consider: Overhead Expense, Business Disability Buyout, Custom UL for key person

For EACH recommended product, provide:
- Specific product name from catalog (e.g., "Term 20", "Whole Life Plus", "DIA")
- Coverage amount or benefit
- Estimated monthly/annual premium
- Clear rationale tied to client's profile

## TOTAL INVESTMENT
- Monthly: $X,XXX
- Annual: $X,XXX
- Breakdown by product

## VALUE PROPOSITION
Why this comprehensive approach vs. DIY solutions.

Use REAL numbers based on client's age ({profile['age']}), income (${profile['annual_income']:,}), and coverage gap (${profile['coverage_gap']:,}).
IMPORTANT: Vary your recommendations - don't just recommend Term + Whole Life + DI for everyone!
"""
    else:
        # Refinement iteration
        proposal_prompt = f"""
You are a Northwestern Mutual insurance advisor refining your proposal after client feedback.

{product_catalog}

IMPORTANT: You MUST recommend products ONLY from the above Northwestern Mutual portfolio.

{profile_context}

ITERATION #{iteration}

YOUR PREVIOUS PROPOSAL (REJECTED):
{previous_proposal}

CLIENT'S CONCERNS (via AI consultation):
{previous_critique}

Create a REVISED proposal that addresses these concerns while still providing adequate coverage.

REFINEMENT STRATEGY:
1. Acknowledge specific concerns raised
2. Adjust product mix - consider SUBSTITUTING products from the catalog:
   - If "too expensive" → Try Term instead of Whole Life, or use 90 Life instead of 65 Life
   - If "don't need permanent coverage" → Focus on Term products + DI + Brokerage
   - If retirement income concerns → Add DIA or SPIA
   - If long-term care worries → Add Accelerated Care Benefit or LTC Insurance
   - If business owner → Consider Overhead Expense or Business Disability Buyout
3. Improve pricing competitiveness
4. Increase transparency
5. Show flexibility

REVISED PROPOSAL STRUCTURE:

## ACKNOWLEDGMENT
Brief acknowledgment of feedback.

## WHAT'S CHANGED
- Products removed/reduced/SUBSTITUTED (name specific products from catalog)
- Pricing adjustments
- New products added to address concerns

## REVISED RECOMMENDATIONS
[List products by specific name from catalog - vary from initial proposal]

## ADDRESSING YOUR CONCERNS
Point-by-point response to critiques.

## REVISED TOTAL INVESTMENT
- Monthly: $X,XXX (was $X,XXX)
- Savings: $XXX/month

Use REAL numbers. Show meaningful improvement from iteration {iteration-1}.
"""
    
    proposal = callModel(proposal_prompt, model=model_name, max_tokens=3000)
    
    # Client consults AI for critique
    if status_callback:
        status_callback(f"Getting AI critique (Iteration {iteration})...")
        
    critique_prompt = f"""
You are a public AI (like ChatGPT) that a client is consulting about an insurance proposal.

{profile_context}

The client received this proposal from an insurance advisor:

{proposal}

The client asks: "What do you think about this proposal? Is it good for my situation?"

Provide an objective analysis:

## OVERALL ASSESSMENT
Quick verdict: Good value, Overpriced, or Mixed

## PRODUCT-BY-PRODUCT ANALYSIS

### Term Life Insurance
- Quality: Good/Fair/Poor
- Suitability: Suitable/Not Suitable
- Concerns: [any issues]

### Whole Life Insurance
- Quality: Good/Fair/Poor
- Suitability: Suitable/Not Suitable  
- Concerns: [commission-driven? too expensive?]

### Disability Insurance
- Quality: Good/Fair/Poor
- Suitability: Suitable/Not Suitable
- Concerns: [any issues]

### Other Products
[Analysis of annuity, etc.]

## COST ANALYSIS
- Total monthly cost vs. client's income
- Value for money assessment
- Comparison to DIY approach

## RED FLAGS
- High commissions
- Unnecessary products
- Overpriced components

## RECOMMENDATION
Accept, Reject, or Negotiate

Be objective but consider the client's skepticism level ({profile['skepticism_level']}/10).
"""
    
    ai_critique = callModel(critique_prompt, model=model_name, max_tokens=2000)
    
    # Client makes decision
    if status_callback:
        status_callback(f"Client making decision (Iteration {iteration})...")
        
    decision_prompt = f"""
You are simulating the client's decision-making process.

{profile_context}

ADVISOR'S PROPOSAL (Iteration {iteration}):
{proposal}

AI'S CRITIQUE:
{ai_critique}

The client weighs both perspectives and makes a decision.

Consider:
- Skepticism level: {profile['skepticism_level']}/10
- Financial literacy: {profile['financial_literacy']}
- Decision style: {profile['decision_style']}
- Primary concern: {profile['primary_concern']}
- Iteration number: {iteration} (more likely to accept after multiple refinements)

DECISION: ACCEPT or REJECT

## REASONING
Why this decision? What tipped the balance?

## KEY FACTORS
- What convinced them (if accept)
- What concerns remain (if reject)
- How iteration {iteration} compares to previous

## FRICTION SCORE (0-100)
Rate the tension between advisor's proposal and AI's recommendation.

Be realistic: 
- High skepticism + expensive proposal = likely reject
- Multiple iterations showing improvement = more likely to accept
- Good value + addresses concerns = likely accept
"""
    
    decision_text = callModel(decision_prompt, model=model_name, max_tokens=1500)
    
    # Parse decision
    # Parse decision - look for explicit DECISION: ACCEPT or DECISION: REJECT
    import re
    decision_upper = decision_text.upper()
    
    # Look for "DECISION: ACCEPT" or "DECISION: REJECT" pattern
    decision_match = re.search(r'DECISION[:\s]*(\w+)', decision_upper)
    
    if decision_match:
        decision_word = decision_match.group(1)
        accepted = decision_word.startswith('ACCEPT')
    else:
        # Fallback: check if ACCEPT appears before REJECT
        accept_pos = decision_upper.find('ACCEPT')
        reject_pos = decision_upper.find('REJECT')
        
        if accept_pos >= 0 and reject_pos >= 0:
            accepted = accept_pos < reject_pos
        elif accept_pos >= 0:
            accepted = True
        else:
            accepted = False
    
    # Extract friction score
    friction_score = 50.0
    score_match = re.search(r'FRICTION SCORE.*?(\d+)', decision_text, re.IGNORECASE | re.DOTALL)
    if score_match:
        friction_score = float(score_match.group(1))
    
    return {
        'iteration': iteration,
        'proposal': proposal,
        'ai_critique': ai_critique,
        'decision_text': decision_text,
        'accepted': accepted,
        'friction_score': friction_score,
        'timestamp': datetime.now().isoformat()
    }


def generate_iteration_summary(
    iteration_data: Dict[str, Any],
    previous_iteration: Dict[str, Any] = None
) -> str:
    """
    Generates a concise summary of an iteration.
    
    Args:
        iteration_data: Current iteration data
        previous_iteration: Previous iteration data for comparison
    
    Returns:
        Formatted summary string
    """
    
    iteration = iteration_data['iteration']
    accepted = iteration_data['accepted']
    friction = iteration_data['friction_score']
    
    # Extract key changes if refinement
    changes = ""
    if previous_iteration and iteration > 0:
        prev_friction = previous_iteration['friction_score']
        friction_change = friction - prev_friction
        changes = f"\n  Friction Change: {friction_change:+.1f} ({prev_friction:.1f} → {friction:.1f})"
    
    status_emoji = "✅ ACCEPTED" if accepted else "❌ REJECTED"
    
    summary = f"""
{'='*70}
ITERATION {iteration} SUMMARY
{'='*70}

Status: {status_emoji}
Friction Score: {friction:.1f}/100{changes}

Key Points:
{_extract_key_points(iteration_data['decision_text'])}

{'='*70}
"""
    
    return summary


def _extract_key_points(decision_text: str) -> str:
    """Extract key points from decision text."""
    lines = decision_text.split('\n')
    key_lines = []
    
    for line in lines[:15]:  # First 15 lines usually have key info
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 20:
            key_lines.append(f"  • {line[:100]}")
            if len(key_lines) >= 3:
                break
    
    return '\n'.join(key_lines) if key_lines else "  • See full decision text for details"


def analyze_deal_outcome(
    final_iteration: Dict[str, Any],
    all_iterations: List[Dict[str, Any]],
    profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyzes why deal closed or didn't close.
    
    Args:
        final_iteration: Final iteration data
        all_iterations: All iteration data
        profile: Client profile
    
    Returns:
        Dict with closure analysis
    """
    
    accepted = final_iteration['accepted']
    total_iterations = len(all_iterations)
    
    # Extract reasons from decision text
    decision_text = final_iteration['decision_text']
    
    analysis = {
        'deal_closed': accepted,
        'total_iterations': total_iterations,
        'final_friction_score': final_iteration['friction_score'],
        'friction_reduction': all_iterations[0]['friction_score'] - final_iteration['friction_score'] if total_iterations > 1 else 0,
    }
    
    if accepted:
        analysis['closure_reasons'] = _extract_acceptance_reasons(decision_text)
        analysis['winning_factors'] = _extract_winning_factors(all_iterations)
    else:
        analysis['rejection_reasons'] = _extract_rejection_reasons(decision_text)
        analysis['remaining_concerns'] = _extract_remaining_concerns(decision_text)
    
    return analysis


def _extract_acceptance_reasons(decision_text: str) -> List[str]:
    """Extract reasons for acceptance."""
    reasons = []
    
    keywords = [
        ('addresses concerns', 'Addressed key concerns'),
        ('good value', 'Good value for money'),
        ('competitive pricing', 'Competitive pricing'),
        ('comprehensive coverage', 'Comprehensive coverage'),
        ('flexibility', 'Showed flexibility'),
        ('transparent', 'Transparent about fees'),
        ('family protection', 'Protects family'),
    ]
    
    text_lower = decision_text.lower()
    for keyword, reason in keywords:
        if keyword in text_lower:
            reasons.append(reason)
    
    return reasons if reasons else ['See decision text for details']


def _extract_rejection_reasons(decision_text: str) -> List[str]:
    """Extract reasons for rejection."""
    reasons = []
    
    keywords = [
        ('too expensive', 'Still too expensive'),
        ('overpriced', 'Overpriced products'),
        ('commission', 'Commission-driven recommendations'),
        ('unnecessary', 'Unnecessary products included'),
        ('better options', 'Better DIY options available'),
        ('not convinced', 'Not convinced of value'),
    ]
    
    text_lower = decision_text.lower()
    for keyword, reason in keywords:
        if keyword in text_lower:
            reasons.append(reason)
    
    return reasons if reasons else ['See decision text for details']


def _extract_winning_factors(iterations: List[Dict[str, Any]]) -> List[str]:
    """Extract what led to eventual acceptance."""
    factors = []
    
    if len(iterations) > 1:
        factors.append(f"Advisor refined proposal {len(iterations)-1} time(s)")
        
        friction_reduction = iterations[0]['friction_score'] - iterations[-1]['friction_score']
        if friction_reduction > 20:
            factors.append(f"Significant friction reduction ({friction_reduction:.0f} points)")
    
    return factors


def _extract_remaining_concerns(decision_text: str) -> List[str]:
    """Extract remaining concerns after rejection."""
    concerns = []
    
    # Look for concern indicators
    if 'still' in decision_text.lower():
        lines = decision_text.split('\n')
        for line in lines:
            if 'still' in line.lower() and len(line) > 20:
                concerns.append(line.strip()[:100])
                if len(concerns) >= 3:
                    break
    
    return concerns if concerns else ['See decision text for details']


def extract_final_products(proposal_text: str, accepted: bool, callModel: callable = None) -> Dict[str, Any]:
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
    
    # CRITICAL FIX: For revised proposals, the actual recommendations are at the END
    # The beginning often has "WHAT'S CHANGED" which mentions REMOVED products
    # We need to extract from the final/revised sections, not the acknowledgment/changes summary
    
    # Strategy: Look for final recommendations section, or use last 3000 chars
    import re
    
    # Step 1: Remove problematic sections that mention removed products
    # Remove WHAT'S CHANGED section (contains mentions of removed products)
    text_cleaned = re.sub(
        r'##?\s*WHAT[\s\']*S CHANGED.*?(?=##|\Z)',  # From "WHAT'S CHANGED" to next ## or end
        '',
        proposal_text,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # Remove ACKNOWLEDGMENT section (may reference old recommendations)
    text_cleaned = re.sub(
        r'##?\s*ACKNOWLEDGMENT.*?(?=##|\Z)',
        '',
        text_cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # Remove WHY THESE CHANGES section (may reference what was removed)
    text_cleaned = re.sub(
        r'##?\s*WHY THESE CHANGES.*?(?=##|\Z)',
        '',
        text_cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # print(f"DEBUG: Cleaned text length: {len(text_cleaned)} chars (original: {len(proposal_text)})")
    
    # Step 2: Try to find "REVISED RECOMMENDATIONS" or "FINAL RECOMMENDATIONS" or "RECOMMENDATIONS" section
    revised_match = re.search(r'(?:REVISED|FINAL)?\s*RECOMMENDATIONS(.*)', text_cleaned, re.IGNORECASE | re.DOTALL)
    if revised_match:
        # Extract from this section to end
        extract_text = revised_match.group(0)[:3500]  # From section header onwards
        # print(f"DEBUG: Found RECOMMENDATIONS section, extracting from there")
    else:
        # Fallback: Use LAST 3000 chars of cleaned text (final recommendations are at end)
        # This avoids the "WHAT'S CHANGED" section which is now removed
        extract_text = text_cleaned[-3000:] if len(text_cleaned) > 3000 else text_cleaned
        # print(f"DEBUG: No RECOMMENDATIONS section found, using last 3000 chars of cleaned text")
    
    # DEBUG: Print the extract_text to see what's being sent to LLM
    # print(f"\nDEBUG: Text being sent to LLM for extraction ({len(extract_text)} chars):")
    # print("="*70)
    # print(extract_text)
    # print("="*70)
    
    # Simplified, ultra-clear extraction prompt
    extraction_prompt = f"""You are extracting insurance product information. Be extremely concise.

PROPOSAL TEXT (FINAL RECOMMENDATIONS SECTION):
{extract_text}

Task: Extract products that are CURRENTLY RECOMMENDED (not what was removed/changed).

Output ONLY valid JSON in this exact format:
{{
  "products": [
    {{"name": "Term Life Insurance", "monthly_premium": 150}},
    {{"name": "Disability Insurance", "monthly_premium": 95}}
  ],
  "total_monthly": 245
}}

Rules:
1. Extract ONLY currently recommended products
2. IGNORE any products mentioned as "removed", "changed", or "not recommended"
3. Look for the FINAL/CURRENT product list, not historical changes
4. Monthly premium only (not annual, not benefit amount)
5. Simple product names: "Term Life Insurance", "Whole Life Insurance", "Disability Insurance", "Roth IRA"
6. Return ONLY the JSON object - no explanations, no markdown, no other text
7. If no products, return {{"products": [], "total_monthly": 0}}

JSON:"""


    try:
        if callModel:
            response = callModel(extraction_prompt, model="gemini", max_tokens=20000)
        else:
            from project_caii_framework import callModel as default_callModel
            response = default_callModel(extraction_prompt, model="gemini", max_tokens=20000)
        
        # DEBUG: Print actual response to help troubleshoot
        # print(f"DEBUG: LLM response for product extraction:")
        # print(f"Response length: {len(response)} chars")
        # print(f"First 500 chars: {response[:500]}")
        # print("="*70)
        
        import json
        import re
        
        # Clean the response
        cleaned = response.strip()
        
        # Try multiple extraction methods
        json_str = None
        
        # Method 1: Remove markdown code fences if present
        if '```' in cleaned:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
            if match:
                json_str = match.group(1)
                # print("DEBUG: Extracted from markdown code block")
        
        # Method 2: Find JSON object pattern
        if not json_str:
            match = re.search(r'\{[^{}]*"products"[^{}]*\[.*?\][^{}]*\}', cleaned, re.DOTALL)
            if match:
                json_str = match.group(0)
                # print("DEBUG: Extracted via products pattern match")
        
        # Method 3: Find any JSON object
        if not json_str:
            match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
            if match:
                json_str = match.group(0)
                # print("DEBUG: Extracted via generic JSON match")
        
        # Method 4: Assume entire response is JSON
        if not json_str and cleaned.startswith('{') and cleaned.endswith('}'):
            json_str = cleaned
            # print("DEBUG: Using entire response as JSON")
        
        if not json_str:
            raise ValueError(f"No JSON object found in response. First 200 chars: {response[:200]}")
        
        # Parse JSON
        # print(f"DEBUG: Attempting to parse JSON: {json_str[:200]}...")
        data = json.loads(json_str)
        
        products = data.get('products', [])
        total_monthly = data.get('total_monthly', 0)
        
        # print(f"DEBUG: Successfully parsed {len(products)} products")
        
        # Validate and clean up
        cleaned_products = []
        for p in products:
            if 'name' in p and 'monthly_premium' in p:
                premium = p['monthly_premium']
                # Handle string premiums like "$150"
                if isinstance(premium, str):
                    premium = int(re.sub(r'[^\d]', '', premium)) if premium else 0
                if premium > 0:  # Skip zero premiums
                    cleaned_products.append({
                        'name': p['name'],
                        'monthly_premium': str(premium),
                        'premium_value': int(premium)
                    })
        
        # Recalculate total if needed
        if cleaned_products:
            calculated_total = sum(p['premium_value'] for p in cleaned_products)
            if total_monthly == 0 or abs(total_monthly - calculated_total) > 50:
                total_monthly = calculated_total
        
        print(f"✓ EXTRACTION RESULT: {len(cleaned_products)} products, ${total_monthly}/month")
        for p in cleaned_products:
            print(f"   - {p['name']}: ${p['premium_value']}/month")
        
        return {
            'products': cleaned_products,
            'total_monthly': int(total_monthly),
            'total_annual': int(total_monthly * 12),
            'proposal_text': proposal_text
        }
    
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parsing failed: {e}")
        print(f"ERROR: Attempted to parse: {json_str[:500] if json_str else 'No JSON string extracted'}")
        # Fall through to text parsing
    except Exception as e:
        print(f"ERROR: Extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    # FALLBACK: Parse the proposal text directly for product information
    # IMPORTANT: Use text_cleaned (with WHAT'S CHANGED removed) NOT original proposal_text!
    print("WARNING: JSON extraction failed, using text fallback on cleaned proposal")
    try:
        import re
        products = []
        
        # Use the CLEANED text that has WHAT'S CHANGED section removed
        # This prevents extracting mentions of REMOVED products
        search_text = text_cleaned  # NOT proposal_text!
        
        # Look for product mentions with dollar amounts
        # Pattern: "Product Name: $XXX/month" or "Product Name - $XXX monthly"
        product_patterns = {
            'Term Life Insurance': [
                r'Term\s+(?:Life|20|30)[^$\n]*\$\s*([\d,]+)',
                r'(?:^|\n)\s*\*?\*?Term[^$\n]*\$\s*([\d,]+)'
            ],
            'Whole Life Insurance': [
                r'Whole\s+Life[^$\n]*\$\s*([\d,]+)',
                r'(?:^|\n)\s*\*?\*?Whole[^$\n]*\$\s*([\d,]+)'
            ],
            'Disability Insurance': [
                r'Disability[^$\n]*\$\s*([\d,]+)',
                r'(?:^|\n)\s*\*?\*?Disability[^$\n]*\$\s*([\d,]+)'
            ],
            'Long-Term Care': [
                r'Long[- ]Term\s+Care[^$\n]*\$\s*([\d,]+)',
                r'(?:^|\n)\s*\*?\*?(?:LTC|Long[- ]Term)[^$\n]*\$\s*([\d,]+)'
            ],
            'Roth IRA': [
                r'Roth\s+IRA[^$\n]*\$\s*([\d,]+)',
                r'(?:^|\n)\s*\*?\*?Roth[^$\n]*\$\s*([\d,]+)'
            ]
        }
        
        for product_name, patterns in product_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = int(amount_str)
                    # Filter for reasonable monthly premiums
                    if 10 < amount < 2000:
                        products.append({
                            'name': product_name,
                            'monthly_premium': str(amount),
                            'premium_value': amount
                        })
                        print(f"DEBUG: Found {product_name} at ${amount}/month via text parsing")
                        break  # Found this product, skip other patterns
        
        if products:
            total = sum(p['premium_value'] for p in products)
            print(f"DEBUG: Text parsing found {len(products)} products, ${total}/month")
            return {
                'products': products,
                'total_monthly': total,
                'total_annual': total * 12,
                'proposal_text': proposal_text,
                'extraction_method': 'text_fallback'
            }
    
    except Exception as fallback_error:
        print(f"ERROR: Text fallback also failed: {fallback_error}")
    
    # Final fallback: return empty with error
    print("WARNING: All extraction methods failed, returning empty")
    return {
        'products': [],
        'total_monthly': 0,
        'total_annual': 0,
        'proposal_text': proposal_text,
        'extraction_error': 'All extraction methods failed. See proposal text for details.'
    }
