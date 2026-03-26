"""
基础工具包

提供基础的包管理工具。
"""

SKILL_PACKAGE = {
    "name": "base",
    "version": "1.0.0",
    "description": "基础工具包 - 提供包管理工具",
    "author": "SkillMCP Team",
    "tools": ["list_packages", "open_package", "close_package", "get_active_tools"],
    "dependencies": [],
    "default_visible": True,  # 默认加载
    "category": "system",
    "tags": ["base", "management"],
}
