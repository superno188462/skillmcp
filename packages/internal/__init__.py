"""
内部工具包示例 - 不暴露给客户端

这个技能包展示了如何使用 visible=False 来隐藏技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any


SKILL_PACKAGE = {
    "name": "internal",
    "version": "1.0.0",
    "description": "内部工具包 - 仅供系统内部使用",
    "author": "System",
    
    # 不暴露给客户端
    "visible": False,
    
    # 即使设置了 default_enabled，因为 visible=False 也不会启用
    "default_enabled": False,
}


def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="internal_operation",
            description="内部操作 - 系统内部使用",
            parameters=[
                ToolParameter(name="action", type="string", description="操作类型", required=True),
            ],
            handler=internal_operation_handler
        ),
    ]


def internal_operation_handler(action: str) -> Dict[str, Any]:
    """内部操作工具实现"""
    return {
        "success": True,
        "data": {
            "action": action,
            "result": f"执行内部操作：{action}"
        }
    }
