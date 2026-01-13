# Quick Start Guide - Streamlined Simulation

## 🚀 Getting Started

**Streamlit App:** http://localhost:8502

## 📝 Step-by-Step Usage

### 1. Generate Client Profile
Click **"🎲 Generate Random Client Profile"** button

You'll see a comprehensive profile like:
```
═══════════════════════════════════════════════════════════════
CLIENT PROFILE: CLIENT_XXXX
═══════════════════════════════════════════════════════════════

👤 DEMOGRAPHICS
Age: 47, Married, 3 children

💼 EMPLOYMENT & INCOME  
Occupation: Software Engineer
Total Household: $150,000

💰 FINANCIAL POSITION
Assets: $175,880
Debt: $330,998
Coverage Gap: $600,000

🧠 PSYCHOLOGY
Skepticism: 8/10
Decision Style: Analytical
```

### 2. Configure Settings (Sidebar)
- ✅ Enable Proposal Refinement (checked)
- Set Max Iterations: 3 (recommended)

### 3. Run Simulation
Click **"🚀 Run Simulation"**

Watch the console for iteration summaries:
```
ITERATION 0: INITIAL PROPOSAL
Status: ❌ REJECTED
Friction: 75/100

ITERATION 1: REFINING PROPOSAL  
Status: ❌ REJECTED
Friction: 58/100 (-17 points)

ITERATION 2: REFINING PROPOSAL
Status: ✅ ACCEPTED
Friction: 35/100 (-23 points)

✅ DEAL CLOSED AFTER 2 REFINEMENTS!
```

### 4. View Results

**Tab 2: Results Dashboard**
- Deal status (closed/not closed)
- Friction score
- Iteration count

**Tab 3: Documents**
- All proposals
- All AI critiques
- Decision texts

**Tab 4: Analysis**
- Closure reasons (if accepted)
- Rejection reasons (if not)
- Winning factors
- Final products with pricing

**Tab 5: History**
- All past simulations
- Conversion rates
- Download CSV

## 🎯 What You'll See

### If Deal Closes:
```
🎉 CLOSURE REASONS:
  ✓ Addressed key concerns
  ✓ Competitive pricing
  ✓ Showed flexibility

💼 FINAL PRODUCTS:
  • Term Life: $60/month
  • Whole Life: $95/month  
  • Disability: $95/month
  TOTAL: $250/month
```

### If Deal Doesn't Close:
```
❌ REJECTION REASONS:
  ✗ Still too expensive
  ✗ Commission-driven
  ✗ Better DIY options

⚠️ REMAINING CONCERNS:
  • Cost too high for income
  • Whole life not justified
```

## 💡 Tips

1. **High Skepticism Clients** (8-10/10)
   - Harder to close
   - Need more iterations
   - Better pricing required

2. **Low Skepticism Clients** (4-6/10)
   - Easier to close
   - May accept initial proposal
   - Less price sensitive

3. **Coverage Gap**
   - Larger gap = more products needed
   - Affects total premium
   - Influences decision

4. **Financial Literacy**
   - High literacy = more analytical
   - Low literacy = trust-based
   - Affects decision style

## 📊 Analysis

Run 10-20 simulations and analyze:
- What closure reasons are most common?
- What rejection reasons appear most?
- How many iterations typically needed?
- What friction scores lead to acceptance?

## 🔧 Troubleshooting

**Profile not showing:**
- Click generate button again
- Refresh page

**Simulation fails:**
- Check API key in .env
- Check console for errors
- Try different model

**No iteration summaries:**
- Check console output
- Summaries print during simulation

## ✅ You're Ready!

Generate profiles, run simulations, analyze results!
