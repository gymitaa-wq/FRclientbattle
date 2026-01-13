"""
Test script for iterative refinement feature
Demonstrates the negotiation loop with sample data
"""

from iterative_refinement import run_iterative_refinement

# Mock callModel function for testing
def mock_callModel(prompt, model="gemini", max_tokens=4000):
    """Mock LLM for testing without API calls"""
    
    if "REVISED PROPOSAL" in prompt or "ITERATION #" in prompt:
        iteration = 1
        if "ITERATION #2" in prompt:
            iteration = 2
        elif "ITERATION #3" in prompt:
            iteration = 3
        
        return f"""
## ACKNOWLEDGMENT OF FEEDBACK
Thank you for the feedback. I've carefully reviewed the AI's concerns and made significant adjustments.

## REVISED RECOMMENDATIONS (Iteration {iteration})

### What We're Adjusting
- Reduced whole life coverage by 50%
- Lowered overall monthly premium by ${100 * iteration}
- Added more flexible payment options
- Increased transparency on fees

### REVISED PRICING
- Term Life (20-year, $500k): $60/month
- Whole Life (reduced to $125k): ${240 - (50 * iteration)}/month
- Disability Insurance: $95/month
- **Total: ${395 - (50 * iteration)}/month** (was $461/month)

## ADDRESSING SPECIFIC CONCERNS
1. **High Cost**: Reduced by {iteration * 15}%
2. **Whole Life Concerns**: Reduced coverage, better justification
3. **Transparency**: Added detailed fee breakdown

## VALUE BEYOND DIY
- Personalized ongoing support
- Claims assistance
- Annual policy reviews
- Family protection coordination
"""
    
    elif "EVALUATION" in prompt or "ACCEPT" in prompt:
        iteration = 1
        if "Iteration #2" in prompt:
            iteration = 2
        elif "Iteration #3" in prompt:
            iteration = 3
        
        # Accept on iteration 2
        if iteration >= 2:
            return f"""
## YOUR DECISION
**ACCEPT**

## REASONING
The advisor has made significant improvements:
- Reduced total cost by {iteration * 15}%
- Better justified the whole life component
- More transparent about fees
- Shows genuine willingness to work with me

While not perfect, this revised proposal addresses my main concerns and provides good value.

## FRICTION SCORE
{65 - (iteration * 15)}

The advisor listened and adapted. I'm comfortable moving forward with this.
"""
        else:
            return f"""
## YOUR DECISION
**REJECT**

## REASONING
Some improvement, but still concerns:
- Total cost still high
- Whole life component needs more justification
- Want to see more competitive pricing

## NEW CRITIQUE
- Reduce whole life further or remove entirely
- Lower disability insurance premium
- More transparency on commission structure

## FRICTION SCORE
{75 - (iteration * 10)}

Need more refinement to feel comfortable.
"""
    
    return "Mock response"


# Sample data
sample_profile = """
## FINANCIAL STANDING
- Annual Income: $90,000
- Assets: $35,000 in 401k, $12,000 emergency fund
- Mortgage: $450,000
- Age: 34

## PSYCHOLOGY
- Skepticism Level: 7/10
- Communication Style: Analytical and research-heavy

## LEGACY NEEDS
- Married, 1 child (6 months old)
- Needs: Life insurance, disability protection
"""

sample_initial_proposal = """
## LIFE INSURANCE STRATEGY
- Term 20-year ($500k): $60/month
- Whole Life ($250k): $240/month

## DISABILITY INSURANCE
- Coverage: $4,500/month (60% of income)
- Premium: $101/month

## TOTAL: $401/month
"""

sample_critique = """
## WHOLE LIFE INSURANCE
**Quality Rating**: Good Product
**Suitability**: Not Suitable for You

### Key Concerns
- Very expensive at $240/month
- Client has young family, needs more term coverage
- Whole life is commission-heavy product

### Alternative
- Increase term coverage instead
- Invest difference in low-cost index funds

## OVERALL ASSESSMENT
Total cost of $401/month is high for client's income.
Recommend: Accept term and DI, decline whole life.
"""

sample_initial_decision = """
## DECISION
**REJECT**

## WINNING ARGUMENT
The AI makes valid points about whole life being expensive and commission-driven.
For my situation (young family, moderate income), term life + investing makes more sense.

## FRICTION SCORE
75
"""

sample_ai_advice = """
Based on your situation, I recommend:
1. Term life insurance: $500k-$750k for 20-30 years (~$50-70/month)
2. Disability insurance: 60% income replacement (~$90-100/month)
3. Emergency fund: 6 months expenses
4. Low-cost index funds for retirement

Avoid whole life insurance - it's expensive and has high fees.
Focus on term + invest the difference.
"""

# Run the test
print("="*80)
print("TESTING ITERATIVE REFINEMENT MODULE")
print("="*80)
print("\nUsing mock LLM (no API calls)")
print("Simulating: Client rejects initial proposal, FR refines 2 times, client accepts")
print("\n" + "="*80)

result = run_iterative_refinement(
    initial_proposal=sample_initial_proposal,
    initial_critique=sample_critique,
    initial_decision=sample_initial_decision,
    persona_profile=sample_profile,
    initial_ai_advice=sample_ai_advice,
    callModel=mock_callModel,
    max_iterations=3
)

print("\n" + "="*80)
print("TEST RESULTS")
print("="*80)
print(f"\nMessage: {result['message']}")
print(f"Final Accepted: {result['final_accepted']}")
print(f"Total Iterations: {result['total_iterations']}")
print(f"Final Friction Score: {result.get('final_friction_score', 'N/A')}")

print("\n" + "="*80)
print("ITERATION HISTORY")
print("="*80)

for iter_data in result['iteration_history']:
    print(f"\nIteration {iter_data['iteration']}:")
    print(f"  Accepted: {iter_data['accepted']}")
    print(f"  Friction: {iter_data['friction_score']:.1f}")
    print(f"  Proposal length: {len(iter_data['proposal'])} chars")

print("\n" + "="*80)
print("✓ TEST COMPLETE")
print("="*80)
print("\nTo use with real LLM:")
print("  from project_caii_framework import callModel")
print("  result = run_iterative_refinement(..., callModel=callModel)")
