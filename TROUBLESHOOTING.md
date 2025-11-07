# Troubleshooting Hugging Face Integration

## Issue: Still Getting Template Posts Despite API Key

### Common Causes:

1. **API Key Not Being Passed Correctly**
   - Make sure the toggle is ON
   - Enter your API key in the password field
   - Check that it starts with `hf_`
   - The key should be saved after entering

2. **Model Availability (410 Error)**
   - Some models may be temporarily unavailable
   - The app tries multiple models automatically
   - If all fail, it falls back to templates

3. **Rate Limiting**
   - Free tier has rate limits (~30 requests/minute)
   - Wait 1 minute between batches
   - Try again if you see timeout errors

### Solutions:

#### Solution 1: Verify API Key
1. Go to https://huggingface.co/settings/tokens
2. Make sure your token is active
3. Copy the full token (starts with `hf_`)
4. Paste it in the app sidebar
5. Toggle should be ON

#### Solution 2: Check Console Logs
Look at the terminal where Streamlit is running:
- You should see: `🤖 Using AI generation with API key: hf_xxxxx...`
- If you see: `⚠️ LLM enabled but no API key found` → API key not set
- If you see: `⚠️ Model unavailable` → Try a different model

#### Solution 3: Test API Key Manually
```python
import requests
import os

api_key = "your_key_here"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.post(
    "https://api-inference.huggingface.co/models/gpt2",
    headers=headers,
    json={"inputs": "Hello", "parameters": {"max_new_tokens": 20}}
)
print(response.status_code)  # Should be 200
```

#### Solution 4: Use Inference Endpoints (More Reliable)
If models keep failing, consider:
1. Creating a custom Inference Endpoint on Hugging Face
2. Using that endpoint URL instead
3. More reliable but requires setup

### Debug Steps:

1. **Check Toggle State**
   - Sidebar should show toggle ON
   - Should see "✅ API key configured"

2. **Check Generation Mode**
   - After generating, look for indicator:
   - "🤖 These drafts were generated using AI" = Working
   - "📝 These drafts were generated using templates" = Not working

3. **Check Terminal Output**
   - Look for error messages
   - Status codes (200 = success, 410 = gone, 503 = loading)

### If Still Not Working:

1. **Restart Streamlit**
   - Stop the server (Ctrl+C)
   - Restart: `streamlit run app.py`
   - Try again

2. **Clear Session State**
   - Refresh the browser
   - Re-enter API key
   - Toggle ON again

3. **Try Different Model**
   - The code tries multiple models automatically
   - If one fails, it tries the next
   - All failing = API issue or rate limit

### Expected Behavior:

✅ **Working:**
- Toggle ON, API key entered
- Terminal shows: "🤖 Using AI generation..."
- Terminal shows: "✅ Successfully generated post using gpt2"
- Drafts look different from templates (more natural)

❌ **Not Working:**
- Still getting template format
- Terminal shows: "⚠️ All Hugging Face models failed"
- Terminal shows: "⚠️ Hugging Face API returned status 410"

### Need Help?

Check:
1. API key format (must start with `hf_`)
2. Toggle is ON
3. Internet connection
4. Hugging Face service status
5. Rate limits (free tier has limits)

