# Phase III: Conversational AI Todo Management

## Overview
Phase III introduces a conversational AI interface that allows users to manage todos using natural language. The system uses OpenAI Agents SDK to process natural language input, MCP server to expose todo operations as tools, and maintains stateless architecture with database persistence for conversation context.

## Architecture
- **AI Agent**: OpenAI Agent processes natural language and calls appropriate tools
- **MCP Server**: Model Context Protocol server exposes todo operations as callable tools
- **Stateless Services**: All state persisted in database only
- **Chat API**: Stateless endpoint for user interaction

## Features
1. Create Todo via Natural Language
2. View Todos via Natural Language
3. Update and Complete Todos via Natural Language
4. Delete Todos via Natural Language
5. Multi-turn Conversations

## API Endpoints
- `POST /api/chat` - Send natural language message and receive AI response

## Environment Variables
- `OPENAI_API_KEY` - API key for OpenAI services
- `DATABASE_URL` - Database connection string
- `MCP_SERVER_URL` - MCP server URL (if external)

## MCP Tools
- `create_todo` - Create a new todo
- `retrieve_todos` - Retrieve user's todos
- `update_todo` - Update an existing todo
- `delete_todo` - Delete a todo
- `toggle_completion` - Toggle a todo's completion status
- `get_todos_by_title` - Find todos by title

## Data Models
- **Conversation**: Represents a user's conversation with the AI
- **Message**: Individual messages within a conversation
- **Todo**: Extended from Phase II with additional fields

## Implementation Details
- All MCP tools are stateless and persist data via database operations only
- AI agents only interact with the system via MCP tools (no direct database access)
- Conversation context is maintained through database persistence
- Authentication is enforced using Phase II's Better Auth system