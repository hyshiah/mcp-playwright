"""
浏览器操作工具集 - Playwright MCP Server

提供标准的浏览器自动化操作工具
"""

import base64
import json
import logging
import quopri
import re
from typing import Optional, Any, Dict
from playwright.async_api import expect, Dialog
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
            self.browser_manager.headless = headless
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
    def decode_quoted_printable_html(self, html_str: str) -> str:
        """解码包含Quoted-Printable编码的HTML字符串"""
        # 先解码整个字符串
        try:
            decoded_bytes = quopri.decodestring(html_str)
            decoded_str = decoded_bytes.decode('utf-8')
            return decoded_str
        except Exception as e:
            logger.error(f"解码HTML失败: {e}")
            return html_str

    async def save_page_to_file(self, filename: str) -> str:
        """
        将当前页面保存为HTML文件
        Args:
            filename: 保存的文件名
        """
        try:
            session = self._get_current_session()
            page = session.page
            randered_html = page.content()
            randered_html = await randered_html
            #decoded_randered_html = self.decode_quoted_printable_html(randered_html)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(randered_html)

            return f"页面已保存到{filename}"

        except Exception as e:
            logger.error(f"保存页面失败: {e}")
            return f"保存页面失败: {str(e)}"
        
    async def snapshot(self):
        """保存当前页面的快照"""
        try:
            session = self._get_current_session()
            snapshot = await session.page.locator("body").aria_snapshot()
            # 轉換為 YAML 字符串（簡化版本）
            import yaml
            yaml_str = snapshot
            lines = yaml_str.split('\n')
            enhanced_lines = []
            ref_counter = 1
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                if line.strip() and not line.strip().startswith('#'):
                    # 計算 level_counter
                    leading_spaces = len(line) - len(line.lstrip())
                    level_counter = leading_spaces // 2
                    
                    # 識別列表項（真正的元素）
                    stripped_line = line.strip()
                    if stripped_line.startswith('- '):
                        # 在行末添加屬性
                        enhanced_line = f"{line} [ref=e{ref_counter}] [level={level_counter}]"
                        ref_counter += 1
                        enhanced_lines.append(enhanced_line)
                    else:
                        enhanced_lines.append(line)
                else:
                    enhanced_lines.append(line)
                
                i += 1
            
            yaml_str = '\n'.join(enhanced_lines)
            return f"页面快照: {yaml_str}"
        except Exception as e:
            logger.error(f"保存页面快照失败: {e}")
            return f"保存页面快照失败: {str(e)}"

    async def login_teacher_account(self, account: str, password: str) -> str:
        """登入教師帳號"""
        try:
            session = self._get_current_session()
            page = session.page
            await page.goto("https://fac.tumt.edu.tw/personal/personal/", wait_until="networkidle")
            await page.locator("input[name=\"sID\"]").click()
            await page.locator("input[name=\"sID\"]").fill("hyshiah")
            await page.locator("#sPassword").click()
            await page.locator("#sPassword").fill("Aa123456")
            await page.get_by_role("button", name="登入本校個人網頁").click()
            # 等待導師系統連結出現以確認登入成功
            await page.get_by_role("link", name="導師系統").wait_for(timeout=10000)
            return f"教師帳號 {account} 登入成功"
        except Exception as e:
            logger.error(f"教師帳號登入失敗: {e}")
            return f"教師帳號登入失敗: {str(e)}"

    async def login_student_account(self, account: str, password: str) -> str:
        """登入學生帳號"""
        try:
            session = self._get_current_session()
            page = session.page

            await page.goto("https://std.tumt.edu.tw/personal/pstudent/login.aspx", wait_until="networkidle")
            await page.locator("input[name=\"sID\"]").click()
            await page.locator("input[name=\"sID\"]").fill(account)
            await page.locator("input[name=\"sStd_Pw\"]").click()
            await page.locator("input[name=\"sStd_Pw\"]").fill(password)
            await page.get_by_role("button", name="登入本校個人網頁").click()

            return f"學生帳號 {account} 登入成功"

        except PlaywrightTimeoutError:
            return f"學生帳號 {account} 登入失敗，請檢查帳號密碼"
        except Exception as e:
            logger.error(f"學生帳號登入失敗: {e}")
            return f"學生帳號登入失敗: {str(e)}"
        
    async def get_student_leave_list(self) -> str:
        """获取学生请假名单"""
        try:
            session = self._get_current_session()
            page = session.page

            # 假设请假名单在一个特定的表格中
            await page.goto("https://fac.tumt.edu.tw/personal/personal/Index.aspx", wait_until="networkidle")
            await page.get_by_role("link", name="導師系統").click(timeout=10000)
            await page.get_by_role("link", name="學生請假審核").click(timeout=10000)
            table_js = """

                (selector) => {{
                            const element = document.querySelector(selector);
                            if (!element) return "元素未找到";
                            
                            // 複製元素以避免修改原內容
                            const clone = element.cloneNode(true);
                            
                            // 移除所有屬性的函數
                            function removeAllAttributes(element) {{
                                // 移除當前元素的所有屬性
                                const attributes = element.getAttributeNames();
                                for (const attr of attributes) {{
                                    element.removeAttribute(attr);
                                }}
                                
                                // 遞迴處理所有子元素
                                for (const child of element.children) {{
                                    removeAllAttributes(child);
                                }}
                            }}
                            
                            removeAllAttributes(clone);
                            return clone.outerHTML;
                        }}
            """
            selector = "table.table"
            await page.wait_for_selector(selector)
            table_html = await page.evaluate(table_js, selector)

            import re
            def remove_all_control_chars(text):
                """移除所有控制字符和多餘空白"""
                # 方法 1A: 移除特定控制字符並壓縮空白
                cleaned = re.sub(r'[\n\t\u3000]+', ' ', text)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned
            
            def remove_unicode_control_chars(text):
                """使用Unicode類別移除所有控制字符"""
                # \p{C} 匹配所有Unicode控制字符
                # 需要 regex 模組（比 re 更強大）
                try:
                    import regex
                    cleaned = regex.sub(r'\p{C}+', ' ', text)
                    cleaned = regex.sub(r'\s+', ' ', cleaned).strip()
                    return cleaned
                except ImportError:
                    # 降級到標準 re
                    return remove_all_control_chars(text)
            
            clean_html = remove_unicode_control_chars(table_html)

            return f"获取学生请假名单: {clean_html}"

        except Exception as e:
            logger.error(f"获取学生请假名单失败: {e}")
            return f"获取学生请假名单失败: {str(e)}"

    async def accept_student_leave(self, name_info: str, time_info: str ) -> str:
        try:
            session = self._get_current_session()
            page = session.page
            import re
            pattern = f'.*{name_info}.*{time_info}.*'
            #re.compile(r'pattern')
            await page.goto("https://fac.tumt.edu.tw/personal/Teacher/qry/AbsPer.aspx", wait_until="networkidle")
            if isinstance(name_info, str) and isinstance(time_info, str):               
                await page.get_by_role("row", name= name_info ).filter(has_text=time_info).get_by_role("link").click()
                await page.get_by_role("button", name="允許請假").click()
                return f"已接受學生 {name_info} 的請假申請"
            else:
                return "請提供學生姓名以接受請假申請"
        except Exception as e:
            logger.error(f"接受學生請假失敗: {e}")
            return f"接受學生請假失敗: {str(e)}" 

    async def Classroom_log_not_filled_inquiry(self) -> str:
        try:
            session = self._get_current_session()
            page = session.page

            await page.goto("https://fac.tumt.edu.tw/personal/Instructor/index.aspx", wait_until="networkidle")
            await page.get_by_role("link", name="教室日誌未填及未輸入缺曠查詢").click(timeout=10000)
            await page.get_by_role("button", name="確定").click(timeout=10000)
            selector = "body > div:nth-child(7) > table"
            table_js = """

                (selector) => {{
                            const element = document.querySelector(selector);
                            if (!element) return "元素未找到";
                            
                            // 複製元素以避免修改原內容
                            const clone = element.cloneNode(true);
                            
                            // 移除所有屬性的函數
                            function removeAllAttributes(element) {{
                                // 移除當前元素的所有屬性
                                const attributes = element.getAttributeNames();
                                for (const attr of attributes) {{
                                    element.removeAttribute(attr);
                                }}
                                
                                // 遞迴處理所有子元素
                                for (const child of element.children) {{
                                    removeAllAttributes(child);
                                }}
                            }}
                            
                            removeAllAttributes(clone);
                            return clone.outerHTML;
                        }}
            """
            
            import re
            def remove_all_control_chars(text):
                """移除所有控制字符和多餘空白"""
                # 方法 1A: 移除特定控制字符並壓縮空白
                cleaned = re.sub(r'[\n\t\u3000]+', ' ', text)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned
            
            def remove_unicode_control_chars(text):
                """使用Unicode類別移除所有控制字符"""
                # \p{C} 匹配所有Unicode控制字符
                # 需要 regex 模組（比 re 更強大）
                try:
                    import regex
                    cleaned = regex.sub(r'\p{C}+', ' ', text)
                    cleaned = regex.sub(r'\s+', ' ', cleaned).strip()
                    return cleaned
                except ImportError:
                    # 降級到標準 re
                    return remove_all_control_chars(text)
          
            await page.wait_for_selector(selector)
            table_html = await page.evaluate(table_js, selector)
            clean_html = remove_unicode_control_chars(table_html)
            return f"获取教師日誌未填紀錄: {clean_html}"
        except Exception as e:
            logger.error(f"获取教師日誌未填紀錄失败: {e}")
            return f"获取教師日誌未填紀錄失败: {str(e)}"

    async def auto_fill_classroom_log(self, month:str, day:str) -> str:
        try:
            session = self._get_current_session()
            page = session.page
            #全到
            async def handle_dialog(dialog: Dialog):
                """监听后处理"""
                #print(dialog.message)
                await dialog.accept()

            await page.goto("https://fac.tumt.edu.tw/personal/Instructor/index.aspx", wait_until="networkidle")
            await page.get_by_role("link", name="曠課登錄(含教室日誌)").click()
            await page.locator("select[name=\"Month\"]").select_option(month)
            await page.locator("select[name=\"Day\"]").select_option(day)
            await page.get_by_role("button", name="查詢").click()

            try:
                row = 1
                while True:
                    row += 1 
                    locator = page.locator(f"tr:nth-child({row}) > td:nth-child(3)").get_by_role("checkbox")
                    if not await locator.is_checked(timeout=5000):
                        page.on("dialog", handle_dialog)
                        await page.locator(f"tr:nth-child({row}) > td:nth-child(3)").click()
                        text = await page.locator("#AutoNumber1 > tbody > tr:nth-child(6) > td:nth-child(2) > font > textarea").input_value()
                        # if isinstance(text, list):
                        #     text_string = "".join(text)
                        # else:
                        #     text_string = text

                        if text.strip() == "":
                            await page.locator("#AutoNumber1 > tbody > tr:nth-child(7) > td:nth-child(2) > textarea").fill("導師課")
                        else:
                            await page.get_by_role("button", name="同上").click()
                        await page.locator("select[name=\"IsBeforeClear\"]").select_option("Y")
                        await page.locator("select[name=\"IsAfterClear\"]").select_option("Y")
                        await page.get_by_role("button", name="儲存").click()
                        logger.info(f"已填寫第 {row-1} 筆教室日誌 {text}")

                
            except PlaywrightTimeoutError:
                
                return f"{month} {day} 教室日誌填寫完畢"
            
        except Exception as e:
            logger.error(f"填寫教室日誌失敗: {e}")
            return f"填寫教室日誌失敗: {str(e)}"
    
    async def Student_Truancy_Record_inquiry(self) -> str:
        try:
            session = self._get_current_session()
            page = session.page

            await page.goto("https://std.tumt.edu.tw/personal/pstudent/Index.aspx?test2=Y", wait_until="networkidle")
            await page.get_by_role("link", name="請假缺曠查詢").click()

            selector = "body > center:nth-child(10) > table"
            table_js = """

                (selector) => {{
                            const element = document.querySelector(selector);
                            if (!element) return "元素未找到";
                            
                            // 複製元素以避免修改原內容
                            const clone = element.cloneNode(true);
                            
                            // 移除所有屬性的函數
                            function removeAllAttributes(element) {{
                                // 移除當前元素的所有屬性
                                const attributes = element.getAttributeNames();
                                for (const attr of attributes) {{
                                    element.removeAttribute(attr);
                                }}
                                
                                // 遞迴處理所有子元素
                                for (const child of element.children) {{
                                    removeAllAttributes(child);
                                }}
                            }}
                            
                            removeAllAttributes(clone);
                            return clone.outerHTML;
                        }}
            """
            
            import re
            def remove_all_control_chars(text):
                """移除所有控制字符和多餘空白"""
                # 方法 1A: 移除特定控制字符並壓縮空白
                cleaned = re.sub(r'[\n\t\u3000]+', ' ', text)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                return cleaned
            
            def remove_unicode_control_chars(text):
                """使用Unicode類別移除所有控制字符"""
                # \p{C} 匹配所有Unicode控制字符
                # 需要 regex 模組（比 re 更強大）
                try:
                    import regex
                    cleaned = regex.sub(r'\p{C}+', ' ', text)
                    cleaned = regex.sub(r'\s+', ' ', cleaned).strip()
                    return cleaned
                except ImportError:
                    # 降級到標準 re
                    return remove_all_control_chars(text)
          
            await page.wait_for_selector(selector)
            table_html = await page.evaluate(table_js, selector)
            clean_html = remove_unicode_control_chars(table_html)
            return f"获取曠課紀錄: {clean_html}"
        except Exception as e:
            logger.error(f"获取曠課紀錄失败: {e}")
            return f"获取曠課紀錄失败: {str(e)}"

    async def fill_Student_Leave_application(self, month: str, 
                                             date: str, start_sec:str, 
                                             end_sec: str) -> str:
        dialog_message = None
        async def handle_dialog(dialog: Dialog):
                """监听后处理"""
                nonlocal dialog_message
                dialog_message = dialog.message
                logger.info(f"攔截學生請假單{dialog.message}")
                #print(dialog.message)
                await dialog.accept()
        try:
            session = self._get_current_session()
            page = session.page

            await page.goto("https://std.tumt.edu.tw/personal/pstudent/Index.aspx?test2=Y", wait_until="networkidle")
            async with page.expect_popup() as page1_info:
                await page.get_by_role("link", name="學生請假單").click()

            page1 = await page1_info.value
            
            await page1.locator("select[name=\"S_Month\"]").select_option(month)
            await page1.locator("select[name=\"S_Day\"]").select_option(date)         
            await page1.locator("select[name=\"S_Section\"]").select_option(start_sec)

            await page1.locator("select[name=\"E_Month\"]").select_option(month)
            await page1.locator("select[name=\"E_Day\"]").select_option(date)
            await page1.locator("select[name=\"E_Section\"]").select_option(end_sec)

            await page1.locator("select[name=\"Hcode\"]").select_option("AC")
            await page1.locator("input[name=\"Reason\"]").fill("有事")
            page1.on("dialog", handle_dialog)
            await page1.get_by_role("button", name="送出").click()

            return f"已送出學生請假申請: {month}月 {date}日 第 {start_sec} 節 至 第 {end_sec} 節 - 系統回應: {dialog_message}"
        except Exception as e:
            logger.error(f"填寫學生請假申請失敗: {e}")
            return f"填寫學生請假申請失敗: {str(e)}"

    async def out_of_order_accept_student_leave(self, info: dict[str, str] | str = None ) -> str:
        try:
            session = self._get_current_session()
            page = session.page

            await page.goto("https://fac.tumt.edu.tw/personal/Teacher/qry/AbsPer.aspx", wait_until="networkidle")
            if info:
                if isinstance(info, str):
                    name = info
                    await page.get_by_role("cell", name = name).click()
                elif isinstance(info, dict):
                    await page.get_by_role("row", name=f"{info["class"]} {info["number"]} {info["name"]} {info["kind"]} {info["time"]} {info["teacher"]}").get_by_role("link").click()
                    name = info['name']
                else:
                    raise ValueError("info must be a string or dictionary")
                await page.get_by_role("button", name="允許請假").click()

                #await page.wait_for_url(url = "https://fac.tumt.edu.tw/personal/Teacher/qry/AbsPer.aspx", timeout=10000)
                
                # if page.url == "https://fac.tumt.edu.tw/personal/Teacher/qry/AbsPer.aspx":
                #     return f"已接受學生 {name} 的請假申請"
                # else:
                #     return f"接受學生 {name} 的請假申請失敗，請確認學生姓名是否正確"
                return f"已接受學生 {name} 的請假申請"
            else:
                return "請提供學生姓名以接受請假申請"
        except Exception as e:
            logger.error(f"接受學生請假失敗: {e}")
            return f"接受學生請假失敗: {str(e)}"