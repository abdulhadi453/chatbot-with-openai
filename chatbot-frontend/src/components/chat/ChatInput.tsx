import { useState, useRef, useEffect } from 'react';
import type { FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { Button } from '../common/Button';

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export const ChatInput = ({ onSendMessage, isLoading, disabled }: ChatInputProps) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4"
    >
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift + Enter for new line)"
              disabled={disabled || isLoading}
              rows={1}
              className="w-full resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed max-h-32 scrollbar-thin"
              style={{ minHeight: '48px' }}
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={!message.trim() || disabled || isLoading}
            isLoading={isLoading}
            className="h-12 w-12 p-0 flex-shrink-0"
          >
            {!isLoading && <Send size={20} />}
          </Button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          Press Enter to send, Shift + Enter for new line
        </p>
      </form>
    </motion.div>
  );
};
