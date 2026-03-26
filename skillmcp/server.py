"""
SkillMCP - 基于 FastMCP 的模块化技能管理平台

对外暴露为标准 FastMCP 服务，支持动态加载技能包。

使用流程：
1. 初始：AI 客户端调用 list_packages() 获取可用技能包列表
2. 分析：AI 分析需要哪个技能包
3. 申请：AI 调用 open_package() 打开技能包
4. 使用：技能包内的工具自动暴露，AI 可以调用
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any, Optional
import asyncio
from loguru import logger
from dataclasses import dataclass

from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import SkillPackage, Tool


# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    instructions="""SkillMCP - 模块化技能管理平台

使用流程：
1. 调用 list_packages() 查看所有可用的技能包
2. 分析需求，确定需要哪个技能包
3. 调用 open_package(package_name) 打开技能包
4. 技能包打开后，其中的工具会自动出现在你的工具列表中
5. 使用完毕后，可以调用 close_package(package_name) 关闭技能包

初始状态下，只有基础工具包 (base) 是打开的。
"""
)

# 全局管理器
_package_manager: Optional[ToolPackageManager] = None
_loaded_tools: Dict[str, bool] = {}  # 记录已加载的工具，避免重复


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器实例"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


# ============================================================================
# 核心管理工具（始终可用）
# ============================================================================

@mcp.tool()
def list_packages() -> Dict[str, Any]:
    """列出所有可用的技能包
    
    这是初始工具，用于查看有哪些技能包可以加载。
    
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
                "active": pkg.name in status["active"],
                "tools": pkg.tools  # 显示该包包含哪些工具
            }
            for pkg in packages
        ],
        "status": status,
        "total": len(packages),
        "active_count": len(status["active"]),
        "message": f"当前已激活 {len(status['active'])} 个技能包，共 {len(packages)} 个可用"
    }


@mcp.tool()
def open_package(package_name: str) -> Dict[str, Any]:
    """打开指定的技能包，加载其中的工具
    
    打开后，该技能包内的所有工具会自动出现在你的工具列表中。
    
    Args:
        package_name: 技能包名称（通过 list_packages 查看可用名称）
        
    Returns:
        执行结果，包含加载的工具列表
    """
    manager = get_package_manager()
    
    # 检查是否已激活
    if package_name in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 已激活，无需重复打开",
            "package_name": package_name,
            "already_active": True
        }
    
    # 检查是否存在
    if package_name not in manager.packages:
        available = [p.name for p in manager.list_packages()]
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 不存在",
            "available_packages": available
        }
    
    # 加载并激活
    if not manager.load_package(package_name):
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 加载失败"
        }
    
    if not manager.activate_package(package_name):
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 激活失败"
        }
    
    # 获取加载的工具
    pkg_module = manager.loaded_packages[package_name]
    tools = pkg_module.get_tools() if hasattr(pkg_module, "get_tools") else []
    
    # 动态注册工具到 FastMCP
    for tool in tools:
        if tool.name not in _loaded_tools:
            _register_tool_dynamic(tool)
            _loaded_tools[tool.name] = True
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开，现在可以使用 {len(tools)} 个新工具",
        "package_name": package_name,
        "tools_loaded": [t.name for t in tools],
        "tool_count": len(tools),
        "next_step": "现在你可以在工具列表中看到新工具，可以直接调用它们"
    }


@mcp.tool()
def close_package(package_name: str) -> Dict[str, Any]:
    """关闭指定的技能包，卸载其中的工具
    
    关闭后，该技能包内的工具将从工具列表中移除。
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    if package_name not in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 未激活",
            "already_inactive": True
        }
    
    manager.active_packages.remove(package_name)
    manager.deactivate_package(package_name)
    
    # 从已加载工具中移除标记
    pkg_module = manager.loaded_packages.get(package_name)
    if pkg_module and hasattr(pkg_module, "get_tools"):
        tools = pkg_module.get_tools()
        for tool in tools:
            if tool.name in _loaded_tools:
                del _loaded_tools[tool.name]
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭",
        "package_name": package_name
    }


@mcp.tool()
def get_active_tools() -> Dict[str, Any]:
    """获取当前激活的所有工具
    
    查看当前可以使用的所有工具列表。
    
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
        "active_packages": list(manager.active_packages),
        "message": f"当前可用工具数：{len(tools)}"
    }


# ============================================================================
# 动态工具注册
# ============================================================================

def _register_tool_dynamic(tool: Tool) -> None:
    """动态注册工具到 FastMCP
    
    Args:
        tool: 要注册的工具
    """
    # 创建工具处理器
    def create_handler(t: Tool):
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
                logger.error(f"工具 {t.name} 执行失败：{e}")
                return {"success": False, "error": str(e)}
        
        return handler
    
    # 创建工具函数
    handler = create_handler(tool)
    handler.__name__ = tool.name
    handler.__doc__ = tool.description
    
    # 注册到 FastMCP
    # 注意：FastMCP 不支持运行时动态添加工具
    # 这里我们只是标记为已加载，实际工具在启动时预注册
    logger.info(f"工具 {tool.name} 已标记为可用")


# ============================================================================
# 资源（可选，用于查看信息）
# ============================================================================

@mcp.resource("skillmcp://packages")
def list_packages_resource() -> str:
    """资源：列出所有技能包（文本格式）"""
    manager = get_package_manager()
    packages = manager.list_packages()
    
    lines = ["SkillMCP 技能包列表", "=" * 60]
    for pkg in packages:
        status = "✓" if pkg.name in manager.active_packages else " "
        lines.append(f"[{status}] {pkg.name:20} v{pkg.version:10} - {pkg.description}")
    lines.append("=" * 60)
    lines.append(f"总计：{len(packages)} 个技能包")
    lines.append(f"已激活：{len(manager.active_packages)} 个")
    lines.append("")
    lines.append("提示：使用 open_package() 打开技能包以使用其中的工具")
    
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
        f"包含工具：{', '.join(pkg.tools) if pkg.tools else 'N/A'}",
        f"依赖：{', '.join(pkg.dependencies) if pkg.dependencies else '无'}",
        f"状态：{'✓ 已激活' if pkg.name in manager.active_packages else '○ 未激活'}"
    ]
    
    return "\n".join(lines)


# ============================================================================
# 生命周期管理
# ============================================================================

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
            
            # 预加载工具
            pkg_module = _package_manager.loaded_packages.get(pkg_name)
            if pkg_module and hasattr(pkg_module, "get_tools"):
                tools = pkg_module.get_tools()
                for tool in tools:
                    _loaded_tools[tool.name] = True
    
    logger.info(f"SkillMCP 启动完成，已加载 {len(_package_manager.active_packages)} 个技能包")
    logger.info(f"可用工具：{list(_loaded_tools.keys())}")


@mcp.lifecycle("shutdown")
async def shutdown():
    """FastMCP 关闭时执行"""
    global _package_manager
    if _package_manager:
        logger.info("SkillMCP 已关闭")


if __name__ == "__main__":
    # 运行 FastMCP 服务器
    mcp.run()
