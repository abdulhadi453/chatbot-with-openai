# AI Chatbot Frontend

A modern, fully functional chatbot frontend prototype built with React, TypeScript, Vite, and Tailwind CSS. Features realistic interactions, mock data, conversation management, and production-ready UI design.

## ✨ Features

### Core Functionality
- **Multi-Conversation Management** - Create, switch between, and delete multiple chat conversations
- **Real-time Chat Interface** - Smooth message flow with user and assistant messages
- **Conversation History** - Persistent conversation list with previews and timestamps
- **Message Loading States** - Visual feedback during message processing
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- **Dark Mode Ready** - Built-in dark mode support with Tailwind CSS

### User Experience
- **Smooth Animations** - Powered by Framer Motion for polished interactions
- **Mobile-Friendly Sidebar** - Collapsible sidebar with smooth transitions
- **Auto-Scroll Messages** - Automatically scrolls to newest messages
- **Textarea Auto-Resize** - Input field grows with content
- **Loading Indicators** - Clear visual feedback for all async operations
- **Empty States** - Thoughtful empty state designs for new users

### Technical Highlights
- **TypeScript** - Full type safety throughout the application
- **Mock API Service** - Realistic API layer ready for backend integration
- **Custom Hooks** - Clean state management with React hooks
- **Component Architecture** - Well-organized, reusable components
- **Scalable Structure** - Clear separation of concerns

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Production-ready animation library
- **Lucide React** - Beautiful, consistent icons

## 📁 Project Structure

```
chatbot-frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx       # Message input with auto-resize
│   │   │   ├── MessageBubble.tsx   # Individual message component
│   │   │   ├── MessageList.tsx     # Scrollable message container
│   │   │   └── index.ts
│   │   ├── common/
│   │   │   ├── Button.tsx          # Reusable button component
│   │   │   ├── LoadingSpinner.tsx  # Loading indicator
│   │   │   └── index.ts
│   │   └── layout/
│   │       ├── ChatArea.tsx        # Main chat interface
│   │       ├── ConversationItem.tsx # Single conversation in sidebar
│   │       ├── Header.tsx          # Chat header
│   │       ├── Sidebar.tsx         # Conversation list sidebar
│   │       └── index.ts
│   ├── hooks/
│   │   └── useChatStore.ts         # Custom hook for chat state
│   ├── services/
│   │   └── api.ts                  # Mock API service layer
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   ├── App.tsx                     # Root component
│   ├── main.tsx                    # Application entry point
│   └── index.css                   # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Navigate to the project directory:
```bash
cd chatbot-frontend
```

2. Install dependencies (already done):
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to the URL shown (typically `http://localhost:5173` or `http://localhost:5174`)

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## 🏗️ Architecture Overview

### Component Hierarchy

```
App
├── Sidebar
│   └── ConversationItem (multiple)
└── ChatArea
    ├── Header
    ├── MessageList
    │   └── MessageBubble (multiple)
    └── ChatInput
```

### State Management

The application uses a custom hook (`useChatStore`) for centralized state management:

- **Conversations**: Array of all chat conversations
- **Active Conversation**: Currently selected conversation
- **Loading States**: Track async operations
- **Error Handling**: User-friendly error messages

### API Service Layer

The `api.ts` service provides a clean abstraction for data operations:

```typescript
interface ApiService {
  getConversations: () => Promise<Conversation[]>;
  getConversation: (id: string) => Promise<Conversation>;
  createConversation: () => Promise<Conversation>;
  sendMessage: (conversationId: string, content: string) => Promise<Message>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
}
```

Currently uses mock data and simulated delays. Ready to swap with real API calls.

## 🔌 Backend Integration Guide

### Replacing Mock API with Real Backend

1. **Update `src/services/api.ts`**:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

export const apiService: ApiService = {
  async getConversations() {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return response.json();
  },

  async sendMessage(conversationId: string, content: string) {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  },

  // ... implement other methods
};
```

2. **Add Environment Variables**:

Create `.env` file:
```
VITE_API_URL=http://localhost:3000/api
```

3. **Update Type Definitions** (if backend schema differs):

Modify `src/types/index.ts` to match your backend API response structure.

### Streaming Response Support

To add streaming support for AI responses:

```typescript
async sendMessage(conversationId: string, content: string) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  let fullMessage = '';
  
  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    fullMessage += chunk;
    
    // Update UI with partial message
    // You'll need to modify useChatStore to handle streaming
  }

  return fullMessage;
}
```

## 🎨 Customization

### Theming

Colors are defined in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Customize your brand colors
      },
    },
  },
}
```

### Component Styling

All components use Tailwind utility classes. Modify the `className` props to adjust styling.

## 📱 Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

Sidebar automatically collapses on mobile with a hamburger menu.

## 🧪 Mock Data

The application includes three pre-populated conversations with realistic messages about:
- React development
- TypeScript best practices
- API design patterns

Mock data is defined in `src/services/api.ts` and can be modified or removed.

## 🚧 Future Enhancements

### Recommended Features
- User authentication and authorization
- Message editing and deletion
- Code syntax highlighting in messages
- File upload support
- Voice input
- Export conversation history
- Search within conversations
- Conversation tags/labels
- Multi-language support
- Keyboard shortcuts

### Technical Improvements
- Add unit tests (Jest/Vitest)
- Add E2E tests (Playwright/Cypress)
- Implement proper error boundaries
- Add offline support with service workers
- Implement WebSocket for real-time updates
- Add performance monitoring
- Optimize bundle size with code splitting

## 🔒 Security Considerations

When integrating with a backend:

1. **Never store sensitive data in localStorage** without encryption
2. **Implement proper authentication** (JWT, OAuth, etc.)
3. **Sanitize user input** before sending to backend
4. **Use HTTPS** in production
5. **Implement rate limiting** on the client side
6. **Validate all API responses** before using data

## 📊 Build Information

- **Production Build Size**: ~340 KB (gzipped: ~108 KB)
- **CSS Size**: ~24 KB (gzipped: ~5.5 KB)
- **Build Time**: ~3 seconds

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
