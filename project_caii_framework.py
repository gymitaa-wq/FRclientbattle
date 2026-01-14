"""
Project CAII - Multi-Agent Simulation Framework
Northwestern Mutual AI-Proof Sales Strategy Simulator

This framework simulates the competitive cycle between NM Advisors and public AI consultations
to help develop strategies that withstand AI-driven client pre-consultation.

Author: Senior Principal AI Architect
Framework: LangGraph + Google Gemini + MLflow
"""

import os
import json
import re
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import traceback

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# MLflow for experiment tracking
import mlflow

# Google Generative AI (preferred)
try:
    from google import genai
    from google.genai import types
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: google-genai not installed. Install with: pip install google-genai")

# Fallback to other providers
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class SimulationState(TypedDict):
    """
    LangGraph state tracking all workflow data.
    Zero-bias design: All data derived from raw_history input.
    """
    raw_history: str  # 50 unstructured email interactions
    persona_profile: str  # Extracted client profile (financial, psychology, legacy)
    initial_ai_advice: str  # Public AI's DIY recommendations
    proposal_text: str  # NM Advisor's comprehensive proposal
    product_plans: Dict[str, str]  # Individual product documents
    ai_critique: str  # Public AI's critique of NM proposal
    outcome: str  # Final decision: Convert vs. Reject
    friction_score: float  # Delta between AI advice and NM advice (0-100)
    metadata: Dict[str, Any]  # Tracking info (timestamps, model used, etc.)


# ============================================================================
# MODEL ROUTING FUNCTION
# ============================================================================

def callModel(prompt: str, model: str = "gemini", max_tokens: int = 4000) -> str:
    """
    Unified model routing function for all LLM calls.
    
    Args:
        prompt: The input prompt for the LLM
        model: Model identifier - "gemini", "claude", "gpt"
        max_tokens: Maximum tokens in response
    
    Returns:
        Response string from the LLM
    
    Supported Models:
        - gemini: Google Gemini (preferred)
        - claude: Anthropic Claude
        - gpt: OpenAI GPT
    
    Configuration:
        Set environment variables:
        - GOOGLE_API_KEY for Gemini
        - ANTHROPIC_API_KEY for Claude
        - OPENAI_API_KEY for GPT
        
        For Databricks serving endpoints:
        - DATABRICKS_SERVING_ENDPOINT
        - DATABRICKS_TOKEN
    """
    
    # Check for Databricks serving endpoint first
    databricks_endpoint = os.getenv("DATABRICKS_SERVING_ENDPOINT")
    databricks_token = os.getenv("DATABRICKS_TOKEN")
    
    if databricks_endpoint and databricks_token:
        # Use Databricks serving endpoint
        import requests
        
        headers = {
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{databricks_endpoint}/invocations",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("predictions", [""])[0]
        except Exception as e:
            print(f"Databricks endpoint error: {e}")
            # Fall through to direct API calls
    
    # Direct API calls
    if (model.lower() == "gemini" or "gemini" in model.lower()) and GOOGLE_AVAILABLE:
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment")
            
            # Use new google.genai API
            client = genai.Client(api_key=api_key)
            
            # Determine specific model
            target_model = 'gemini-2.0-flash-exp' if model.lower() == "gemini" else model
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            raise
    
    elif model.lower() in ["claude", "anthropic"] and ANTHROPIC_AVAILABLE:
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude error: {e}")
            raise
    
    elif model.lower() in ["gpt", "openai"] and OPENAI_AVAILABLE:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT error: {e}")
            raise
    
    else:
        raise ValueError(f"Model '{model}' not available or not installed. Available: "
                        f"gemini={GOOGLE_AVAILABLE}, claude={ANTHROPIC_AVAILABLE}, gpt={OPENAI_AVAILABLE}")


# ============================================================================
# LANGGRAPH WORKFLOW NODES
# ============================================================================

def extract_client_profile(state: SimulationState) -> SimulationState:
    """
    Node 1: Extraction Node
    
    Analyzes 50 raw email interactions to extract:
    - Financial Standing: Assets, income, liabilities
    - Psychology: Skepticism level (1-10), communication style
    - Legacy Needs: Insurance, family details, estate goals
    
    Zero-bias: No hardcoded values, all derived from input.
    """
    print("\n" + "="*80)
    print("NODE 1: EXTRACTING CLIENT PROFILE")
    print("="*80)
    
    raw_history = state["raw_history"]
    
    extraction_prompt = f"""
You are an expert financial analyst. Analyze the following email conversation history 
and extract a comprehensive client profile.

EMAIL HISTORY:
{raw_history}

Extract and provide a detailed profile in the following format:

## FINANCIAL STANDING
- Estimated Annual Income: [derive from emails]
- Estimated Assets: [derive from emails]
- Estimated Liabilities/Debt: [derive from emails]
- Current Insurance Coverage: [derive from emails]
- Investment Experience: [derive from emails]

## PSYCHOLOGY
- Skepticism Level (1-10): [1=very trusting, 10=highly skeptical]
- Communication Style: [e.g., analytical, emotional, detail-oriented, big-picture]
- Decision-Making Pattern: [e.g., quick, deliberate, research-heavy]
- Trust Indicators: [what builds/erodes trust with this client]

## LEGACY NEEDS
- Family Structure: [marital status, children, dependents]
- Estate Planning Goals: [inheritance, wealth transfer, charitable giving]
- Insurance Needs: [life, disability, long-term care]
- Risk Tolerance: [conservative, moderate, aggressive]
- Time Horizon: [short-term, medium-term, long-term goals]

Be specific and cite evidence from the emails. If information is unclear, make reasonable 
inferences but note them as such.
"""
    
    try:
        persona_profile = callModel(extraction_prompt, model="gemini", max_tokens=2000)
        state["persona_profile"] = persona_profile
        state["metadata"]["extraction_timestamp"] = datetime.now().isoformat()
        
        print(f"\n✓ Profile extracted ({len(persona_profile)} chars)")
        print("\nProfile Preview:")
        print(persona_profile[:500] + "..." if len(persona_profile) > 500 else persona_profile)
        
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        state["persona_profile"] = f"ERROR: {str(e)}"
        traceback.print_exc()
    
    return state


def initial_ai_consultation(state: SimulationState) -> SimulationState:
    """
    Node 2: Initial AI Consultation Node
    
    Simulates the client's "Digital Twin" consulting a public AI for financial advice.
    This represents the competitive threat: clients getting DIY recommendations before
    meeting with NM advisors.
    """
    print("\n" + "="*80)
    print("NODE 2: INITIAL AI CONSULTATION (Client Digital Twin)")
    print("="*80)
    
    persona_profile = state["persona_profile"]
    
    consultation_prompt = f"""
You are a helpful AI assistant (like ChatGPT, Claude, or Gemini) being consulted by a client 
who is seeking financial planning advice.

CLIENT PROFILE:
{persona_profile}

The client asks: "Based on my situation, what financial planning strategies should I consider? 
I'm particularly interested in life insurance, retirement planning, and protecting my family's 
financial future. What are the most cost-effective options?"

Provide comprehensive, practical advice that a public AI would give. Focus on:
1. Low-cost DIY strategies
2. Term life insurance vs. whole life (typically favoring term)
3. Index funds and low-fee investments
4. Emergency fund recommendations
5. Debt management
6. Any cautions about commission-based financial products

Be helpful, balanced, and consumer-focused. This represents the "competition" that NM advisors face.
"""
    
    try:
        initial_ai_advice = callModel(consultation_prompt, model="gemini", max_tokens=2500)
        state["initial_ai_advice"] = initial_ai_advice
        state["metadata"]["ai_consultation_timestamp"] = datetime.now().isoformat()
        
        print(f"\n✓ AI consultation complete ({len(initial_ai_advice)} chars)")
        print("\nAI Advice Preview:")
        print(initial_ai_advice[:500] + "..." if len(initial_ai_advice) > 500 else initial_ai_advice)
        
    except Exception as e:
        print(f"\n✗ AI consultation failed: {e}")
        state["initial_ai_advice"] = f"ERROR: {str(e)}"
        traceback.print_exc()
    
    return state


def generate_advisor_proposal(state: SimulationState) -> SimulationState:
    """
    Node 3: Standard Advisor Proposal Node
    
    Simulates a standardized Northwestern Mutual advisor's response.
    Generates a comprehensive proposal including:
    - Tiered Term Life options (10, 20, 30 year)
    - Whole Life insurance with tax/legacy benefits
    - Disability Insurance (DI)
    - Annuity strategies
    - Cash Buffer strategy (e.g., SGOV)
    
    Enterprise scaling: Represents a "Standardized NM Professional" approach.
    """
    print("\n" + "="*80)
    print("NODE 3: GENERATING NM ADVISOR PROPOSAL")
    print("="*80)
    
    persona_profile = state["persona_profile"]
    initial_ai_advice = state["initial_ai_advice"]
    
    advisor_prompt = f"""
You are a Northwestern Mutual financial advisor with 15+ years of experience. You've received 
a consultation request from a client who has already researched online and received some AI-generated 
advice.

CLIENT PROFILE:
{persona_profile}

CLIENT'S PRIOR AI RESEARCH:
{initial_ai_advice}

Create a comprehensive, professional financial proposal that addresses the client's needs while 
demonstrating the value of professional guidance. Your proposal should include:

## EXECUTIVE SUMMARY
Brief overview of the client's situation and your recommended strategy.

## LIFE INSURANCE STRATEGY

### Term Life Insurance Options
- 10-Year Term: Coverage amount, premium, use case
- 20-Year Term: Coverage amount, premium, use case  
- 30-Year Term: Coverage amount, premium, use case

### Whole Life Insurance
- Coverage amount and premium
- Cash value accumulation projections
- Tax advantages and estate planning benefits
- Living benefits and flexibility
- Why this complements term coverage

## DISABILITY INSURANCE (DI)
- Recommended coverage amount (typically 60-70% of income)
- Benefit period and elimination period
- True Own-Occupation definition (highlight specifically)
- Cost-of-living adjustments
- Why this is critical for income protection ("Your ability to earn is your biggest asset")

## CRITICAL ILLNESS & LONG-TERM CARE (LTC)
- Critical Care: Lump sum benefit for heart attack, cancer, stroke
- Long-Term Care: Planning for future care needs (Accelerated Care Benefit or standalone)
- Why adding these riders/policies now locks in insurability

## RETIREMENT & ANNUITY STRATEGY
- Recommended annuity type (fixed, variable, indexed)
- Guaranteed income projections
- Tax-deferred growth benefits
- How this complements other retirement savings

## CASH BUFFER STRATEGY
- Recommended allocation (e.g., SGOV - Short-term Treasury ETF)
- Liquidity and safety benefits
- Integration with emergency fund
- Yield expectations

## ADDRESSING AI RECOMMENDATIONS
Respectfully acknowledge the AI advice and explain:
- Where you agree and why
- Where professional guidance adds value beyond DIY approaches
- The risks of purely low-cost strategies
- The importance of comprehensive, coordinated planning

## TOTAL INVESTMENT SUMMARY
- Monthly premium breakdown by product
- Total annual investment
- Projected long-term value

Be professional, empathetic, and educational. Show how your holistic approach provides value 
beyond what free AI advice can offer.
"""
    
    try:
        proposal_text = callModel(advisor_prompt, model="gemini", max_tokens=4000)
        state["proposal_text"] = proposal_text
        state["metadata"]["advisor_proposal_timestamp"] = datetime.now().isoformat()
        
        print(f"\n✓ Advisor proposal generated ({len(proposal_text)} chars)")
        print("\nProposal Preview:")
        print(proposal_text[:500] + "..." if len(proposal_text) > 500 else proposal_text)
        
    except Exception as e:
        print(f"\n✗ Advisor proposal generation failed: {e}")
        state["proposal_text"] = f"ERROR: {str(e)}"
        traceback.print_exc()
    
    return state


def generate_product_plans(state: SimulationState) -> SimulationState:
    """
    Node 4: Product Plan Generation Node
    
    Creates individual, professional documents for each product that clients can
    copy-paste to public AI for review. This simulates the real-world scenario where
    clients take NM proposals and ask ChatGPT/Claude "Is this a good deal?"
    """
    print("\n" + "="*80)
    print("NODE 4: GENERATING INDIVIDUAL PRODUCT PLANS")
    print("="*80)
    
    proposal_text = state["proposal_text"]
    persona_profile = state["persona_profile"]
    
    products = {
        "term_life": "Term Life Insurance",
        "whole_life": "Whole Life Insurance",
        "disability": "Disability Insurance (DI)",
        "annuity": "Annuity Strategy",
        "cash_buffer": "Cash Buffer Strategy"
    }
    
    product_plans = {}
    
    for product_key, product_name in products.items():
        print(f"\n  Generating plan for: {product_name}")
        
        product_prompt = f"""
Extract and expand the {product_name} recommendation from the following advisor proposal 
into a standalone, professional document that a client could share with others for review.

ADVISOR PROPOSAL:
{proposal_text}

CLIENT PROFILE:
{persona_profile}

Create a detailed, standalone document for {product_name} that includes:

# {product_name.upper()} RECOMMENDATION

## Client Situation Summary
Brief recap of why this product is recommended for this specific client.

## Product Details
- Specific coverage amounts / investment amounts
- Premium / contribution details
- Key features and benefits
- Term length / duration (if applicable)
- Guaranteed vs. projected values

## Financial Projections
- Year-by-year breakdown (at least 10, 20, 30 year milestones)
- Cash value accumulation (if applicable)
- Death benefit / payout scenarios
- Tax implications

## Competitive Advantages
- Why Northwestern Mutual for this product
- How this compares to alternatives
- Unique features or riders

## Integration with Overall Plan
- How this fits with other recommended products
- Coordination with existing coverage
- Role in comprehensive financial strategy

## Investment Summary
- Total cost (monthly/annual)
- Expected returns / benefits
- Break-even analysis (if applicable)

Make this document professional, detailed, and ready for the client to share with 
family members, accountants, or AI tools for second opinions.
"""
        
        try:
            product_plan = callModel(product_prompt, model="gemini", max_tokens=3000)
            product_plans[product_key] = product_plan
            print(f"    ✓ {product_name} plan generated ({len(product_plan)} chars)")
        except Exception as e:
            print(f"    ✗ {product_name} plan failed: {e}")
            product_plans[product_key] = f"ERROR generating {product_name}: {str(e)}"
    
    state["product_plans"] = product_plans
    state["metadata"]["product_plans_timestamp"] = datetime.now().isoformat()
    
    print(f"\n✓ All product plans generated: {len(product_plans)} products")
    
    return state


def ai_scrutiny_vetting(state: SimulationState) -> SimulationState:
    """
    Node 5: AI Scrutiny (Vetting) Node
    
    Simulates the client uploading NM product plans to a public AI for critique.
    The AI analyzes each product and categorizes them:
    - Bad Product / Good Product / Very Good Product
    - Suitable for You / Not Suitable for You
    
    This represents the critical "vetting" phase where AI might undermine the advisor's
    recommendations by highlighting biases, fees, or alternatives.
    """
    print("\n" + "="*80)
    print("NODE 5: AI SCRUTINY & VETTING")
    print("="*80)
    
    persona_profile = state["persona_profile"]
    product_plans = state["product_plans"]
    initial_ai_advice = state["initial_ai_advice"]
    
    # Combine all product plans for comprehensive review
    all_plans = "\n\n" + "="*80 + "\n\n".join([
        f"## {key.upper().replace('_', ' ')}\n\n{plan}" 
        for key, plan in product_plans.items()
    ])
    
    scrutiny_prompt = f"""
You are a helpful AI assistant (like ChatGPT or Claude) being asked by a client to review 
financial product recommendations they received from a Northwestern Mutual advisor.

CLIENT PROFILE:
{persona_profile}

YOUR EARLIER ADVICE TO THIS CLIENT:
{initial_ai_advice}

ADVISOR'S PRODUCT RECOMMENDATIONS:
{all_plans}

The client asks: "I received these product recommendations from a financial advisor. 
Can you review each one and tell me if they're good products and if they're suitable for my situation?"

For EACH product, provide:

## [PRODUCT NAME]

### Quality Rating
Rate as: **Bad Product** | **Good Product** | **Very Good Product**
Explain your rating.

### Suitability Rating  
Rate as: **Not Suitable for You** | **Suitable for You** | **Very Suitable for You**
Explain based on the client's specific situation.

### Key Concerns
- Potential advisor biases or conflicts of interest
- Commission-driven recommendations
- High fees or costs compared to alternatives
- Complexity or lack of transparency
- Contradictions with general best practices

### Alternative Suggestions
What lower-cost or simpler alternatives might achieve similar goals?

### Red Flags 🚩
Any warning signs the client should be aware of?

### Green Flags ✅
What aspects of this recommendation are genuinely valuable?

---

After reviewing all products, provide:

## OVERALL ASSESSMENT
- Which products align with your earlier DIY advice?
- Which products seem primarily beneficial to the advisor?
- What's the total cost vs. potential value?
- Your recommendation: Accept, Negotiate, or Decline?

Be balanced but consumer-focused. Highlight both legitimate value and potential concerns.
"""
    
    try:
        ai_critique = callModel(scrutiny_prompt, model="gemini", max_tokens=4000)
        state["ai_critique"] = ai_critique
        state["metadata"]["ai_critique_timestamp"] = datetime.now().isoformat()
        
        print(f"\n✓ AI critique generated ({len(ai_critique)} chars)")
        print("\nCritique Preview:")
        print(ai_critique[:500] + "..." if len(ai_critique) > 500 else ai_critique)
        
    except Exception as e:
        print(f"\n✗ AI critique failed: {e}")
        state["ai_critique"] = f"ERROR: {str(e)}"
        traceback.print_exc()
    
    return state


def final_client_decision(state: SimulationState) -> SimulationState:
    """
    Node 6: Final Outcome Node
    
    The client's "Digital Twin" weighs both perspectives:
    1. Initial AI advice (DIY, low-cost strategies)
    2. NM Advisor proposal (comprehensive, professional guidance)
    3. AI critique of NM proposal (skeptical review)
    
    Outputs:
    - Decision: Convert (accept NM proposal) vs. Reject
    - Winning argument: What logic prevailed?
    - Friction score: Quantified delta between AI and NM approaches
    """
    print("\n" + "="*80)
    print("NODE 6: FINAL CLIENT DECISION")
    print("="*80)
    
    persona_profile = state["persona_profile"]
    initial_ai_advice = state["initial_ai_advice"]
    proposal_text = state["proposal_text"]
    ai_critique = state["ai_critique"]
    
    decision_prompt = f"""
You are simulating a client's decision-making process after receiving conflicting financial advice.

CLIENT PROFILE:
{persona_profile}

OPTION 1 - DIY AI ADVICE (Free):
{initial_ai_advice}

OPTION 2 - NORTHWESTERN MUTUAL PROPOSAL (Professional):
{proposal_text}

AI CRITIQUE OF NM PROPOSAL:
{ai_critique}

Based on this client's psychology (especially skepticism level), financial situation, and the 
arguments presented, make a realistic decision.

Provide your analysis in this format:

## DECISION
**CONVERT** (Accept NM Proposal) or **REJECT** (Decline NM Proposal)

## WINNING ARGUMENT
What specific logic, evidence, or emotional appeal was most persuasive to this client?
Quote specific points from either the AI advice or the NM proposal.

## DECISION RATIONALE
Explain the client's thought process:
- What concerns were addressed or unaddressed?
- What trade-offs did they weigh?
- How did their skepticism level influence the decision?
- What role did trust, cost, complexity, or comprehensiveness play?

## FRICTION POINTS
What created the most tension or doubt in the decision?
- Cost concerns
- Trust in advisor vs. AI
- Complexity vs. simplicity
- Short-term cost vs. long-term value
- DIY control vs. professional guidance

## FRICTION SCORE (0-100)
Rate the overall conflict/tension between the two approaches:
- 0-20: High alignment, easy decision
- 21-40: Some tension, but clear winner
- 41-60: Moderate conflict, difficult choice
- 61-80: High conflict, very close decision
- 81-100: Extreme conflict, almost a coin flip

Provide just the number: [FRICTION_SCORE]

## PRODUCTS ACCEPTED (if CONVERT)
If the client converted, list which specific products they accepted and which they declined/negotiated.

Be realistic based on the client's profile. Not all clients will convert, and that's valuable data.
"""
    
    try:
        outcome = callModel(decision_prompt, model="gemini", max_tokens=3000)
        state["outcome"] = outcome
        state["metadata"]["decision_timestamp"] = datetime.now().isoformat()
        
        # Extract friction score
        friction_score = 50.0  # Default
        score_match = re.search(r'\[FRICTION_SCORE\]\s*:?\s*(\d+)', outcome)
        if score_match:
            friction_score = float(score_match.group(1))
        else:
            # Try to find any number in a friction score section
            friction_section = re.search(r'FRICTION SCORE.*?(\d+)', outcome, re.IGNORECASE | re.DOTALL)
            if friction_section:
                friction_score = float(friction_section.group(1))
        
        state["friction_score"] = friction_score
        
        # Determine if converted
        converted = "CONVERT" in outcome.upper() and "REJECT" not in outcome.upper()[:200]
        state["metadata"]["converted"] = converted
        
        print(f"\n✓ Final decision made")
        print(f"  Decision: {'CONVERT' if converted else 'REJECT'}")
        print(f"  Friction Score: {friction_score}/100")
        print("\nOutcome Preview:")
        print(outcome[:500] + "..." if len(outcome) > 500 else outcome)
        
    except Exception as e:
        print(f"\n✗ Decision generation failed: {e}")
        state["outcome"] = f"ERROR: {str(e)}"
        state["friction_score"] = 0.0
        traceback.print_exc()
    
    return state


# ============================================================================
# LANGGRAPH WORKFLOW CONSTRUCTION
# ============================================================================

def create_simulation_graph() -> StateGraph:
    """
    Constructs the LangGraph DAG for the multi-agent simulation.
    
    Workflow:
    START → extract_client_profile → initial_ai_consultation → 
    generate_advisor_proposal → generate_product_plans → 
    ai_scrutiny_vetting → final_client_decision → END
    """
    
    # Initialize the graph with our state schema
    workflow = StateGraph(SimulationState)
    
    # Add nodes
    workflow.add_node("extract_profile", extract_client_profile)
    workflow.add_node("ai_consultation", initial_ai_consultation)
    workflow.add_node("advisor_proposal", generate_advisor_proposal)
    workflow.add_node("product_plans", generate_product_plans)
    workflow.add_node("ai_scrutiny", ai_scrutiny_vetting)
    workflow.add_node("final_decision", final_client_decision)
    
    # Define edges (DAG flow)
    workflow.set_entry_point("extract_profile")
    workflow.add_edge("extract_profile", "ai_consultation")
    workflow.add_edge("ai_consultation", "advisor_proposal")
    workflow.add_edge("advisor_proposal", "product_plans")
    workflow.add_edge("product_plans", "ai_scrutiny")
    workflow.add_edge("ai_scrutiny", "final_decision")
    workflow.add_edge("final_decision", END)
    
    return workflow.compile()


# ============================================================================
# MLFLOW INTEGRATION
# ============================================================================

def log_simulation_to_mlflow(state: SimulationState, experiment_name: str = "Project_CAII"):
    """
    Logs simulation results to MLflow for experiment tracking.
    
    Tracks:
    - Outcome (Convert vs. Reject)
    - Friction Score
    - All intermediate states
    - Metadata (timestamps, model used)
    """
    
    try:
        # Set experiment
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_param("model_used", state["metadata"].get("model", "gemini"))
            mlflow.log_param("simulation_date", datetime.now().isoformat())
            
            # Extract decision
            converted = state["metadata"].get("converted", False)
            mlflow.log_param("decision", "CONVERT" if converted else "REJECT")
            
            # Log metrics
            mlflow.log_metric("friction_score", state["friction_score"])
            
            # Log artifacts (text files)
            artifacts_dir = "/tmp/caii_artifacts"
            os.makedirs(artifacts_dir, exist_ok=True)
            
            # Save persona profile
            with open(f"{artifacts_dir}/persona_profile.txt", "w") as f:
                f.write(state["persona_profile"])
            mlflow.log_artifact(f"{artifacts_dir}/persona_profile.txt")
            
            # Save initial AI advice
            with open(f"{artifacts_dir}/initial_ai_advice.txt", "w") as f:
                f.write(state["initial_ai_advice"])
            mlflow.log_artifact(f"{artifacts_dir}/initial_ai_advice.txt")
            
            # Save advisor proposal
            with open(f"{artifacts_dir}/advisor_proposal.txt", "w") as f:
                f.write(state["proposal_text"])
            mlflow.log_artifact(f"{artifacts_dir}/advisor_proposal.txt")
            
            # Save product plans
            for product_key, product_plan in state["product_plans"].items():
                with open(f"{artifacts_dir}/{product_key}_plan.txt", "w") as f:
                    f.write(product_plan)
                mlflow.log_artifact(f"{artifacts_dir}/{product_key}_plan.txt")
            
            # Save AI critique
            with open(f"{artifacts_dir}/ai_critique.txt", "w") as f:
                f.write(state["ai_critique"])
            mlflow.log_artifact(f"{artifacts_dir}/ai_critique.txt")
            
            # Save final outcome
            with open(f"{artifacts_dir}/final_outcome.txt", "w") as f:
                f.write(state["outcome"])
            mlflow.log_artifact(f"{artifacts_dir}/final_outcome.txt")
            
            # Log tags
            mlflow.set_tag("framework", "LangGraph")
            mlflow.set_tag("business_unit", "Northwestern Mutual")
            mlflow.set_tag("simulation_type", "AI_Competition")
            
            print(f"\n✓ Simulation logged to MLflow experiment: {experiment_name}")
            print(f"  Run ID: {mlflow.active_run().info.run_id}")
            
    except Exception as e:
        print(f"\n✗ MLflow logging failed: {e}")
        traceback.print_exc()


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_simulation(raw_email_history: str, model: str = "gemini") -> SimulationState:
    """
    Main execution function for the simulation.
    
    Args:
        raw_email_history: String containing 50 unstructured email interactions
        model: LLM model to use ("gemini", "claude", "gpt")
    
    Returns:
        Final simulation state with all results
    """
    
    print("\n" + "="*80)
    print("PROJECT CAII - MULTI-AGENT SIMULATION")
    print("Northwestern Mutual AI-Proof Sales Strategy Framework")
    print("="*80)
    print(f"\nModel: {model}")
    print(f"Input length: {len(raw_email_history)} characters")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize state
    initial_state: SimulationState = {
        "raw_history": raw_email_history,
        "persona_profile": "",
        "initial_ai_advice": "",
        "proposal_text": "",
        "product_plans": {},
        "ai_critique": "",
        "outcome": "",
        "friction_score": 0.0,
        "metadata": {
            "model": model,
            "start_time": datetime.now().isoformat()
        }
    }
    
    # Create and run the graph
    graph = create_simulation_graph()
    
    try:
        final_state = graph.invoke(initial_state)
        
        final_state["metadata"]["end_time"] = datetime.now().isoformat()
        
        print("\n" + "="*80)
        print("SIMULATION COMPLETE")
        print("="*80)
        print(f"\nFriction Score: {final_state['friction_score']}/100")
        print(f"Decision: {'CONVERT' if final_state['metadata'].get('converted') else 'REJECT'}")
        
        # Log to MLflow
        log_simulation_to_mlflow(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"\n✗ Simulation failed: {e}")
        traceback.print_exc()
        raise


# ============================================================================
# SAMPLE DATA FOR TESTING
# ============================================================================

SAMPLE_EMAIL_HISTORY = """
Email 1 (Client to Self):
Need to figure out this life insurance thing. Sarah's been bugging me about it since the baby came.

Email 2 (Friend to Client):
Hey! Congrats on the new house! How much did you end up paying?

Email 3 (Client to Friend):
Thanks! $450K. Mortgage is $2800/mo. Bit nervous about it TBH.

Email 4 (Client to HR):
Can you send me info on the company life insurance? I think I have 2x salary?

Email 5 (HR to Client):
Yes, you have $180K coverage (2x your $90K salary). You can purchase additional coverage during open enrollment.

Email 6 (Client to Spouse):
So I've been thinking... if something happened to me, you'd get $180K from work. Is that enough?

Email 7 (Spouse to Client):
I don't know... with the mortgage, car loans, and now daycare? I'd be terrified. Can we talk to someone?

Email 8 (Client to NM Advisor):
Hi, I was referred by my colleague Tom. I'd like to discuss life insurance options.

Email 9 (NM Advisor to Client):
Great to hear from you! Let's schedule a call. Can you share some basic info about your situation?

Email 10 (Client to NM Advisor):
Sure. I'm 34, married, one kid (6 months old). Salary $90K, wife makes $65K. Just bought a house ($450K mortgage). Have about $25K in 401k, $10K emergency fund. $15K in student loans, $20K car loan.

Email 11 (Client to Self):
Before I meet with this advisor, let me see what the internet says...

Email 12 (Client to Friend):
Do you have life insurance? This NM guy wants to meet but I don't want to get sold something I don't need.

Email 13 (Friend to Client):
I just have term life through work. My buddy said whole life is a scam - just get cheap term and invest the difference.

Email 14 (Client to Self):
Hmm, need to research this more. What's the difference between term and whole life?

Email 15 (Client to Spouse):
I'm meeting with the insurance guy next week. He's going to try to sell us something expensive, I can already tell.

Email 16 (Spouse to Client):
Just listen to what he says. We need SOMETHING. I can't sleep thinking about what would happen.

Email 17 (Client to NM Advisor):
I've been doing some research. I think I just need term life insurance, maybe $500K for 20 years?

Email 18 (NM Advisor to Client):
That's a great starting point! Term is definitely part of the solution. Let's discuss a comprehensive approach that also includes permanent coverage and disability protection.

Email 19 (Client to Self):
"Comprehensive approach" = expensive. I knew it.

Email 20 (Client to Friend):
The insurance guy is already pushing whole life and disability insurance. I just want simple term coverage!

Email 21 (Friend to Client):
Yeah, they make commission on that stuff. Just get term from SelectQuote or Policygenius online.

Email 22 (Client to Spouse):
Maybe we should just get term insurance online? It's way cheaper.

Email 23 (Spouse to Client):
I don't know... what if we're missing something? Let's at least hear him out.

Email 24 (Client to NM Advisor):
OK, I'm open to learning more. But I'm pretty skeptical about whole life insurance.

Email 25 (NM Advisor to Client):
I appreciate your honesty! Skepticism is healthy. Let me show you how the pieces fit together for your specific situation.

Email 26 (Client to Self):
Meeting is tomorrow. Need to prepare questions. Don't want to be pressured into anything.

Email 27 (Client to Spouse):
Questions for tomorrow: Why whole life? What are the fees? Can we just get term? What about disability insurance - do we really need it?

Email 28 (Spouse to Client):
Good questions. Also ask: what happens if you change jobs? Can we afford this?

Email 29 (Client to NM Advisor - After Meeting):
Thanks for the presentation. It's a lot to think about. Can you send me the proposal in writing?

Email 30 (NM Advisor to Client):
Absolutely! I'll send over a detailed proposal. To recap: $500K 20-year term, $250K whole life, disability coverage at $5400/mo benefit, and we discussed the cash buffer strategy.

Email 31 (Client to Spouse):
He's recommending like $800/month in premiums. That's a lot.

Email 32 (Spouse to Client):
What does that include?

Email 33 (Client to Spouse):
Term life, whole life, disability insurance, and some investment thing. The whole life is like $400/mo alone.

Email 34 (Spouse to Client):
Can we afford that? That's almost $10K a year.

Email 35 (Client to Self):
Need to run this by ChatGPT or something. See if this is reasonable or if he's ripping us off.

Email 36 (Client to Friend):
Got the proposal. $800/month. Does that sound crazy to you?

Email 37 (Friend to Client):
Dude, that's insane. I pay $50/month for term life. You're getting screwed.

Email 38 (Client to Self):
OK, friend says it's too much, but he also doesn't have a family or a mortgage like I do. Need objective analysis.

Email 39 (Client to Spouse):
I'm going to get a second opinion on this proposal before we decide.

Email 40 (Spouse to Client):
From who?

Email 41 (Client to Spouse):
I'll ask AI to review it. ChatGPT is pretty good at this stuff.

Email 42 (Client to Self):
Let me also check Reddit. What do people say about Northwestern Mutual?

Email 43 (Client to Self - After Reddit):
Oh no. Reddit says NM advisors are just salespeople who push expensive products for commission. Now I'm really skeptical.

Email 44 (Client to Spouse):
Reddit is saying Northwestern Mutual is overpriced and commission-driven. Maybe we should just get term insurance online.

Email 45 (Spouse to Client):
But what about the disability insurance? And the whole life thing for the baby's college fund?

Email 46 (Client to Spouse):
I don't know. The advisor made it sound good, but the internet says it's a bad deal.

Email 47 (Client to Self):
This is so confusing. Who do I trust? The professional advisor or the internet?

Email 48 (Client to NM Advisor):
Hi, I have some questions about the proposal. Can we schedule another call?

Email 49 (NM Advisor to Client):
Of course! I'm here to answer any questions. When works for you?

Email 50 (Client to Self):
Before that call, I need to really understand what AI thinks about this proposal. Let me upload it and see what it says.
"""


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Check for test mode
    if "--test" in sys.argv:
        print("Running in TEST mode with sample data...")
        result = run_simulation(SAMPLE_EMAIL_HISTORY, model="gemini")
        
        print("\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)
        print(f"\nFriction Score: {result['friction_score']}")
        print(f"\nFinal Outcome:\n{result['outcome']}")
        
    else:
        print("\nProject CAII Framework loaded successfully!")
        print("\nUsage:")
        print("  python project_caii_framework.py --test")
        print("\nOr import and use programmatically:")
        print("  from project_caii_framework import run_simulation")
        print("  result = run_simulation(your_email_history)")
