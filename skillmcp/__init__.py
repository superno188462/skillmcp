"""
SkillMCP - 模块化技能管理平台

一个采用工具包机制的 MCP 服务，支持按需加载工具、插件化架构。
"""

__version__ = "0.1.0"
__author__ = "superno188462"

from skillmcp.core.gateway import SkillMCPGateway
from skillmcp.core.registry import SkillRegistry
from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import Skill, Tool, ToolParameter

__all__ = [
    "SkillMCPGateway",
    "SkillRegistry",
    "ToolPackageManager",
    "Skill",
    "Tool",
    "ToolParameter",
]
