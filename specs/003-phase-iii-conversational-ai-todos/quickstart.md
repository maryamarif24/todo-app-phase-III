# Quickstart Guide: Phase III - Conversational AI Todo Management

## Overview
This guide explains how to set up and use the conversational AI todo management system. The system allows users to manage their todos using natural language through an AI-powered chat interface.

## Prerequisites
- Python 3.11+
- Access to OpenAI API
- Access to MCP server
- Phase II authentication system (Better Auth) already configured
- Neon DB connection

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Update the following variables in .env:
OPENAI_API_KEY=your_openai_api_key
MCP_SERVER_URL=your_mcp_server_url
DATABASE_URL=your_neon_db_connection_string
AUTH_JWT_SECRET=your_auth_secret_from_phase_ii
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlmodel openai python-multipart
```

### 3. Database Setup
```bash
# Run database migrations to create new tables
python -m backend.src.models.migrate
```

## Architecture Overview

### Components
1. **Chat API**: Stateless endpoint that handles user requests
2. **OpenAI Agent**: Processes natural language and calls tools
3. **MCP Server**: Exposes todo operations as callable tools
4. **Backend Services**: Handle business logic and database operations
5. **Database**: Stores todos, conversations, and messages

### Data Flow
```
User Message
      ↓
   Chat API
      ↓
  OpenAI Agent
      ↓
   MCP Tools
      ↓
 Backend Services
      ↓
   Database
```

## API Endpoints

### Chat Endpoint
```
POST /api/chat
Headers: Authorization: Bearer <auth_token>
Body: { "message": "Add buy groceries to my todos" }
Response: { "response": "I've added 'buy groceries' to your todos." }
```

## Natural Language Commands

The AI supports various ways to interact with your todos:

### Creating Todos
- "Add buy groceries to my todos"
- "I need to call mom tomorrow"
- "Create a todo to finish the report"

### Viewing Todos
- "Show me my todos"
- "What are my incomplete todos?"
- "List all my tasks"

### Updating Todos
- "Update my call mom todo to call mom and dad"
- "Change 'finish report' to 'finish quarterly report'"

### Completing Todos
- "Mark buy groceries as complete"
- "Complete the first todo"
- "Finish the shopping task"

### Deleting Todos
- "Delete buy groceries"
- "Remove the call mom todo"
- "Delete my shopping task"

## Conversation Context
The AI maintains context within a conversation, allowing for multi-turn interactions:
- "What do I have to do today?" → "Mark the first one as complete"
- "Show me my todos" → "Complete number 2"

## Error Handling
- If the AI cannot understand your request, it will ask for clarification
- If a tool operation fails, the AI will provide an appropriate error message
- Authentication failures will return a 401 status code

## Development
To run the service locally:
```bash
uvicorn backend.src.main:app --reload --port 8000
```

## Testing
Run the tests to verify functionality:
```bash
pytest tests/
```