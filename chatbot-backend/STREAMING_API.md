# Real-Time Streaming API Documentation

## Overview

The backend now supports **real-time streaming responses** using Server-Sent Events (SSE). This provides a much better user experience by displaying the AI's response as it's being generated, rather than waiting for the complete response.

## Endpoints

### 1. Standard (Non-Streaming) - Original
```
POST /api/conversations/{conversation_id}/messages
```
- Returns complete message after AI finishes generating
- Simple request/response model
- Use when streaming is not needed

**Response:**
```json
{
  "id": "message-uuid",
  "role": "assistant",
  "content": "Complete AI response here",
  "timestamp": "2026-08-29T10:00:00.000000",
  "isLoading": null
}
```

### 2. Streaming (Real-Time) - NEW ⚡
```
POST /api/conversations/{conversation_id}/messages/stream
```
- Streams response in real-time as it's generated
- Uses Server-Sent Events (SSE)
- Better user experience with immediate feedback

**Request:**
```json
{
  "content": "Your message here"
}
```

**Response Format:** Server-Sent Events (text/event-stream)

The response consists of multiple SSE events:

#### Event 1: User Message Confirmation
```
data: {"type":"user_message","message":{"id":"uuid","role":"user","content":"...","timestamp":"..."}}

```

#### Event 2-N: Content Chunks (Streaming)
```
data: {"type":"chunk","content":"word "}

data: {"type":"chunk","content":"by "}

data: {"type":"chunk","content":"word"}

```

#### Final Event: Complete Message
```
data: {"type":"done","message":{"id":"uuid","role":"assistant","content":"Full response","timestamp":"..."}}

```

#### Error Event (if error occurs)
```
data: {"type":"error","detail":"Error message"}

```

## Frontend Integration

### JavaScript/TypeScript Example

```typescript
async function sendMessageWithStreaming(
  conversationId: string, 
  content: string,
  onChunk: (text: string) => void,
  onComplete: (message: any) => void,
  onError: (error: string) => void
) {
  const response = await fetch(
    `http://localhost:8000/api/conversations/${conversationId}/messages/stream`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    }
  );

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));

        switch (data.type) {
          case 'user_message':
            console.log('User message saved:', data.message.id);
            break;

          case 'chunk':
            onChunk(data.content); // Update UI with each chunk
            break;

          case 'done':
            onComplete(data.message); // Message complete
            break;

          case 'error':
            onError(data.detail);
            break;
        }
      }
    }
  }
}
```

### React Example

```tsx
import { useState } from 'react';

function ChatMessage() {
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = async (conversationId: string, content: string) => {
    setIsStreaming(true);
    setStreamingContent('');

    const response = await fetch(
      `http://localhost:8000/api/conversations/${conversationId}/messages/stream`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      }
    );

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));

          if (data.type === 'chunk') {
            setStreamingContent(prev => prev + data.content);
          } else if (data.type === 'done') {
            setIsStreaming(false);
          }
        }
      }
    }
  };

  return (
    <div>
      <div className={isStreaming ? 'streaming' : ''}>
        {streamingContent}
      </div>
    </div>
  );
}
```

### EventSource API (Alternative)

```javascript
// Note: EventSource doesn't support POST, so this is for GET streaming
// For POST with SSE, use fetch with ReadableStream as shown above

// If you modify the endpoint to accept GET:
const eventSource = new EventSource(
  `http://localhost:8000/api/conversations/${conversationId}/messages/stream?content=${encodeURIComponent(message)}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'chunk') {
    updateUI(data.content);
  } else if (data.type === 'done') {
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE Error:', error);
  eventSource.close();
};
```

## Performance Comparison

### Non-Streaming (Original)
- User sends message → Wait 3-10 seconds → Complete response appears
- **Time to First Content**: 3-10 seconds
- **User Experience**: Waiting spinner, then full response

### Streaming (NEW)
- User sends message → Words appear immediately as generated
- **Time to First Content**: 0.5-1 second
- **User Experience**: Real-time typing effect, feels responsive

## Testing the Streaming Endpoint

### Using Python Test Script
```bash
cd "E:\OpenAI\chatbot with openai\frontend\chatbot-backend"
.\.venv\Scripts\python.exe test_streaming.py
```

### Using curl
```bash
curl -N -X POST http://localhost:8000/api/conversations/{conversation_id}/messages/stream \
  -H "Content-Type: application/json" \
  -d '{"content":"Tell me a short joke"}'
```

The `-N` flag disables buffering to see the streaming in real-time.

### Using Browser Console
```javascript
fetch('http://localhost:8000/api/conversations/{conversation_id}/messages/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: 'Hello!' })
})
.then(response => response.body.getReader())
.then(reader => {
  const decoder = new TextDecoder();
  function read() {
    reader.read().then(({ done, value }) => {
      if (done) return;
      console.log(decoder.decode(value));
      read();
    });
  }
  read();
});
```

## Configuration

No additional configuration needed. The streaming uses the same settings from `.env`:
- `AGENT_MODEL` - OpenAI model (default: gpt-4o)
- `AGENT_TEMPERATURE` - Response randomness (default: 0.7)
- `AGENT_MAX_TOKENS` - Max response length (default: 2000)

## Headers

The streaming endpoint sets these headers automatically:
- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`
- `X-Accel-Buffering: no` (for nginx compatibility)

## Error Handling

Errors during streaming are sent as SSE events:
```
data: {"type":"error","detail":"Error message here"}

```

Your frontend should handle these errors gracefully and display appropriate messages to users.

## Migration Guide

### Updating Existing Frontend

**Before (Non-Streaming):**
```typescript
const response = await fetch(`/api/conversations/${id}/messages`, {
  method: 'POST',
  body: JSON.stringify({ content: message })
});
const assistantMessage = await response.json();
// Display complete message
```

**After (Streaming):**
```typescript
const response = await fetch(`/api/conversations/${id}/messages/stream`, {
  method: 'POST',
  body: JSON.stringify({ content: message })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let fullContent = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  // Parse and handle SSE events
  // Update UI with chunks
}
```

## Benefits

✅ **Better UX** - Users see responses immediately
✅ **Feels Faster** - Perceived performance improvement
✅ **Engagement** - Users stay engaged while AI generates
✅ **Modern** - Industry-standard approach (ChatGPT, Claude, etc.)
✅ **Backward Compatible** - Original endpoint still works

## Next Steps

1. Update your frontend to use the streaming endpoint
2. Add typing indicators and loading states
3. Test with different message lengths
4. Consider adding a fallback to non-streaming for slow connections
