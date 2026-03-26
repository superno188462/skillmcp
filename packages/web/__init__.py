"""
Web 工具包

提供 HTTP 请求、Webhook 等 Web 相关工具。
"""

SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 工具包 - 提供 HTTP 请求、Webhook 等工具",
    "author": "SkillMCP Team",
    "tools": ["http_get", "http_post", "http_put", "http_delete"],
    "dependencies": [],
    "default_visible": False,  # 默认不激活，需要时打开
    "category": "network",
    "tags": ["http", "web", "network", "api"],
}
