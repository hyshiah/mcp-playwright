"""
Playwright MCP Server - 入口点

运行 Playwright MCP 服务器
"""

from mcp_playwright.server import mcp

if __name__ == "__main__":
    mcp.run()
