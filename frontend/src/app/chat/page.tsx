'use client';

import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/components/auth/auth-provider';
import type { User } from '@/types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  messages: Message[];
}

export default function ChatPage() {
  const { user, isAuthenticated } = useAuth();
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Initialize a new conversation when user authenticates
  useEffect(() => {
    if (isAuthenticated && user) {
      createNewConversation();
    }
  }, [isAuthenticated, user]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: '', // Empty ID initially - will be set when first message is sent
      messages: [],
    };
    setConversations(prev => [...prev, newConversation]);
    setCurrentConversationId(newConversation.id);
  };

  const getCurrentConversation = () => {
    // Find conversation by ID, or if ID is empty, get the conversation with empty ID
    return conversations.find(conv =>
      conv.id === currentConversationId ||
      (currentConversationId === '' && conv.id === '')
    );
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    // Add user message to current conversation
    setConversations(prev =>
      prev.map(conv =>
        conv.id === currentConversationId
          ? { ...conv, messages: [...conv.messages, userMessage] }
          : conv
      )
    );

    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      // Send message to backend API
      const response = await api.post<{
        response: string;
        conversation_id: string;
        timestamp: string;
      }>('/chat/chat', {
        message: inputValue,
        conversation_id: currentConversationId || undefined,
      });

      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        const aiMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: response.data.response,
          timestamp: response.data.timestamp,
        };

        // Update conversation with AI response
        setConversations(prev =>
          prev.map(conv =>
            conv.id === response.data!.conversation_id
              ? { ...conv, messages: [...conv.messages, aiMessage] }
              : conv
          )
        );

        // Update conversation ID if it's new
        if (response.data.conversation_id !== currentConversationId) {
          setCurrentConversationId(response.data.conversation_id);

          // Update the conversation ID in the conversations array
          setConversations(prev =>
            prev.map(conv =>
              conv.id === '' || conv.id === currentConversationId
                ? { ...conv, id: response.data!.conversation_id }
                : conv
            )
          );
        }
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const currentConv = getCurrentConversation();

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold mb-4" style={{ color: '#7F1734' }}>Chat Requires Authentication</h2>
          <p className="mb-6 text-gray-600">Please sign in to use the chat feature.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div
          className="p-6 border-b"
          style={{
            background: 'linear-gradient(135deg, #7F1734 0%, #C44569 100%)',
            color: 'white'
          }}
        >
          <h1 className="text-2xl font-bold">Todo Assistant</h1>
          <p className="opacity-90">Ask me anything about your todos!</p>
        </div>

        {/* Messages Container */}
        <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
          {currentConv && currentConv.messages.length > 0 ? (
            currentConv.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-black text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div
                    className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-gray-300' : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <div className="text-5xl mb-4">💬</div>
                <h3 className="text-lg font-medium">Start a conversation</h3>
                <p className="mt-1">Ask me to help you manage your todos!</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t p-4 bg-gray-50">
          {error && (
            <div className="mb-3 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your todos..."
              className="flex-1 border border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 resize-none"
              style={{
                minHeight: '60px',
                maxHeight: '120px',
                '--tw-ring-color': '#7F1734'
              } as React.CSSProperties}
              disabled={isLoading}
              rows={1}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-3 bg-black text-white rounded-2xl hover:bg-gray-800 disabled:opacity-50 transition"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            Ask me to add, complete, or manage your todos
          </div>
        </div>
      </div>
    </div>
  );
}