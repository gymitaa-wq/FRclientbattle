# Project CAII - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd c:\Users\guang\OneDrive\git\FRclientbattle
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file:

```bash
# Copy the template
copy .env.template .env
```

Edit `.env` and add your Google Gemini API key:

```
GOOGLE_API_KEY=your-api-key-here
```

> **Get a free API key:** https://makersuite.google.com/app/apikey

### Step 3: Run the Application

**Option A: Streamlit UI (Recommended)**

```bash
streamlit run streamlit_app.py
```

Then open your browser to: http://localhost:8501

**Option B: Command Line Test**

```bash
python project_caii_framework.py --test
```

**Option C: Python Script**

```python
from project_caii_framework import run_simulation

# Use the sample email history or provide your own
result = run_simulation(your_email_history, model="gemini")

print(f"Decision: {'CONVERT' if result['metadata']['converted'] else 'REJECT'}")
print(f"Friction Score: {result['friction_score']}/100")
```

---

## 📊 Using the Streamlit UI

1. **Input & Run Tab**
   - Use sample data or paste your own 50 email interactions
   - Click "Run Simulation"
   - Watch real-time progress

2. **Results Dashboard Tab**
   - View key metrics
   - Expand each workflow node to see details
   - Download individual outputs

3. **Documents Tab**
   - Browse all generated documents
   - Download individually or as JSON

4. **Analysis Tab**
   - See friction score interpretation
   - Review strategic insights
   - Understand decision factors

---

## 🎯 What You'll Get

Each simulation produces:

- **Client Profile** - Extracted from emails
- **Initial AI Advice** - DIY recommendations
- **NM Advisor Proposal** - Professional recommendation
- **5 Product Plans** - Individual documents for:
  - Term Life Insurance
  - Whole Life Insurance
  - Disability Insurance
  - Annuity Strategy
  - Cash Buffer
- **AI Critique** - Public AI's review
- **Final Decision** - Convert/Reject with reasoning
- **Friction Score** - 0-100 conflict measure

---

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt --upgrade
```

### "API key not set" error
Make sure your `.env` file exists and contains:
```
GOOGLE_API_KEY=your-actual-key
```

### Streamlit not loading
```bash
streamlit cache clear
streamlit run streamlit_app.py
```

---

## 📚 Next Steps

- Read the full [README.md](file:///c:/Users/guang/OneDrive/git/FRclientbattle/README.md) for detailed documentation
- Review the [walkthrough.md](file:///C:/Users/guang/.gemini/antigravity/brain/0bf5c89a-ee73-44c7-864b-7bd8b303c8f2/walkthrough.md) for implementation details
- Explore Databricks deployment options in the README

---

**Ready to simulate!** 🎉
