"""
Enhanced run_simulation with iterative refinement
Wrapper for project_caii_framework that adds negotiation loop
"""

from project_caii_framework import run_simulation as original_run_simulation, callModel
from iterative_refinement import run_iterative_refinement
import traceback


def run_simulation_with_refinement(
    email_history: str,
    model: str = "gemini",
    enable_refinement: bool = True,
    max_iterations: int = 3
):
    """
    Enhanced simulation with iterative proposal refinement.
    
    Args:
        email_history: 50 email interactions
        model: LLM model to use
        enable_refinement: Enable iterative refinement loop
        max_iterations: Maximum refinement attempts
    
    Returns:
        Final simulation state with refinement results
    """
    
    # Run initial simulation
    print("\n" + "="*80)
    print("RUNNING INITIAL SIMULATION")
    print("="*80)
    
    state = original_run_simulation(email_history, model=model)
    
    # Check if refinement is needed
    converted = state['metadata'].get('converted', False)
    
    if not converted and enable_refinement:
        print("\n" + "="*80)
        print("CLIENT REJECTED - STARTING ITERATIVE REFINEMENT")
        print(f"Maximum iterations: {max_iterations}")
        print("="*80)
        
        try:
            refinement_result = run_iterative_refinement(
                initial_proposal=state['proposal_text'],
                initial_critique=state['ai_critique'],
                initial_decision=state['outcome'],
                persona_profile=state['persona_profile'],
                initial_ai_advice=state['initial_ai_advice'],
                callModel=callModel,
                max_iterations=max_iterations
            )
            
            # Update state with refinement results
            state['proposal_text'] = refinement_result['final_proposal']
            state['metadata']['converted'] = refinement_result['final_accepted']
            state['metadata']['total_iterations'] = refinement_result['total_iterations']
            state['metadata']['iteration_history'] = refinement_result['iteration_history']
            state['metadata']['refinement_enabled'] = True
            state['friction_score'] = refinement_result.get('final_friction_score', state['friction_score'])
            
            # Update outcome
            if refinement_result['final_accepted']:
                state['outcome'] = f"✅ CONVERTED after {refinement_result['total_iterations']} refinement iteration(s)\n\n{refinement_result['final_evaluation']}"
            else:
                state['outcome'] = f"❌ REJECTED after {refinement_result['total_iterations']} refinement iteration(s)\n\n{refinement_result['final_evaluation']}"
            
            print("\n" + "="*80)
            print("REFINEMENT COMPLETE")
            print("="*80)
            print(f"Final Decision: {'CONVERT ✅' if refinement_result['final_accepted'] else 'REJECT ❌'}")
            print(f"Total Iterations: {refinement_result['total_iterations']}")
            print(f"Final Friction Score: {refinement_result.get('final_friction_score', 'N/A'):.1f}/100")
            
        except Exception as e:
            print(f"\n⚠ Refinement failed: {e}")
            traceback.print_exc()
            state['metadata']['refinement_error'] = str(e)
    else:
        state['metadata']['total_iterations'] = 0
        state['metadata']['refinement_enabled'] = False
        
        if converted:
            print("\n✅ Initial proposal ACCEPTED - No refinement needed")
        else:
            print("\n⚠ Refinement disabled - Final decision: REJECT")
    
    return state


# Convenience function
def run_simulation(email_history: str, model: str = "gemini", **kwargs):
    """
    Main entry point - automatically uses refinement if available.
    
    Args:
        email_history: Email interactions
        model: LLM model
        enable_refinement: Enable refinement loop (default: True)
        max_iterations: Max refinement attempts (default: 3)
    
    Returns:
        Simulation state
    """
    enable_refinement = kwargs.get('enable_refinement', True)
    max_iterations = kwargs.get('max_iterations', 3)
    
    return run_simulation_with_refinement(
        email_history=email_history,
        model=model,
        enable_refinement=enable_refinement,
        max_iterations=max_iterations
    )


if __name__ == "__main__":
    # Test with sample data
    from project_caii_framework import SAMPLE_EMAIL_HISTORY
    
    print("Testing enhanced simulation with refinement...")
    result = run_simulation(
        SAMPLE_EMAIL_HISTORY,
        model="gemini",
        enable_refinement=True,
        max_iterations=3
    )
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Converted: {result['metadata'].get('converted')}")
    print(f"Iterations: {result['metadata'].get('total_iterations', 0)}")
    print(f"Friction Score: {result['friction_score']:.1f}/100")
