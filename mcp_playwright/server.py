"""
Playwright MCP Server - 基于FastMCP框架的重新实现

提供专业级的浏览器自动化MCP服务，具备完善的生命周期管理和错误处理
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Annotated, Union, Optional

from fastmcp import FastMCP

from .core.browser_manager import BrowserManager
from .tools.browser_tools import BrowserTools

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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
            headless=False,
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

# 创建FastMCP服务器
mcp = FastMCP("Playwright MCP Server", lifespan = server_lifespan )
# 设置生命周期
#mcp.lifespan = server_lifespan


# ==================== 浏览器控制工具 ====================

@mcp.tool()
async def create_browser_session(
    browser_type: str = "chromium",
    headless: bool = False,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    timeout: int = 30000
) -> str:
    """
    创建新的浏览器会话，空白頁面
    Args:
        browser_type: 浏览器类型 (chromium, firefox, webkit)
        headless: 是否无头模式預設有頭模式
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
        url: 目标URL，例如"https://www.deepseek.com"
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
    return await browser_tools.take_screenshot(path, full_page, quality)


@mcp.tool()
async def execute_javascript(code: str) -> str:
    """
    执行JavaScript代码

    Args:
        code: JavaScript代码
    """
    return await browser_tools.execute_javascript(code)

@mcp.tool()
async def save_page_to_file(filename:str) -> str:
    """
    将当前页面保存为HTML文件
    Args:
        filename: 保存的文件名
    """
    return await browser_tools.save_page_to_file(filename)

@mcp.tool()
async def snapshot() -> str:
    """
    回傳当前页面的快照
    """
    return await browser_tools.snapshot()

@mcp.tool()
async def login_teacher_account(account: str, password: str) -> str:
    """
    登入教師帳號
    Args:
        account: 教師帳號
        password: 教師密碼
    """
    return await browser_tools.login_teacher_account(account, password)

@mcp.tool()
async def login_student_account(account: str, password: str) -> str:
    """
    登入學生帳號
    Args:
        account: 學生帳號
        password: 學生密碼
    """
    return await browser_tools.login_student_account(account, password)   

@mcp.tool()
async def Student_Leaved_List() -> str:
    """
    查詢學生已請假名單
    """
    return await browser_tools.get_student_leave_list()


@mcp.tool()
async def Accept_Student_Leave_Request(info_name:str, info_time:str) -> str:
    """
    執行同意學生請假相關流程
    Args:
        info_name: 學生姓名
        info_time: 建檔時間
    """
    return await browser_tools.accept_student_leave(info_name, info_time)

@mcp.tool()
async def Class_log_not_filled_inquire() -> str:
    """
    查詢教室日誌未填及未輸入缺曠清單
    """
    return await browser_tools.Classroom_log_not_filled_inquiry()

@mcp.tool()
async def auto_fill_classroom_log(month:str, day:str) -> str:
    """
    自動填寫教室日誌
    Args:
        month: 月份
        day: 日期
    """
    return await browser_tools.auto_fill_classroom_log(month, day)

@mcp.tool()
async def student_Truancy_Record() -> str:
    """
    查詢學生曠課紀錄

    """
    return await browser_tools.Student_Truancy_Record_inquiry()


@mcp.tool()
async def fill_Student_Leave_application(month: str, date: str, 
                                         start_sec: int, 
                                         end_sec: int) -> str:
    """
    填寫學生請假申請單
    Args:
        month: 請假月份 合法(str) "1", "2" 至 "12"
        date: 請假日期 合法(str) "1" 至 "31"
        start_sec: 開始節次(int) 合法 1,2,...12
        end_sec: 結束節次(int) 合法 1,2,...12
    """
    def format_number(num: int) -> str:
        """
        將整數轉換為字串格式：
        - 1-9 轉為 01-09
        - 10及以上保持原樣
        """
        if num < 10:
            return f"0{num}"
        else:
            return str(num)

    return await browser_tools.fill_Student_Leave_application(month, date, format_number(start_sec),
                                                              format_number(end_sec))

# student_name = Annotated[str, "學生姓名" ]
# student_all = Annotated[dict[str,str], '{"class":班級, "number":學號, "name":姓名, "kind":假別, "time":建檔時間,  "teacher":導師審核結果}']
# async def outoforder_Accept_Student_Leave(name :Union[student_name, student_all] ) -> str:
#     """
#     同意學生請假 注意 學生請假名單 姓名重複時，請提供完整資訊以避免誤判    
#     """
#     return await browser_tools.accept_student_leave(name)

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
        },
        "教師管理": {
            "login_teacher_account": "登入教師帳號",
            "Student_Leaved_List": "查詢學生已請假名單",
            "Accept_Student_Leave": "同意學生請假",
            "Class_log_not_filled_inquire": "查詢教室日誌未填及未輸入缺曠清單",
            "auto_fill_classroom_log": "自動填寫教室日誌",
            "close_browser_session": "完成後关闭当前浏览器会话"
        },
        "學生請假": {
            "login_student_account": "登入學生帳號",
            "student_Truancy_Record": "查詢學生曠課紀錄",
            "fill_Student_Leave_application": "填寫學生請假申請單",
            "close_browser_session": "完成後关闭当前浏览器会话"
        }
    }

    return json.dumps(help_info, ensure_ascii=False, indent=2)


# ==================== 提示模板 ====================
from .prompt.fastmcp_template import MCPPromptClient
my_prompt_client = MCPPromptClient()
@mcp.prompt()
def default_prompt(user_input: str) -> str:
    """
    默认提示模板，基于用户身份进行工作流处理
    Args:
        user_input: 用户输入的文本
    """
    return my_prompt_client.identity_based_workflow(user_input)

# def web_automation_prompt(task: str, url: str = "https://example.com") -> str:
#     """
#     网页自动化任务提示模板

#     Args:
#         task: 要执行的任务描述
#         url: 目标网站URL
#     """
#     return f"""
# 请使用Playwright MCP工具完成以下网页自动化任务：

# 任务：{task}
# 目标网站：{url}

# 建议步骤：
# 1. 首先使用 create_browser_session 创建浏览器会话
# 2. 使用 navigate_to_url 导航到目标网站
# 3. 根据任务需要使用相应的交互和数据提取工具
# 4. 完成后使用 close_browser_session 关闭会话

# 可用工具：
# - 页面导航：navigate_to_url
# - 元素交互：click_element, fill_input
# - 数据提取：get_text_content, get_element_attribute, get_page_title
# - 页面分析：execute_javascript, take_screenshot
# - 等待机制：wait_for_selector

# 请根据具体任务选择合适的工具组合。
# """
# @mcp.prompt()
# def teacher_management_prompt(action: str) -> str:
#     """
#     教師管理系统自動化操作模板
#     Args:
#         task: 要执行的任务描述
#     """
#     return f"""
# 请帮我执行管理操作：{action}

# 可用工具：
# - login_teacher_account: 登入教師帳號
# - Student_Leaved_List: 教師查看學生请假名单
# - Accept_Student_Leave: 教師批准學生请假
# - Classroom_log_not_filled: 教師查看未填寫的教室日誌
# - auto_fill_classroom_log: 教師自動填寫教室日誌
# - create_browser_session 创建浏览器会话
# - close_browser_session 关闭会话

# 典型流程：
# 1. 首先确保身份是教師 
# 2. 首先使用 create_browser_session 创建浏览器会话
# 3. 登录教师账号 login_teacher_account
# 4. 根据具体需求选择相应工具
# 5. 解析調用結果
# 5. 按提示提供必要参数（如学生姓名、日期等
# 6. 完成后使用 close_browser_session 关闭会话
# """

# @mcp.prompt()
# def student_management_prompt(action: str) -> str:
#     """
#     學生請假自動化系统操作模板
#     Args:
#         task: 要执行的任务描述
#     """
#     return f"""
# 请帮我执行學生請假操作：{action}

# 可用工具：
# - student_Truancy_Record: 查詢曠課紀錄
# - fill_Student_Leave_application: 學生填寫请假申請單
# - login_student_account: 登入學生帳號
# - create_browser_session 创建浏览器会话
# - close_browser_session 关闭会话

# 典型流程：
# 1. 首先确保身份是學生
# 2. 首先使用 create_browser_session 创建浏览器会话
# 3. 登录學生账号 login_teacher_account
# 4. 查詢曠課紀錄 student_Truancy_Record
# 5. 選擇請假日期及起訖節次 
# 6. 填寫请假申請單 fill_Student_Leave_application
# 7. 根据具体需求选择相应工具
# 8. 按提示提供必要参数（如学生姓名、日期等）
# 9. 完成后使用 close_browser_session 关闭会话
# """


if __name__ == "__main__":
    # 运行服务器
    mcp.run()
