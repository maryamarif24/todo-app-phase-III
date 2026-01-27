# Implementation Plan: Phase III - Conversational AI Todo Management

**Branch**: `003-phase-iii-conversational-ai-todos` | **Date**: 2026-01-06 | **Spec**: [link](specs/003-phase-iii-conversational-ai-todos/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a conversational AI interface that allows users to manage todos using natural language. The system uses OpenAI Agents SDK to process natural language input, MCP server to expose todo operations as tools, and maintains stateless architecture with database persistence for conversation context.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK, Neon DB
**Storage**: PostgreSQL (Neon DB)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web
**Performance Goals**: 90% of user queries result in successful AI responses within 5 seconds
**Constraints**: <200ms p95 for database operations, <5s response time for AI processing, stateless services with database persistence
**Scale/Scope**: 10k users, 1M todos, 100k conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Spec Compliance**: ✅ All requirements derived from approved Phase III specification
**Technology Compliance**: ✅ All technologies (OpenAI Agents SDK, MCP) are approved for Phase III per constitution
**Architecture Compliance**: ✅ MCP tools are stateless and rely on database persistence per quality principles
**Agent Compliance**: ✅ AI agents only interact via MCP tools (no direct database access) per constitution
**Phase Compliance**: ✅ No features from future phases (IV/V) are included
**Statelessness**: ✅ Services are stateless with database persistence as required

## Project Structure

### Documentation (this feature)

```text
specs/003-phase-iii-conversational-ai-todos/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── todo.py          # Todo entity model
│   │   ├── conversation.py  # Conversation entity model
│   │   └── message.py       # Message entity model
│   ├── services/
│   │   ├── todo_service.py     # Todo business logic
│   │   ├── conversation_service.py  # Conversation management
│   │   └── mcp_tools.py      # MCP tool implementations
│   ├── agents/
│   │   └── todo_agent.py     # OpenAI agent implementation
│   ├── api/
│   │   └── chat_api.py       # Chat endpoint
│   └── main.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

**Structure Decision**: Web application structure with backend API containing models, services, agents, and API layers with proper separation of concerns.

## AI & Agent Plan

### Agent Responsibilities
1. **Natural Language Processing**: The OpenAI agent will parse user input to identify intent (create, read, update, delete, complete)
2. **Tool Selection**: Based on intent, the agent will select appropriate MCP tools
3. **Tool Invocation**: Execute selected tools with proper parameters
4. **Response Generation**: Format tool results into natural language responses

### Natural Language Processing
- Use OpenAI Agents SDK to create an agent with instructions for understanding todo-related commands
- Agent will be trained with examples of various ways to express todo operations
- Intent classification: create_todo, view_todos, update_todo, delete_todo, complete_todo

### Tool Selection & Invocation
- Define MCP tools for each todo operation (create, read, update, delete, mark complete)
- Agent will call appropriate tools based on identified intent
- Tools will return structured data that the agent uses to craft responses

### Agent Lifecycle
- Agent is instantiated per user request
- Agent processes the user's message
- Agent calls MCP tools as needed
- Agent returns response to the chat API
- Agent is destroyed after response is generated

## MCP Server Plan

### MCP Server Responsibilities
1. **Tool Registration**: Register todo operation tools with the MCP server
2. **Tool Execution**: Execute tools when called by the AI agent
3. **Database Interface**: Handle all database interactions through service layer
4. **Error Handling**: Propagate errors back to the agent with appropriate detail

### Stateless MCP Tools
- **create_todo_tool**: Takes todo text, creates new todo in database
- **view_todos_tool**: Returns list of user's todos based on filters
- **update_todo_tool**: Updates todo text or properties
- **delete_todo_tool**: Removes todo from database
- **complete_todo_tool**: Updates todo completion status
- All tools are stateless and persist data through database operations only

### Database Interaction
- MCP tools call backend services to interact with database
- Services use SQLModel to interact with Neon DB
- All state changes are persisted to database immediately
- No in-memory state is maintained in MCP tools

### Error Propagation
- MCP tools catch database errors and format them appropriately
- Errors are returned to the agent with sufficient context
- Agent uses error information to generate user-friendly error responses

## Chat API Plan

### Stateless Chat Endpoint
- **Endpoint**: `POST /api/chat`
- **Authentication**: Uses Phase II authentication (Better Auth) via middleware
- **Request**: User message text
- **Response**: AI-generated response with updated conversation context

### Conversation Context Management
- Retrieve user's conversation history from database
- Pass conversation context to the agent
- Persist new messages to database after response is generated
- Maintain conversation state through database only

### Authentication Enforcement
- All chat endpoints require valid authentication token
- Uses same authentication scheme as Phase II
- Unauthorized requests return 401 status code

### Request/Response Lifecycle
1. Request received at `/api/chat`
2. Authentication validated
3. User's conversation context retrieved from database
4. OpenAI agent instantiated with conversation context
5. Agent processes user message and calls MCP tools
6. Agent generates response
7. New message pair (user + AI) stored in database
8. Response returned to client

## Data Plan

### Conversation Data Model
- **Conversation**:
  - id: UUID (primary key)
  - user_id: UUID (foreign key to users table from Phase II)
  - created_at: DateTime
  - updated_at: DateTime
  - metadata: JSON (for future extensibility)

### Message Data Model
- **Message**:
  - id: UUID (primary key)
  - conversation_id: UUID (foreign key to conversation)
  - role: String (either "user" or "assistant")
  - content: Text (the message content)
  - timestamp: DateTime
  - metadata: JSON (for future extensibility)

### Todo Data Model (extends Phase II model)
- **Todo** (reuses existing model from Phase II with possible extensions):
  - id: UUID (primary key)
  - user_id: UUID (foreign key to users table from Phase II)
  - content: Text (todo description)
  - completed: Boolean (completion status)
  - created_at: DateTime
  - updated_at: DateTime
  - completed_at: DateTime (nullable)

### Relationship Model
- Users have many conversations (one-to-many)
- Conversations have many messages (one-to-many)
- Users have many todos (one-to-many)
- All relationships are managed through foreign keys

### Persistence Strategy
- All data persisted in Neon DB (PostgreSQL)
- SQLModel used for ORM operations
- Database transactions ensure data consistency
- Proper indexing for efficient retrieval of conversation history

## Integration Plan

### Chat API ↔ Agent Interaction
- Chat API instantiates OpenAI agent with user's conversation context
- API passes user message to agent for processing
- Agent returns AI-generated response to API
- API persists conversation to database and returns response to client

### Agent ↔ MCP Tool Interaction
- Agent identifies user intent from natural language input
- Agent calls appropriate MCP tools with required parameters
- Tools execute database operations and return results
- Agent uses results to generate natural language response

### MCP ↔ Database Interaction
- MCP tools call backend services to perform database operations
- Services use SQLModel to interact with Neon DB
- All data changes are persisted to database immediately
- Errors are propagated back through the chain to the agent

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple new technologies (OpenAI Agents SDK, MCP) | Required for conversational AI functionality | No simpler alternative meets the natural language processing requirement |