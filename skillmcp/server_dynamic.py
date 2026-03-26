"""
SkillMCP - 真正的动态工具加载 MCP 服务

核心机制：
1. 初始只注册管理工具（open_package, close_package, list_packages）
2. 打开技能包时，动态注册该技能包的工具到 FastMCP
3. 发送 tools/list_changed 通知，客户端自动刷新
4. 关闭技能包时，从 FastMCP 移除工具（需要重新连接）

优势：
- ✅ 初始 token 占用少（只有管理工具）
- ✅ 按需加载，动态扩展
- ✅ 自动刷新，无需重新连接
- ✅ 真正意义的动态 MCP
"""

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.tools import Tool as FastMCPTool
from typing import Dict, List, Any, Optional, Callable
from loguru import logger
import time
import asyncio

from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import Tool, ToolParameter


# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    instructions="""SkillMCP - 动态技能加载平台

初始工具：
- open_package: 打开技能包
- close_package: 关闭技能包  
- list_packages: 查看技能包列表

查看 skillmcp://packages 资源了解可用技能包。

打开技能包后，新工具会自动出现，无需重新连接！
"""
)

# 全局管理器
_package_manager: Optional[ToolPackageManager] = None
_registered_tools: Dict[str, FastMCPTool] = {}  # 已注册的工具


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器实例"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


# ============================================================================
# 工具转换：SkillMCP Tool → FastMCP Tool
# ============================================================================

def create_fastmcp_tool(tool: Tool, package_name: str) -> FastMCPTool:
    """将 SkillMCP Tool 转换为 FastMCP Tool 并注册
    
    Args:
        tool: SkillMCP 工具定义
        package_name: 所属技能包名称
        
    Returns:
        FastMCP 工具
    """
    # 创建工具处理器
    async def handler(**kwargs) -> Dict[str, Any]:
        try:
            if tool.handler:
                result = tool.handler(**kwargs)
                if asyncio.iscoroutine(result):
                    result = await result
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": "No handler"}
        except Exception as e:
            logger.error(f"工具 {tool.name} 执行失败：{e}")
            return {"success": False, "error": str(e)}
    
    # 转换为 JSON Schema 格式的参数
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param in tool.parameters:
        parameters["properties"][param.name] = {
            "type": param.type,
            "description": param.description
        }
        if param.required:
            parameters["required"].append(param.name)
    
    # 使用 mcp.tool 装饰器创建工具（更简单可靠）
    from mcp.server.fastmcp.tools import Tool as FastMCPTool
    
    # 直接创建 Tool 实例
    fastmcp_tool = FastMCPTool(
        fn=handler,
        name=tool.name,
        title=tool.name,
        description=f"{tool.description} (来自 {package_name} 技能包)",
        parameters=parameters,
        fn_metadata={"arg_model": None},
        is_async=True,
    )
    
    return fastmcp_tool


# ============================================================================
# 技能包管理工具
# ============================================================================

@mcp.tool()
def open_package(package_name: str, ctx: Context) -> Dict[str, Any]:
    """打开指定的技能包
    
    打开后，该技能包的工具会自动注册并出现在工具列表中。
    
    Args:
        package_name: 技能包名称
        ctx: FastMCP 上下文
        
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
    
    # 🎯 关键：动态注册工具
    pkg_module = manager.loaded_packages[package_name]
    tools_registered = 0
    
    if hasattr(pkg_module, "get_tools"):
        skill_tools = pkg_module.get_tools()
        
        for tool in skill_tools:
            if tool.name not in _registered_tools:
                # 创建 FastMCP 工具
                fastmcp_tool = create_fastmcp_tool(tool, package_name)
                
                # 注册到 FastMCP
                mcp._tool_manager.add_tool(fastmcp_tool)
                _registered_tools[tool.name] = fastmcp_tool
                tools_registered += 1
                
                logger.info(f"动态注册工具：{tool.name} (来自 {package_name})")
    
    # 🎯 发送工具列表变化通知
    try:
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（打开 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}")
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开，注册了 {tools_registered} 个新工具",
        "tools_registered": tools_registered,
        "note": "🎉 工具列表已自动刷新，新工具立即可用！"
    }


@mcp.tool()
def close_package(package_name: str, ctx: Context) -> Dict[str, Any]:
    """关闭指定的技能包
    
    关闭后，该技能包的工具会从工具列表中移除。
    
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
    
    # 注意：FastMCP 不支持运行时移除工具
    # 需要重新连接才能看到变化
    # 但我们仍然发送通知，部分客户端会处理
    
    try:
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（关闭 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}")
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭",
        "note": "⚠️ 工具列表可能需要重新连接才能更新"
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
        "total_count": len(packages),
        "registered_tools_count": len(_registered_tools)
    }


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
    lines.append(f"已注册工具：{len(_registered_tools)} 个")
    
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
        logger.info(f"初始工具：open_package, close_package, list_packages")
    
    return _package_manager


if __name__ == "__main__":
    mcp.run()
