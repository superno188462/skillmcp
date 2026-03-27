"""
Web 工具包

提供 HTTP 请求、Webhook 等 Web 相关工具。

FastMCP v3 要求：
- 工具函数必须有明确的参数签名
- 不支持 **kwargs
- 参数必须有类型注解
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="http_get",
            description="HTTP GET 请求",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
                ToolParameter(name="params", type="object", description="查询参数", required=False),
            ],
            handler=http_get_handler
        ),
        Tool(
            name="http_post",
            description="HTTP POST 请求",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="data", type="object", description="表单数据", required=False),
                ToolParameter(name="json_data", type="object", description="JSON 数据", required=False),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
            ],
            handler=http_post_handler
        ),
        Tool(
            name="http_put",
            description="HTTP PUT 请求",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="data", type="object", description="请求数据", required=False),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
            ],
            handler=http_put_handler
        ),
        Tool(
            name="http_delete",
            description="HTTP DELETE 请求",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
            ],
            handler=http_delete_handler
        ),
    ]


# 工具实现（明确的参数签名，不使用 **kwargs）
def http_get_handler(url: str, headers: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """HTTP GET 请求实现"""
    # TODO: 实现实际 HTTP 请求
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "GET",
            "status": 200,
            "headers": headers,
            "params": params,
            "body": "示例响应"
        }
    }


def http_post_handler(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """HTTP POST 请求实现"""
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "POST",
            "status": 201,
            "data": data,
            "json": json_data,
            "headers": headers,
            "body": "示例响应"
        }
    }


def http_put_handler(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """HTTP PUT 请求实现"""
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "PUT",
            "status": 200,
            "data": data,
            "headers": headers,
            "body": "示例响应"
        }
    }


def http_delete_handler(url: str, headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """HTTP DELETE 请求实现"""
    return {
        "success": True,
        "data": {
            "url": url,
            "method": "DELETE",
            "status": 204,
            "headers": headers,
            "body": None
        }
    }


SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 工具包 - 提供 HTTP 请求、Webhook 等网络相关工具",
    "author": "SkillMCP Team",
    "dependencies": [],
    "default_visible": False,
    "category": "network",
    "tags": ["http", "web", "network", "api"],
}
