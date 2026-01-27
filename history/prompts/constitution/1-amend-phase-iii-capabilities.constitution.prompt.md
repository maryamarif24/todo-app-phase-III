---
id: 1
title: "Amend Phase III Capabilities"
stage: constitution
date_iso: "2026-01-06"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "002-phase-ii-web-todo"
user: "user"
command: "sp.constitution"
labels: ["constitution", "phase-iii", "mcp", "ai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .specify/memory/constitution.md
tests_yaml: |
  - none
---

# Constitution Amendment: Enable Phase III MCP and AI Capabilities

## Original Prompt

Amend the global constitution to enable Phase III capabilities as follows:

Phase III:
- AI Logic: OpenAI Agents SDK
- Conversational Interface: Stateless chat API
- Tooling: Model Context Protocol (MCP)
- MCP Server: Official MCP SDK
- Architecture: Agent-driven task management
- State Management: Persist conversation and task state in database
- MCP tools must be stateless and rely on database persistence

Rules:
- AI agents may ONLY interact with the system via MCP tools
- MCP tools must not store in-memory state
- Conversation context must be persisted and retrievable
- Phase II authentication, frontend, and database remain unchanged
- No autonomous background agents
- No multi-agent orchestration beyond documented scope

This amendment authorizes AI and MCP usage starting Phase III only.

## Response Summary

The constitution has been successfully updated to version 2.2.0, enabling MCP and AI capabilities starting in Phase III instead of Phase IV. Key changes include:

1. Updated Phase Technology Matrix to move OpenAI Agents SDK and MCP from Phase IV to Phase III
2. Added new Quality Principles requiring stateless MCP tools and database persistence
3. Updated Phase III definition to include AI and MCP capabilities
4. Added new "AI Agent Role" section in Development Workflow
5. Enhanced Compliance Review section to validate MCP statelessness
6. Updated prohibited technologies to include direct database access by AI agents
7. Added architectural patterns for agent-driven task management and database-backed state

## Outcome

The constitution now properly authorizes AI and MCP usage starting in Phase III, with clear requirements that:
- AI agents may ONLY interact with the system via MCP tools
- MCP tools must not store in-memory state
- All state must be persisted in the database
- Phase II technologies remain unchanged