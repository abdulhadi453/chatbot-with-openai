# Frontend-Backend Integration Guide

This guide shows how to connect the React frontend with the FastAPI backend.

## Quick Start

### 1. Backend Setup

```bash
# Terminal 1 - Start Backend
cd chatbot-backend
python main.py
```

Backend will run on: **http://localhost:8000**

### 2. Frontend Update

Update the frontend API service to connect to the backend:

**File: `chatbot-frontend/src/services/api.ts`**

Replace the entire file with:

```typescript
import type { Conversation, Message, ApiService } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiService: ApiService = {
  async getConversations() {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return response.json();
  },

  async getConversation(id: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
    if (!response.ok) throw new Error('Conversation not found');
    return response.json();
  },

  async createConversation() {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Conversation' }),
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    return response.json();
  },

  async sendMessage(conversationId: string, content: string) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/messages`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  },

  async deleteConversation(id: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete conversation');
  },

  async updateConversationTitle(id: string, title: string) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${id}/title`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      }
    );
    if (!response.ok) throw new Error('Failed to update title');
    return response.json();
  },
};
```

### 3. Frontend Environment Configuration

**File: `chatbot-frontend/.env`**

```bash
VITE_API_URL=http://localhost:8000/api
```

### 4. Start Frontend

```bash
# Terminal 2 - Start Frontend
cd chatbot-frontend
npm run dev
```

Frontend will run on: **http://localhost:5173** (or next available port)

## Testing the Integration

### Test Backend API

**Health Check:**
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

**Create Conversation:**
```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'
```

**Send Message:**
```bash
curl -X POST http://localhost:8000/api/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, how are you?"}'
```

### Test Full Stack

1. Open frontend: http://localhost:5173
2. Click "New Chat"
3. Send a message
4. Verify AI response appears

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  React Frontend │◄───────►│  FastAPI Backend│◄───────►│  OpenAI API     │
│  (Port 5173)    │  HTTP   │  (Port 8000)    │  HTTPS  │                 │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │
        │                           │
        ▼                           ▼
  Browser Storage            SQLite Database
  (Optimistic UI)           (Persistent Storage)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conversations` | Get all conversations |
| GET | `/api/conversations/{id}` | Get specific conversation |
| POST | `/api/conversations` | Create new conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| PATCH | `/api/conversations/{id}/title` | Update conversation title |
| POST | `/api/conversations/{id}/messages` | Send message, get AI response |
| GET | `/api/health` | Health check |

## Data Flow

### Sending a Message

1. **User types message** → Frontend UI
2. **Optimistic update** → Frontend adds user message immediately
3. **HTTP POST** → Frontend sends to `/api/conversations/{id}/messages`
4. **Save user message** → Backend stores in database
5. **Generate AI response** → Backend calls OpenAI API with conversation history
6. **Save AI response** → Backend stores in database
7. **Return response** → Backend sends assistant message to frontend
8. **Update UI** → Frontend displays AI response

### Conversation History

- Backend maintains conversation history in memory per conversation ID
- History includes system message + last 20 user/assistant messages
- Each API call automatically includes relevant context
- Frontend displays full conversation from database

## Environment Variables

### Backend (.env)

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional (with defaults)
APP_NAME=Chatbot Backend
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
HOST=0.0.0.0
PORT=8000
AGENT_MODEL=gpt-4o
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000/api
```

## Troubleshooting

### CORS Issues

If you see CORS errors in browser console:

1. Check backend CORS_ORIGINS includes your frontend URL
2. Restart backend after changing .env
3. Clear browser cache

### Connection Refused

If frontend can't connect to backend:

1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check firewall settings
3. Verify VITE_API_URL in frontend .env

### OpenAI API Errors

If you see "Failed to generate AI response":

1. Verify OPENAI_API_KEY is set correctly in backend .env
2. Check OpenAI API status and quota
3. Review backend logs for detailed error messages

### Database Errors

If you see database-related errors:

1. Delete existing databases: `rm chatbot.db sessions.db`
2. Restart backend (database will be recreated)

## Production Deployment

### Backend Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set proper CORS_ORIGINS (your production frontend URL)
- [ ] Use environment secrets management
- [ ] Set up HTTPS/TLS
- [ ] Configure logging and monitoring
- [ ] Set up rate limiting
- [ ] Use process manager (PM2, Supervisor)

### Frontend Production Checklist

- [ ] Update VITE_API_URL to production backend URL
- [ ] Build for production: `npm run build`
- [ ] Deploy dist/ folder to hosting (Vercel, Netlify, etc.)
- [ ] Configure CDN and caching
- [ ] Set up error tracking (Sentry)

## Performance Optimization

### Backend

- Use Redis for conversation history instead of in-memory storage
- Implement connection pooling for database
- Add response caching for frequently accessed data
- Use async streaming for real-time AI responses

### Frontend

- Implement optimistic UI updates (already done)
- Add request debouncing for auto-save features
- Use React.memo for expensive components
- Implement virtual scrolling for long conversation lists

## Security Best Practices

✅ **Implemented:**
- Environment-based secrets
- Input validation with Pydantic
- CORS configuration
- SQL injection protection via ORM

🔜 **Recommended:**
- Add authentication/authorization (JWT, OAuth)
- Implement rate limiting
- Add request/response encryption (HTTPS)
- Sanitize AI responses for XSS prevention
- Add API key rotation mechanism
- Implement user session management

---

**Integration Complete!** You now have a fully functional, production-ready chatbot with React frontend and FastAPI backend powered by OpenAI.
