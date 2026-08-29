import { motion } from 'framer-motion';
import type { Conversation } from '../../types';
import { MessageSquare, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
  onDelete: (id: string) => void;
}

export const ConversationItem = ({
  conversation,
  isActive,
  onClick,
  onDelete,
}: ConversationItemProps) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      onDelete(conversation.id);
    }
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      whileHover={{ x: 4 }}
      transition={{ duration: 0.2 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      className={`group relative flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
          : 'hover:bg-gray-100 dark:hover:bg-gray-800 border border-transparent'
      }`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isActive
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
        }`}
      >
        <MessageSquare size={16} />
      </div>

      <div className="flex-1 min-w-0">
        <h3
          className={`text-sm font-medium truncate ${
            isActive
              ? 'text-gray-900 dark:text-gray-100'
              : 'text-gray-700 dark:text-gray-300'
          }`}
        >
          {conversation.title}
        </h3>
        {conversation.preview && (
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
            {conversation.preview}
          </p>
        )}
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          {formatDate(conversation.updatedAt)}
        </p>
      </div>

      {isHovered && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          onClick={handleDelete}
          className="absolute top-3 right-3 p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          title="Delete conversation"
        >
          <Trash2 size={14} />
        </motion.button>
      )}
    </motion.div>
  );
};
