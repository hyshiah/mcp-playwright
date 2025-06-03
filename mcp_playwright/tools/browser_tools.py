"""
浏览器操作工具集 - Playwright MCP Server

提供标准的浏览器自动化操作工具
"""

import base64
import json
import logging
from typing import Optional, Any, Dict

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ..core.browser_manager import BrowserManager, BrowserSession

logger = logging.getLogger(__name__)


class BrowserTools:
    """浏览器工具集合类"""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self._current_session: Optional[BrowserSession] = None

    def _get_current_session(self) -> BrowserSession:
        """获取当前会话，如果不存在则抛出异常"""
        if not self._current_session or not self._current_session.is_ready:
            raise RuntimeError("浏览器会话未初始化，请先创建会话")
        return self._current_session

    async def create_session(
        self,
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
        try:
            # 如果存在当前会话，先清理
            if self._current_session:
                await self.browser_manager.remove_session(self._current_session.session_id)

            # 创建新会话
            session = await self.browser_manager.create_session(
                viewport={"width": viewport_width, "height": viewport_height},
                timeout=timeout
            )

            self._current_session = session

            return f"成功创建浏览器会话 {session.session_id} ({browser_type}, 无头模式: {headless})"

        except Exception as e:
            logger.error(f"创建浏览器会话失败: {e}")
            return f"创建浏览器会话失败: {str(e)}"

    async def close_session(self) -> str:
        """关闭当前浏览器会话"""
        try:
            if not self._current_session:
                return "没有活动的浏览器会话"

            session_id = self._current_session.session_id
            await self.browser_manager.remove_session(session_id)
            self._current_session = None

            return f"浏览器会话 {session_id} 已关闭"

        except Exception as e:
            logger.error(f"关闭浏览器会话失败: {e}")
            return f"关闭浏览器会话失败: {str(e)}"

    async def navigate_to_url(
        self,
        url: str,
        wait_until: str = "domcontentloaded"
    ) -> str:
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
        """
        try:
            session = self._get_current_session()
            await session.navigate(url, wait_until)
            return f"成功导航到: {url}"

        except PlaywrightTimeoutError:
            return f"导航超时: {url}"
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return f"导航失败: {str(e)}"

    async def click_element(
        self,
        selector: str,
        timeout: Optional[int] = None,
        force: bool = False
    ) -> str:
        """
        点击页面元素

        Args:
            selector: CSS选择器或XPath
            timeout: 超时时间(毫秒)
            force: 强制点击
        """
        try:
            session = self._get_current_session()
            page = session.page

            timeout = timeout or session.timeout
            await page.click(selector, timeout=timeout, force=force)

            return f"成功点击元素: {selector}"

        except PlaywrightTimeoutError:
            return f"点击超时: {selector}"
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return f"点击失败: {str(e)}"

    async def fill_input(
        self,
        selector: str,
        text: str,
        timeout: Optional[int] = None
    ) -> str:
        """
        填写输入框

        Args:
            selector: CSS选择器或XPath
            text: 要输入的文本
            timeout: 超时时间(毫秒)
        """
        try:
            session = self._get_current_session()
            page = session.page

            timeout = timeout or session.timeout
            await page.fill(selector, text, timeout=timeout)

            return f"成功填写输入框 {selector}: {text}"

        except PlaywrightTimeoutError:
            return f"填写超时: {selector}"
        except Exception as e:
            logger.error(f"填写失败: {e}")
            return f"填写失败: {str(e)}"

    async def get_text_content(
        self,
        selector: str,
        timeout: Optional[int] = None
    ) -> str:
        """
        获取元素文本内容

        Args:
            selector: CSS选择器或XPath
            timeout: 超时时间(毫秒)
        """
        try:
            session = self._get_current_session()
            page = session.page

            timeout = timeout or session.timeout
            element = await page.wait_for_selector(selector, timeout=timeout)

            if element:
                text = await element.text_content()
                return text or ""
            return "元素未找到"

        except PlaywrightTimeoutError:
            return f"获取文本内容超时: {selector}"
        except Exception as e:
            logger.error(f"获取文本内容失败: {e}")
            return f"获取文本内容失败: {str(e)}"

    async def get_element_attribute(
        self,
        selector: str,
        attribute: str,
        timeout: Optional[int] = None
    ) -> str:
        """
        获取元素属性值

        Args:
            selector: CSS选择器或XPath
            attribute: 属性名
            timeout: 超时时间(毫秒)
        """
        try:
            session = self._get_current_session()
            page = session.page

            timeout = timeout or session.timeout
            element = await page.wait_for_selector(selector, timeout=timeout)

            if element:
                value = await element.get_attribute(attribute)
                return value or ""
            return "元素未找到"

        except PlaywrightTimeoutError:
            return f"获取属性超时: {selector}"
        except Exception as e:
            logger.error(f"获取属性失败: {e}")
            return f"获取属性失败: {str(e)}"

    async def take_screenshot(
        self,
        path: Optional[str] = None,
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
        try:
            session = self._get_current_session()

            screenshot_bytes = await session.take_screenshot(
                path=path,
                full_page=full_page,
                quality=quality if path and (path.endswith('.jpg') or path.endswith('.jpeg')) else None
            )

            if path:
                return f"截图已保存到: {path}"
            else:
                # 返回base64编码的截图
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                return f"data:image/png;base64,{screenshot_b64}"

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return f"截图失败: {str(e)}"

    async def wait_for_selector(
        self,
        selector: str,
        timeout: Optional[int] = None,
        state: str = "visible"
    ) -> str:
        """
        等待元素出现

        Args:
            selector: CSS选择器或XPath
            timeout: 超时时间(毫秒)
            state: 元素状态 (attached, detached, visible, hidden)
        """
        try:
            session = self._get_current_session()
            page = session.page

            timeout = timeout or session.timeout
            await page.wait_for_selector(selector, timeout=timeout, state=state)

            return f"元素已出现: {selector}"

        except PlaywrightTimeoutError:
            return f"等待元素超时: {selector}"
        except Exception as e:
            logger.error(f"等待元素失败: {e}")
            return f"等待元素失败: {str(e)}"

    async def execute_javascript(self, code: str) -> str:
        """
        执行JavaScript代码

        Args:
            code: JavaScript代码
        """
        try:
            session = self._get_current_session()
            page = session.page

            result = await page.evaluate(code)

            if result is not None:
                return json.dumps(result, ensure_ascii=False, indent=2)
            else:
                return "JavaScript执行成功"

        except Exception as e:
            logger.error(f"JavaScript执行失败: {e}")
            return f"JavaScript执行失败: {str(e)}"

    async def get_page_title(self) -> str:
        """获取页面标题"""
        try:
            session = self._get_current_session()
            page = session.page

            title = await page.title()
            return title

        except Exception as e:
            logger.error(f"获取页面标题失败: {e}")
            return f"获取页面标题失败: {str(e)}"

    async def get_page_url(self) -> str:
        """获取当前页面URL"""
        try:
            session = self._get_current_session()
            page = session.page

            return page.url

        except Exception as e:
            logger.error(f"获取页面URL失败: {e}")
            return f"获取页面URL失败: {str(e)}"

    def get_session_status(self) -> Dict[str, Any]:
        """获取会话状态"""
        if not self._current_session:
            return {
                "status": "no_session",
                "session_id": None,
                "ready": False
            }

        return {
            "status": "active",
            "session_id": self._current_session.session_id,
            "ready": self._current_session.is_ready,
            "viewport": self._current_session.viewport,
            "timeout": self._current_session.timeout
        }
