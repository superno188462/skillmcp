"""
Web 工具包

提供 HTTP 请求、Webhook 等 Web 相关工具。
"""

from skillmcp.core.interfaces import Tool, ToolParameter


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
                ToolParameter(name="json", type="object", description="JSON 数据", required=False),
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


# 工具实现
def http_get_handler(url: str, headers: dict = None, params: dict = None) -> dict:
    """HTTP GET 请求实现"""
    # TODO: 实现实际 HTTP 请求
    return {
        "url": url,
        "method": "GET",
        "status": 200,
        "body": "示例响应"
    }


def http_post_handler(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
    """HTTP POST 请求实现"""
    return {
        "url": url,
        "method": "POST",
        "status": 201,
        "body": "示例响应"
    }


def http_put_handler(url: str, data: dict = None, headers: dict = None) -> dict:
    """HTTP PUT 请求实现"""
    return {
        "url": url,
        "method": "PUT",
        "status": 200,
        "body": "示例响应"
    }


def http_delete_handler(url: str, headers: dict = None) -> dict:
    """HTTP DELETE 请求实现"""
    return {
        "url": url,
        "method": "DELETE",
        "status": 204,
        "body": None
    }


SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 工具包 - 提供 HTTP 请求、Webhook 等工具",
    "author": "SkillMCP Team",
    "tools": ["http_get", "http_post", "http_put", "http_delete"],
    "dependencies": [],
    "default_visible": False,
    "category": "network",
    "tags": ["http", "web", "network", "api"],
}
