import { motion } from 'framer-motion';
import type { Message as MessageType } from '../../types';
import { User, Bot, Search } from 'lucide-react';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface MessageBubbleProps {
  message: MessageType;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-4`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
        }`}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div
        className={`flex flex-col max-w-[70%] ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-sm'
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700 rounded-tl-sm'
          }`}
        >
          {/* Show web search status */}
          {message.searchStatus && (
            <div className="flex items-center gap-2 mb-2 text-sm text-blue-600 dark:text-blue-400">
              <Search size={14} className="animate-pulse" />
              <span className="italic">{message.searchStatus}</span>
            </div>
          )}

          {/* Show loading spinner for initial loading */}
          {message.isLoading && !message.content ? (
            <div className="flex items-center gap-2">
              <LoadingSpinner size="sm" />
              <span className="text-sm">Thinking...</span>
            </div>
          ) : (
            <>
              {/* Show message content */}
              <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                {message.content}
              </p>

              {/* Show streaming cursor */}
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 ml-1 bg-gray-400 dark:bg-gray-500 animate-pulse" />
              )}
            </>
          )}
        </div>

        <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 px-2">
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </motion.div>
  );
};
