"""
浏览器管理器 - Playwright MCP Server 核心组件

负责管理Playwright浏览器实例的生命周期、资源池化和会话隔离
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Optional, Any
from uuid import uuid4
import weakref

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError
)

logger = logging.getLogger(__name__)


class BrowserSession:
    """浏览器会话类 - 管理单个会话的浏览器上下文"""

    def __init__(
        self,
        session_id: str,
        browser: Browser,
        viewport: Dict[str, int],
        timeout: int = 30000
    ):
        self.session_id = session_id
        self.browser = browser
        self.viewport = viewport
        self.timeout = timeout
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._closed = False

    async def initialize(self) -> None:
        """初始化浏览器上下文和页面"""
        if self._closed:
            raise RuntimeError("会话已关闭")

        try:
            self.context = await self.browser.new_context(
                viewport=self.viewport
            )
            self.page = await self.context.new_page()
            logger.info(f"会话 {self.session_id} 初始化成功")
        except Exception as e:
            logger.error(f"会话 {self.session_id} 初始化失败: {e}")
            await self.cleanup()
            raise

    async def cleanup(self) -> None:
        """清理会话资源"""
        if self._closed:
            return

        self._closed = True
        try:
            if self.context:
                await self.context.close()
                logger.info(f"会话 {self.session_id} 上下文已关闭")
        except Exception as e:
            logger.warning(f"关闭会话 {self.session_id} 上下文时出错: {e}")
        finally:
            self.context = None
            self.page = None

    @property
    def is_ready(self) -> bool:
        """检查会话是否准备就绪"""
        return not self._closed and self.page is not None

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """导航到指定URL"""
        if not self.is_ready:
            raise RuntimeError("会话未准备就绪")

        await self.page.goto(url, wait_until=wait_until, timeout=self.timeout)

    async def take_screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        quality: Optional[int] = None
    ) -> bytes:
        """截取页面截图"""
        if not self.is_ready:
            raise RuntimeError("会话未准备就绪")

        return await self.page.screenshot(
            path=path,
            full_page=full_page,
            quality=quality
        )


class BrowserManager:
    """浏览器管理器 - 核心管理类"""

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        max_sessions: int = 10,
        default_viewport: Optional[Dict[str, int]] = None,
        default_timeout: int = 30000
    ):
        self.browser_type = browser_type
        self.headless = headless
        self.max_sessions = max_sessions
        self.default_viewport = default_viewport or {"width": 1280, "height": 720}
        self.default_timeout = default_timeout

        # 内部状态
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSession] = {}
        self._session_refs: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化浏览器管理器"""
        async with self._lock:
            if self._initialized:
                return

            try:
                logger.info("初始化 Playwright...")
                self._playwright = await async_playwright().start()

                logger.info(f"启动 {self.browser_type} 浏览器...")
                browser_launcher = getattr(self._playwright, self.browser_type)
                self._browser = await browser_launcher.launch(
                    headless=self.headless
                )

                self._initialized = True
                logger.info("浏览器管理器初始化完成")

            except Exception as e:
                logger.error(f"浏览器管理器初始化失败: {e}")
                await self._cleanup_resources()
                raise

    async def cleanup(self) -> None:
        """清理所有资源"""
        async with self._lock:
            if not self._initialized:
                return

            logger.info("开始清理浏览器管理器...")

            # 清理所有会话
            cleanup_tasks = []
            for session in list(self._sessions.values()):
                cleanup_tasks.append(session.cleanup())

            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)

            self._sessions.clear()

            # 清理浏览器资源
            await self._cleanup_resources()
            self._initialized = False
            logger.info("浏览器管理器清理完成")

    async def _cleanup_resources(self) -> None:
        """内部资源清理方法"""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
                logger.info("浏览器实例已关闭")
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")

        try:
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                logger.info("Playwright 已停止")
        except Exception as e:
            logger.warning(f"停止 Playwright 时出错: {e}")

    async def create_session(
        self,
        session_id: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        timeout: Optional[int] = None
    ) -> BrowserSession:
        """创建新的浏览器会话"""
        if not self._initialized:
            await self.initialize()

        session_id = session_id or str(uuid4())
        viewport = viewport or self.default_viewport
        timeout = timeout or self.default_timeout

        async with self._lock:
            if len(self._sessions) >= self.max_sessions:
                raise RuntimeError(f"已达到最大会话数限制: {self.max_sessions}")

            if session_id in self._sessions:
                raise ValueError(f"会话 {session_id} 已存在")

            try:
                session = BrowserSession(
                    session_id=session_id,
                    browser=self._browser,
                    viewport=viewport,
                    timeout=timeout
                )

                await session.initialize()
                self._sessions[session_id] = session
                self._session_refs[session_id] = session

                logger.info(f"创建会话成功: {session_id}")
                return session

            except Exception as e:
                logger.error(f"创建会话失败: {e}")
                raise

    async def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """获取会话"""
        return self._sessions.get(session_id)

    async def remove_session(self, session_id: str) -> bool:
        """移除会话"""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            await session.cleanup()
            del self._sessions[session_id]
            logger.info(f"会话已移除: {session_id}")
            return True

    @asynccontextmanager
    async def session_context(
        self,
        session_id: Optional[str] = None,
        **session_kwargs
    ) -> AsyncIterator[BrowserSession]:
        """会话上下文管理器"""
        session = await self.create_session(session_id, **session_kwargs)
        try:
            yield session
        finally:
            await self.remove_session(session.session_id)

    @property
    def session_count(self) -> int:
        """当前会话数量"""
        return len(self._sessions)

    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "initialized": self._initialized,
            "browser_type": self.browser_type,
            "headless": self.headless,
            "session_count": self.session_count,
            "max_sessions": self.max_sessions,
            "active_sessions": list(self._sessions.keys())
        }
