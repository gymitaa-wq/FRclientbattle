# Product Names Backfill Guide

## Purpose
This script backfills missing `product_names` in the history table by extracting product information from accepted proposals using LLM.

## When to Use This

Run this script if:
- ✅ You see empty "Product Names" column in Tab 4: History
- ✅ The simulations were completed (deal_closed = True)
- ✅ The proposals contain product information but weren't extracted

## How It Works

1. **Queries Database**
   - Finds all accepted simulations (`deal_closed = True`)
   - Where `product_names` is empty or NULL

2. **Extracts Proposals**
   - Reads the final proposal from `iterations_data` JSON blob
   - This is the accepted proposal that closed the deal

3. **Uses LLM to Extract**
   - Sends proposal to Gemini for product extraction
   - Gets back: `["Term Life Insurance", "Disability Insurance"]`
   - Joins them: `"Term Life Insurance; Disability Insurance"`

4. **Updates Database**
   - Sets `product_names` field
   - Optionally sets `total_monthly_premium` if missing

## Usage

### Local Execution

```bash
cd c:\Users\guang\OneDrive\git\FRclientbattle
python backfill_product_names.py
```

**Expected Output**:
```
🔍 Searching for simulations with missing product names...
📊 Found 15 accepted deals with missing product names

[1/15] Processing Simulation #42
  Client: CLIENT_1234, Age: 35, Software Engineer
  📄 Extracting from proposal (2847 chars)...
  ✅ Updated: Term Life Insurance; Disability Insurance
  💰 Premium: $245/month

[2/15] Processing Simulation #43
  ...

======================================================================
BACKFILL COMPLETE
======================================================================
✅ Successfully updated: 14 records
⚠️ Failed/Skipped: 1 records
📊 Total processed: 15 records
```

### Production (Render) Execution

**Option 1: Temporary Container (Recommended)**

1. Go to Render Dashboard: https://dashboard.render.com/web/srv-d5jfchumcj7s738a69q0
2. Click **"Shell"** tab
3. Run:
```bash
python backfill_product_names.py
```

**Option 2: One-Time Job**

Create a one-time job in Render:
- **Command**: `python backfill_product_names.py`
- **Environment**: Same as web service

## Prerequisites

### Required Environment Variables
- `GEMINI_API_KEY` (or your configured LLM API key)
- `DATABASE_URL` (PostgreSQL connection string)

These should already be set if your app is running.

### Required Database Connection
- PostgreSQL database must be accessible
- Same database as used by the main app

## What Gets Updated

### Before Backfill
```sql
SELECT id, product_names, total_monthly_premium 
FROM simulation_results 
WHERE deal_closed = true AND id = 42;

| id | product_names | total_monthly_premium |
|----|---------------|------------------------|
| 42 | (empty)       | 0.0                    |
```

### After Backfill
```sql
| id | product_names                                | total_monthly_premium |
|----|----------------------------------------------|------------------------|
| 42 | Term Life Insurance; Disability Insurance    | 245.0                  |
```

## Safety Features

### 1. Only Updates Empty Records
```python
.filter(
    SimulationResult.deal_closed == True,
    (SimulationResult.product_names == "") | (SimulationResult.product_names == None)
)
```
Won't overwrite existing data.

### 2. Read-Only on Most Fields
Only updates:
- `product_names` (always)
- `total_monthly_premium` (only if currently 0 or NULL)

### 3. Transaction Safety
- Each update is committed individually
- Failed updates don't affect other records
- Rollback on critical errors

## Troubleshooting

### Issue: "No JSON found in LLM response"
**Cause**: LLM didn't return JSON format

**Solution**: 
- Check that Gemini API key is valid
- Verify proposal text is well-formatted
- Re-run script (LLM responses can vary)

### Issue: "No iterations data found"
**Cause**: Simulation record incomplete

**Solution**:
- This simulation can't be backfilled
- Record will be skipped (counted in "Failed")
- No action needed

### Issue: Rate Limit Errors
**Cause**: Too many LLM calls in short time

**Solution**:
- Add delay between calls:
  ```python
  import time
  time.sleep(1)  # After each extraction
  ```
- Run script during off-peak hours
- Use higher tier API if available

## Performance

### Execution Time
- **~2-3 seconds per record** (LLM call + database update)
- **Example**: 50 records = ~2-3 minutes total

### Cost Estimate (Gemini API)
- **~300 tokens per extraction** (proposal truncated to 3000 chars)
- **Example**: 50 records × 300 tokens = 15,000 tokens
- **Cost**: ~$0.01 (Gemini is very cheap)

## Verification

After running the script, verify in the app:

1. Go to **Tab 4: History**
2. Check records that were previously empty
3. Product Names column should now show: `"Term Life Insurance; Disability Insurance"`
4. Total Monthly Premium should show dollar amounts

## Alternative: Manual SQL Update

If you prefer SQL instead of Python:

```sql
-- View records that need updating
SELECT id, client_id, product_names, total_monthly_premium
FROM simulation_results
WHERE deal_closed = true 
  AND (product_names IS NULL OR product_names = '')
ORDER BY timestamp DESC;

-- Manual update example
UPDATE simulation_results
SET product_names = 'Term Life Insurance; Disability Insurance',
    total_monthly_premium = 245.0
WHERE id = 42;
```

But this requires manually extracting products from each proposal - tedious!

## Script Maintenance

### To Update Extraction Logic

Edit the `extract_products_from_proposal_llm()` function in `backfill_product_names.py`:

```python
def extract_products_from_proposal_llm(proposal_text: str) -> tuple[str, float]:
    # Modify prompt here
    prompt = f"""..."""
    
    # Modify extraction logic here
    ...
```

### To Change Filter Criteria

Edit the query in `backfill_product_names()`:

```python
simulations = db.query(SimulationResult).filter(
    # Modify filters here
    SimulationResult.deal_closed == True,
    # Add more conditions...
).all()
```

## Next Steps After Backfill

1. ✅ Verify data in History tab
2. ✅ Run new simulations to confirm extraction works automatically
3. ✅ Monitor logs for extraction failures
4. 🔄 Re-run backfill if new empty records appear

## Files

- **Script**: `backfill_product_names.py`
- **Database Module**: `database.py`
- **LLM Framework**: `project_caii_framework.py`

---

**Last Updated**: 2026-01-28
**Status**: Ready to use
**Impact**: Improves history table completeness
