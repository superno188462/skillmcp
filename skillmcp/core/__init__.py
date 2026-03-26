"""
SkillMCP 核心模块
"""

from skillmcp.core.interfaces import Skill, Tool, ToolParameter, ToolResult, PackageInfo, SkillInfo
from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.registry import SkillRegistry
from skillmcp.core.gateway import SkillMCPGateway

__all__ = [
    "Skill",
    "Tool",
    "ToolParameter",
    "ToolResult",
    "PackageInfo",
    "SkillInfo",
    "ToolPackageManager",
    "SkillRegistry",
    "SkillMCPGateway",
]
