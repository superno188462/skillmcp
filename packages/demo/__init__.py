"""
示例技能包 - 展示 visible 和 default_enabled 字段用法

这个技能包展示如何配置技能包的可见性和默认启用状态。

配置说明：
- visible: 控制技能包是否对客户端可见
- default_enabled: 控制技能包是否在服务器启动时自动启用
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


SKILL_PACKAGE = {
    "name": "demo",
    "version": "1.0.0",
    "description": "示例技能包 - 展示 visible 和 default_enabled 字段用法",
    "author": "SkillMCP Team",
    
    # 字段 1: visible - 是否对客户端可见
    # True (默认): 客户端可以看到并控制
    # False: 完全隐藏，客户端看不到
    "visible": True,
    
    # 字段 2: default_enabled - 是否默认启用
    # True: 服务器启动时自动启用
    # False (默认): 需要手动启用
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


# ============================================================================
# 配置示例（供参考）
# ============================================================================

# 场景 1: 可见但默认不启用（最常见，当前配置）
# visible=True, default_enabled=False
# 客户端可以看到技能包，需要手动启用

# 场景 2: 可见且默认启用
# visible=True, default_enabled=True
# 客户端可以看到，启动时自动启用

# 场景 3: 不可见但默认启用（内部使用）
# visible=False, default_enabled=True
# 客户端看不到，启动时自动启用（仅供内部使用）

# 场景 4: 不可见且默认不启用（完全隐藏）
# visible=False, default_enabled=False
# 客户端看不到，也不启用（相当于禁用）
