#prompt_template.py

from typing import Dict, List, Any, Optional
import json
import inspect

class PromptTemplate:
    """基础提示模板类"""
    
    def __init__(self, name: str, description: str, template: str, tools: list , workflow: dict):
        self.name = name
        self.description = description
        self.tools = tools
        self.workflow = workflow
        self.template = template
        self.parameters = self._extract_parameters()
    
    def _extract_parameters(self) -> List[str]:
        """从模板中提取参数占位符"""
        import re
        # 查找 {{parameter}} 格式的占位符
        pattern = r'\{\{(\w+)\}\}'
        return re.findall(pattern, self.template)
    
    def render(self, **kwargs) -> str:
        """渲染模板"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"缺少必需的参数: {e}")
    
    def get_parameter_info(self) -> Dict[str, str]:
        """获取参数信息"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": "\n".join(self.parameters),
            "tools": "\n".join(self.tools),
            "workflow": "\n".join(f"{a}:  調用工具：{b}" for a, b in self.workflow.items()),
            "template_preview": self.template[:100] + "..." if len(self.template) > 100 else self.template
        }