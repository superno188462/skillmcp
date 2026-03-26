"""
核心工具包

提供基础的包管理和技能管理工具。
"""

SKILL_PACKAGE = {
    "name": "core",
    "version": "1.0.0",
    "description": "核心工具包 - 提供基础的包管理和技能管理工具",
    "author": "SkillMCP Team",
    "tools": ["list_packages", "open_package", "close_package", "get_active_tools"],
    "dependencies": [],
    "default_visible": True,  # 默认显示/加载
    "category": "system",
    "tags": ["core", "management", "essential"],
}
