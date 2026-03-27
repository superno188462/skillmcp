"""
示例技能包 2 - visible=False, default_enabled=True

这个技能包展示：
- visible=False: 对客户端不可见（完全隐藏）
- default_enabled=True: 启动时自动启用（但因为不可见，客户端无法控制）

注意：visible=False 时，技能包完全不会暴露给客户端
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any


SKILL_PACKAGE = {
    "name": "demo_hidden",
    "version": "1.0.0",
    "description": "示例技能包 2 - 不可见但默认启用（仅供内部使用）",
    "author": "SkillMCP Team",
    
    # 对客户端不可见（完全隐藏）
    "visible": False,
    
    # 默认启用（但因为 visible=False，客户端看不到）
    "default_enabled": True,
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
