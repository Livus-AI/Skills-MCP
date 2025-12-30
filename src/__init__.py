"""
Workflows MCP Server

A Model Context Protocol server for creating and executing Python workflow scripts.
"""

from .server import mcp, main

__version__ = "0.1.0"
__all__ = ["mcp", "main"]
