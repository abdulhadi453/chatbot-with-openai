import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Menu, X } from 'lucide-react';
import type { Conversation } from '../../types';
import { ConversationItem } from './ConversationItem';
import { Button } from '../common/Button';
import { useState } from 'react';

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onConversationSelect: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  isLoading?: boolean;
}

export const Sidebar = ({
  conversations,
  activeConversationId,
  onConversationSelect,
  onNewConversation,
  onDeleteConversation,
  isLoading,
}: SidebarProps) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Conversations
          </h2>
          <button
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X size={20} />
          </button>
        </div>
        <Button
          onClick={onNewConversation}
          variant="primary"
          size="md"
          className="w-full"
          disabled={isLoading}
        >
          <Plus size={20} className="mr-2" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-2">
        <AnimatePresence>
          {conversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === activeConversationId}
              onClick={() => {
                onConversationSelect(conversation.id);
                setIsMobileOpen(false);
              }}
              onDelete={onDeleteConversation}
            />
          ))}
        </AnimatePresence>

        {conversations.length === 0 && !isLoading && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
            No conversations yet.
            <br />
            Start a new chat to begin!
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          <p className="font-medium">AI Chatbot</p>
          <p className="mt-1">Powered by React + TypeScript</p>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-40 p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <Menu size={24} className="text-gray-700 dark:text-gray-300" />
      </button>

      {/* Desktop sidebar */}
      <aside className="hidden lg:block w-80 h-full">{sidebarContent}</aside>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/50 z-40"
            />
            <motion.aside
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="lg:hidden fixed left-0 top-0 bottom-0 w-80 z-50"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
