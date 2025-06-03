#!/usr/bin/env python3
"""
Playwright MCP Server 测试套件
"""

import pytest
import asyncio
import json
from mcp_playwright.server import mcp, _browser, _page


class TestPlaywrightMCPServer:
    """Playwright MCP服务器测试类"""

    @pytest.mark.asyncio
    async def test_launch_browser(self):
        """测试启动浏览器功能"""
        # 测试启动Chromium浏览器
        result = await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True,
            "viewport_width": 1280,
            "viewport_height": 720
        })

        assert "成功启动" in result
        assert "chromium" in result

        # 清理
        await mcp.call_tool("close_browser", {})

    @pytest.mark.asyncio
    async def test_navigate_to_url(self):
        """测试页面导航功能"""
        # 首先启动浏览器
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        # 导航到测试页面
        result = await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        assert "成功导航到" in result
        assert "example.com" in result

        # 清理
        await mcp.call_tool("close_browser", {})

    @pytest.mark.asyncio
    async def test_get_page_info(self):
        """测试获取页面信息功能"""
        # 启动浏览器并导航
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        # 获取页面标题
        title = await mcp.call_tool("get_page_title", {})
        assert isinstance(title, str)
        assert len(title) > 0

        # 获取页面URL
        url = await mcp.call_tool("get_page_url", {})
        assert "example.com" in url

        # 清理
        await mcp.call_tool("close_browser", {})

    @pytest.mark.asyncio
    async def test_execute_javascript(self):
        """测试JavaScript执行功能"""
        # 启动浏览器并导航
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        # 执行JavaScript
        result = await mcp.call_tool("execute_javascript", {
            "code": "return {title: document.title, url: window.location.href}"
        })

        # 解析结果
        data = json.loads(result)
        assert "title" in data
        assert "url" in data
        assert "example.com" in data["url"]

        # 清理
        await mcp.call_tool("close_browser", {})

    @pytest.mark.asyncio
    async def test_take_screenshot(self):
        """测试截图功能"""
        # 启动浏览器并导航
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        # 截图并保存到临时文件
        result = await mcp.call_tool("take_screenshot", {
            "path": "/tmp/test_screenshot.png",
            "full_page": True
        })

        assert "截图已保存到" in result
        assert "/tmp/test_screenshot.png" in result

        # 清理
        await mcp.call_tool("close_browser", {})

    def test_browser_status_resource(self):
        """测试浏览器状态资源"""
        status = mcp.get_resource("browser://status")
        data = json.loads(status)

        assert "playwright_launched" in data
        assert "browser_launched" in data
        assert "context_created" in data
        assert "page_available" in data
        assert "status" in data

    def test_page_current_resource(self):
        """测试当前页面资源"""
        page_info = mcp.get_resource("page://current")
        data = json.loads(page_info)

        # 当浏览器未启动时应该返回错误信息
        assert "error" in data or "url" in data

    @pytest.mark.asyncio
    async def test_error_handling_without_browser(self):
        """测试未启动浏览器时的错误处理"""
        # 确保浏览器未启动
        await mcp.call_tool("close_browser", {})

        # 尝试导航应该返回错误
        result = await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        assert "错误：需要先启动浏览器" in result

        # 尝试点击元素应该返回错误
        result = await mcp.call_tool("click_element", {
            "selector": "button"
        })

        assert "错误：需要先启动浏览器" in result

    @pytest.mark.asyncio
    async def test_element_operations(self):
        """测试元素操作功能"""
        # 启动浏览器并导航到表单页面
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        await mcp.call_tool("navigate_to_url", {
            "url": "https://httpbin.org/forms/post"
        })

        # 等待页面加载
        await asyncio.sleep(2)

        # 测试填写输入框
        result = await mcp.call_tool("fill_input", {
            "selector": "input[name='custname']",
            "text": "测试用户"
        })

        assert "成功填写输入框" in result or "填写" in result

        # 测试获取文本内容
        result = await mcp.call_tool("get_text_content", {
            "selector": "h1"
        })

        # 应该能获取到页面标题
        assert isinstance(result, str)

        # 清理
        await mcp.call_tool("close_browser", {})

    @pytest.mark.asyncio
    async def test_wait_for_selector(self):
        """测试等待元素功能"""
        # 启动浏览器并导航
        await mcp.call_tool("launch_browser", {
            "browser_type": "chromium",
            "headless": True
        })

        await mcp.call_tool("navigate_to_url", {
            "url": "https://example.com"
        })

        # 等待body元素出现
        result = await mcp.call_tool("wait_for_selector", {
            "selector": "body",
            "timeout": 5000,
            "state": "visible"
        })

        assert "元素已出现" in result or "body" in result

        # 清理
        await mcp.call_tool("close_browser", {})


if __name__ == "__main__":
    """运行测试"""
    pytest.main([__file__, "-v"])
