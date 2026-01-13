"""
Insurance Premium Calculator for Project CAII

Calculates realistic insurance premiums and projections based on client profile.
Uses industry-standard formulas and actuarial tables.
"""

from typing import Dict, Tuple
import math


class InsurancePremiumCalculator:
    """
    Calculates realistic insurance premiums based on client profile.
    """
    
    # Base rates per $1,000 of coverage (monthly)
    TERM_BASE_RATES = {
        # Age ranges: (min_age, max_age): base_rate_per_1000
        (25, 29): 0.06,
        (30, 34): 0.08,
        (35, 39): 0.12,
        (40, 44): 0.18,
        (45, 49): 0.30,
        (50, 54): 0.50,
        (55, 59): 0.85,
        (60, 64): 1.40,
    }
    
    # Whole life rates (higher than term)
    WHOLE_LIFE_MULTIPLIER = 8.0  # Whole life is ~8x term rates
    
    # Disability insurance: % of income (monthly premium per $100 of monthly benefit)
    DI_RATE_PER_100_BENEFIT = 2.5  # $2.50 per $100 of monthly benefit
    
    def __init__(self, age: int, gender: str = "M", health_class: str = "standard"):
        """
        Initialize calculator with client basics.
        
        Args:
            age: Client age
            gender: "M" or "F"
            health_class: "preferred_plus", "preferred", "standard", "substandard"
        """
        self.age = age
        self.gender = gender
        self.health_class = health_class
        
        # Health class multipliers
        self.health_multipliers = {
            "preferred_plus": 0.75,
            "preferred": 0.85,
            "standard": 1.0,
            "substandard": 1.35
        }
    
    def get_term_base_rate(self) -> float:
        """Get base term life rate per $1,000 of coverage."""
        for (min_age, max_age), rate in self.TERM_BASE_RATES.items():
            if min_age <= self.age <= max_age:
                return rate
        # Default for ages outside range
        if self.age < 25:
            return 0.05
        else:  # 65+
            return 2.00
    
    def calculate_term_life(self, coverage_amount: int, term_years: int) -> Dict:
        """
        Calculate term life insurance premium.
        
        Args:
            coverage_amount: Death benefit amount
            term_years: Term length (10, 20, 30)
        
        Returns:
            Dict with monthly_premium, annual_premium, total_cost
        """
        base_rate = self.get_term_base_rate()
        
        # Term length multiplier (longer terms slightly more expensive)
        term_multipliers = {10: 0.90, 20: 1.0, 30: 1.15}
        term_mult = term_multipliers.get(term_years, 1.0)
        
        # Gender multiplier (females typically 10-15% cheaper)
        gender_mult = 0.88 if self.gender == "F" else 1.0
        
        # Health class multiplier
        health_mult = self.health_multipliers.get(self.health_class, 1.0)
        
        # Calculate monthly premium
        monthly_premium = (coverage_amount / 1000) * base_rate * term_mult * gender_mult * health_mult
        
        # Round to nearest dollar
        monthly_premium = round(monthly_premium, 2)
        annual_premium = monthly_premium * 12
        total_cost = annual_premium * term_years
        
        return {
            "monthly_premium": monthly_premium,
            "annual_premium": annual_premium,
            "total_cost_over_term": total_cost,
            "coverage_amount": coverage_amount,
            "term_years": term_years
        }
    
    def calculate_whole_life(self, coverage_amount: int) -> Dict:
        """
        Calculate whole life insurance premium and cash value projections.
        
        Args:
            coverage_amount: Death benefit amount
        
        Returns:
            Dict with premiums and cash value projections
        """
        # Base on term rate but much higher
        base_term_rate = self.get_term_base_rate()
        whole_life_rate = base_term_rate * self.WHOLE_LIFE_MULTIPLIER
        
        # Health and gender adjustments
        gender_mult = 0.88 if self.gender == "F" else 1.0
        health_mult = self.health_multipliers.get(self.health_class, 1.0)
        
        # Monthly premium
        monthly_premium = (coverage_amount / 1000) * whole_life_rate * gender_mult * health_mult
        monthly_premium = round(monthly_premium, 2)
        annual_premium = monthly_premium * 12
        
        # Cash value projections (simplified model)
        # Typically 0 for first 2-3 years, then builds
        cash_values = self._project_cash_value(annual_premium, coverage_amount)
        
        return {
            "monthly_premium": monthly_premium,
            "annual_premium": annual_premium,
            "coverage_amount": coverage_amount,
            "cash_value_year_10": cash_values[10],
            "cash_value_year_20": cash_values[20],
            "cash_value_year_30": cash_values[30],
            "guaranteed_death_benefit": coverage_amount,
        }
    
    def _project_cash_value(self, annual_premium: float, coverage: int) -> Dict[int, int]:
        """
        Project cash value accumulation over time.
        Simplified model based on industry averages.
        """
        cash_values = {}
        accumulated = 0
        
        for year in range(1, 41):
            if year <= 2:
                # Little to no cash value in first 2 years (fees)
                growth = annual_premium * 0.05
            elif year <= 10:
                # Years 3-10: moderate growth
                growth = annual_premium * 0.70 + (accumulated * 0.04)
            else:
                # Years 11+: better growth
                growth = annual_premium * 0.85 + (accumulated * 0.045)
            
            accumulated += growth
            
            # Cap at death benefit
            accumulated = min(accumulated, coverage * 0.95)
            
            cash_values[year] = int(accumulated)
        
        return cash_values
    
    def calculate_disability_insurance(self, annual_income: int, 
                                       benefit_percentage: float = 0.60,
                                       benefit_period: str = "to_age_65",
                                       elimination_period: int = 90) -> Dict:
        """
        Calculate disability insurance premium.
        
        Args:
            annual_income: Client's annual income
            benefit_percentage: % of income covered (typically 60-70%)
            benefit_period: "to_age_65", "5_year", "2_year"
            elimination_period: Days before benefits start (30, 60, 90, 180)
        
        Returns:
            Dict with premium and benefit details
        """
        monthly_income = annual_income / 12
        monthly_benefit = monthly_income * benefit_percentage
        
        # Base rate per $100 of monthly benefit
        base_rate = self.DI_RATE_PER_100_BENEFIT
        
        # Benefit period multiplier
        period_multipliers = {
            "to_age_65": 1.0,
            "5_year": 0.65,
            "2_year": 0.45
        }
        period_mult = period_multipliers.get(benefit_period, 1.0)
        
        # Elimination period multiplier (longer wait = cheaper)
        elim_multipliers = {30: 1.25, 60: 1.10, 90: 1.0, 180: 0.85}
        elim_mult = elim_multipliers.get(elimination_period, 1.0)
        
        # Age multiplier (older = more expensive)
        if self.age < 30:
            age_mult = 0.75
        elif self.age < 40:
            age_mult = 0.90
        elif self.age < 50:
            age_mult = 1.0
        elif self.age < 60:
            age_mult = 1.30
        else:
            age_mult = 1.70
        
        # Gender (females slightly more expensive for DI)
        gender_mult = 1.15 if self.gender == "F" else 1.0
        
        # Calculate premium
        monthly_premium = (monthly_benefit / 100) * base_rate * period_mult * elim_mult * age_mult * gender_mult
        monthly_premium = round(monthly_premium, 2)
        
        return {
            "monthly_premium": monthly_premium,
            "annual_premium": monthly_premium * 12,
            "monthly_benefit": round(monthly_benefit, 2),
            "annual_benefit": round(monthly_benefit * 12, 2),
            "benefit_period": benefit_period,
            "elimination_period_days": elimination_period,
            "coverage_percentage": int(benefit_percentage * 100)
        }
    
    def calculate_annuity(self, initial_investment: int, 
                         annuity_type: str = "fixed_indexed",
                         deferral_years: int = 10) -> Dict:
        """
        Calculate annuity projections.
        
        Args:
            initial_investment: Lump sum or total contributions
            annuity_type: "fixed", "variable", "fixed_indexed"
            deferral_years: Years before annuitization
        
        Returns:
            Dict with projections
        """
        # Growth rates (conservative estimates)
        growth_rates = {
            "fixed": 0.035,  # 3.5% guaranteed
            "variable": 0.06,  # 6% average (not guaranteed)
            "fixed_indexed": 0.045  # 4.5% average with floor
        }
        
        rate = growth_rates.get(annuity_type, 0.04)
        
        # Project accumulation value
        accumulation_value = initial_investment * ((1 + rate) ** deferral_years)
        
        # Calculate lifetime income (simplified)
        # Using 4% withdrawal rate as baseline
        years_in_retirement = max(85 - (self.age + deferral_years), 15)
        annual_income = accumulation_value * 0.045  # 4.5% payout rate
        monthly_income = annual_income / 12
        
        return {
            "initial_investment": initial_investment,
            "annuity_type": annuity_type,
            "deferral_years": deferral_years,
            "projected_accumulation_value": int(accumulation_value),
            "guaranteed_annual_income": int(annual_income),
            "guaranteed_monthly_income": int(monthly_income),
            "income_start_age": self.age + deferral_years,
            "assumed_growth_rate": f"{rate*100:.1f}%"
        }
    
    def calculate_cash_buffer(self, allocation_amount: int) -> Dict:
        """
        Calculate cash buffer / short-term treasury allocation.
        
        Args:
            allocation_amount: Amount to allocate
        
        Returns:
            Dict with yield projections
        """
        # Current short-term treasury yields (approximate)
        current_yield = 0.045  # 4.5% for short-term treasuries
        
        annual_income = allocation_amount * current_yield
        monthly_income = annual_income / 12
        
        return {
            "allocation_amount": allocation_amount,
            "investment_type": "Short-term Treasury ETF (e.g., SGOV)",
            "current_yield": f"{current_yield*100:.2f}%",
            "annual_income": round(annual_income, 2),
            "monthly_income": round(monthly_income, 2),
            "liquidity": "Same-day",
            "risk_level": "Very Low"
        }
    
    def generate_complete_proposal(self, profile: Dict) -> Dict:
        """
        Generate complete insurance proposal with all products.
        
        Args:
            profile: Dict with client info (age, income, coverage_needs, etc.)
        
        Returns:
            Dict with all product recommendations and premiums
        """
        age = profile.get('age', 35)
        annual_income = profile.get('annual_income', 90000)
        coverage_need = profile.get('coverage_need', 500000)
        
        # Update calculator age
        self.age = age
        
        # Calculate all products
        term_10 = self.calculate_term_life(coverage_need, 10)
        term_20 = self.calculate_term_life(coverage_need, 20)
        term_30 = self.calculate_term_life(coverage_need, 30)
        
        whole_life = self.calculate_whole_life(int(coverage_need * 0.5))
        
        disability = self.calculate_disability_insurance(annual_income)
        
        annuity = self.calculate_annuity(
            initial_investment=int(annual_income * 0.15),
            deferral_years=max(65 - age, 10)
        )
        
        cash_buffer = self.calculate_cash_buffer(int(annual_income * 0.25))
        
        # Total monthly investment
        recommended_monthly = (
            term_20['monthly_premium'] +
            whole_life['monthly_premium'] +
            disability['monthly_premium']
        )
        
        return {
            "term_life_options": {
                "10_year": term_10,
                "20_year": term_20,
                "30_year": term_30
            },
            "whole_life": whole_life,
            "disability_insurance": disability,
            "annuity": annuity,
            "cash_buffer": cash_buffer,
            "total_monthly_investment": round(recommended_monthly, 2),
            "total_annual_investment": round(recommended_monthly * 12, 2)
        }


# Helper function for easy use
def calculate_premiums(age: int, annual_income: int, coverage_amount: int, 
                      gender: str = "M", health_class: str = "standard") -> Dict:
    """
    Convenience function to calculate all premiums at once.
    
    Args:
        age: Client age
        annual_income: Annual income
        coverage_amount: Desired life insurance coverage
        gender: "M" or "F"
        health_class: "preferred_plus", "preferred", "standard", "substandard"
    
    Returns:
        Complete proposal with all products
    """
    calculator = InsurancePremiumCalculator(age, gender, health_class)
    
    profile = {
        'age': age,
        'annual_income': annual_income,
        'coverage_need': coverage_amount
    }
    
    return calculator.generate_complete_proposal(profile)


# Test
if __name__ == "__main__":
    # Example: 35-year-old making $90k wanting $500k coverage
    proposal = calculate_premiums(
        age=35,
        annual_income=90000,
        coverage_amount=500000,
        gender="M",
        health_class="standard"
    )
    
    import json
    print(json.dumps(proposal, indent=2))
