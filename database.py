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
        
        # Extract product names
        p_names = [p['name'] for p in final_products.get('products', [])]
        p_names_str = "; ".join(p_names)
        
        # Extract reasons
        rejection_str = "; ".join(outcome_analysis.get('rejection_reasons', []))
        winning_str = "; ".join(outcome_analysis.get('winning_factors', []))
        
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
            deal_closed=result.get('deal_closed', False),
            final_friction_score=result.get('final_friction_score', 0.0),
            total_iterations=result.get('total_iterations', 0),
            rejection_reasons=rejection_str,
            winning_factors=winning_str,
            
            # Product fields
            total_monthly_premium=final_products.get('total_monthly', 0.0),
            product_names=p_names_str,
            
            # Full JSON blobs
            profile_data=profile,
            iterations_data=result.get('iterations', []),
            outcome_analysis_data=result.get('outcome_analysis', {}),
            final_products_data=final_products
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record.id
    except Exception as e:
        print(f"Error saving to DB: {e}")
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
