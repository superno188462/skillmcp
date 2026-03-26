"""
SkillMCP - 基于 FastMCP 的模块化技能管理平台

设计理念：
1. 初始暴露所有技能包的描述（作为资源）
2. 技能包描述中说明功能和打开方式
3. AI 根据描述决定打开哪个技能包
4. 打开后，技能包内的工具自动可用
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any, Optional
import asyncio
from loguru import logger
import time
import json

from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import SkillPackage, Tool


# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    instructions="""你是一个模块化技能管理平台的助手。

可用技能包：
- web: HTTP 请求、Webhook 等网络工具
- data: 数据处理、文件操作工具

使用方式：
当用户需要某个功能时，你可以说：
"我可以使用 [技能包名] 技能包来完成这个任务，需要我打开它吗？"

用户同意后，调用 open_package 打开技能包，然后使用其中的工具。
"""
)

# 全局管理器
_package_manager: Optional[ToolPackageManager] = None
_loaded_tools: Dict[str, bool] = {}
_package_open_times: Dict[str, float] = {}


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器实例"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


# ============================================================================
# 核心工具：打开/关闭技能包
# ============================================================================

@mcp.tool()
def open_package(package_name: str, reason: str = None) -> Dict[str, Any]:
    """打开指定的技能包以使用其中的工具
    
    Args:
        package_name: 技能包名称
        reason: 打开原因（可选）
        
    Returns:
        执行结果
    """
    import time
    from mcp.server.fastmcp import Context
    
    manager = get_package_manager()
    
    # 检查是否已激活
    if package_name in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 已激活，可以直接使用其中的工具",
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
        return {"success": False, "error": f"技能包 '{package_name}' 加载失败"}
    
    if not manager.activate_package(package_name):
        return {"success": False, "error": f"技能包 '{package_name}' 激活失败"}
    
    # 记录打开时间
    _package_open_times[package_name] = time.time()
    
    # 获取工具
    pkg_module = manager.loaded_packages[package_name]
    tools = pkg_module.get_tools() if hasattr(pkg_module, "get_tools") else []
    
    # 标记工具
    for tool in tools:
        if tool.name not in _loaded_tools:
            _loaded_tools[tool.name] = True
    
    # 警告
    total_tools = len(_loaded_tools)
    warning = ""
    if total_tools > 20:
        warning = f"\n⚠️ 当前已有 {total_tools} 个工具，建议完成后清理"
    
    # 发送工具列表变化通知（如果支持）
    try:
        # 尝试获取上下文并发送通知
        # 注意：这需要在请求上下文中才能工作
        pass
    except Exception:
        # 如果无法发送通知，在消息中提示
        pass
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开，可以使用 {len(tools)} 个新工具{warning}",
        "tools_loaded": [t.name for t in tools],
        "tool_count": len(tools),
        "total_active_tools": total_tools,
        "note": "💡 提示：如果看不到新工具，请重新连接 MCP 服务器"
    }


@mcp.tool()
def close_package(package_name: str) -> Dict[str, Any]:
    """关闭技能包，释放其中的工具
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    if package_name not in manager.active_packages:
        return {"success": True, "message": f"技能包 '{package_name}' 未激活"}
    
    manager.active_packages.remove(package_name)
    manager.deactivate_package(package_name)
    
    # 清理标记
    pkg_module = manager.loaded_packages.get(package_name)
    if pkg_module and hasattr(pkg_module, "get_tools"):
        for tool in pkg_module.get_tools():
            _loaded_tools.pop(tool.name, None)
    
    return {"success": True, "message": f"技能包 '{package_name}' 已关闭"}


@mcp.tool()
def close_all_packages(exclude: List[str] = None) -> Dict[str, Any]:
    """关闭所有技能包（可选排除）
    
    Args:
        exclude: 不关闭的技能包列表
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    if exclude is None:
        exclude = []
    
    closed = []
    for pkg_name in list(manager.active_packages):
        if pkg_name not in exclude:
            manager.active_packages.remove(pkg_name)
            manager.deactivate_package(pkg_name)
            closed.append(pkg_name)
    
    # 清理标记
    for pkg_name in closed:
        pkg_module = manager.loaded_packages.get(pkg_name)
        if pkg_module and hasattr(pkg_module, "get_tools"):
            for tool in pkg_module.get_tools():
                _loaded_tools.pop(tool.name, None)
    
    return {
        "success": True,
        "message": f"已关闭 {len(closed)} 个技能包",
        "closed_packages": closed,
        "remaining": list(manager.active_packages)
    }


# ============================================================================
# 资源：技能包描述（关键！）
# ============================================================================

@mcp.resource("skillmcp://packages")
def list_all_packages() -> str:
    """资源：所有可用技能包及其功能描述
    
    这个资源会暴露给 AI，让 AI 知道有哪些技能包可用。
    """
    manager = get_package_manager()
    packages = manager.list_packages()
    
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║              SkillMCP 可用技能包列表                      ║",
        "╚══════════════════════════════════════════════════════════╝",
        ""
    ]
    
    for pkg in packages:
        status = "✓ 已激活" if pkg.name in manager.active_packages else "○ 未激活"
        lines.append(f"┌─────────────────────────────────────────────────────┐")
        lines.append(f"│ 📦 {pkg.name.upper():20} {status:15} │")
        lines.append(f"├─────────────────────────────────────────────────────┤")
        lines.append(f"│ 描述：{pkg.description:48} │")
        lines.append(f"│ 分类：{pkg.category:48} │")
        lines.append(f"│ 工具：{', '.join(pkg.tools) if pkg.tools else '见详情':48} │")
        lines.append(f"│ 标签：{', '.join(pkg.tags) if pkg.tags else 'N/A':48} │")
        lines.append(f"├─────────────────────────────────────────────────────┤")
        
        if pkg.name not in manager.active_packages:
            lines.append(f"│ 💡 提示：如需使用此技能包，请调用 open_package    │")
        else:
            lines.append(f"│ ✅ 此技能包已激活，可以直接使用其中的工具        │")
        
        lines.append(f"└─────────────────────────────────────────────────────┘")
        lines.append("")
    
    lines.append(f"总计：{len(packages)} 个技能包 | 已激活：{len(manager.active_packages)} 个")
    
    return "\n".join(lines)


@mcp.resource("skillmcp://packages/{package_name}/details")
def get_package_details(package_name: str) -> str:
    """资源：技能包详细信息
    
    Args:
        package_name: 技能包名称
    """
    manager = get_package_manager()
    packages = manager.discover_packages()
    
    pkg = next((p for p in packages if p.name == package_name), None)
    
    if not pkg:
        return f"❌ 技能包 '{package_name}' 不存在\n\n可用技能包：{[p.name for p in packages]}"
    
    lines = [
        f"╔══════════════════════════════════════════════════════════╗",
        f"║  技能包详情：{pkg.name.upper():42} ║",
        f"╚══════════════════════════════════════════════════════════╝",
        "",
        f"📦 名称：{pkg.name}",
        f"📌 版本：{pkg.version}",
        f"📝 描述：{pkg.description}",
        f"🏷️  分类：{pkg.category}",
        f"🏷️  标签：{', '.join(pkg.tags) if pkg.tags else 'N/A'}",
        f"👤 作者：{pkg.author or 'N/A'}",
        "",
        f"🔧 包含工具:",
    ]
    
    for tool_name in pkg.tools:
        lines.append(f"   • {tool_name}")
    
    if pkg.dependencies:
        lines.append(f"\n🔗 依赖：{', '.join(pkg.dependencies)}")
    
    lines.append(f"\n💡 使用方式:")
    if pkg.name in manager.active_packages:
        lines.append(f"   ✅ 已激活，可以直接使用上述工具")
    else:
        lines.append(f"   1. 调用 open_package(package_name='{pkg.name}') 打开")
        lines.append(f"   2. 使用上述工具完成任务")
        lines.append(f"   3. 调用 close_package(package_name='{pkg.name}') 关闭")
    
    return "\n".join(lines)


# ============================================================================
# 辅助工具
# ============================================================================

@mcp.tool()
def get_package_info(package_name: str) -> Dict[str, Any]:
    """获取技能包详细信息
    
    Args:
        package_name: 技能包名称
        
    Returns:
        技能包信息
    """
    manager = get_package_manager()
    packages = manager.discover_packages()
    
    pkg = next((p for p in packages if p.name == package_name), None)
    
    if not pkg:
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 不存在",
            "available": [p.name for p in packages]
        }
    
    return {
        "success": True,
        "package": pkg.to_dict(),
        "active": pkg.name in manager.active_packages
    }


@mcp.tool()
def get_usage_stats() -> Dict[str, Any]:
    """获取使用情况统计
    
    Returns:
        统计信息
    """
    manager = get_package_manager()
    tools = manager.get_active_tools()
    
    estimated_tokens = len(tools) * 75
    
    return {
        "active_packages": list(manager.active_packages),
        "active_package_count": len(manager.active_packages),
        "active_tools_count": len(tools),
        "estimated_token_usage": estimated_tokens,
        "total_packages": len(manager.packages),
        "warning": "⚠️ 工具数量过多可能影响性能" if len(tools) > 20 else "✅ 工具数量合理",
        "suggestion": "建议调用 close_all_packages() 清理" if len(tools) > 15 else "当前状态良好"
    }


# ============================================================================
# 初始化
# ============================================================================

def initialize_server() -> ToolPackageManager:
    """初始化服务器"""
    global _package_manager
    
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
        
        # 不自动加载任何技能包，所有技能包默认都是未激活状态
        # AI 需要根据需求主动打开技能包
        logger.info(f"SkillMCP 初始化完成，发现 {len(_package_manager.packages)} 个技能包")
        logger.info(f"可用技能包：{list(_package_manager.packages.keys())}")
        logger.info("提示：所有技能包默认未激活，需要时调用 open_package 打开")
    
    return _package_manager


if __name__ == "__main__":
    mcp.run()
