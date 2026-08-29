# Quick Start Guide

## Starting the Backend

### PowerShell (Recommended)
```powershell
cd "E:\OpenAI\chatbot with openai\frontend\chatbot-backend"
.\.venv\Scripts\activate
uv run main.py
```

### Alternative: Direct Python
```powershell
cd "E:\OpenAI\chatbot with openai\frontend\chatbot-backend"
.\.venv\Scripts\python.exe main.py
```

## Stopping the Backend

Press `Ctrl+C` in the terminal where the backend is running.

## If You Get "Port Already in Use" Error

Find and kill the process using port 8000:
```powershell
# Find the process
netstat -ano | findstr ":8000" | findstr "LISTENING"

# Kill it (replace XXXX with the PID from above)
taskkill //PID XXXX //F
```

## API Endpoints

Once started, the backend will be available at `http://localhost:8000`

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Application info
curl http://localhost:8000/

# Get conversations
curl http://localhost:8000/api/conversations
```

## Environment Configuration

All configuration is in `.env` file:
- ✅ OpenAI API Key configured
- ✅ Database: SQLite (chatbot.db)
- ✅ Port: 8000
- ✅ CORS enabled for localhost:5173-5175

## Troubleshooting

### Import Errors
Make sure you're using the virtual environment:
```powershell
.\.venv\Scripts\activate
```

### Dependency Issues
Reinstall dependencies:
```powershell
uv pip install -r requirements.txt
```

### Check Environment Health
```powershell
# Verify virtual environment
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"

# Test imports
.\.venv\Scripts\python.exe -c "from app.services.agent_service import agent_service; print('OK')"

# Check for conflicts
uv pip check
```

## Next Steps

1. Start the backend: `uv run main.py`
2. Verify it's running: Open http://localhost:8000 in your browser
3. Connect your frontend to http://localhost:8000
4. Test the chat functionality

## Documentation

See `BACKEND_FIX_SUMMARY.md` for detailed information about:
- All fixes applied
- Complete environment setup
- API documentation
- Maintenance guide
