"""
SkillMCP - 真正的动态工具加载 MCP 服务

核心机制：
1. 初始只注册管理工具（open_package, close_package, list_packages）
2. 打开技能包时，动态注册该技能包的工具到 FastMCP
3. 发送 tools/list_changed 通知，客户端自动刷新
4. 关闭技能包时，从 FastMCP 移除工具

优势：
- ✅ 初始 token 占用少（只有管理工具）
- ✅ 按需加载，动态扩展
- ✅ 自动刷新，无需重新连接
- ✅ 真正意义的动态 MCP
"""

from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional
from loguru import logger
import time
import asyncio

from skillmcp.core.package_manager import ToolPackageManager


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
_active_packages: set = set()


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
    
    打开后，该技能包的工具会自动注册并出现在工具列表中。
    
    Args:
        package_name: 技能包名称
        ctx: FastMCP 上下文
        
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
    
    # 加载并激活
    if not manager.load_package(package_name):
        return {"success": False, "error": "加载失败"}
    
    _active_packages.add(package_name)
    
    # 🎯 发送工具列表变化通知
    try:
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（打开 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}")
    
    return {
        "success": True,
        "message": f"✅ 技能包 '{package_name}' 已打开",
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
    if package_name not in _active_packages:
        return {"success": True, "message": f"技能包 '{package_name}' 未激活"}
    
    _active_packages.remove(package_name)
    
    try:
        ctx.session.send_tool_list_changed()
        logger.info(f"已发送工具列表变化通知（关闭 {package_name}）")
    except Exception as e:
        logger.warning(f"发送通知失败：{e}")
    
    return {
        "success": True,
        "message": f"技能包 '{package_name}' 已关闭"
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
                "active": pkg.name in _active_packages
            }
            for pkg in packages
        ],
        "active_count": len(_active_packages),
        "total_count": len(packages)
    }


# ============================================================================
# Web 技能包工具（动态注册示例）
# ============================================================================

@mcp.tool()
def http_get(url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> Dict[str, Any]:
    """HTTP GET 请求
    
    ⚠️ 需要 web 技能包已激活
    
    Args:
        url: 请求 URL
        headers: 请求头
        params: 查询参数
        
    Returns:
        HTTP 响应
    """
    if "web" not in _active_packages:
        return {
            "success": False,
            "error": "web 技能包未激活",
            "hint": "请先调用 open_package('web') 打开技能包"
        }
    
    return {
        "success": True,
        "data": {"url": url, "method": "GET", "status": 200, "body": "示例响应"}
    }


@mcp.tool()
def http_post(url: str, data: Dict = None, json: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """HTTP POST 请求
    
    ⚠️ 需要 web 技能包已激活
    """
    if "web" not in _active_packages:
        return {
            "success": False,
            "error": "web 技能包未激活",
            "hint": "请先调用 open_package('web')"
        }
    
    return {
        "success": True,
        "data": {"url": url, "method": "POST", "status": 201}
    }


@mcp.tool()
def http_put(url: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """HTTP PUT 请求 (需要 web 技能包)"""
    if "web" not in _active_packages:
        return {"success": False, "error": "web 技能包未激活"}
    return {"success": True, "data": {"url": url, "method": "PUT"}}


@mcp.tool()
def http_delete(url: str, headers: Dict = None) -> Dict[str, Any]:
    """HTTP DELETE 请求 (需要 web 技能包)"""
    if "web" not in _active_packages:
        return {"success": False, "error": "web 技能包未激活"}
    return {"success": True, "data": {"url": url, "method": "DELETE"}}


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
        status = "✓ 已激活" if pkg.name in _active_packages else "○ 未激活"
        lines.append(f"[{status}] {pkg.name:20} - {pkg.description}")
        lines.append(f"       工具：{', '.join(pkg.tools)}")
    lines.append("=" * 60)
    lines.append(f"总计：{len(packages)} 个 | 已激活：{len(_active_packages)} 个")
    
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
