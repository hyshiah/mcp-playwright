"""
Playwright MCP Server - 基于FastMCP框架的专业级浏览器自动化服务

为LLM应用提供强大的网页交互和数据提取能力
"""

__version__ = "0.1.0"
__author__ = "ma-pony"
__description__ = "基于Playwright的模型上下文协议(MCP)服务器，为AI助手提供强大的浏览器自动化能力"

from .server import mcp

__all__ = ["mcp", "__version__"]
