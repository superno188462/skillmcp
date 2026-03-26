"""
SkillMCP - 基于 FastMCP 的模块化技能管理平台

对外暴露为标准 FastMCP 服务，支持动态加载技能包。
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any
import asyncio
from loguru import logger

from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import SkillPackage, Tool


# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    instructions="模块化技能管理平台 - 支持动态加载技能包"
)

# 全局管理器
_package_manager: ToolPackageManager = None


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器实例"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


@mcp.tool()
def list_packages() -> Dict[str, Any]:
    """列出所有可用的技能包
    
    Returns:
        包含技能包列表和状态的字典
    """
    manager = get_package_manager()
    packages = manager.list_packages()
    status = manager.get_package_status()
    
    return {
        "packages": [
            {
                "name": pkg.name,
                "version": pkg.version,
                "description": pkg.description,
                "category": pkg.category,
                "tags": pkg.tags,
                "default_visible": pkg.default_visible,
                "active": pkg.name in status["active"]
            }
            for pkg in packages
        ],
        "status": status,
        "total": len(packages),
        "active_count": len(status["active"])
    }


@mcp.tool()
def open_package(package_name: str) -> Dict[str, Any]:
    """打开指定的技能包，加载其中的工具
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    # 检查是否已激活
    if package_name in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 已激活",
            "package_name": package_name
        }
    
    # 加载并激活
    if not manager.load_package(package_name):
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 不存在或加载失败"
        }
    
    if not manager.activate_package(package_name):
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 激活失败"
        }
    
    # 获取加载的工具
    pkg_module = manager.loaded_packages[package_name]
    tools = pkg_module.get_tools() if hasattr(pkg_module, "get_tools") else []
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已打开",
        "package_name": package_name,
        "tools_loaded": [t.name for t in tools],
        "tool_count": len(tools)
    }


@mcp.tool()
def close_package(package_name: str) -> Dict[str, Any]:
    """关闭指定的技能包，卸载其中的工具
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    if package_name not in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 未激活"
        }
    
    manager.active_packages.remove(package_name)
    manager.deactivate_package(package_name)
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭",
        "package_name": package_name
    }


@mcp.tool()
def get_active_tools() -> Dict[str, Any]:
    """获取当前激活的所有工具
    
    Returns:
        工具列表和统计信息
    """
    manager = get_package_manager()
    tools = manager.get_active_tools()
    
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": [p.to_dict() for p in tool.parameters]
            }
            for tool in tools
        ],
        "count": len(tools),
        "active_packages": list(manager.active_packages)
    }


# 动态添加工具包中的工具
def load_package_tools(package_name: str) -> None:
    """从技能包加载工具并注册到 FastMCP
    
    Args:
        package_name: 技能包名称
    """
    manager = get_package_manager()
    
    if package_name not in manager.loaded_packages:
        if not manager.load_package(package_name):
            return
    
    pkg_module = manager.loaded_packages[package_name]
    if not hasattr(pkg_module, "get_tools"):
        return
    
    tools = pkg_module.get_tools()
    
    for tool in tools:
        # 为每个工具创建 FastMCP tool 装饰器
        def create_tool_handler(t: Tool):
            @mcp.tool()
            async def handler(**kwargs) -> Dict[str, Any]:
                try:
                    if t.handler:
                        result = t.handler(**kwargs)
                        if asyncio.iscoroutine(result):
                            result = await result
                        return {"success": True, "data": result}
                    else:
                        return {"success": False, "error": "No handler"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            
            return handler
        
        # 创建工具函数
        tool_func = create_tool_handler(tool)
        tool_func.__name__ = tool.name
        tool_func.__doc__ = tool.description


@mcp.resource("skillmcp://packages")
def list_packages_resource() -> str:
    """资源：列出所有技能包（文本格式）"""
    manager = get_package_manager()
    packages = manager.list_packages()
    
    lines = ["SkillMCP 技能包列表", "=" * 50]
    for pkg in packages:
        status = "✓" if pkg.name in manager.active_packages else " "
        lines.append(f"[{status}] {pkg.name:20} v{pkg.version:10} - {pkg.description}")
    lines.append("=" * 50)
    lines.append(f"总计：{len(packages)} 个技能包")
    
    return "\n".join(lines)


@mcp.resource("skillmcp://packages/{package_name}")
def get_package_info(package_name: str) -> str:
    """资源：获取技能包详情
    
    Args:
        package_name: 技能包名称
    """
    manager = get_package_manager()
    packages = manager.discover_packages()
    
    pkg = next((p for p in packages if p.name == package_name), None)
    
    if not pkg:
        return f"错误：技能包 '{package_name}' 不存在"
    
    lines = [
        f"技能包：{pkg.name}",
        f"版本：{pkg.version}",
        f"描述：{pkg.description}",
        f"作者：{pkg.author or 'N/A'}",
        f"分类：{pkg.category}",
        f"标签：{', '.join(pkg.tags) if pkg.tags else 'N/A'}",
        f"默认加载：{'是' if pkg.default_visible else '否'}",
        f"工具：{', '.join(pkg.tools) if pkg.tools else 'N/A'}",
        f"依赖：{', '.join(pkg.dependencies) if pkg.dependencies else '无'}",
        f"状态：{'已激活' if pkg.name in manager.active_packages else '未激活'}"
    ]
    
    return "\n".join(lines)


@mcp.prompt()
def open_package_prompt(package_name: str) -> str:
    """提示词模板：打开技能包
    
    Args:
        package_name: 技能包名称
    """
    return f"请打开技能包 '{package_name}' 以使用其中的工具。"


@mcp.prompt()
def list_tools_prompt() -> str:
    """提示词模板：列出当前可用工具"""
    return "请列出当前所有可用的工具。"


# 初始化时自动加载默认可见的技能包
@mcp.lifecycle("startup")
async def startup():
    """FastMCP 启动时执行"""
    global _package_manager
    _package_manager = ToolPackageManager()
    _package_manager.discover_packages()
    
    # 自动加载默认可见的技能包
    for pkg_name, pkg_info in _package_manager.packages.items():
        if _package_manager._get_package_default_visibility(pkg_name):
            _package_manager.activate_package(pkg_name)
            logger.info(f"自动加载默认技能包：{pkg_name}")
    
    logger.info(f"SkillMCP 启动完成，已加载 {len(_package_manager.active_packages)} 个技能包")


@mcp.lifecycle("shutdown")
async def shutdown():
    """FastMCP 关闭时执行"""
    global _package_manager
    if _package_manager:
        logger.info("SkillMCP 已关闭")


if __name__ == "__main__":
    # 运行 FastMCP 服务器
    mcp.run()
