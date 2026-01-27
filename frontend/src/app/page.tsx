import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8" style={{ color: '#7F1734' }}>Welcome to Todo App</h1>
      <p className="mb-8 text-lg" style={{ color: '#7F1734' }}>
        A full-stack web application for managing your todos
      </p>
      <div className="flex gap-4">
        <Link
          href="/signin"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Sign In
        </Link>
        <Link
          href="/signup"
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          Sign Up
        </Link>
      </div>
      <div className="mt-8">
        <Link
          href="/chat"
          className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
        >
          Chat with AI Assistant
        </Link>
      </div>
    </main>
  );
}
