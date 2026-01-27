# Todo App with Conversational AI

This is a full-stack todo application with a conversational AI assistant that can help manage your todos using natural language.

## Features

- **Full-stack web application**: Backend API with FastAPI and frontend with Next.js
- **Todo management**: Create, read, update, delete, and toggle completion status of todos
- **Conversational AI**: Natural language processing for todo management through the chat interface
- **Authentication**: Secure user authentication and authorization
- **Responsive design**: Works on desktop and mobile devices

## Tech Stack

- **Backend**: FastAPI, SQLModel, PostgreSQL (Neon), OpenRouter AI
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Authentication**: Better Auth
- **AI Integration**: OpenRouter with Gemini 2.5 Flash model
- **Database**: PostgreSQL (via Neon)

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- pip
- npm

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo-app-cli
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up environment variables**

   Copy the example environment files:
   ```bash
   # In the backend directory
   cp .env.example .env
   ```

   Update the `.env` file with your actual configuration:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: Generate with `openssl rand -base64 32`
   - `OPENROUTER_API_KEY`: Your OpenRouter API key for AI functionality

5. **Return to the root directory**
   ```bash
   cd ..
   ```

## Running the Application

### Method 1: Using the startup script (recommended)

Run the provided startup script:

**On Windows with PowerShell:**
```bash
.\start-servers.ps1
```

**On Windows with Command Prompt:**
```bash
start-servers.bat
```

### Method 2: Manual startup

1. **Start the backend server** (in a new terminal):
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --port 8000
   ```

2. **Start the frontend server** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health check**: http://localhost:8000/health
- **Chat interface**: http://localhost:3000/chat

## Using the Chat Agent

1. Navigate to the chat interface at http://localhost:3000/chat
2. Sign in to authenticate
3. Start chatting with the AI assistant using natural language:
   - "Add a todo to buy groceries"
   - "Show me my todos"
   - "Mark the first todo as complete"
   - "Delete the todo about buying milk"

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/signout` - User logout

### Todos
- `GET /todos` - Get all todos for the authenticated user
- `POST /todos` - Create a new todo
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Update a todo
- `PATCH /todos/{id}/toggle` - Toggle completion status
- `DELETE /todos/{id}` - Delete a todo

### Chat
- `POST /chat` - Send a message to the AI assistant
- `GET /conversations` - Get conversation history

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for authentication
- `FRONTEND_URL`: URL of the frontend for CORS (default: http://localhost:3000)
- `OPENROUTER_API_KEY`: API key for OpenRouter AI service

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `BETTER_AUTH_URL`: Backend URL for auth (default: http://localhost:8000)

## Troubleshooting

- If the backend doesn't start, ensure your database connection is correct
- If the frontend doesn't connect to the backend, check that both are running and the API URL is correct
- If the chat agent doesn't work, verify that your OpenRouter API key is valid and properly configured
- For authentication issues, ensure the BETTER_AUTH_SECRET is properly set and consistent
- If you see "An error occurred while processing your request" in the chat, check:
  - That your OPENROUTER_API_KEY is correctly set in the backend .env file
  - That the database is accessible and properly configured
  - That the MCP server is running and accessible
  - Check the backend logs for detailed error messages

## Development

For development, both servers run in watch mode with hot reloading enabled. Changes to the code will automatically restart the servers.