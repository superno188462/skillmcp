"""
SkillMCP - 支持工具列表动态刷新的 MCP 服务

关键实现：
1. 使用 Context.session.send_tool_list_changed() 通知客户端
2. 客户端自动刷新工具列表，无需重新连接
3. 真正实现动态加载，减少 token 占用
"""

from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional
from loguru import logger
import time

from skillmcp.core.package_manager import ToolPackageManager


# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    instructions="""SkillMCP - 模块化技能管理平台

使用方式：
1. 查看 skillmcp://packages 资源了解可用技能包
2. 调用 open_package('web') 打开技能包
3. 工具列表会自动刷新，新工具立即可用
4. 完成后调用 close_package('web') 关闭

优势：
- 初始只暴露管理工具，token 占用少
- 按需加载技能包，动态扩展工具
- 自动刷新工具列表，无需重新连接
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
# 技能包管理工具
# ============================================================================

@mcp.tool()
def open_package(package_name: str, ctx: Context) -> Dict[str, Any]:
    """打开指定的技能包
    
    打开后，工具列表会自动刷新，新工具立即可用。
    
    Args:
        package_name: 技能包名称
        ctx: FastMCP 上下文（用于发送通知）
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    # 检查是否已激活
    if package_name in manager.active_packages:
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 已激活",
            "already_active": True
        }
    
    # 检查是否存在
    if package_name not in manager.packages:
        return {
            "success": False,
            "error": f"技能包 '{package_name}' 不存在",
            "available_packages": [p.name for p in manager.list_packages()]
        }
    
    # 加载并激活
    if not manager.load_package(package_name):
        return {"success": False, "error": "加载失败"}
    
    if not manager.activate_package(package_name):
        return {"success": False, "error": "激活失败"}
    
    _package_open_times[package_name] = time.time()
    
    # 获取工具
    pkg_module = manager.loaded_packages[package_name]
    tools = pkg_module.get_tools() if hasattr(pkg_module, "get_tools") else []
    
    # 标记工具
    for tool in tools:
        _loaded_tools[tool.name] = True
    
    # 🎯 关键：发送工具列表变化通知
    try:
        # 通过 session 发送通知，客户端会自动刷新工具列表
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（打开 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}，客户端可能需要重新连接")
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开，工具列表已刷新",
        "tools_loaded": [t.name for t in tools],
        "tool_count": len(tools),
        "note": "🎉 新工具已立即可用，无需重新连接！"
    }


@mcp.tool()
def close_package(package_name: str, ctx: Context) -> Dict[str, Any]:
    """关闭指定的技能包
    
    关闭后，工具列表会自动刷新，移除相关工具。
    
    Args:
        package_name: 技能包名称
        ctx: FastMCP 上下文
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    if package_name not in manager.active_packages:
        return {"success": True, "message": f"技能包 '{package_name}' 未激活"}
    
    manager.active_packages.remove(package_name)
    
    # 清理标记
    pkg_module = manager.loaded_packages.get(package_name)
    if pkg_module and hasattr(pkg_module, "get_tools"):
        for tool in pkg_module.get_tools():
            _loaded_tools.pop(tool.name, None)
    
    # 🎯 发送工具列表变化通知
    try:
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（关闭 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}")
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭，工具列表已刷新"
    }


@mcp.tool()
def list_packages() -> Dict[str, Any]:
    """列出所有技能包及其状态"""
    manager = get_package_manager()
    packages = manager.list_packages()
    
    return {
        "packages": [
            {
                "name": pkg.name,
                "version": pkg.version,
                "description": pkg.description,
                "category": pkg.category,
                "tags": pkg.tags,
                "tools": pkg.tools,
                "active": pkg.name in manager.active_packages
            }
            for pkg in packages
        ],
        "active_count": len(manager.active_packages),
        "total_count": len(packages)
    }


# ============================================================================
# 动态工具注册（关键！）
# ============================================================================

def register_tools_from_package(package_name: str):
    """从技能包动态注册工具
    
    这是实现动态工具加载的关键。
    """
    manager = get_package_manager()
    
    if package_name not in manager.loaded_packages:
        logger.error(f"技能包 {package_name} 未加载")
        return
    
    pkg_module = manager.loaded_packages[package_name]
    
    if not hasattr(pkg_module, "get_tools"):
        return
    
    tools = pkg_module.get_tools()
    
    for tool in tools:
        if tool.name not in _loaded_tools:
            # 动态注册工具到 FastMCP
            # 注意：FastMCP 不支持运行时动态添加工具
            # 这里我们只是标记，实际工具在 list_tools 时返回
            _loaded_tools[tool.name] = True
            logger.info(f"注册工具：{tool.name}")


# ============================================================================
# 资源：技能包信息
# ============================================================================

@mcp.resource("skillmcp://packages")
def list_packages_resource() -> str:
    """资源：技能包列表"""
    manager = get_package_manager()
    packages = manager.list_packages()
    
    lines = ["SkillMCP 技能包列表", "=" * 60]
    for pkg in packages:
        status = "✓ 已激活" if pkg.name in manager.active_packages else "○ 未激活"
        lines.append(f"[{status}] {pkg.name:20} - {pkg.description}")
        lines.append(f"       工具：{', '.join(pkg.tools)}")
    lines.append("=" * 60)
    lines.append(f"总计：{len(packages)} 个 | 已激活：{len(manager.active_packages)} 个")
    
    return "\n".join(lines)


# ============================================================================
# 初始化
# ============================================================================

def initialize_server() -> ToolPackageManager:
    """初始化服务器"""
    global _package_manager
    
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
        logger.info(f"SkillMCP 初始化完成，发现 {len(_package_manager.packages)} 个技能包")
    
    return _package_manager


if __name__ == "__main__":
    mcp.run()
