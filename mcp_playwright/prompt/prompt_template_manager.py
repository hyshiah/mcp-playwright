#prompt_template_manager.py

from .prompt_template import PromptTemplate
from typing import Dict, List, Any, Optional
class PromptTemplateManager:
    """提示模板管理器"""
    
    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self._register_default_templates()
    
    def register_template(self, template: PromptTemplate):
        """注册模板"""
        self.templates[template.name]=template 
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates[name]

    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有模板信息"""
        return [template.get_parameter_info() for template in self.templates.values()]
    
    def _register_default_templates(self):
        """注册默认模板"""
        default_templates = [
            PromptTemplate(
                name="teacher_management",
                description="教師管理系统自動化操作模板",
                tools=["login_teacher_account 登入教師帳號", 
                       "Check_Student_Leaved_List 查詢學生请假名单", 
                       "Accept_Student_Leave_Request 批准學生请假", 
                       "check_Classroom_log_not_filled 查看未填写的教室日誌", 
                       "auto_fill_classroom_log 自動填寫教室日誌", 
                       "create_browser_session 创建浏览器会话", 
                       "close_browser_session 关闭会话"],
                workflow={"登入教師系統": ["create_browser_session","login_teacher_account"], 
                          "學生請假查詢及准假": ["check_Student_Leaved_List", "Accept_Student_Leave_Request"], 
                          "教室日誌查閱及填寫": ["check_Classroom_log_not_filled", "auto_fill_classroom_log"],
                          "關閉": ["close_browser_session"]},
                template= f"依據用戶任務，參考工作流提示，調用 MCP 工具。"
            ),
        PromptTemplate(
                name="student_management",
                description="學生請假自動化系统操作模板",
                tools=["create_browser_session 创建浏览器会话",
                       "login_student_account: 登入學生帳號",
                       "student_Truancy_Record: 查詢曠課紀錄",
                       "fill_Student_Leave_application: 學生填寫请假申請單",
                       "close_browser_session 关闭会话"],
                workflow={"登入學生系統": ["create_browser_session","login_student_account"], 
                          "曠課查詢": ["student_Truancy_Record"], 
                          "填寫請假單": ["fill_Student_Leave_application"],
                          "關閉": ["close_browser_session"]},
                template=f"依據用戶任務，參考工作流提示，調用 MCP 工具。"
            ),

            PromptTemplate(
                name="general_user",
                description="瀏覽器自動化系统操作模板",
                tools=["create_browser_session 创建浏览器会话",
                       "navigate_to_url 页面导航",
                       "click_element 点击元素",
                       "fill_input 输入框填充",
                       "get_text_content 获取文本内容",
                       "get_element_attribute 获取元素属性",
                       "get_page_title 获取页面标题",
                       "execute_javascript 执行JavaScript",
                       "take_screenshot 截图",
                       "wait_for_selector 等待选择器",
                       "close_browser_session 关闭会话"],
                workflow={},
                template=f"请根据具体任务选择合适的工具组合。"
            ),
            PromptTemplate(
                name="chatbot",
                description="聊天机器人模板",
                tools=[],
                workflow={},
                template="请回答我的问题：\n\n\"{{question}}\""
            ),
            PromptTemplate(
                tools=[],
                workflow={},
                name="sentiment_analysis",
                description="情感分析模板",
                template="请分析以下文本：\n\n\"{{text}}\"\n\n请提供：\n1. 情感分析\n2. 主要主题\n3. 关键要点\n4. 改进建议"
            ),
            PromptTemplate(
                tools=[],
                workflow={},
                name="code_review",
                description="代码审查模板",
                template="请审查以下{{language}}代码：\n\n```{{language}}\n{{code}}\n```\n\n请提供：\n1. 代码质量评估\n2. 潜在问题\n3. 性能建议\n4. 最佳实践建议"
            ),
            PromptTemplate(
                tools=[],
                workflow={},
                name="content_summary",
                description="内容摘要模板",
                template="请总结以下内容：\n\n{{content}}\n\n总结要求：\n- 长度：{{length}}字\n- 重点：{{focus}}\n- 格式：{{format}}"
            ),
            PromptTemplate(
                tools=[],
                workflow={},
                name="translation",
                description="翻译模板",
                template="请将以下{{source_language}}文本翻译成{{target_language}}：\n\n{{text}}\n\n翻译要求：\n- 保持原意\n- 符合{{target_language}}表达习惯\n- 专业术语准确"
            )
        ]
        
        for template in default_templates:
            self.register_template(template)

