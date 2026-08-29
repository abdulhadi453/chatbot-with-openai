import { motion } from 'framer-motion';
import { Bot, Sparkles } from 'lucide-react';

interface HeaderProps {
  conversationTitle?: string;
}

export const Header = ({ conversationTitle }: HeaderProps) => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4"
    >
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {conversationTitle || 'AI Assistant'}
            </h1>
            <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
              <Sparkles size={12} className="text-green-500" />
              <span>Online</span>
            </div>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-md">
            React + TypeScript
          </span>
        </div>
      </div>
    </motion.header>
  );
};
