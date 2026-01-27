"""
MCP Server initialization using Official SDK.

This module initializes the MCP server to expose todo operations as tools.
"""
import os
from typing import Dict, Any, Callable
from .mcp_tools import MCPTools


class MCPServer:
    """
    MCP Server that registers and manages tools for the AI agent.
    """

    def __init__(self):
        """
        Initialize the MCP Server.
        """
        self.tools = {}
        self.mcp_tools = MCPTools()
        self._register_tools()

    def _register_tools(self):
        """
        Register all available tools with the MCP server.
        """
        # Register create todo tool
        self.tools["create_todo"] = self.mcp_tools.create_todo_tool

        # Register retrieve todos tool
        self.tools["retrieve_todos"] = self.mcp_tools.retrieve_todos_tool

        # Register update todo tool
        self.tools["update_todo"] = self.mcp_tools.update_todo_tool

        # Register delete todo tool
        self.tools["delete_todo"] = self.mcp_tools.delete_todo_tool

        # Register toggle completion tool
        self.tools["toggle_completion"] = self.mcp_tools.toggle_completion_tool

        # Register get todos by title tool (for natural language processing)
        self.tools["get_todos_by_title"] = self.mcp_tools.get_todos_by_title_tool

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool

        Returns:
            Result from the tool execution
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        try:
            tool = self.tools[tool_name]
            result = tool(**kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_available_tools(self) -> list:
        """
        Get a list of all available tool names.

        Returns:
            List of available tool names
        """
        return list(self.tools.keys())


# Initialize the MCP server
def get_mcp_server() -> MCPServer:
    """
    Get the singleton instance of the MCP server.

    Returns:
        MCPServer instance
    """
    if not hasattr(get_mcp_server, '_instance'):
        get_mcp_server._instance = MCPServer()
    return get_mcp_server._instance