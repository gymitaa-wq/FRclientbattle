"""
Main Orchestrator for Streamlined Simulation
Runs complete simulation from profile to final results
"""

from typing import Dict, Any
from structured_profile_generator import generate_structured_client_profile, format_profile_for_display
from streamlined_simulation import (
    simulate_fr_client_interaction,
    generate_iteration_summary,
    analyze_deal_outcome,
    extract_final_products
)
from project_caii_framework import callModel


def run_streamlined_simulation(
    profile: Dict[str, Any] = None,
    max_iterations: int = 3,
    enable_refinement: bool = True
) -> Dict[str, Any]:
    """
    Runs complete streamlined simulation from profile.
    
    Args:
        profile: Client profile dict (generates if None)
        max_iterations: Max refinement iterations
        enable_refinement: Enable iterative refinement
    
    Returns:
        Complete simulation results
    """
    
    # Generate profile if not provided
    if profile is None:
        print("\n" + "="*70)
        print("GENERATING CLIENT PROFILE")
        print("="*70)
        profile = generate_structured_client_profile()
        print(format_profile_for_display(profile))
    
    print("\n" + "="*70)
    print("STARTING SIMULATION")
    print(f"Client: {profile['profile_id']}")
    print(f"Max Iterations: {max_iterations}")
    print(f"Refinement: {'Enabled' if enable_refinement else 'Disabled'}")
    print("="*70)
    
    all_iterations = []
    iteration = 0
    
    # Initial iteration
    print(f"\n{'='*70}")
    print(f"ITERATION {iteration}: INITIAL PROPOSAL")
    print(f"{'='*70}")
    
    iteration_result = simulate_fr_client_interaction(
        profile=profile,
        iteration=iteration,
        callModel=callModel
    )
    
    all_iterations.append(iteration_result)
    
    # Print iteration summary
    summary = generate_iteration_summary(iteration_result)
    print(summary)
    
    # Check if accepted
    if iteration_result['accepted']:
        print("\n✅ DEAL CLOSED ON FIRST PROPOSAL!")
    elif not enable_refinement:
        print("\n❌ DEAL NOT CLOSED (Refinement disabled)")
    else:
        # Refinement loop
        previous_iteration = iteration_result
        
        for iteration in range(1, max_iterations + 1):
            if previous_iteration['accepted']:
                break
            
            print(f"\n{'='*70}")
            print(f"ITERATION {iteration}: REFINING PROPOSAL")
            print(f"{'='*70}")
            
            iteration_result = simulate_fr_client_interaction(
                profile=profile,
                iteration=iteration,
                previous_proposal=previous_iteration['proposal'],
                previous_critique=previous_iteration['ai_critique'],
                callModel=callModel
            )
            
            all_iterations.append(iteration_result)
            
            # Print iteration summary
            summary = generate_iteration_summary(iteration_result, previous_iteration)
            print(summary)
            
            if iteration_result['accepted']:
                print(f"\n✅ DEAL CLOSED AFTER {iteration} REFINEMENT(S)!")
                break
            elif iteration == max_iterations:
                print(f"\n❌ MAX ITERATIONS REACHED - DEAL NOT CLOSED")
            
            previous_iteration = iteration_result
    
    # Analyze outcome
    print("\n" + "="*70)
    print("ANALYZING DEAL OUTCOME")
    print("="*70)
    
    final_iteration = all_iterations[-1]
    outcome_analysis = analyze_deal_outcome(final_iteration, all_iterations, profile)
    
    # Extract final products if accepted (using LLM, not regex!)
    final_products = extract_final_products(
        final_iteration['proposal'],
        final_iteration['accepted'],
        callModel=callModel
    )
    
    # Build complete results
    results = {
        'profile': profile,
        'iterations': all_iterations,
        'outcome_analysis': outcome_analysis,
        'final_products': final_products,
        'deal_closed': final_iteration['accepted'],
        'total_iterations': len(all_iterations),
        'final_friction_score': final_iteration['friction_score'],
        'simulation_complete': True
    }
    
    # Print final summary
    print_final_summary(results)
    
    return results


def print_final_summary(results: Dict[str, Any]):
    """Prints final simulation summary."""
    
    analysis = results['outcome_analysis']
    
    print("\n" + "="*70)
    print("FINAL SIMULATION SUMMARY")
    print("="*70)
    
    print(f"\nClient: {results['profile']['profile_id']}")
    print(f"Total Iterations: {results['total_iterations']}")
    print(f"Final Friction Score: {results['final_friction_score']:.1f}/100")
    
    if analysis['friction_reduction'] > 0:
        print(f"Friction Reduction: {analysis['friction_reduction']:.1f} points")
    
    print(f"\nDeal Status: {'✅ CLOSED' if results['deal_closed'] else '❌ NOT CLOSED'}")
    
    if results['deal_closed']:
        print("\n🎉 CLOSURE REASONS:")
        for reason in analysis.get('closure_reasons', []):
            print(f"  ✓ {reason}")
        
        if analysis.get('winning_factors'):
            print("\n🏆 WINNING FACTORS:")
            for factor in analysis['winning_factors']:
                print(f"  • {factor}")
        
        print("\n💼 FINAL PRODUCTS:")
        products = results['final_products']
        if products['products']:
            for product in products['products']:
                print(f"  • {product['name']}: ${product['monthly_premium']}/month")
            print(f"\n  TOTAL: ${products['total_monthly']:,}/month (${products['total_annual']:,}/year)")
        else:
            print("  (See proposal text for details)")
    
    else:
        print("\n❌ REJECTION REASONS:")
        for reason in analysis.get('rejection_reasons', []):
            print(f"  ✗ {reason}")
        
        if analysis.get('remaining_concerns'):
            print("\n⚠️  REMAINING CONCERNS:")
            for concern in analysis['remaining_concerns'][:3]:
                print(f"  • {concern}")
    
    print("\n" + "="*70)


# Test function
if __name__ == "__main__":
    print("="*70)
    print("STREAMLINED SIMULATION TEST")
    print("="*70)
    print("\nThis will run a complete simulation with a random client profile.")
    print("Note: This uses real LLM calls and will take a few minutes.")
    print("\nPress Ctrl+C to cancel, or wait to continue...")
    
    import time
    time.sleep(3)
    
    results = run_streamlined_simulation(
        max_iterations=3,
        enable_refinement=True
    )
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print(f"\nResults available in 'results' variable")
    print(f"Deal closed: {results['deal_closed']}")
    print(f"Total iterations: {results['total_iterations']}")
