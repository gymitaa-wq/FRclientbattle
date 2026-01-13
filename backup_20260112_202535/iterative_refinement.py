"""
Iterative Proposal Refinement Module for Project CAII

Adds negotiation loop where FR refines proposals based on AI feedback until acceptance.
"""

from typing import Dict, Any, List
from datetime import datetime


def refine_proposal_based_on_critique(
    original_proposal: str,
    ai_critique: str,
    persona_profile: str,
    initial_ai_advice: str,
    iteration_number: int,
    callModel: callable
) -> str:
    """
    FR refines their proposal based on AI critique.
    
    Args:
        original_proposal: The previous proposal that was rejected
        ai_critique: AI's critique identifying issues
        persona_profile: Client profile
        initial_ai_advice: Original DIY AI advice
        iteration_number: Which iteration this is (1, 2, 3...)
        callModel: Function to call LLM
    
    Returns:
        Refined proposal text
    """
    
    refinement_prompt = f"""
You are an experienced insurance advisor who just received feedback that your proposal was rejected.
The client consulted a public AI, which critiqued your proposal.

ITERATION #{iteration_number} - PROPOSAL REFINEMENT

CLIENT PROFILE:
{persona_profile}

YOUR PREVIOUS PROPOSAL (REJECTED):
{original_proposal}

AI'S CRITIQUE OF YOUR PROPOSAL:
{ai_critique}

ORIGINAL AI ADVICE TO CLIENT:
{initial_ai_advice}

Your task: Create a REVISED proposal that addresses the AI's concerns while still providing comprehensive coverage.

REFINEMENT STRATEGY:
1. **Acknowledge Valid Concerns**: If the AI identified legitimate issues (high fees, unnecessary products), address them
2. **Adjust Product Mix**: Consider reducing or removing products the AI flagged as "bad" or "not suitable"
3. **Improve Value Proposition**: Emphasize features that AI cannot replicate (personalized service, ongoing support)
4. **Be More Transparent**: Clearly explain fees, commissions, and long-term value
5. **Find Middle Ground**: Balance between comprehensive coverage and cost concerns
6. **Address Specific Objections**: Directly respond to each major criticism

REVISED PROPOSAL STRUCTURE:

## ACKNOWLEDGMENT OF FEEDBACK
Briefly acknowledge the client's concerns and the AI feedback.

## REVISED RECOMMENDATIONS

### What We're Keeping (and Why)
Products that remain in the proposal with clear justification.

### What We're Adjusting
Changes made based on feedback:
- Products removed or reduced
- Premium adjustments
- Feature modifications

### What We're Adding
Any new options or flexibility based on concerns.

## REVISED PRICING
Updated monthly/annual premiums with clear breakdown.

## ADDRESSING SPECIFIC CONCERNS
Point-by-point response to AI's main criticisms.

## VALUE BEYOND DIY APPROACHES
What professional guidance provides that free AI cannot.

## TOTAL INVESTMENT SUMMARY
Clear, transparent cost breakdown.

IMPORTANT: 
- Use REAL numbers (not placeholders)
- Be more competitive on pricing if appropriate
- Show flexibility and willingness to customize
- Maintain professionalism while being responsive to feedback
- This is iteration #{iteration_number} - show you're listening and adapting
"""
    
    refined_proposal = callModel(refinement_prompt, model="gemini", max_tokens=4000)
    return refined_proposal


def evaluate_refined_proposal(
    refined_proposal: str,
    ai_critique_of_original: str,
    persona_profile: str,
    initial_ai_advice: str,
    iteration_number: int,
    callModel: callable
) -> Dict[str, Any]:
    """
    Client (via AI) evaluates the refined proposal.
    
    Returns:
        Dict with 'accepted' (bool), 'new_critique' (str), 'reasoning' (str)
    """
    
    evaluation_prompt = f"""
You are simulating a client's decision-making after receiving a REVISED proposal from their insurance advisor.

This is ITERATION #{iteration_number} of the negotiation.

CLIENT PROFILE:
{persona_profile}

ORIGINAL AI ADVICE (Your Initial Recommendation):
{initial_ai_advice}

PREVIOUS CRITIQUE OF FIRST PROPOSAL:
{ai_critique_of_original}

ADVISOR'S REVISED PROPOSAL (Iteration #{iteration_number}):
{refined_proposal}

The client asks: "The advisor revised their proposal based on the AI feedback. Should I accept this new version?"

Evaluate whether the advisor adequately addressed the concerns:

## EVALUATION CRITERIA

1. **Did they address the main criticisms?**
   - Were high-cost products removed or justified?
   - Are fees more transparent?
   - Is pricing more competitive?

2. **Is the revised proposal more aligned with DIY advice?**
   - Better balance of term vs. whole life?
   - More reasonable total cost?
   - Fewer commission-driven products?

3. **Does it still meet the client's needs?**
   - Adequate coverage?
   - Appropriate for their situation?
   - Good value for money?

4. **Client psychology factor:**
   - Skepticism level from profile
   - How much improvement is needed to overcome doubt?
   - Is the advisor showing genuine flexibility?

## YOUR DECISION

**ACCEPT** or **REJECT**

## REASONING
Explain your decision based on:
- What improved
- What still concerns you
- Whether this is good enough or needs more refinement
- How iteration #{iteration_number} compares to iteration 1

## NEW CRITIQUE (if REJECT)
If rejecting, provide specific feedback on what still needs improvement.

## FRICTION SCORE (0-100)
Rate the remaining tension between this revised proposal and the DIY approach.

Be realistic: 
- If iteration #{iteration_number} shows significant improvement, consider accepting
- If advisor is being stubborn or not addressing concerns, reject
- Client's skepticism level affects how much improvement is needed
- After 2-3 iterations, client may accept "good enough" even if not perfect
"""
    
    evaluation = callModel(evaluation_prompt, model="gemini", max_tokens=2000)
    
    # Parse the evaluation
    accepted = "ACCEPT" in evaluation.upper() and "REJECT" not in evaluation.upper()[:200]
    
    # Extract friction score
    import re
    friction_score = 50.0
    score_match = re.search(r'FRICTION SCORE.*?(\d+)', evaluation, re.IGNORECASE | re.DOTALL)
    if score_match:
        friction_score = float(score_match.group(1))
    
    return {
        'accepted': accepted,
        'evaluation_text': evaluation,
        'friction_score': friction_score,
        'iteration': iteration_number
    }


def run_iterative_refinement(
    initial_proposal: str,
    initial_critique: str,
    initial_decision: str,
    persona_profile: str,
    initial_ai_advice: str,
    callModel: callable,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """
    Main loop for iterative proposal refinement.
    
    Args:
        initial_proposal: First proposal that was rejected
        initial_critique: AI's critique of first proposal
        initial_decision: Initial rejection decision
        persona_profile: Client profile
        initial_ai_advice: Original DIY recommendations
        callModel: LLM function
        max_iterations: Maximum refinement attempts
    
    Returns:
        Dict with final proposal, all iterations, and acceptance status
    """
    
    # Check if initial proposal was accepted
    if "CONVERT" in initial_decision.upper() and "REJECT" not in initial_decision.upper()[:200]:
        return {
            'final_proposal': initial_proposal,
            'final_accepted': True,
            'total_iterations': 0,
            'iteration_history': [],
            'message': 'Initial proposal accepted - no refinement needed'
        }
    
    print("\n" + "="*80)
    print("STARTING ITERATIVE REFINEMENT PROCESS")
    print(f"Maximum iterations: {max_iterations}")
    print("="*80)
    
    current_proposal = initial_proposal
    current_critique = initial_critique
    iteration_history = []
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n{'='*80}")
        print(f"ITERATION #{iteration}: REFINING PROPOSAL")
        print(f"{'='*80}")
        
        # FR refines proposal based on critique
        refined_proposal = refine_proposal_based_on_critique(
            original_proposal=current_proposal,
            ai_critique=current_critique,
            persona_profile=persona_profile,
            initial_ai_advice=initial_ai_advice,
            iteration_number=iteration,
            callModel=callModel
        )
        
        print(f"\n✓ Refined proposal generated ({len(refined_proposal)} chars)")
        
        # Client evaluates refined proposal
        evaluation = evaluate_refined_proposal(
            refined_proposal=refined_proposal,
            ai_critique_of_original=initial_critique,
            persona_profile=persona_profile,
            initial_ai_advice=initial_ai_advice,
            iteration_number=iteration,
            callModel=callModel
        )
        
        # Store iteration
        iteration_history.append({
            'iteration': iteration,
            'proposal': refined_proposal,
            'evaluation': evaluation['evaluation_text'],
            'accepted': evaluation['accepted'],
            'friction_score': evaluation['friction_score']
        })
        
        print(f"\n✓ Evaluation complete")
        print(f"  Decision: {'ACCEPT' if evaluation['accepted'] else 'REJECT'}")
        print(f"  Friction Score: {evaluation['friction_score']:.1f}/100")
        
        if evaluation['accepted']:
            print(f"\n{'='*80}")
            print(f"✅ PROPOSAL ACCEPTED AFTER {iteration} ITERATION(S)!")
            print(f"{'='*80}")
            
            return {
                'final_proposal': refined_proposal,
                'final_accepted': True,
                'total_iterations': iteration,
                'iteration_history': iteration_history,
                'final_evaluation': evaluation['evaluation_text'],
                'final_friction_score': evaluation['friction_score'],
                'message': f'Proposal accepted after {iteration} refinement iteration(s)'
            }
        
        # Update for next iteration
        current_proposal = refined_proposal
        current_critique = evaluation['evaluation_text']
        
        if iteration < max_iterations:
            print(f"\n  → Proceeding to iteration #{iteration + 1}")
    
    # Max iterations reached without acceptance
    print(f"\n{'='*80}")
    print(f"❌ MAX ITERATIONS REACHED ({max_iterations}) - FINAL REJECTION")
    print(f"{'='*80}")
    
    return {
        'final_proposal': current_proposal,
        'final_accepted': False,
        'total_iterations': max_iterations,
        'iteration_history': iteration_history,
        'final_evaluation': iteration_history[-1]['evaluation'],
        'final_friction_score': iteration_history[-1]['friction_score'],
        'message': f'Proposal rejected after {max_iterations} refinement attempts'
    }
