#fastmcp_template.py

from typing import Optional
from fastmcp import FastMCP
from .prompt_template_manager import PromptTemplateManager
from .prompt_template import PromptTemplate
class MCPPromptClient:
    """MCP 提示客户端"""
    
    def __init__(self):
        self.template_manager = PromptTemplateManager()
        self.identity: Optional[str] = None


    def identity_based_workflow(self, user_input: str) -> str:
        """
        基于用户指令智能识别身份并提供相应工作流指导
        
        身份识别规则：
        - 包含「教師」、「老師」、「teacher」等关键词 → 教师身份
        - 包含「學生」、「student」等关键词 → 学生身份
        - 包含「請假」、「缺曠」、「曠課」等关键词 → 根据上下文判断身份
        - 其他情况 → 一般用户
        """
        if self.identity is None or self.identity == "general_user":
            self.identity = self._identify_user_identity(user_input)
        self.identity = self._identify_user_identity(user_input)
        template = self.template_manager.get_template(self.identity)
        if not template:
            self.identity = None
            return "未找到匹配模板，请确认身份或提供更多信息。"
        prompt_template = template.get_parameter_info()
        
            
        workflow = prompt_template["workflow"]
        tools = prompt_template["tools"]
        description = prompt_template["description"]
        parameters = prompt_template["parameters"]
        template = prompt_template["template_preview"]
        
        return f"""
任務：「{user_input}」，系统已识别为 **{self.identity}** 身份。

描述: 
{description}

可用的工具: 
{tools}

工作流：
{workflow}

執行：    
{template}
    """.strip()

    def _identify_user_identity(self, text: str) -> str:
        lower_text = text.lower()
        reset_keywords = ['重置', 'reset','重設']
        teacher_keywords = ['教師', '老師', 'teacher', '導師', '審核', '批准']
        student_keywords = ['學生', '学号', 'student', '請假', '缺曠', '旷课', 'leave', 'truancy']
        if any(k in lower_text for k in teacher_keywords):
            return "teacher_management"
        elif any(k in lower_text for k in student_keywords):
            return "student_management"
        elif any(k in lower_text for k in reset_keywords):
            return "reset"
        else:
            return "general_user"





#==========================================
    def list_prompt_templates(self) -> str:
        """列出所有可用的提示模板"""
        templates_info = self.template_manager.list_templates()
        
        if not templates_info:
            return "当前没有可用的提示模板。"
        
        response = "可用的提示模板：\n\n"
        for template in templates_info:
            response += f"**{template['name']}**\n"
            response += f"描述: {template['description']}\n"
            response += f"参数: {', '.join(template['parameters'])}\n"
            response += f"预览: {template['template_preview']}\n\n"
        
        return response
    

    def text_analysis(self, text: str) -> str:
        """文本分析提示"""
        template = self.template_manager.get_template("text_analysis")
        if not template:
            return "文本分析模板未找到。"
        
        return template.render(text=text)
    

    def code_review(self, code: str, language: str = "python") -> str:
        """代码审查提示"""
        template = self.template_manager.get_template("code_review")
        if not template:
            return "代码审查模板未找到。"
        
        return template.render(code=code, language=language)
    

    def content_summary(self, content: str, length: str = "300", focus: str = "主要观点", format: str = "段落") -> str:
        """内容摘要提示"""
        template = self.template_manager.get_template("content_summary")
        if not template:
            return "内容摘要模板未找到。"
        
        return template.render(content=content, length=length, focus=focus, format=format)
    

    def translation(self, text: str, source_language: str = "中文", target_language: str = "英文") -> str:
        """翻译提示"""
        template = self.template_manager.get_template("translation")
        if not template:
            return "翻译模板未找到。"
        
        return template.render(text=text, source_language=source_language, target_language=target_language)
    

    def custom_prompt(self, template_name: str, **kwargs) -> str:
        """自定义提示模板"""
        template = self.template_manager.get_template(template_name)
        if not template:
            available_templates = ", ".join(self.template_manager.templates.keys())
            return f"模板 '{template_name}' 未找到。可用的模板: {available_templates}"
        
        # 验证参数
        missing_params = set(template.parameters) - set(kwargs.keys())
        if missing_params:
            return f"缺少必需的参数: {', '.join(missing_params)}"
        
        return template.render(**kwargs)
    
    def create_custom_template(self, name: str, description: str, template: str):
        """动态创建自定义模板"""
        new_template = PromptTemplate(name, description, template, tools=[], workflow={})
        self.template_manager.register_template(new_template)
        return f"模板 '{name}' 创建成功！"