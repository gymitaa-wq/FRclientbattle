# Iterative Proposal Refinement - Integration Guide

## Overview

This feature adds a **negotiation loop** to the simulation:
- When client **rejects** initial proposal
- FR **refines** proposal based on AI critique
- Client **re-evaluates** refined proposal
- **Repeats** until acceptance or max iterations (default: 3)

## How It Works

### Flow Diagram

```
Initial Proposal → AI Critique → Client Decision
                                      ↓
                                   REJECT?
                                      ↓
                        ┌─────────────┴─────────────┐
                        ↓                           ↓
                  FR Refines Proposal          ACCEPT → END
                        ↓
                  AI Re-evaluates
                        ↓
                  Client Decision
                        ↓
                    REJECT?
                        ↓
                  (Repeat up to max_iterations)
```

### Example Scenario

**Iteration 0 (Initial):**
- FR proposes: $461/month (Term + Whole Life + DI)
- AI critiques: "Whole life unnecessary, too expensive"
- Client: **REJECT** (Friction: 75)

**Iteration 1:**
- FR refines: $250/month (Term + DI only, removed whole life)
- AI evaluates: "Better, but still pricey"
- Client: **REJECT** (Friction: 55)

**Iteration 2:**
- FR refines: $180/month (Optimized term, competitive DI)
- AI evaluates: "Good value, addresses concerns"
- Client: **ACCEPT** ✅ (Friction: 35)

## Files Created

1. **`iterative_refinement.py`** - Core refinement logic
   - `refine_proposal_based_on_critique()` - FR revises proposal
   - `evaluate_refined_proposal()` - Client re-evaluates
   - `run_iterative_refinement()` - Main loop

## Integration into Framework

### Option 1: Quick Test (Standalone)

```python
from iterative_refinement import run_iterative_refinement
from project_caii_framework import callModel

# After initial simulation shows REJECT
result = run_iterative_refinement(
    initial_proposal=state['proposal_text'],
    initial_critique=state['ai_critique'],
    initial_decision=state['outcome'],
    persona_profile=state['persona_profile'],
    initial_ai_advice=state['initial_ai_advice'],
    callModel=callModel,
    max_iterations=3
)

print(f"Final result: {result['message']}")
print(f"Total iterations: {result['total_iterations']}")
print(f"Accepted: {result['final_accepted']}")
```

### Option 2: Full Integration (Modify Framework)

Add to `project_caii_framework.py` after the `final_client_decision` node:

```python
from iterative_refinement import run_iterative_refinement

def final_decision_with_refinement(state: SimulationState) -> SimulationState:
    """
    Enhanced final decision node with iterative refinement.
    """
    # Run initial decision (existing code)
    state = final_client_decision(state)
    
    # Check if rejected
    converted = state['metadata'].get('converted', False)
    
    if not converted:
        print("\n" + "="*80)
        print("CLIENT REJECTED - STARTING REFINEMENT PROCESS")
        print("="*80)
        
        # Run refinement loop
        refinement_result = run_iterative_refinement(
            initial_proposal=state['proposal_text'],
            initial_critique=state['ai_critique'],
            initial_decision=state['outcome'],
            persona_profile=state['persona_profile'],
            initial_ai_advice=state['initial_ai_advice'],
            callModel=callModel,
            max_iterations=3
        )
        
        # Update state with final results
        state['proposal_text'] = refinement_result['final_proposal']
        state['metadata']['converted'] = refinement_result['final_accepted']
        state['metadata']['total_iterations'] = refinement_result['total_iterations']
        state['metadata']['iteration_history'] = refinement_result['iteration_history']
        state['friction_score'] = refinement_result.get('final_friction_score', state['friction_score'])
        
        # Update outcome
        if refinement_result['final_accepted']:
            state['outcome'] = f"CONVERTED after {refinement_result['total_iterations']} iterations\n\n" + refinement_result['final_evaluation']
        else:
            state['outcome'] = f"REJECTED after {refinement_result['total_iterations']} iterations\n\n" + refinement_result['final_evaluation']
    
    return state
```

### Option 3: Streamlit Integration

Add checkbox in Streamlit UI:

```python
# In streamlit_app.py, Tab 1
enable_refinement = st.checkbox(
    "Enable Iterative Refinement",
    value=True,
    help="If client rejects, FR will refine proposal up to 3 times"
)

max_iterations = st.slider(
    "Max Refinement Iterations",
    min_value=1,
    max_value=5,
    value=3,
    help="How many times FR can refine the proposal"
)
```

Then pass to simulation:

```python
result = run_simulation(
    email_history,
    model=model_option,
    enable_refinement=enable_refinement,
    max_iterations=max_iterations
)
```

## Configuration

### Parameters

- **`max_iterations`**: Maximum refinement attempts (default: 3)
  - 1 = One revision attempt
  - 3 = Up to three revisions (recommended)
  - 5 = Extended negotiation

### Stopping Conditions

Loop stops when:
1. **Client accepts** proposal
2. **Max iterations** reached
3. **Error** occurs

## Output Structure

```python
{
    'final_proposal': str,  # Last proposal (accepted or final rejected)
    'final_accepted': bool,  # True if eventually accepted
    'total_iterations': int,  # Number of refinement cycles
    'iteration_history': [
        {
            'iteration': 1,
            'proposal': str,
            'evaluation': str,
            'accepted': bool,
            'friction_score': float
        },
        # ... more iterations
    ],
    'final_evaluation': str,  # Last evaluation text
    'final_friction_score': float,  # Final friction score
    'message': str  # Summary message
}
```

## CSV Export Enhancement

Update `csv_export.py` to track iterations:

```python
row_data = {
    "timestamp": datetime.now().isoformat(),
    "decision": "CONVERT" if state['metadata'].get('converted') else "REJECT",
    "friction_score": state['friction_score'],
    "iterations": state['metadata'].get('total_iterations', 0),  # NEW
    "model_used": state['metadata'].get('model', 'unknown'),
    # ... rest of fields
}
```

## Benefits

✅ **More Realistic**: Simulates actual negotiation process  
✅ **Better Insights**: See what changes lead to acceptance  
✅ **Adaptive FR**: FR learns to address AI concerns  
✅ **Conversion Tracking**: Measure how many rejections become conversions  
✅ **Strategy Development**: Identify winning refinement patterns  

## Example Output

```
================================================================================
STARTING ITERATIVE REFINEMENT PROCESS
Maximum iterations: 3
================================================================================

================================================================================
ITERATION #1: REFINING PROPOSAL
================================================================================

✓ Refined proposal generated (3,245 chars)

✓ Evaluation complete
  Decision: REJECT
  Friction Score: 58.0/100

  → Proceeding to iteration #2

================================================================================
ITERATION #2: REFINING PROPOSAL
================================================================================

✓ Refined proposal generated (2,987 chars)

✓ Evaluation complete
  Decision: ACCEPT
  Friction Score: 38.0/100

================================================================================
✅ PROPOSAL ACCEPTED AFTER 2 ITERATION(S)!
================================================================================
```

## Testing

Test the module:

```bash
python -c "from iterative_refinement import run_iterative_refinement; print('✓ Module loaded')"
```

## Next Steps

1. **Test standalone** with sample data
2. **Integrate into framework** (Option 2)
3. **Add to Streamlit UI** (Option 3)
4. **Update CSV export** to track iterations
5. **Run simulations** and analyze refinement patterns

## Advanced: Analysis

After running multiple simulations, analyze:
- **Average iterations to convert**: How many refinements typically needed?
- **Conversion rate improvement**: % of rejections that become conversions
- **Friction score reduction**: How much friction decreases per iteration
- **Common refinement patterns**: What changes work best?

This creates a powerful tool for developing "AI-proof" sales strategies!
