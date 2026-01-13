# Project CAII - Enhanced Features

## New Features Added

### 1. Random Client Profile Generator (`profile_generator.py`)

Generates realistic, randomized client profiles with:
- Varied demographics (age, income, family status)
- Different financial situations (assets, debts, insurance needs)
- Randomized skepticism levels (4-9 scale)
- 50 unique email interactions per profile

**Usage:**
```python
from profile_generator import generate_random_client_profile

profile = generate_random_client_profile()
# Returns a string with 50 email interactions
```

### 2. CSV Export for Simulation History (`csv_export.py`)

Automatically saves all simulation results to `simulation_history.csv` with:
- Timestamp
- Decision (CONVERT/REJECT)
- Friction score
- Model used
- Profile and outcome previews

**Usage:**
```python
from csv_export import save_simulation_to_csv, load_simulation_history, get_history_stats

# Save a simulation
save_simulation_to_csv(simulation_state)

# Load history
df = load_simulation_history()

# Get statistics
stats = get_history_stats()
# Returns: total_simulations, conversion_rate, avg_friction_score
```

## How to Integrate into Streamlit App

### Step 1: Add Imports

Add these imports near the top of `streamlit_app.py` (after the existing imports):

```python
# Import profile generator and CSV export
try:
    from profile_generator import generate_random_client_profile
    PROFILE_GENERATOR_AVAILABLE = True
except ImportError:
    PROFILE_GENERATOR_AVAILABLE = False

try:
    from csv_export import save_simulation_to_csv, load_simulation_history, get_history_stats
    import pandas as pd
    CSV_EXPORT_AVAILABLE = True
except ImportError:
    CSV_EXPORT_AVAILABLE = False
```

### Step 2: Add Profile Generator Button

In Tab 1 (Input & Run), add this code before the email history text area:

```python
# Profile generation button
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    if PROFILE_GENERATOR_AVAILABLE:
        if st.button("🎲 Generate Random Profile", use_container_width=True):
            new_profile = generate_random_client_profile()
            st.session_state['generated_profile'] = new_profile
            st.success("✅ New random client profile generated!")
            st.rerun()

# Use generated profile if available
if 'generated_profile' in st.session_state:
    email_history = st.text_area(
        "Email History (50 interactions)",
        value=st.session_state['generated_profile'],
        height=400
    )
else:
    # Original code for sample/custom input
    ...
```

### Step 3: Add CSV Export After Simulation

In the simulation completion section (after `result = run_simulation(...)`), add:

```python
# Save to CSV
if CSV_EXPORT_AVAILABLE:
    csv_path = save_simulation_to_csv(result)
    st.info(f"📊 Results saved to {csv_path}")
```

### Step 4: Add History Tab

Add a new tab for viewing history:

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📧 Input & Run",
    "📊 Results Dashboard",
    "📄 Documents",
    "🔬 Analysis",
    "📈 History"  # NEW
])

# ... existing tabs ...

# NEW: History Tab
with tab5:
    st.markdown("## 📈 Simulation History")
    
    if CSV_EXPORT_AVAILABLE:
        df = load_simulation_history()
        
        if not df.empty:
            # Statistics
            stats = get_history_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Simulations", stats['total_simulations'])
            with col2:
                st.metric("Conversion Rate", f"{stats['conversion_rate']:.1f}%")
            with col3:
                st.metric("Avg Friction Score", f"{stats['avg_friction_score']:.1f}")
            
            # Data table
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download History CSV",
                csv,
                "simulation_history.csv",
                "text/csv"
            )
        else:
            st.info("No simulation history yet. Run some simulations to see data here.")
    else:
        st.error("CSV export module not available")
```

## Quick Integration Script

Or simply copy the enhanced `streamlit_app_enhanced.py` file (if provided) to replace your current `streamlit_app.py`.

## Testing

1. **Test Profile Generator:**
   ```bash
   python profile_generator.py
   ```
   Should output a random 50-email profile.

2. **Test CSV Export:**
   Run a simulation and check for `simulation_history.csv` file.

3. **Test Streamlit Integration:**
   - Click "Generate Random Profile" button
   - Run simulation
   - Check History tab for saved results

## Files Created

- `profile_generator.py` - Random profile generation
- `csv_export.py` - CSV export and history management
- `INTEGRATION_GUIDE.md` - This file

## Dependencies

Make sure these are installed:
```bash
pip install pandas openpyxl
```

Already in requirements.txt.
