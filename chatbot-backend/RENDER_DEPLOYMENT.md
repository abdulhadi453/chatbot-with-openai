# Render Deployment Configuration

## Required Updates in Render Dashboard

### 1. Update Start Command
Go to your service settings and change the start command to:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
```

**Or use this simpler version:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 2. Set Environment Variables
Add these environment variables in the Render dashboard:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | Your frontend URL (e.g., `https://your-frontend.com`) |

### 3. Service Configuration
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
- **Python Version:** 3.11 or higher

## Quick Steps

1. Go to: https://dashboard.render.com/web/srv-damd1me1egvs73bp5bcg
2. Click "Environment" → Add the environment variables above
3. Click "Settings" → Update the start command
4. Click "Manual Deploy" → "Deploy latest commit"

## Verification
After deployment, visit:
- Service URL: https://chatbot-with-openai-dfom.onrender.com
- Health check: https://chatbot-with-openai-dfom.onrender.com/

Expected response:
```json
{
  "name": "Chatbot Backend",
  "version": "1.0.0",
  "status": "running",
  "environment": "production"
}
```
