"""
SkillMCP - 基于 FastMCP Provider 系统的动态工具加载平台

设计理念：
1. 每个技能包作为一个"工具"暴露给 AI
2. 工具包有开关参数控制启用/禁用
3. 启用后，技能包内的子工具自动可用
4. 没有"管理工具"，所有工具都是业务工具
"""

from fastmcp import FastMCP
from fastmcp.server.providers import LocalProvider
from typing import Dict, List, Any, Optional
from loguru import logger
import asyncio

from skillmcp.core.package_manager import ToolPackageManager


# 创建 LocalProvider
provider = LocalProvider()

# 创建 FastMCP 实例
mcp = FastMCP(
    name="SkillMCP",
    providers=[provider],
    instructions="""SkillMCP - 模块化技能平台

可用技能包（作为工具暴露）：
- web_tool: Web 技能包（启用后提供 http_get, http_post 等工具）
- data_tool: 数据技能包（启用后提供数据处理工具）

使用方式：
调用 web_tool(enable=True) 启用 Web 技能包
调用 web_tool(enable=False) 禁用 Web 技能包
"""
)

# 全局状态
_package_manager: Optional[ToolPackageManager] = None
_active_packages: set = set()
_package_tools: Dict[str, List[str]] = {}  # 记录每个技能包注册的子工具


def get_package_manager() -> ToolPackageManager:
    """获取工具包管理器"""
    global _package_manager
    if _package_manager is None:
        _package_manager = ToolPackageManager()
        _package_manager.discover_packages()
    return _package_manager


# ============================================================================
# 动态创建技能包工具
# ============================================================================

def create_package_tool(package_name: str, package_info: dict) -> None:
    """为技能包创建一个控制工具
    
    Args:
        package_name: 技能包名称
        package_info: 技能包信息
    """
    
    # 创建技能包控制工具
    tool_name = f"{package_name}_tool"
    tool_desc = f"{package_info['description']}（启用后提供：{', '.join(package_info.get('tools', []))}）"
    
    # 动态创建工具函数
    def make_package_tool(pkg_name: str, pkg_desc: str, pkg_tools: list):
        async def package_tool(enable: bool) -> Dict[str, Any]:
            """技能包控制工具
            
            Args:
                enable: 是否启用此技能包
            """
            manager = get_package_manager()
            
            if enable:
                # 启用技能包
                if pkg_name in _active_packages:
                    return {
                        "success": True,
                        "message": f"技能包 '{pkg_name}' 已启用",
                        "already_active": True,
                        "sub_tools": pkg_tools
                    }
                
                # 加载并注册子工具
                if not manager.load_package(pkg_name):
                    return {"success": False, "error": "加载失败"}
                
                _active_packages.add(pkg_name)
                
                # 注册子工具
                pkg_module = manager.loaded_packages[pkg_name]
                sub_tools_registered = 0
                
                if hasattr(pkg_module, "get_tools"):
                    skill_tools = pkg_module.get_tools()
                    sub_tool_names = []
                    
                    for tool in skill_tools:
                        try:
                            tool_name = tool.name
                            tool_desc = tool.description if hasattr(tool, 'description') else ''
                            tool_handler = tool.handler if hasattr(tool, 'handler') else None
                            tool_params = tool.parameters if hasattr(tool, 'parameters') and tool.parameters else []
                            
                            # 构建参数字符串
                            import inspect
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
                            
                            # 动态创建子工具函数
                            if tool_handler:
                                func_code = f"""
async def sub_handler({params_str}):
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
async def sub_handler({params_str}):
    return {{"success": False, "error": "No handler"}}
"""
                            
                            local_ns = {
                                'asyncio': asyncio,
                                'logger': logger,
                                'tool_handler': tool_handler,
                                'Optional': Optional,
                                'Dict': Dict,
                                'Any': Any
                            }
                            exec(func_code, {}, local_ns)
                            sub_handler = local_ns['sub_handler']
                            
                            # 设置函数属性
                            sub_handler.__name__ = tool_name
                            sub_handler.__doc__ = f"{tool_desc} (来自 {pkg_name} 技能包)"
                            
                            # 注册子工具
                            provider.tool()(sub_handler)
                            sub_tool_names.append(tool_name)
                            sub_tools_registered += 1
                            
                            logger.info(f"注册子工具：{tool_name} (来自 {pkg_name})")
                            
                        except Exception as e:
                            logger.error(f"注册子工具失败：{e}")
                    
                    _package_tools[pkg_name] = sub_tool_names
                
                return {
                    "success": True,
                    "message": f"✅ 技能包 '{pkg_name}' 已启用，注册了 {sub_tools_registered} 个子工具",
                    "sub_tools_registered": sub_tools_registered,
                    "sub_tools": sub_tool_names,
                    "note": "🎉 子工具已立即可用！"
                }
            
            else:
                # 禁用技能包
                if pkg_name not in _active_packages:
                    return {
                        "success": True,
                        "message": f"技能包 '{pkg_name}' 未启用",
                        "already_inactive": True
                    }
                
                _active_packages.remove(pkg_name)
                
                # 移除子工具
                sub_tools_removed = 0
                if pkg_name in _package_tools:
                    for sub_tool_name in _package_tools[pkg_name]:
                        try:
                            provider.remove_tool(sub_tool_name)
                            sub_tools_removed += 1
                            logger.info(f"移除子工具：{sub_tool_name}")
                        except Exception as e:
                            logger.warning(f"移除子工具失败：{e}")
                    
                    del _package_tools[pkg_name]
                
                return {
                    "success": True,
                    "message": f"技能包 '{pkg_name}' 已禁用，移除了 {sub_tools_removed} 个子工具",
                    "sub_tools_removed": sub_tools_removed
                }
        
        return package_tool
    
    # 创建工具
    package_tool_fn = make_package_tool(package_name, tool_desc, package_info.get('tools', []))
    package_tool_fn.__name__ = tool_name
    package_tool_fn.__doc__ = tool_desc
    
    # 注册到 Provider
    provider.tool()(package_tool_fn)
    logger.info(f"注册技能包工具：{tool_name}")


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
        status = "✓ 已启用" if pkg.name in _active_packages else "○ 未启用"
        tool_name = f"{pkg.name}_tool"
        lines.append(f"[{status}] {tool_name:20} - {pkg.description}")
        lines.append(f"       子工具：{', '.join(pkg.tools)}")
        lines.append(f"       使用：调用 {tool_name}(enable=True) 启用")
    lines.append("=" * 60)
    lines.append(f"总计：{len(packages)} 个技能包")
    lines.append(f"已启用：{len(_active_packages)} 个")
    lines.append(f"已注册子工具：{sum(len(tools) for tools in _package_tools.values())} 个")
    
    return "\n".join(lines)


# ============================================================================
# 初始化
# ============================================================================

def initialize_server() -> ToolPackageManager:
    """初始化服务器"""
    manager = get_package_manager()
    
    # 为每个技能包创建控制工具
    for pkg_name, pkg_info in manager.packages.items():
        create_package_tool(pkg_name, pkg_info.to_dict() if hasattr(pkg_info, 'to_dict') else pkg_info.__dict__)
    
    logger.info(f"SkillMCP 初始化完成 (FastMCP {__import__('fastmcp').__version__})")
    logger.info(f"发现 {len(manager.packages)} 个技能包")
    logger.info(f"注册技能包工具：{[f'{p}_tool' for p in manager.packages.keys()]}")
    
    return manager


if __name__ == "__main__":
    initialize_server()
    mcp.run()
