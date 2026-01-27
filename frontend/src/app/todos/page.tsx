'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { Todo, TodoListResponse, CreateTodoResponse } from '@/types';
import { useAuth } from '@/components/auth/auth-provider';


export default function TodosPage() {
  const { user, session } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    setLoading(true);
    const response = await api.get<TodoListResponse>('/todos');

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setTodos(response.data.todos);
    }

    setLoading(false);
  };

  const handleToggle = async (todoId: string) => {
    const response = await api.patch<Todo>(`/todos/${todoId}/toggle`);

    if (response.data) {
      setTodos(todos.map(t => t.id === todoId ? response.data! : t));
    }
  };

  const handleDelete = async (todoId: string) => {
    if (!confirm('Are you sure you want to delete this todo?')) return;

    const response = await api.delete<{ message: string }>(`/todos/${todoId}`);

    if (!response.error) {
      setTodos(todos.filter(t => t.id !== todoId));
    }
  };

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;

    // Check if user is authenticated before attempting to add todo
    if (!session?.token) {
      setError('You must be logged in to add a todo. Please sign in.');
      return;
    }

    setIsAdding(true);
    const request = {
      title: newTodoTitle.trim(),
      description: newTodoDescription.trim() || undefined,
    };

    const response = await api.post<CreateTodoResponse>('/todos', request);

    if (response.error) {
      setError(response.error);
      setIsAdding(false);
      console.error('Failed to add todo:', response.error); // Debug log
      // Additional debugging information
      console.error('Request payload:', request);
      return;
    }

    setNewTodoTitle('');
    setNewTodoDescription('');
    setIsAdding(false);
    fetchTodos();
  };

  const pendingTodos = todos.filter(todo => !todo.is_complete);
  const completedTodos = todos.filter(todo => todo.is_complete);

  // Calculate progress percentage
  const totalTodos = todos.length;
  const progressPercentage = totalTodos > 0
    ? Math.round((completedTodos.length / totalTodos) * 100)
    : 0;

  if (loading) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Loading todos...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold" style={{ color: 'rgb(127, 23, 52)' }}>Your Todos</h2>
        <Link
          href="/chat"
          className="px-4 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition"
        >
          Chat with AI
        </Link>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Progress and Add Todo Sections */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Progress Section */}
        <div
          className="rounded-3xl p-6 relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, #FF6B9D 0%, #C44569 50%, #7F1734 100%)'
          }}
        >
          {/* Subtle abstract geometric pattern */}
          <div className="absolute inset-0 opacity-5 pointer-events-none">
            <div className="absolute top-4 right-4 w-32 h-32 rounded-full" style={{ background: 'white' }} />
            <div className="absolute bottom-4 left-4 w-24 h-24 rounded-full" style={{ background: 'white' }} />
            <div className="absolute top-1/2 right-1/4 w-16 h-16 rotate-45" style={{ background: 'white' }} />
          </div>

          <div className="relative z-10">
            <div className="flex justify-between items-center mb-3">
              <span className="text-lg font-semibold text-white">Daily Progress</span>
              <span className="text-2xl font-bold text-white">
                {progressPercentage}%
              </span>
            </div>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-4">
              <div
                className="h-4 rounded-full transition-all duration-500 ease-out shadow-lg"
                style={{
                  width: `${progressPercentage}%`,
                  background: 'linear-gradient(90deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)'
                }}
              />
            </div>
            <div className="flex justify-between mt-3 text-sm text-white text-opacity-90">
              <span>{completedTodos.length} completed</span>
              <span>{pendingTodos.length} pending</span>
            </div>
          </div>
        </div>

        {/* Add Todo Section */}
        <div className="bg-white rounded-3xl shadow-lg p-6 relative overflow-hidden">
          {/* Subtle abstract geometric pattern */}
          <div className="absolute inset-0 opacity-5 pointer-events-none">
            <div className="absolute top-4 left-4 w-20 h-20 rounded-full" style={{ background: 'rgb(255, 182, 193)' }} />
            <div className="absolute bottom-4 right-4 w-16 h-16 rounded-full" style={{ background: 'rgb(255, 107, 157)' }} />
            <div className="absolute top-1/2 left-1/4 w-12 h-12 rotate-45" style={{ background: 'rgb(196, 69, 105)' }} />
          </div>

          <div className="relative z-10">
            <h3 className="text-lg font-semibold mb-4 text-black">Add New Todo</h3>
            <form onSubmit={handleAddTodo} className="flex flex-col gap-4">
              <input
                type="text"
                value={newTodoTitle}
                onChange={(e) => setNewTodoTitle(e.target.value)}
                placeholder="What needs to be done?"
                className="w-full px-3 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 text-black"
                style={{ '--tw-ring-color': 'rgb(127, 23, 52)' } as React.CSSProperties}
                maxLength={200}
              />
              <textarea
                value={newTodoDescription}
                onChange={(e) => setNewTodoDescription(e.target.value)}
                placeholder="Add more details... (optional)"
                className="w-full px-3 py-2 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 h-20 text-black"
                style={{ '--tw-ring-color': 'rgb(127, 23, 52)' } as React.CSSProperties}
                maxLength={2000}
              />
              <button
                type="submit"
                disabled={isAdding || !newTodoTitle.trim()}
                className="px-6 py-2 text-white rounded-full hover:opacity-90 disabled:opacity-50 transition self-start"
                style={{ backgroundColor: 'black' }}
              >
                {isAdding ? 'Adding...' : 'Add Todo'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Pending and Completed Sections */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Pending Section */}
        <div className="bg-white rounded-3xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4 pb-2 border-b text-black">
            Pending ({pendingTodos.length})
          </h3>

          {pendingTodos.length === 0 ? (
            <p className="text-gray-600 text-center py-8">No pending todos</p>
          ) : (
            <div className="space-y-3">
              {pendingTodos.map((todo) => (
                <div
                  key={todo.id}
                  className="bg-gray-50 rounded-2xl shadow p-4 flex items-center gap-4"
                >
                  <input
                    type="checkbox"
                    checked={todo.is_complete}
                    onChange={() => handleToggle(todo.id)}
                    className="w-5 h-5"
                    style={{ accentColor: 'black' }}
                  />
                  <div className="flex-1">
                    <h3 className="font-medium text-black">{todo.title}</h3>
                    {todo.description && (
                      <p className="text-sm text-gray-700 mt-1">{todo.description}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-2">
                      Created: {mounted ? new Date(todo.created_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link
                      href={`/todos/${todo.id}`}
                      className="px-3 py-1 text-sm rounded-full text-gray-500 hover:text-green-500 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                        <path d="m15 5 4 4" />
                      </svg>
                    </Link>
                    <button
                      onClick={() => handleDelete(todo.id)}
                      className="px-3 py-1 text-sm rounded-full text-gray-500 hover:text-red-500 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 6h18" />
                        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Completed Section */}
        <div className="bg-white rounded-3xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4 pb-2 border-b text-black">
            Completed ({completedTodos.length})
          </h3>

          {completedTodos.length === 0 ? (
            <p className="text-gray-600 text-center py-8">No completed todos yet</p>
          ) : (
            <div className="space-y-3">
              {completedTodos.map((todo) => (
                <div
                  key={todo.id}
                  className="bg-gray-50 rounded-2xl shadow p-4 flex items-center gap-4"
                >
                  <input
                    type="checkbox"
                    checked={todo.is_complete}
                    onChange={() => handleToggle(todo.id)}
                    className="w-5 h-5"
                    style={{ accentColor: 'black' }}
                  />
                  <div className="flex-1">
                    <h3 className="font-medium line-through text-gray-500">{todo.title}</h3>
                    {todo.description && (
                      <p className="text-sm text-gray-500 mt-1 line-through">{todo.description}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-2">
                      Created: {mounted ? new Date(todo.created_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link
                      href={`/todos/${todo.id}`}
                      className="px-3 py-1 text-sm rounded-full text-gray-500 hover:text-green-500 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                        <path d="m15 5 4 4" />
                      </svg>
                    </Link>
                    <button
                      onClick={() => handleDelete(todo.id)}
                      className="px-3 py-1 text-sm rounded-full text-gray-500 hover:text-red-500 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 6h18" />
                        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
