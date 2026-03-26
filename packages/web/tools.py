"""
Web 工具包 - 工具实现
"""

import requests
from skillmcp.core.interfaces import Tool, ToolParameter


def http_get_handler(url: str, headers: dict = None, params: dict = None) -> dict:
    """HTTP GET 请求"""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def http_post_handler(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
    """HTTP POST 请求"""
    try:
        response = requests.post(url, data=data, json=json, headers=headers, timeout=30)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def http_put_handler(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
    """HTTP PUT 请求"""
    try:
        response = requests.put(url, data=data, json=json, headers=headers, timeout=30)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def http_delete_handler(url: str, headers: dict = None) -> dict:
    """HTTP DELETE 请求"""
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_tools() -> list:
    """获取 Web 工具列表"""
    return [
        Tool(
            name="http_get",
            description="发送 HTTP GET 请求",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="请求 URL",
                    required=True
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="请求头",
                    required=False
                ),
                ToolParameter(
                    name="params",
                    type="object",
                    description="查询参数",
                    required=False
                ),
            ],
            handler=http_get_handler
        ),
        Tool(
            name="http_post",
            description="发送 HTTP POST 请求",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="请求 URL",
                    required=True
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="表单数据",
                    required=False
                ),
                ToolParameter(
                    name="json",
                    type="object",
                    description="JSON 数据",
                    required=False
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="请求头",
                    required=False
                ),
            ],
            handler=http_post_handler
        ),
        Tool(
            name="http_put",
            description="发送 HTTP PUT 请求",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="请求 URL",
                    required=True
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="表单数据",
                    required=False
                ),
                ToolParameter(
                    name="json",
                    type="object",
                    description="JSON 数据",
                    required=False
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="请求头",
                    required=False
                ),
            ],
            handler=http_put_handler
        ),
        Tool(
            name="http_delete",
            description="发送 HTTP DELETE 请求",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="请求 URL",
                    required=True
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="请求头",
                    required=False
                ),
            ],
            handler=http_delete_handler
        ),
    ]
