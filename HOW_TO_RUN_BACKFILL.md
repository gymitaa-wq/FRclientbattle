# How to Run the Backfill on Production

## Option 1: Admin Tools Page (RECOMMENDED) ✨

1. **Wait for Render deployment** to complete (~2-3 minutes from now)

2. **Open your deployed app** on Render:
   - Go to: `https://your-app-name.onrender.com`

3. **Navigate to Admin Tools**:
   - Look in the sidebar for **"99_Admin_Tools"** page
   - Click on it

4. **Enter Admin Password**:
   - Default password: `admin123`
   - (You can change this by setting `ADMIN_PASSWORD` environment variable in Render)

5. **Run the Backfill**:
   - Option A: **Dry Run First** (recommended)
     - Keep "Dry Run (Preview Only)" checked
     - Click "🚀 Run Backfill"
     - Review what would change
   
   - Option B: **Fix Specific Simulation**
     - Enter `128` in "Specific Simulation ID"
     - Uncheck "Dry Run" 
     - Click "🚀 Run Backfill"
   
   - Option C: **Fix All Simulations**
     - Leave Simulation ID as `0`
     - Uncheck "Dry Run"
     - Click "🚀 Run Backfill"

6. **View Results**:
   - Real-time progress bar
   - Summary metrics (Fixed, Unchanged, Errors)
   - Detailed changes log showing old vs new products

## Option 2: Command Line (If you have Render Shell access)

```bash
# SSH into Render container
render shell

# Dry run
python backfill_products.py --dry-run

# Fix specific simulation
python backfill_products.py --live --sim-id 128

# Fix all simulations
python backfill_products.py --live
```

## What to Expect

### For Simulation ID 128 (the buggy one):

**Before (Bug):**
- Products: `['Whole Life Insurance']` (WRONG - was removed)
- Monthly Premium: $200

**After (Fixed):**
- Products: `['Term 20', 'Disability Insurance', 'Roth IRA']` (CORRECT)
- Monthly Premium: $345

### Safety Features

- ✅ **Dry run by default** - Won't change anything until you uncheck it
- ✅ **Compares old vs new** - Only updates if products actually changed
- ✅ **Detailed logging** - Shows exactly what changed for each simulation
- ✅ **Progress tracking** - Real-time progress bar
- ✅ **Error handling** - Continues even if one simulation fails

## Recommended Steps

1. Run **dry run** on all simulations to see what would change
2. Review the changes log
3. If looks good, run **live mode** to update database
4. Verify Simulation 128 now shows correct products

---

**The Admin Tools page is the easiest way!** Just wait for deployment, open the app, go to Admin Tools, and click the button. You'll see everything in the UI.
