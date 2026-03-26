"""
核心工具包 - 工具实现
"""

from skillmcp.core.interfaces import Tool, ToolParameter


def list_packages_handler(gateway) -> dict:
    """列出所有工具包"""
    packages = gateway.package_manager.list_packages()
    status = gateway.package_manager.get_package_status()
    
    return {
        "packages": [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "active": p.name in status["active"]
            }
            for p in packages
        ],
        "status": status
    }


async def open_package_handler(gateway, package_name: str) -> dict:
    """打开工具包"""
    result = await gateway.open_package(package_name)
    return result.to_dict()


async def close_package_handler(gateway, package_name: str) -> dict:
    """关闭工具包"""
    result = await gateway.close_package(package_name)
    return result.to_dict()


def get_active_tools_handler(gateway) -> dict:
    """获取激活的工具"""
    tools = gateway.get_all_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description
            }
            for t in tools
        ],
        "count": len(tools)
    }


def get_tools() -> list:
    """获取核心工具列表"""
    return [
        Tool(
            name="list_packages",
            description="列出所有可用的工具包",
            parameters=[],
            handler=lambda: list_packages_handler(None)  # 实际使用时会注入 gateway
        ),
        Tool(
            name="open_package",
            description="打开指定的工具包，加载其中的工具",
            parameters=[
                ToolParameter(
                    name="package_name",
                    type="string",
                    description="工具包名称",
                    required=True
                )
            ],
            handler=lambda package_name: open_package_handler(None, package_name)
        ),
        Tool(
            name="close_package",
            description="关闭指定的工具包，卸载其中的工具",
            parameters=[
                ToolParameter(
                    name="package_name",
                    type="string",
                    description="工具包名称",
                    required=True
                )
            ],
            handler=lambda package_name: close_package_handler(None, package_name)
        ),
        Tool(
            name="get_active_tools",
            description="获取当前激活的所有工具",
            parameters=[],
            handler=lambda: get_active_tools_handler(None)
        ),
    ]
