# Project CAII - Migration to New Google Genai API

## What Changed

Google deprecated the `google.generativeai` package and replaced it with `google.genai`.

### Updates Made:

1. **Installed New Package**
   ```bash
   pip install google-genai
   ```

2. **Updated Code** (`project_caii_framework.py`)
   - Changed import: `from google import genai`
   - Added types import: `from google.genai import types`
   - Updated API calls to use new `Client` pattern:
     ```python
     client = genai.Client(api_key=api_key)
     response = client.models.generate_content(
         model='gemini-2.0-flash-exp',
         contents=prompt,
         config=types.GenerateContentConfig(...)
     )
     ```

3. **Updated Model**
   - Now using: `gemini-2.0-flash-exp` (latest experimental model)
   - Previous attempts: `gemini-pro` (deprecated), `gemini-1.5-flash` (not available)

4. **Updated requirements.txt**
   - Changed: `google-generativeai>=0.3.0` → `google-genai>=0.2.0`

## How to Use

The Streamlit app should automatically reload. If not:

1. **Refresh your browser** at http://localhost:8501
2. **Click "🚀 Run Simulation"**
3. The framework will now use the latest Gemini 2.0 model

## If You Still Get Errors

If you see any errors, try:

1. **Restart Streamlit**:
   - Stop the current app (Ctrl+C in terminal)
   - Run: `streamlit run streamlit_app.py`

2. **Verify API Key**:
   - Make sure your `.env` file has: `GOOGLE_API_KEY=your-key-here`
   - No quotes, no spaces

3. **Check Package Installation**:
   ```bash
   pip list | findstr google
   ```
   Should show `google-genai` (not `google-generativeai`)

## Alternative: Use Claude or GPT

If Gemini continues to have issues, you can switch models in the Streamlit sidebar:
- **Claude**: Get key at https://console.anthropic.com/
- **GPT**: Get key at https://platform.openai.com/api-keys

---

**Status**: Framework updated to use latest Google Genai API
**Ready**: Refresh browser and run simulation
