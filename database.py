"""
Database Manager for Insurance Simulation
Handles persistence of simulation results using SQLAlchemy.
Supports SQLite (local) and PostgreSQL (production).
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Base class for models
Base = declarative_base()

class SimulationResult(Base):
    """Model for storing complete simulation results"""
    __tablename__ = 'simulation_results'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    username = Column(String(100), index=True)
    
    # Client Profile (flattened key fields + JSON for full dump)
    client_id = Column(String(50))
    age = Column(Integer)
    annual_income = Column(Float)
    total_household_income = Column(Float)
    occupation = Column(String(100))
    
    # Outcome
    deal_closed = Column(Boolean)
    final_friction_score = Column(Float)
    total_iterations = Column(Integer)
    
    # Detail fields
    rejection_reasons = Column(Text)
    winning_factors = Column(Text)
    net_worth = Column(Float)
    marital_status = Column(String(50))

    # Product fields
    total_monthly_premium = Column(Float)
    product_names = Column(String(500))
    
    # Full Data Blobs (for detailed reconstruction)
    profile_data = Column(JSON)  # Full profile dict
    iterations_data = Column(JSON)  # List of iteration detailed dicts
    outcome_analysis_data = Column(JSON) # Outcome analysis dict
    final_products_data = Column(JSON) # Full product details


class BattleResult(Base):
    """Model for storing Battle Engine stress test results"""
    __tablename__ = 'battle_results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    username = Column(String(100), index=True)
    
    # Client Profile (key fields)
    client_id = Column(String(50))
    age = Column(Integer)
    occupation = Column(String(100))
    skepticism_level = Column(Integer)  # 1-10 scale
    
    # Model used for stress test
    model_name = Column(String(50))
    
    # Battle Results
    success = Column(Boolean)  # Did all 3 stages complete?
    error_message = Column(Text)  # If failed, what was the error?
    
    # Full Data Blobs (all three stages)
    profile_data = Column(JSON)  # Full client profile
    stage1_proposal = Column(Text)  # Initial hybrid proposal
    stage2_attack = Column(Text)  # AI adversary critique
    stage3_defense = Column(Text)  # Refined battle-hardened proposal
    
    # New: Friction Score and Public AI Simulation
    friction_score = Column(Float)  # 0-100 score of proposal persuasiveness
    friction_analysis = Column(Text)  # Detailed analysis of friction points
    public_ai_response = Column(Text)  # What client sees from ChatGPT/Claude/Gemini

def get_database_url():
    """Get DB URL from environment or default to local SQLite"""
    # Render provides DATABASE_URL for Postgres
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        # Fix for SQLAlchemy requiring postgresql://
        url = url.replace("postgres://", "postgresql://", 1)
    
    if not url:
        # Default to local SQLite in current directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "simulation_data.db")
        url = f"sqlite:///{db_path}"
        
    return url

# Initialize engine and session factory
engine = create_engine(get_database_url(), echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Data Access Layer

def save_simulation(result: Dict[str, Any], username: str = "anonymous") -> int:
    """Save a simulation result to the database"""
    db = SessionLocal()
    try:
        profile = result.get('profile', {})
        final_products = result.get('final_products', {})
        outcome_analysis = result.get('outcome_analysis', {})
        deal_closed = result.get('deal_closed', False)
        
        # Extract product names
        products_list = final_products.get('products', [])
        if products_list:
            p_names = [p.get('name', 'Unknown Product') for p in products_list]
            p_names_str = "; ".join(p_names)
        else:
            p_names_str = "No products" if not deal_closed else ""
        
        # Extract total monthly premium
        total_monthly = final_products.get('total_monthly', 0)
        if total_monthly == 0 and products_list:
            # Try to calculate from products if missing
            try:
                total_monthly = sum(p.get('premium_value', 0) for p in products_list)
            except:
                pass
        
        # Extract reasons based on deal outcome
        if deal_closed:
            # Deal accepted - get winning factors
            winning_factors = outcome_analysis.get('winning_factors', [])
            closure_reasons = outcome_analysis.get('closure_reasons', [])
            
            # Combine both for comprehensive view
            all_reasons = winning_factors + closure_reasons
            winning_str = "; ".join(all_reasons) if all_reasons else "Deal accepted"
            rejection_str = ""  # Empty for accepted deals
        else:
            # Deal rejected - get rejection reasons
            rejection_reasons = outcome_analysis.get('rejection_reasons', [])
            remaining_concerns = outcome_analysis.get('remaining_concerns', [])
            
            # Combine both for comprehensive view
            all_rejections = rejection_reasons + remaining_concerns[:2]  # Limit concerns to 2
            rejection_str = "; ".join(all_rejections) if all_rejections else "Deal rejected"
            winning_str = ""  # Empty for rejected deals
        
        # Debug logging
        print(f"DEBUG: Saving simulation - Deal closed: {deal_closed}")
        print(f"DEBUG: Product names: {p_names_str}")
        print(f"DEBUG: Total monthly: {total_monthly}")
        print(f"DEBUG: Rejection reasons: {rejection_str}")
        print(f"DEBUG: Winning factors: {winning_str}")
        
        # Create record
        db_record = SimulationResult(
            username=username,
            timestamp=datetime.now(),
            
            # Profile fields
            client_id=profile.get('profile_id', 'unknown'),
            age=profile.get('age', 0),
            annual_income=profile.get('annual_income', 0.0),
            total_household_income=profile.get('total_household_income', 0.0),
            occupation=profile.get('occupation', 'unknown'),
            net_worth=profile.get('net_worth', 0.0),
            marital_status=profile.get('marital_status', 'unknown'),
            
            # Outcome fields
            deal_closed=deal_closed,
            final_friction_score=result.get('final_friction_score', 0.0),
            total_iterations=result.get('total_iterations', 0),
            rejection_reasons=rejection_str,
            winning_factors=winning_str,
            
            # Product fields
            total_monthly_premium=float(total_monthly),
            product_names=p_names_str,
            
            # Full JSON blobs
            profile_data=profile,
            iterations_data=result.get('iterations', []),
            outcome_analysis_data=outcome_analysis,
            final_products_data=final_products
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record.id
    except Exception as e:
        print(f"Error saving to DB: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise e
    finally:
        db.close()

def load_history_df(username: Optional[str] = None):
    """Load history as a Pandas DataFrame (for API compatibility)"""
    import pandas as pd
    
    db = SessionLocal()
    try:
        query = db.query(SimulationResult)
        if username:
            query = query.filter(SimulationResult.username == username)
            
        results = query.order_by(SimulationResult.timestamp.desc()).all()
        
        if not results:
            return pd.DataFrame()
            
        # Convert to dict list for DataFrame
        data = []
        for r in results:
            row = {
                "id": r.id,
                "username": r.username,
                "timestamp": r.timestamp,
                "client_id": r.client_id,
                "age": r.age,
                "occupation": r.occupation,
                "total_household_income": r.total_household_income,
                "net_worth": r.net_worth,
                "marital_status": r.marital_status,
                "deal_closed": r.deal_closed,
                "decision": "CONVERT" if r.deal_closed else "REJECT",
                "final_friction_score": r.final_friction_score,
                "total_iterations": r.total_iterations,
                "rejection_reasons": r.rejection_reasons,
                "winning_factors": r.winning_factors,
                "product_names": r.product_names,
                "total_monthly_premium": r.total_monthly_premium
            }
            data.append(row)
            
        return pd.DataFrame(data)
    finally:
        db.close()

def get_simulation_details(sim_id: int):
    """Fetch full details for a single simulation"""
    db = SessionLocal()
    try:
        result = db.query(SimulationResult).filter(SimulationResult.id == sim_id).first()
        if result:
             return {
                 "id": result.id,
                 "iterations_data": result.iterations_data,
                 "profile_data": result.profile_data,
                 "outcome_analysis": result.outcome_analysis_data,
                 "final_products": result.final_products_data
             }
        return None
    finally:
        db.close()

def get_stats(username: Optional[str] = None) -> Dict[str, Any]:
    """Get aggregated statistics"""
    db = SessionLocal()
    try:
        query = db.query(SimulationResult)
        if username:
            query = query.filter(SimulationResult.username == username)
            
        total = query.count()
        if total == 0:
            return {
                "total_simulations": 0,
                "conversion_rate": 0.0,
                "avg_friction_score": 0.0,
                "latest_timestamp": "N/A"
            }
            
        wins = query.filter(SimulationResult.deal_closed == True).count()
        
        # Calculate avg friction (sqlite doesn't like complex aggregations sometimes, doing python side for safety/speed on small data)
        # For larger datasets, use func.avg
        from sqlalchemy import func
        avg_friction = db.query(func.avg(SimulationResult.final_friction_score)).scalar() or 0.0
        
        latest = query.order_by(SimulationResult.timestamp.desc()).first()
        latest_ts = latest.timestamp.isoformat() if latest else "N/A"
        
        return {
            "total_simulations": total,
            "conversion_rate": (wins / total * 100) if total > 0 else 0.0,
            "avg_friction_score": float(avg_friction),
            "latest_timestamp": latest_ts
        }
    finally:
        db.close()


# ============================================================================
# BATTLE ENGINE DATA ACCESS FUNCTIONS
# ============================================================================

def save_battle_result(
    profile: Dict[str, Any],
    stage1_proposal: str,
    stage2_attack: str,
    stage3_defense: str,
    model_name: str,
    username: str = "anonymous",
    success: bool = True,
    error_message: str = None,
    friction_score: float = None,
    friction_analysis: str = None,
    public_ai_response: str = None
) -> int:
    """Save a Battle Engine stress test result to the database"""
    db = SessionLocal()
    try:
        # Extract key profile fields
        client_id = profile.get('profile_id', 'unknown')
        age = profile.get('age', 0)
        occupation = profile.get('occupation', 'unknown')
        skepticism_level = profile.get('ai_skepticism_level', 5)
        
        # Create record
        db_record = BattleResult(
            username=username,
            timestamp=datetime.now(),
            
            # Profile fields
            client_id=client_id,
            age=age,
            occupation=occupation,
            skepticism_level=skepticism_level,
            
            # Battle metadata
            model_name=model_name,
            success=success,
            error_message=error_message,
            
            # Full data blobs
            profile_data=profile,
            stage1_proposal=stage1_proposal,
            stage2_attack=stage2_attack,
            stage3_defense=stage3_defense,
            
            # New: Friction and Public AI fields
            friction_score=friction_score,
            friction_analysis=friction_analysis,
            public_ai_response=public_ai_response
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record.id
    except Exception as e:
        print(f"Error saving battle result to DB: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


def load_battle_history_df(username: Optional[str] = None):
    """Load battle history as a Pandas DataFrame"""
    import pandas as pd
    
    db = SessionLocal()
    try:
        query = db.query(BattleResult)
        if username:
            query = query.filter(BattleResult.username == username)
            
        results = query.order_by(BattleResult.timestamp.desc()).all()
        
        if not results:
            return pd.DataFrame()
            
        # Convert to dict list for DataFrame
        data = []
        for r in results:
            row = {
                "id": r.id,
                "username": r.username,
                "timestamp": r.timestamp,
                "client_id": r.client_id,
                "age": r.age,
                "occupation": r.occupation,
                "skepticism": f"{r.skepticism_level}/10",
                "model": r.model_name,
                "status": "✅ Success" if r.success else "❌ Failed",
                "success": r.success
            }
            data.append(row)
            
        return pd.DataFrame(data)
    finally:
        db.close()


def get_battle_details(battle_id: int):
    """Fetch full details for a single battle"""
    db = SessionLocal()
    try:
        result = db.query(BattleResult).filter(BattleResult.id == battle_id).first()
        if result:
            return {
                "id": result.id,
                "timestamp": result.timestamp,
                "username": result.username,
                "client_id": result.client_id,
                "age": result.age,
                "occupation": result.occupation,
                "skepticism_level": result.skepticism_level,
                "model_name": result.model_name,
                "success": result.success,
                "error_message": result.error_message,
                "profile_data": result.profile_data,
                "stage1_proposal": result.stage1_proposal,
                "stage2_attack": result.stage2_attack,
                "stage3_defense": result.stage3_defense,
                "friction_score": result.friction_score,
                "friction_analysis": result.friction_analysis,
                "public_ai_response": result.public_ai_response
            }
        return None
    finally:
        db.close()


def get_battle_stats(username: Optional[str] = None) -> Dict[str, Any]:
    """Get aggregated battle statistics"""
    db = SessionLocal()
    try:
        query = db.query(BattleResult)
        if username:
            query = query.filter(BattleResult.username == username)
            
        total = query.count()
        if total == 0:
            return {
                "total_battles": 0,
                "success_rate": 0.0,
                "avg_skepticism": 0.0,
                "latest_timestamp": "N/A"
            }
            
        successes = query.filter(BattleResult.success == True).count()
        
        # Calculate avg skepticism
        from sqlalchemy import func
        avg_skepticism = db.query(func.avg(BattleResult.skepticism_level)).scalar() or 0.0
        
        latest = query.order_by(BattleResult.timestamp.desc()).first()
        latest_ts = latest.timestamp.isoformat() if latest else "N/A"
        
        return {
            "total_battles": total,
            "success_rate": (successes / total * 100) if total > 0 else 0.0,
            "avg_skepticism": float(avg_skepticism),
            "latest_timestamp": latest_ts
        }
    finally:
        db.close()
