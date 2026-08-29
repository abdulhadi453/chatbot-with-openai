import { useState, useEffect, useCallback } from 'react';
import type { Message, ChatState } from '../types';
import { apiService } from '../services/api';

export const useChatStore = () => {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    activeConversationId: null,
    isLoading: false,
    error: null,
  });

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const conversations = await apiService.getConversations();
      setState(prev => ({
        ...prev,
        conversations,
        isLoading: false,
        activeConversationId: prev.activeConversationId || (conversations[0]?.id ?? null),
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to load conversations',
      }));
    }
  }, []);

  const createConversation = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));
    try {
      const newConversation = await apiService.createConversation();
      setState(prev => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        activeConversationId: newConversation.id,
        isLoading: false,
      }));
      return newConversation;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Failed to create conversation',
      }));
      return null;
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    const conversationId = state.activeConversationId;
    if (!conversationId) return;

    // Add optimistic user message
    const tempUserMessage: Message = {
      id: `temp-user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const tempAssistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };

    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(conv =>
        conv.id === conversationId
          ? {
              ...conv,
              messages: [...conv.messages, tempUserMessage, tempAssistantMessage],
              updatedAt: new Date(),
            }
          : conv
      ),
    }));

    try {
      // Use streaming API for real-time responses
      await apiService.sendMessageStreaming(
        conversationId,
        content,
        // onChunk: Update streaming content
        (chunk: string) => {
          setState(prev => ({
            ...prev,
            conversations: prev.conversations.map(conv =>
              conv.id === conversationId
                ? {
                    ...conv,
                    messages: conv.messages.map(msg =>
                      msg.id === tempAssistantMessage.id
                        ? {
                            ...msg,
                            content: msg.content + chunk,
                            isStreaming: true,
                            searchStatus: undefined // Clear search status when content arrives
                          }
                        : msg
                    ),
                  }
                : conv
            ),
          }));
        },
        // onSearchStatus: Show web search activity
        (searchQuery: string) => {
          setState(prev => ({
            ...prev,
            conversations: prev.conversations.map(conv =>
              conv.id === conversationId
                ? {
                    ...conv,
                    messages: conv.messages.map(msg =>
                      msg.id === tempAssistantMessage.id
                        ? { ...msg, searchStatus: `Searching: ${searchQuery}` }
                        : msg
                    ),
                  }
                : conv
            ),
          }));
        },
        // onComplete: Finalize message
        (finalMessage: Message) => {
          setState(prev => ({
            ...prev,
            conversations: prev.conversations.map(conv =>
              conv.id === conversationId
                ? {
                    ...conv,
                    messages: conv.messages.map(msg =>
                      msg.id === tempAssistantMessage.id
                        ? {
                            ...finalMessage,
                            id: finalMessage.id,
                            isStreaming: false,
                            searchStatus: undefined
                          }
                        : msg
                    ),
                    updatedAt: new Date(),
                    preview: content.slice(0, 60),
                    title: conv.messages.length === 0
                      ? content.slice(0, 50) + (content.length > 50 ? '...' : '')
                      : conv.title,
                  }
                : conv
            ),
          }));
        }
      );
    } catch (error) {
      console.error('Streaming error:', error);
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === conversationId
            ? {
                ...conv,
                messages: conv.messages.filter(m => m.id !== tempAssistantMessage.id),
              }
            : conv
        ),
        error: 'Failed to send message',
      }));
    }
  }, [state.activeConversationId]);

  const deleteConversation = useCallback(async (id: string) => {
    try {
      await apiService.deleteConversation(id);
      setState(prev => {
        const filtered = prev.conversations.filter(c => c.id !== id);
        return {
          ...prev,
          conversations: filtered,
          activeConversationId:
            prev.activeConversationId === id
              ? filtered[0]?.id ?? null
              : prev.activeConversationId,
        };
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to delete conversation',
      }));
    }
  }, []);

  const setActiveConversation = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      activeConversationId: id,
    }));
  }, []);

  const activeConversation = state.conversations.find(
    c => c.id === state.activeConversationId
  );

  return {
    conversations: state.conversations,
    activeConversation,
    isLoading: state.isLoading,
    error: state.error,
    createConversation,
    sendMessage,
    deleteConversation,
    setActiveConversation,
  };
};
