"""
SkillMCP - 基于 FastMCP Provider 系统的动态工具加载平台

使用 FastMCP v3.0.0+ 的 Provider 系统实现：
- LocalProvider 管理工具
- remove_tool() 动态移除工具
- enable()/disable() 控制可见性
- 真正的动态 MCP

优势：
- ✅ 官方 Provider 系统支持
- ✅ 完整的工具生命周期管理
- ✅ 更优雅的 API
- ✅ 未来兼容性更好
"""

from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider
from typing import Dict, List, Any, Optional
from loguru import logger
import asyncio

from skillmcp.core.package_manager import ToolPackageManager


# 创建 LocalProvider
provider = LocalProvider()

# 创建 FastMCP 实例，使用 Provider
mcp = FastMCP(
    name="SkillMCP",
    providers=[provider],
    instructions="""SkillMCP - 动态技能加载平台

初始工具（仅 3 个）：
- open_package: 打开技能包
- close_package: 关闭技能包
- list_packages: 查看技能包列表

查看 skillmcp://packages 资源了解可用技能包。

打开技能包后，新工具会自动出现，无需重新连接！
"""
)

# 全局状态
_package_manager: Optional[ToolPackageManager] = None
_active_packages: set = set()
_package_tools: Dict[str, List[str]] = {}  # 记录每个技能包注册的工具


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


# ============================================================================
# 管理工具
# ============================================================================

@provider.tool
def open_package(package_name: str) -> Dict[str, Any]:
    """打开指定的技能包
    
    打开后，该技能包的工具会自动注册并出现在工具列表中。
    客户端会自动刷新工具列表，无需重新连接。
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    manager = get_package_manager()
    
    # 检查是否已激活
    if package_name in _active_packages:
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
    
    # 加载技能包
    if not manager.load_package(package_name):
        return {"success": False, "error": "加载失败"}
    
    _active_packages.add(package_name)
    
    # 🎯 使用 Provider 动态注册工具
    pkg_module = manager.loaded_packages[package_name]
    tools_registered = 0
    
    if hasattr(pkg_module, "get_tools"):
        skill_tools = pkg_module.get_tools()
        tool_names = []
        
        for tool in skill_tools:
            try:
                # 创建工具处理器
                tool_desc = tool.description if hasattr(tool, 'description') else ''
                tool_handler = tool.handler if hasattr(tool, 'handler') else None
                tool_name = tool.name
                tool_params = tool.parameters if hasattr(tool, 'parameters') and tool.parameters else []
                
                # 使用 inspect 创建有明确签名的处理器
                import inspect
                
                # 构建参数字符串
                param_strs = []
                for param in tool_params:
                    param_name = param.name
                    param_type = param.type if hasattr(param, 'type') else 'Any'
                    if param_type == 'object':
                        param_type = 'Dict[str, Any]'
                    elif param_type == 'string':
                        param_type = 'str'
                    elif param_type == 'number':
                        param_type = 'float'
                    elif param_type == 'integer':
                        param_type = 'int'
                    elif param_type == 'boolean':
                        param_type = 'bool'
                    else:
                        param_type = 'Any'
                    
                    if hasattr(param, 'required') and param.required:
                        param_strs.append(f"{param_name}: {param_type}")
                    else:
                        param_strs.append(f"{param_name}: Optional[{param_type}] = None")
                
                params_str = ", ".join(param_strs)
                
                # 动态创建函数
                if tool_handler:
                    # 创建函数代码
                    func_code = f"""
async def handler({params_str}):
    try:
        kwargs = {{}}
        for name, value in locals().items():
            if name != 'self':
                kwargs[name] = value
        result = tool_handler(**kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return {{"success": True, "data": result}}
    except Exception as e:
        logger.error(f"工具执行失败：{{e}}")
        return {{"success": False, "error": str(e)}}
"""
                else:
                    func_code = f"""
async def handler({params_str}):
    return {{"success": False, "error": "No handler"}}
"""
                
                # 执行代码创建函数
                local_ns = {
                    'asyncio': asyncio,
                    'logger': logger,
                    'tool_handler': tool_handler,
                    'Optional': Optional,
                    'Dict': Dict,
                    'Any': Any
                }
                exec(func_code, {}, local_ns)
                handler = local_ns['handler']
                
                # 设置函数属性
                handler.__name__ = tool_name
                handler.__doc__ = f"{tool_desc} (来自 {package_name} 技能包)"
                
                # 使用 provider.tool 装饰器注册
                provider.tool()(handler)
                tool_names.append(tool_name)
                tools_registered += 1
                
                logger.info(f"Provider 注册工具：{tool_name} (来自 {package_name})")
                
            except Exception as e:
                logger.error(f"注册工具 {tool.name} 失败：{e}")
        
        _package_tools[package_name] = tool_names
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开，注册了 {tools_registered} 个新工具",
        "tools_registered": tools_registered,
        "note": "🎉 工具列表已自动刷新，新工具立即可用！"
    }


@provider.tool
def close_package(package_name: str) -> Dict[str, Any]:
    """关闭指定的技能包
    
    关闭后，该技能包的工具会从工具列表中移除。
    
    Args:
        package_name: 技能包名称
        
    Returns:
        执行结果
    """
    if package_name not in _active_packages:
        return {"success": True, "message": f"技能包 '{package_name}' 未激活"}
    
    _active_packages.remove(package_name)
    
    # 🎯 使用 Provider 移除工具
    tools_removed = 0
    
    if package_name in _package_tools:
        for tool_name in _package_tools[package_name]:
            try:
                provider.remove_tool(tool_name)
                tools_removed += 1
                logger.info(f"Provider 移除工具：{tool_name}")
            except Exception as e:
                logger.warning(f"移除工具 {tool_name} 失败：{e}")
        
        del _package_tools[package_name]
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭，移除了 {tools_removed} 个工具",
        "tools_removed": tools_removed,
        "note": "⚠️ 工具列表已更新"
    }


@provider.tool
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
                "active": pkg.name in _active_packages
            }
            for pkg in packages
        ],
        "active_count": len(_active_packages),
        "total_count": len(packages),
        "registered_tools_count": sum(len(tools) for tools in _package_tools.values())
    }


# ============================================================================
# 资源：技能包信息
# ============================================================================

@provider.resource("skillmcp://packages")
def list_packages_resource() -> str:
    """资源：技能包列表"""
    manager = get_package_manager()
    packages = manager.list_packages()
    
    lines = ["SkillMCP 技能包列表", "=" * 60]
    for pkg in packages:
        status = "✓ 已激活" if pkg.name in _active_packages else "○ 未激活"
        lines.append(f"[{status}] {pkg.name:20} - {pkg.description}")
        lines.append(f"       工具：{', '.join(pkg.tools)}")
    lines.append("=" * 60)
    lines.append(f"总计：{len(packages)} 个 | 已激活：{len(_active_packages)} 个")
    lines.append(f"已注册工具：{sum(len(tools) for tools in _package_tools.values())} 个")
    
    return "\n".join(lines)


# ============================================================================
# 初始化
# ============================================================================

def initialize_server() -> ToolPackageManager:
    """初始化服务器"""
    manager = get_package_manager()
    logger.info(f"SkillMCP 初始化完成 (FastMCP {__import__('fastmcp').__version__})")
    logger.info(f"发现 {len(manager.packages)} 个技能包")
    logger.info(f"初始工具：open_package, close_package, list_packages")
    logger.info(f"使用 Provider 系统：{type(provider).__name__}")
    return manager


if __name__ == "__main__":
    initialize_server()
    mcp.run()
