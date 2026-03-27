"""
示例技能包 1 - visible=True, default_enabled=False

这个技能包展示：
- visible=True: 对客户端可见
- default_enabled=False: 默认不启用，需要手动启用
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


SKILL_PACKAGE = {
    "name": "demo_visible",
    "version": "1.0.0",
    "description": "示例技能包 1 - 可见但默认不启用（需要手动启用）",
    "author": "SkillMCP Team",
    
    # 对客户端可见（默认值，可省略）
    "visible": True,
    
    # 默认不启用（默认值，可省略）
    "default_enabled": False,
}


def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="http_get",
            description="HTTP GET 请求 - 发送 GET 请求获取数据",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
            ],
            handler=http_get_handler
        ),
        Tool(
            name="http_post",
            description="HTTP POST 请求 - 发送 POST 请求提交数据",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="data", type="object", description="请求数据", required=False),
            ],
            handler=http_post_handler
        ),
    ]


def http_get_handler(url: str, headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """HTTP GET 请求实现"""
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "GET",
            "status": 200,
            "headers": headers,
            "body": "示例响应数据"
        }
    }


def http_post_handler(url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """HTTP POST 请求实现"""
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "POST",
            "status": 201,
            "data": data,
            "body": "示例响应数据"
        }
    }
