import type { Conversation, Message, ApiService } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiService: ApiService = {
  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    const data = await response.json();

    // Parse date strings to Date objects
    return data.map((conv: any) => ({
      ...conv,
      createdAt: new Date(conv.createdAt),
      updatedAt: new Date(conv.updatedAt),
      messages: conv.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    }));
  },

  async getConversation(id: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
    if (!response.ok) throw new Error('Conversation not found');
    const data = await response.json();

    // Parse date strings to Date objects
    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      messages: data.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    };
  },

  async createConversation() {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'New Conversation' }),
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    const data = await response.json();

    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      messages: []
    };
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
    const data = await response.json();

    return {
      ...data,
      timestamp: new Date(data.timestamp)
    };
  },

  async sendMessageStreaming(
    conversationId: string,
    content: string,
    onChunk: (chunk: string) => void,
    onSearchStatus?: (status: string) => void,
    onComplete?: (message: Message) => void
  ) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/messages/stream`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Stream not available');
    }

    const decoder = new TextDecoder();
    let fullContent = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'user_message':
                  // User message saved confirmation
                  console.log('User message saved:', data.message.id);
                  break;

                case 'chunk':
                  // Streaming content chunk
                  fullContent += data.content;
                  onChunk(data.content);
                  break;

                case 'done':
                  // Complete message received
                  if (onComplete) {
                    const message: Message = {
                      id: data.message.id,
                      role: data.message.role,
                      content: data.message.content,
                      timestamp: new Date(data.message.timestamp)
                    };
                    onComplete(message);
                  }
                  break;

                case 'error':
                  throw new Error(data.detail);
              }

              // Check for search status in chunk content
              if (data.content && data.content.includes('[Searching the web')) {
                if (onSearchStatus) {
                  const match = data.content.match(/\[Searching the web for: (.+?)\.\.\.\]/);
                  if (match) {
                    onSearchStatus(match[1]);
                  }
                }
              }
            } catch (e) {
              // Skip invalid JSON lines
              console.warn('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
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
    const data = await response.json();

    return {
      ...data,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      messages: data.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    };
  },
};
