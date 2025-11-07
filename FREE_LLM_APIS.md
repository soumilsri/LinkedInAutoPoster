# Free LLM APIs for Post Generation

## 🚀 Recommended: Groq API (Fastest!)

**Why Groq?**
- ⚡ **Extremely fast** - Generates posts in 1-2 seconds
- 🆓 **Free tier** - 14,400 requests/day
- ✅ **Reliable** - No authentication issues
- 🎯 **Easy setup** - Simple API

**Get API Key:**
1. Go to: https://console.groq.com
2. Sign up (free)
3. Go to API Keys section
4. Create new API key
5. Copy and paste in the app

**Model Used:** `llama-3.1-8b-instant` (fast and free)

---

## 🎯 Together AI (Alternative)

**Why Together AI?**
- 🆓 **Free tier** - $25 free credits
- 📚 **Multiple models** - Access to various LLMs
- 🔄 **Reliable** - Good uptime

**Get API Key:**
1. Go to: https://together.ai
2. Sign up (free)
3. Navigate to API Keys
4. Create new key
5. Copy and paste in the app

**Model Used:** `meta-llama/Llama-3-8b-chat-hf`

---

## 🔄 Hugging Face (Fallback)

**Status:** Currently having authentication issues with router endpoint

**Get API Key:**
1. Go to: https://huggingface.co/settings/tokens
2. Create token with "Read" permissions
3. Copy and paste in the app

---

## 📊 Comparison

| Feature | Groq | Together AI | Hugging Face |
|---------|------|------------|--------------|
| Speed | ⚡⚡⚡ Very Fast | ⚡⚡ Fast | ⚡ Slow |
| Free Tier | 14,400 req/day | $25 credits | Limited |
| Reliability | ✅ Excellent | ✅ Good | ⚠️ Issues |
| Setup | Easy | Easy | Complex |
| **Recommendation** | ⭐⭐⭐ Best | ⭐⭐ Good | ⭐ Fallback |

---

## 🎯 Quick Start

### Option 1: Groq (Recommended)
1. Get free API key: https://console.groq.com
2. Paste in app sidebar
3. Toggle AI generation ON
4. Generate posts!

### Option 2: Together AI
1. Get free API key: https://together.ai
2. Paste in app sidebar
3. Toggle AI generation ON
4. Generate posts!

### Option 3: Both
- Enter both API keys
- App will try Groq first, then Together AI, then Hugging Face
- Automatic fallback if one fails

---

## 💡 Tips

1. **Start with Groq** - It's the fastest and most reliable
2. **Keep both keys** - For redundancy
3. **Check free tier limits** - Both have generous free tiers
4. **Monitor usage** - Free tiers are usually enough for personal use

---

## 🔧 How It Works

The app tries APIs in this order:
1. **Groq** (if key provided) - Fastest
2. **Together AI** (if key provided) - Reliable
3. **Hugging Face** (if key provided) - Fallback
4. **AI-Enhanced Templates** - If all APIs fail

This ensures you always get AI-generated content when possible!

