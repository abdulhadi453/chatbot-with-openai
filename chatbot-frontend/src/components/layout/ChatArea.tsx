import { motion } from 'framer-motion';
import { Header } from './Header';
import { MessageList } from '../chat/MessageList';
import { ChatInput } from '../chat/ChatInput';
import type { Conversation } from '../../types';
import { Bot } from 'lucide-react';

interface ChatAreaProps {
  conversation: Conversation | undefined;
  onSendMessage: (content: string) => void;
  isLoading?: boolean;
}

export const ChatArea = ({ conversation, onSendMessage, isLoading }: ChatAreaProps) => {
  if (!conversation) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="text-center max-w-md"
        >
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
            <Bot size={40} className="text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-3">
            Welcome to AI Chat
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
            Start a new conversation or select an existing one from the sidebar to continue chatting.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-sm">
              💡 Ask me anything
            </div>
            <div className="px-4 py-2 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-lg text-sm">
              🚀 Get instant help
            </div>
            <div className="px-4 py-2 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-lg text-sm">
              ⚡ Lightning fast
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const hasMessages = conversation.messages.length > 0;
  const isWaitingForResponse = conversation.messages.some(m => m.isLoading);

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-950">
      <Header conversationTitle={conversation.title} />

      <MessageList messages={conversation.messages} />

      <ChatInput
        onSendMessage={onSendMessage}
        isLoading={isWaitingForResponse}
        disabled={!hasMessages && isLoading}
      />
    </div>
  );
};
