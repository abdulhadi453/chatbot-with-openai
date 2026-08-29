# AI Chatbot Backend

Production-ready backend for the AI chatbot application built with FastAPI and OpenAI Agents SDK.

## ✨ Features

### Core Functionality
- **OpenAI Agents SDK Integration** - Official SDK for intelligent agent interactions
- **Conversation Management** - Create, retrieve, update, and delete conversations
- **Message History** - Automatic conversation history with SQLite sessions
- **RESTful API** - Clean REST endpoints matching frontend requirements
- **Async Architecture** - Fully asynchronous with SQLAlchemy async
- **Database Persistence** - SQLite for conversations and session storage

### Production Features
- **Environment Configuration** - Pydantic Settings for validation
- **Error Handling** - Comprehensive error handling and logging
- **CORS Support** - Configured for frontend integration
- **Input Validation** - Pydantic models for request/response validation
- **Health Checks** - Health endpoint for monitoring
- **Structured Logging** - Detailed logging for debugging

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework
- **OpenAI Agents SDK** - Official agent orchestration framework
- **SQLAlchemy** - Async ORM for database operations
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for production
- **SQLite** - Lightweight database for conversations and sessions

## 📁 Project Structure

```
chatbot-backend/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # Database connection & session
│   │   └── models.py           # SQLAlchemy models
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic request/response models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── conversations.py    # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py    # OpenAI Agent integration
│   │   └── conversation_service.py  # Business logic
│   └── utils/
│       └── __init__.py
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- pip (Python package manager)

### Installation

1. **Navigate to the backend directory:**
```bash
cd chatbot-backend
```

2. **Create and activate virtual environment:**

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` and configure your settings:
```bash
OPENAI_API_KEY=your-actual-api-key-here
```

### Running the Server

**Development mode (with auto-reload):**
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs` (development only)
- **ReDoc:** `http://localhost:8000/redoc` (development only)

## 📡 API Endpoints

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations` | Get all conversations |
| GET | `/api/conversations/{id}` | Get specific conversation |
| POST | `/api/conversations` | Create new conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| PATCH | `/api/conversations/{id}/title` | Update conversation title |
| POST | `/api/conversations/{id}/messages` | Send message and get AI response |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |
| GET | `/` | Root endpoint with API info |

### Example API Calls

**Create a new conversation:**
```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Chat"}'
```

**Send a message:**
```bash
curl -X POST http://localhost:8000/api/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is quantum computing?"}'
```

**Get all conversations:**
```bash
curl http://localhost:8000/api/conversations
```

## 🏗️ Architecture

### Agent Service

The `AgentService` uses the official OpenAI Agents SDK:
- Automatic conversation history via `SQLiteSession`
- Configurable model settings (temperature, max tokens)
- Support for streaming responses (future enhancement)
- Built-in error handling and logging

### Conversation Service

The `ConversationService` handles database operations:
- CRUD operations for conversations and messages
- Automatic timestamp management
- Title generation from first message
- Preview text extraction

### Data Flow

1. **Client sends message** → API endpoint receives request
2. **Save user message** → ConversationService stores in database
3. **Generate AI response** → AgentService uses SDK with session history
4. **Save AI response** → ConversationService stores in database
5. **Return response** → API sends assistant message to client

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `APP_NAME` | Application name | Chatbot Backend |
| `DEBUG` | Debug mode | False |
| `ENVIRONMENT` | Environment (dev/prod) | production |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:5173,5174,5175 |
| `DATABASE_URL` | Database connection URL | sqlite+aiosqlite:///./chatbot.db |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `AGENT_MODEL` | OpenAI model to use | gpt-4o |
| `AGENT_TEMPERATURE` | Model temperature | 0.7 |
| `AGENT_MAX_TOKENS` | Max tokens per response | 2000 |

### Agent Configuration

Customize the AI agent behavior in `.env`:

```bash
# Agent personality and behavior
AGENT_NAME=AI Assistant
AGENT_INSTRUCTIONS=You are a helpful, knowledgeable AI assistant.

# Model settings
AGENT_MODEL=gpt-4o
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

## 🗄️ Database

### Schema

**Conversations Table:**
- `id` (Primary Key)
- `title`
- `preview`
- `created_at`
- `updated_at`

**Messages Table:**
- `id` (Primary Key)
- `conversation_id` (Foreign Key)
- `role` (user/assistant)
- `content`
- `timestamp`

**Session Storage:**
- SQLite database for Agent SDK session history
- Automatic conversation context management

### Migrations

Database tables are automatically created on startup. To reset the database:

```bash
rm chatbot.db sessions.db
python main.py
```

## 🔌 Frontend Integration

The backend is designed to integrate seamlessly with the React frontend:

1. **Update frontend API URL:**

In `chatbot-frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
```

2. **Update frontend service:**

Replace mock API calls in `src/services/api.ts` with real HTTP requests to the backend endpoints.

3. **Start both servers:**
```bash
# Terminal 1 - Backend
cd chatbot-backend
python main.py

# Terminal 2 - Frontend
cd chatbot-frontend
npm run dev
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong database credentials
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Use process manager (PM2, Supervisor)
- [ ] Configure firewall rules

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 --env-file .env chatbot-backend
```

### Systemd Service

Create `/etc/systemd/system/chatbot-backend.service`:
```ini
[Unit]
Description=Chatbot Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/chatbot-backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable chatbot-backend
sudo systemctl start chatbot-backend
```

## 🧪 Testing

### Manual Testing

Test the API with curl or tools like Postman, Insomnia, or the built-in API docs at `/docs`.

### Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "chatbot-backend"
}
```

## 📊 Monitoring

### Logs

Application logs include:
- Request/response information
- Database operations
- Agent interactions
- Error traces

View logs in real-time:
```bash
tail -f logs/app.log
```

### Metrics

Monitor these key metrics:
- API response times
- Database query performance
- OpenAI API usage and costs
- Error rates
- Active conversations

## 🔒 Security

### Best Practices Implemented

✅ Environment-based configuration  
✅ Input validation with Pydantic  
✅ SQL injection protection via ORM  
✅ CORS configuration  
✅ Error message sanitization  
✅ Logging without sensitive data  

### Additional Recommendations

- [ ] Implement rate limiting (e.g., slowapi)
- [ ] Add authentication/authorization (JWT, OAuth)
- [ ] Use HTTPS in production
- [ ] Implement request size limits
- [ ] Add API key rotation
- [ ] Set up security headers
- [ ] Regular dependency updates

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
```

**2. Database locked errors**
```bash
# Stop all running instances
# Delete lock files
rm chatbot.db-shm chatbot.db-wal
```

**3. CORS errors**
```bash
# Update CORS_ORIGINS in .env to include your frontend URL
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**4. OpenAI API errors**
```bash
# Verify API key is set correctly
# Check API quota and billing
# Test with: curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

## 📝 Development

### Code Style

Follow PEP 8 guidelines. Use formatters:
```bash
pip install black isort
black .
isort .
```

### Adding New Features

1. Define Pydantic models in `app/models/schemas.py`
2. Add database models in `app/database/models.py`
3. Implement business logic in `app/services/`
4. Create API routes in `app/routes/`
5. Update tests and documentation

## 📄 License

This is a production prototype for educational and development purposes.

## 🤝 Support

For issues or questions:
1. Check the documentation
2. Review logs for error messages
3. Test with the `/docs` endpoint
4. Verify environment configuration

---

**Built with FastAPI, OpenAI Agents SDK, and Python**
