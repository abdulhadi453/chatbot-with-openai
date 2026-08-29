import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../../types';
import { Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
}

export const MessageList = ({ messages }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="text-center max-w-md"
        >
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot size={32} className="text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Start a Conversation
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Send a message to begin chatting. I'm here to help with any questions you have!
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6"
    >
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
