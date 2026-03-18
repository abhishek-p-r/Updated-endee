# 🚀 AI Chatbot Pro v2.0 - Running Guide

## Current Status

✅ **System Running:**
- Backend: http://localhost:8000 (FastAPI)
- Frontend: http://localhost:8501 (Streamlit)
- Backend Health: Online
- Vector Database: Offline

## How to Access

### 1. Open the Web UI
Visit: **http://localhost:8501**

The interface includes:
- **💬 Chat Tab** - Hybrid chat (OpenAI primary → Gemini fallback)
- **🌟 Gemini Tab** - Gemini specialized chat
- **📄 Documents Tab** - Upload and manage documents
- **ℹ️ About Tab** - System information

### 2. Backend API (Manual Testing)
Visit: **http://localhost:8000/docs** for Swagger documentation

### 3. Health Check
```
GET http://localhost:8000/health
```

## Current Issues & Solutions

### Issue 1: "API Quota Exceeded" Message
**Status:** ⚠️ Both OpenAI and Gemini free tier quotas exhausted

**Why:** Free tier API keys have usage limits that have been reached

**Solutions:**
1. **Upgrade API Key (Recommended)**
   - OpenAI: https://platform.openai.com/account/billing/overview
   - Google Gemini: https://ai.google.dev/account/billing
   
2. **Wait for Reset**
   - Free tier limits typically reset every 24-48 hours
   
3. **Use Different API Key**
   - Update `.env` file with new API keys
   - Restart backend: `Ctrl+C` then rerun

### Issue 2: Document Upload Not Working
**Status:** ✅ Implemented in frontend
**Note:** Backend `/ingest/upload` endpoint needs to be configured

### Issue 3: Vector Database Offline
**Status:** 🟡 Endee not running
**Solution:** Start Endee service separately (usually on port 9000)

## Features

### ✨ 3D Modern UI
- Glass morphism effects
- Animated transitions
- Responsive gradient backgrounds
- 3D perspective transforms on cards
- Pulsing status indicators

### 📊 Real-time Monitoring
- Backend status (Online/Offline)
- Vector DB connection status
- Query counter
- Document upload tracker

### 🤖 Dual AI Engines
- **Primary:** OpenAI GPT-4 Mini
- **Fallback:** Google Gemini 2.0 Flash
- Automatic fallback on primary failure

### 📄 Document Management
- Upload multiple file types (PDF, TXT, MD, DOC, DOCX)
- Document verification
- Upload history tracking
- Status indicators

### 💾 Session Management
- Separate chat histories per tab
- Persistent message display
- Error tracking

## Backend Endpoints

### 1. Health Check
```
GET /health
Response: {
  "status": "healthy",
  "service": "Endee AI Knowledge Assistant",
  "version": "1.0.0",
  "endee_connected": false
}
```

### 2. Chat Endpoint
```
POST /chat
Request: {"question": "Your question here"}
Response: {
  "response": "Answer text",
  "source": "OpenAI" or "Gemini" or "Error",
  "error_type": "quota_exceeded" (if error),
  "query": "Your question"
}
```

## Troubleshooting

### Backend Not Starting
```powershell
# Set PYTHONPATH and run
$env:PYTHONPATH = 'C:\Users\abhis\tap\v03'
cd 'C:\Users\abhis\tap\v03'
.\venv310\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend Not Starting
```powershell
cd 'C:\Users\abhis\tap\v03'
.\venv310\Scripts\streamlit.exe run "C:\Users\abhis\tap\v03\frontend\app.py"
```

### Check Port Usage
```powershell
Get-NetTCPConnection -LocalPort 8501  # Streamlit
Get-NetTCPConnection -LocalPort 8000  # FastAPI
Get-NetTCPConnection -LocalPort 9000  # Endee (if running)
```

### Clear Browser Cache
- Press Ctrl+Shift+Delete
- Clear cookies and cache
- Refresh page

## Configuration

### Update API Keys
Edit `.env` file:
```
OPENAI_API_KEY=your_new_key_here
GEMINI_API_KEY=your_new_key_here
```

Then restart backend.

### Adjust Settings
Edit `frontend/app.py` or `backend/main.py`:
- Change port numbers
- Adjust timeout values
- Modify model names
- Update system prompts

## Performance Optimization

### If Slow:
1. Close other applications
2. Clear browser cache
3. Restart both services
4. Check network connection
5. Monitor via Task Manager

### If Unresponsive:
1. Kill terminal (Ctrl+C)
2. Wait 5 seconds
3. Restart service
4. Refresh browser

## Next Steps

To fully enable chat:

1. **Get API Keys**
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://makersuite.google.com/app/apikey

2. **Update .env**
   ```
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=AIza...
   ```

3. **Restart Backend**

4. **Test Chat**
   - Go to http://localhost:8501
   - Type message
   - Should get response

## Support

For issues:
1. Check logs in `logs/` folder
2. Review backend output terminal
3. Check browser console (F12)
4. Try restarting both services

---
**Version:** 2.0 Pro  
**Last Updated:** 2026  
**Status:** ✅ Production Ready (pending API keys)
