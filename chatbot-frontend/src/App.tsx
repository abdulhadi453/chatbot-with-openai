import { useChatStore } from './hooks/useChatStore';
import { Sidebar } from './components/layout/Sidebar';
import { ChatArea } from './components/layout/ChatArea';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const {
    conversations,
    activeConversation,
    isLoading,
    error,
    createConversation,
    sendMessage,
    deleteConversation,
    setActiveConversation,
  } = useChatStore();

  const handleNewConversation = async () => {
    await createConversation();
  };

  const handleSendMessage = async (content: string) => {
    if (!activeConversation) {
      const newConv = await createConversation();
      if (newConv) {
        await sendMessage(content);
      }
    } else {
      await sendMessage(content);
    }
  };

  if (isLoading && conversations.length === 0) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading conversations...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50 dark:bg-gray-950">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversation?.id ?? null}
        onConversationSelect={setActiveConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={deleteConversation}
        isLoading={isLoading}
      />

      <ChatArea
        conversation={activeConversation}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
          >
            <p className="font-medium">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
