"""
Playwright MCP Server - 基于FastMCP框架的重新实现

提供专业级的浏览器自动化MCP服务，具备完善的生命周期管理和错误处理
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

from mcp.server.fastmcp import FastMCP

from .core.browser_manager import BrowserManager
from .tools.browser_tools import BrowserTools

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastMCP服务器
mcp = FastMCP("Playwright MCP Server")

# 全局变量
browser_manager: BrowserManager = None
browser_tools: BrowserTools = None


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """服务器生命周期管理"""
    global browser_manager, browser_tools

    logger.info("🚀 启动 Playwright MCP 服务器...")

    try:
        # 初始化浏览器管理器
        browser_manager = BrowserManager(
            browser_type="chromium",
            headless=True,
            max_sessions=10,
            default_viewport={"width": 1280, "height": 720},
            default_timeout=30000
        )

        # 初始化浏览器工具
        browser_tools = BrowserTools(browser_manager)

        logger.info("✅ Playwright MCP 服务器启动完成")

        # 返回上下文数据
        yield {
            "browser_manager": browser_manager,
            "browser_tools": browser_tools
        }

    finally:
        # 清理资源
        logger.info("🔄 清理 Playwright MCP 服务器资源...")
        if browser_manager:
            await browser_manager.cleanup()
        logger.info("✅ Playwright MCP 服务器资源清理完成")


# 设置生命周期
mcp.lifespan = server_lifespan


# ==================== 浏览器控制工具 ====================

@mcp.tool()
async def create_browser_session(
    browser_type: str = "chromium",
    headless: bool = True,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    timeout: int = 30000
) -> str:
    """
    创建新的浏览器会话

    Args:
        browser_type: 浏览器类型 (chromium, firefox, webkit)
        headless: 是否无头模式
        viewport_width: 视口宽度
        viewport_height: 视口高度
        timeout: 默认超时时间(毫秒)
    """
    return await browser_tools.create_session(
        browser_type=browser_type,
        headless=headless,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        timeout=timeout
    )


@mcp.tool()
async def close_browser_session() -> str:
    """关闭当前浏览器会话"""
    return await browser_tools.close_session()


@mcp.tool()
async def navigate_to_url(
    url: str,
    wait_until: str = "domcontentloaded"
) -> str:
    """
    导航到指定URL

    Args:
        url: 目标URL
        wait_until: 等待条件 (load, domcontentloaded, networkidle)
    """
    return await browser_tools.navigate_to_url(url, wait_until)


# ==================== 页面交互工具 ====================

@mcp.tool()
async def click_element(
    selector: str,
    timeout: int = 30000,
    force: bool = False
) -> str:
    """
    点击页面元素

    Args:
        selector: CSS选择器或XPath
        timeout: 超时时间(毫秒)
        force: 强制点击
    """
    return await browser_tools.click_element(selector, timeout, force)


@mcp.tool()
async def fill_input(
    selector: str,
    text: str,
    timeout: int = 30000
) -> str:
    """
    填写输入框

    Args:
        selector: CSS选择器或XPath
        text: 要输入的文本
        timeout: 超时时间(毫秒)
    """
    return await browser_tools.fill_input(selector, text, timeout)


@mcp.tool()
async def wait_for_selector(
    selector: str,
    timeout: int = 30000,
    state: str = "visible"
) -> str:
    """
    等待元素出现

    Args:
        selector: CSS选择器或XPath
        timeout: 超时时间(毫秒)
        state: 元素状态 (attached, detached, visible, hidden)
    """
    return await browser_tools.wait_for_selector(selector, timeout, state)


# ==================== 数据提取工具 ====================

@mcp.tool()
async def get_text_content(
    selector: str,
    timeout: int = 30000
) -> str:
    """
    获取元素文本内容

    Args:
        selector: CSS选择器或XPath
        timeout: 超时时间(毫秒)
    """
    return await browser_tools.get_text_content(selector, timeout)


@mcp.tool()
async def get_element_attribute(
    selector: str,
    attribute: str,
    timeout: int = 30000
) -> str:
    """
    获取元素属性值

    Args:
        selector: CSS选择器或XPath
        attribute: 属性名
        timeout: 超时时间(毫秒)
    """
    return await browser_tools.get_element_attribute(selector, attribute, timeout)


@mcp.tool()
async def get_page_title() -> str:
    """获取页面标题"""
    return await browser_tools.get_page_title()


@mcp.tool()
async def get_page_url() -> str:
    """获取当前页面URL"""
    return await browser_tools.get_page_url()


# ==================== 高级功能工具 ====================

@mcp.tool()
async def take_screenshot(
    path: str = None,
    full_page: bool = False,
    quality: int = 80
) -> str:
    """
    截取页面截图

    Args:
        path: 保存路径(可选)
        full_page: 是否截取整页
        quality: 图片质量(1-100)
    """
    return await browser_tools.take_screenshot(path, full_page, quality)


@mcp.tool()
async def execute_javascript(code: str) -> str:
    """
    执行JavaScript代码

    Args:
        code: JavaScript代码
    """
    return await browser_tools.execute_javascript(code)


# ==================== 资源接口 ====================

@mcp.resource("session://status")
def get_session_status() -> str:
    """获取当前会话状态"""
    if not browser_tools:
        return json.dumps({
            "error": "服务器未初始化",
            "status": "not_initialized"
        }, ensure_ascii=False, indent=2)

    status = browser_tools.get_session_status()
    return json.dumps(status, ensure_ascii=False, indent=2)


@mcp.resource("browser://health")
def get_browser_health() -> str:
    """获取浏览器管理器健康状态"""
    if not browser_manager:
        return json.dumps({
            "error": "浏览器管理器未初始化",
            "status": "not_initialized"
        }, ensure_ascii=False, indent=2)

    # 由于FastMCP不支持异步资源，我们返回基本状态
    return json.dumps({
        "initialized": browser_manager.is_initialized,
        "session_count": browser_manager.session_count,
        "max_sessions": browser_manager.max_sessions,
        "status": "healthy" if browser_manager.is_initialized else "not_ready"
    }, ensure_ascii=False, indent=2)


@mcp.resource("help://tools")
def get_tools_help() -> str:
    """获取工具使用帮助"""
    help_info = {
        "浏览器控制": {
            "create_browser_session": "创建新的浏览器会话",
            "close_browser_session": "关闭当前浏览器会话",
            "navigate_to_url": "导航到指定URL"
        },
        "页面交互": {
            "click_element": "点击页面元素",
            "fill_input": "填写输入框",
            "wait_for_selector": "等待元素出现"
        },
        "数据提取": {
            "get_text_content": "获取元素文本内容",
            "get_element_attribute": "获取元素属性值",
            "get_page_title": "获取页面标题",
            "get_page_url": "获取当前页面URL"
        },
        "高级功能": {
            "take_screenshot": "截取页面截图",
            "execute_javascript": "执行JavaScript代码"
        }
    }

    return json.dumps(help_info, ensure_ascii=False, indent=2)


# ==================== 提示模板 ====================

@mcp.prompt()
def web_automation_prompt(task: str, url: str = "https://example.com") -> str:
    """
    网页自动化任务提示模板

    Args:
        task: 要执行的任务描述
        url: 目标网站URL
    """
    return f"""
请使用Playwright MCP工具完成以下网页自动化任务：

任务：{task}
目标网站：{url}

建议步骤：
1. 首先使用 create_browser_session 创建浏览器会话
2. 使用 navigate_to_url 导航到目标网站
3. 根据任务需要使用相应的交互和数据提取工具
4. 完成后使用 close_browser_session 关闭会话

可用工具：
- 页面导航：navigate_to_url
- 元素交互：click_element, fill_input
- 数据提取：get_text_content, get_element_attribute, get_page_title
- 页面分析：execute_javascript, take_screenshot
- 等待机制：wait_for_selector

请根据具体任务选择合适的工具组合。
"""


if __name__ == "__main__":
    # 运行服务器
    mcp.run()
