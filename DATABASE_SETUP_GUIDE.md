# Setting Up Persistent Database on Render

## Current Problem
Currently using SQLite (file-based database) which gets deleted on every Render deployment because Render uses ephemeral storage.

## Solution: PostgreSQL Database

Your code already supports PostgreSQL! Just need to add a database and configure the environment variable.

---

## Step-by-Step Setup

### Option 1: Render PostgreSQL (Recommended - Free Tier Available)

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Create PostgreSQL Database**:
   - Click "New +" button → Select "PostgreSQL"
   - **Name**: `frclientbattle-db`
   - **Database**: `frclientbattle` (default is fine)
   - **User**: Leave default
   - **Region**: Same as your web service (probably Oregon)
   - **Plan**: Free (limited to 90 days, then $7/month for Starter)
   - Click "Create Database"

3. **Get Database URL**:
   - Once created, click on the database
   - Scroll to "Connections" section
   - Copy the **Internal Database URL** (looks like: `postgres://user:pass@dpg-xxxxx/dbname`)
   - **IMPORTANT**: Use the "Internal Database URL", not the external one (faster & free)

4. **Add to Web Service**:
   - Go to your web service: https://dashboard.render.com/web/srv-d5jfchumcj7s738a69q0
   - Click "Environment" tab on the left
   - Click "Add Environment Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL from step 3
   - Click "Save Changes"
   - **The service will auto-redeploy** (takes ~2 minutes)

5. **Verify It Works**:
   - After redeployment, run a simulation
   - Check Tab 4: History - your data should be there
   - Redeploy again - history should persist! ✅

---

### Option 2: Supabase PostgreSQL (Alternative - Generous Free Tier)

If you want an alternative with a more generous free tier:

1. Go to https://supabase.com/ and create account
2. Create new project
3. Get connection string from Settings → Database → Connection string (URI)
4. Add to Render environment variables as `DATABASE_URL`

---

### Option 3: Neon PostgreSQL (Alternative - Free Tier)

Another good option:

1. Go to https://neon.tech/ and create account
2. Create new project
3. Copy connection string
4. Add to Render environment variables as `DATABASE_URL`

---

## What Happens Automatically

Once you add `DATABASE_URL`:

1. ✅ `database.py` detects it and uses PostgreSQL instead of SQLite
2. ✅ Tables are auto-created on first run (`init_db()`)
3. ✅ All simulations and battle results are saved permanently
4. ✅ History persists across deployments
5. ✅ All users' data is preserved

---

## Verifying Database Connection

After setup, check the logs:

```bash
# In Render dashboard, go to Logs tab
# You should see:
# "Using PostgreSQL database at postgres://..."
# NOT "Using SQLite at /opt/render/..."
```

---

## Database Schema

Your database already has these tables:
- `simulation_results` - Regular simulations (Tab 1-4)
- `battle_results` - Battle Engine results (Tab 6)

These will be auto-created when you first connect.

---

## Migration Notes

**Current SQLite data will be lost** when switching to PostgreSQL. This is expected since:
- SQLite file is on ephemeral storage (already lost on each deploy)
- No existing data to migrate

After setup, all NEW data will be permanent! 🎉

---

## Troubleshooting

**Error: "could not connect to database"**
- Check that DATABASE_URL is correct
- Use "Internal Database URL" from Render (not External)
- Ensure database and web service are in same region

**Error: "relation does not exist"**
- Tables not created yet
- Restart the service or run any simulation
- Tables are auto-created by `init_db()`

**Data still disappearing**
- Check environment variables are saved
- Verify DATABASE_URL doesn't contain SQLite path
- Check logs to confirm PostgreSQL is being used

---

## Cost Estimate

**Render Free Tier**:
- PostgreSQL: Free for 90 days, then $7/month (Starter plan)
- Web Service: Free tier available

**Supabase**:
- PostgreSQL: Free tier is generous (500MB, 2 CPU hours/day)
- Good for development/testing

**Neon**:
- PostgreSQL: Free tier (3GB storage, 1 active project)
- Scales to zero when not in use

---

## Next Steps

1. Choose a database provider (Render recommended for simplicity)
2. Create PostgreSQL database
3. Add `DATABASE_URL` to Render environment variables
4. Wait for auto-redeploy (~2 minutes)
5. Test - run simulations and verify history persists! ✅
