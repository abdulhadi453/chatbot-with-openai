export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  isStreaming?: boolean;
  searchStatus?: string; // For showing web search activity
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  preview?: string;
}

export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface ApiService {
  getConversations: () => Promise<Conversation[]>;
  getConversation: (id: string) => Promise<Conversation>;
  createConversation: () => Promise<Conversation>;
  sendMessage: (conversationId: string, content: string) => Promise<Message>;
  sendMessageStreaming: (
    conversationId: string,
    content: string,
    onChunk: (chunk: string) => void,
    onSearchStatus?: (status: string) => void,
    onComplete?: (message: Message) => void
  ) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
}
