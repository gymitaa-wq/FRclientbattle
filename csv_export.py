"""
Enhanced CSV Export Module for Streamlined Simulation
Comprehensive data export with all simulation details
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any

CSV_FILE_PATH = "simulation_history.csv"

def save_simulation_to_csv(result: Dict[str, Any], username: str = "anonymous") -> None:
    """
    Saves complete streamlined simulation results to CSV file.
    
    Args:
        result: Streamlined simulation result dictionary
        username: Username of the logged-in user
    """
    
    # Extract data from result structure
    profile = result.get('profile', {})
    analysis = result.get('outcome_analysis', {})
    final_products = result.get('final_products', {})
    iterations = result.get('iterations', [])
    
    # Build comprehensive row data
    row_data = {
        # User Info
        "username": username,
        
        # Timestamp
        "timestamp": datetime.now().isoformat(),
        
        # Client Profile
        "client_id": profile.get('profile_id', 'unknown'),
        "age": profile.get('age', 0),
        "gender": profile.get('gender', ''),
        "marital_status": profile.get('marital_status', ''),
        "num_children": profile.get('num_children', 0),
        "occupation": profile.get('occupation', ''),
        "annual_income": profile.get('annual_income', 0),
        "total_household_income": profile.get('total_household_income', 0),
        "net_worth": profile.get('net_worth', 0),
        "coverage_gap": profile.get('coverage_gap', 0),
        "skepticism_level": profile.get('skepticism_level', 0),
        "risk_tolerance": profile.get('risk_tolerance', ''),
        "decision_style": profile.get('decision_style', ''),
        "financial_literacy": profile.get('financial_literacy', ''),
        "health_status": profile.get('health_status', ''),
        "primary_concern": profile.get('primary_concern', ''),
        
        # Simulation Results
        "deal_closed": result.get('deal_closed', False),
        "decision": "CONVERT" if result.get('deal_closed', False) else "REJECT",
        "total_iterations": result.get('total_iterations', 0),
        "final_friction_score": result.get('final_friction_score', 0.0),
        "initial_friction_score": iterations[0]['friction_score'] if iterations else 0.0,
        "friction_reduction": analysis.get('friction_reduction', 0.0),
        
        # Deal Analysis
        "closure_reasons": "; ".join(analysis.get('closure_reasons', [])) if result.get('deal_closed') else "",
        "rejection_reasons": "; ".join(analysis.get('rejection_reasons', [])) if not result.get('deal_closed') else "",
        "winning_factors": "; ".join(analysis.get('winning_factors', [])) if result.get('deal_closed') else "",
        "remaining_concerns": "; ".join(analysis.get('remaining_concerns', [])[:3]) if not result.get('deal_closed') else "",
        
        # Final Products (if deal closed)
        "total_monthly_premium": final_products.get('total_monthly', 0),
        "total_annual_premium": final_products.get('total_annual', 0),
        "num_products": len(final_products.get('products', [])),
        "products_list": "; ".join([p['name'] for p in final_products.get('products', [])]),
        
        # Iteration Details
        "iteration_0_friction": iterations[0]['friction_score'] if len(iterations) > 0 else 0,
        "iteration_1_friction": iterations[1]['friction_score'] if len(iterations) > 1 else 0,
        "iteration_2_friction": iterations[2]['friction_score'] if len(iterations) > 2 else 0,
        "iteration_0_decision": "ACCEPT" if (len(iterations) > 0 and iterations[0]['accepted']) else "REJECT",
        "iteration_1_decision": "ACCEPT" if (len(iterations) > 1 and iterations[1]['accepted']) else "REJECT" if len(iterations) > 1 else "",
        "iteration_2_decision": "ACCEPT" if (len(iterations) > 2 and iterations[2]['accepted']) else "REJECT" if len(iterations) > 2 else "",
    }
    
    # Create DataFrame
    df_new = pd.DataFrame([row_data])
    
    # Append to existing CSV or create new one
    if os.path.exists(CSV_FILE_PATH):
        df_existing = pd.read_csv(CSV_FILE_PATH)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    
    # Save to CSV
    df_combined.to_csv(CSV_FILE_PATH, index=False)
    
    print(f"✓ Saved simulation to {CSV_FILE_PATH}")
    return CSV_FILE_PATH


def load_simulation_history(username: str = None) -> pd.DataFrame:
    """
    Loads simulation history from CSV file.
    
    Args:
        username: Optional username to filter results. If None, returns all.
    
    Returns:
        DataFrame with simulation history, or empty DataFrame if file doesn't exist
    """
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Filter by username if provided
        if username and 'username' in df.columns:
            df = df[df['username'] == username]
        
        return df
    else:
        return pd.DataFrame()


def get_history_stats(username: str = None) -> Dict[str, Any]:
    """
    Calculates statistics from simulation history.
    
    Args:
        username: Optional username to filter stats. If None, returns all.
    
    Returns:
        Dictionary with statistics
    """
    df = load_simulation_history(username)
    
    if df.empty:
        return {
            "total_simulations": 0,
            "conversion_rate": 0.0,
            "avg_friction_score": 0.0
        }
    
    total = len(df)
    conversions = len(df[df['decision'] == 'CONVERT'])
    
    return {
        "total_simulations": total,
        "conversion_rate": (conversions / total * 100) if total > 0 else 0.0,
        "avg_friction_score": df['final_friction_score'].mean() if total > 0 else 0.0,
        "latest_timestamp": df['timestamp'].iloc[-1] if total > 0 else "N/A"
    }
