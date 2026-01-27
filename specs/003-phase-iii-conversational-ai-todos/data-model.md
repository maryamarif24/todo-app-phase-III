# Data Model: Phase III - Conversational AI Todo Management

## Entity: Conversation
**Description**: Represents a user's conversation with the AI, including message history and context

**Fields**:
- id: UUID (Primary Key) - Unique identifier for the conversation
- user_id: UUID (Foreign Key) - Links to the user who owns this conversation
- created_at: DateTime - Timestamp when conversation was created
- updated_at: DateTime - Timestamp when conversation was last updated
- metadata: JSON (Optional) - Additional data for future extensibility

**Relationships**:
- One-to-Many with Message entity (one conversation has many messages)
- Many-to-One with User entity from Phase II (many conversations belong to one user)

**Validation Rules**:
- user_id must reference an existing user
- created_at and updated_at must be valid timestamps
- metadata must be valid JSON if provided

## Entity: Message
**Description**: An individual message in a conversation, either from the user or the AI response

**Fields**:
- id: UUID (Primary Key) - Unique identifier for the message
- conversation_id: UUID (Foreign Key) - Links to the conversation this message belongs to
- role: String (Enum: "user" or "assistant") - Indicates whether message is from user or AI
- content: Text - The actual content of the message
- timestamp: DateTime - When the message was created
- metadata: JSON (Optional) - Additional data for future extensibility

**Relationships**:
- Many-to-One with Conversation entity (many messages belong to one conversation)
- One-to-Many with Message entity for conversation thread (messages in chronological order)

**Validation Rules**:
- conversation_id must reference an existing conversation
- role must be either "user" or "assistant"
- content must not be empty
- timestamp must be valid

## Entity: Todo (Extended from Phase II)
**Description**: Represents a task item with text content, completion status, and timestamps

**Fields**:
- id: UUID (Primary Key) - Unique identifier for the todo
- user_id: UUID (Foreign Key) - Links to the user who owns this todo
- content: Text - Description of the todo item
- completed: Boolean - Whether the todo is completed or not
- created_at: DateTime - When the todo was created
- updated_at: DateTime - When the todo was last updated
- completed_at: DateTime (Optional) - When the todo was marked as completed

**Relationships**:
- Many-to-One with User entity from Phase II (many todos belong to one user)

**Validation Rules**:
- user_id must reference an existing user
- content must not be empty
- completed must be a boolean value
- If completed is true, completed_at should be set to current timestamp

## State Transitions

### Todo State Transitions:
- **Created**: When a new todo is added (completed = false, completed_at = null)
- **Completed**: When a todo is marked as complete (completed = true, completed_at = timestamp)
- **Reopened**: When a completed todo is marked as incomplete (completed = false, completed_at = null)

### Conversation State Transitions:
- **Started**: When a new conversation is created (new Conversation record)
- **Active**: When messages are added to the conversation (updated_at is updated)
- **Inactive**: When no new messages are added for a period (no explicit state change, determined by timestamp)

## Database Schema Relationships

```
Users (Phase II)
  ||
  \\ (One-to-Many)
    \\
     \\
Conversation
  ||
  \\ (One-to-Many)
    \\
     \\
Message

Users (Phase II)
  ||
  \\ (One-to-Many)
    \\
     \\
Todo
```

The data model maintains the existing user relationships from Phase II while adding new entities for conversation management. All new entities follow the same patterns and conventions established in Phase II.