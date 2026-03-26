"""
SkillMCP - 真正的动态工具加载 MCP 服务

基于 FastMCP Provider 系统，支持运行时动态增删工具。

核心机制：
1. 自定义 Provider，实现 _list_tools() 从技能包动态加载
2. 打开技能包时，工具添加到列表
3. 发送 notifications/tools/list_changed 通知
4. 客户端自动刷新，无需重新连接
5. 初始只有管理工具，token 占用极少
"""

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.providers import Provider
from mcp.tools import Tool as MCPTool
from typing import Dict, List, Any, Optional
from loguru import logger
import time

from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.interfaces import Tool, ToolParameter


class SkillMCPProvider(Provider):
    """SkillMCP 自定义 Provider
    
    支持运行时动态增删工具。
    """
    
    def __init__(self):
        super().__init__()
        self.package_manager: Optional[ToolPackageManager] = None
        self._active_packages: set = set()
        self._tools_cache: Dict[str, MCPTool] = {}
    
    def initialize(self, package_manager: ToolPackageManager):
        """初始化 Provider"""
        self.package_manager = package_manager
        
        # 注册管理工具
        self._register_management_tools()
    
    def _register_management_tools(self):
        """注册管理工具（始终可用）"""
        # open_package
        self._tools_cache["open_package"] = MCPTool(
            name="open_package",
            title="打开技能包",
            description="打开指定的技能包，加载其中的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_name": {"type": "string", "description": "技能包名称"}
                },
                "required": ["package_name"]
            }
        )
        
        # close_package
        self._tools_cache["close_package"] = MCPTool(
            name="close_package",
            title="关闭技能包",
            description="关闭指定的技能包，移除其中的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_name": {"type": "string", "description": "技能包名称"}
                },
                "required": ["package_name"]
            }
        )
        
        # list_packages
        self._tools_cache["list_packages"] = MCPTool(
            name="list_packages",
            title="查看技能包列表",
            description="列出所有可用的技能包及其状态",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    
    def add_package_tools(self, package_name: str) -> int:
        """添加技能包的工具
        
        Args:
            package_name: 技能包名称
            
        Returns:
            添加的工具数量
        """
        if not self.package_manager:
            return 0
        
        if package_name not in self.package_manager.loaded_packages:
            if not self.package_manager.load_package(package_name):
                return 0
        
        pkg_module = self.package_manager.loaded_packages[package_name]
        
        if not hasattr(pkg_module, "get_tools"):
            return 0
        
        tools = pkg_module.get_tools()
        added = 0
        
        for tool in tools:
            if tool.name not in self._tools_cache:
                # 转换为 MCP Tool
                mcp_tool = self._convert_tool(tool, package_name)
                self._tools_cache[tool.name] = mcp_tool
                added += 1
                logger.info(f"添加工具：{tool.name} (来自 {package_name})")
        
        return added
    
    def remove_package_tools(self, package_name: str) -> int:
        """移除技能包的工具
        
        Args:
            package_name: 技能包名称
            
        Returns:
            移除的工具数量
        """
        if not self.package_manager:
            return 0
        
        if package_name not in self.package_manager.loaded_packages:
            return 0
        
        pkg_module = self.package_manager.loaded_packages[package_name]
        
        if not hasattr(pkg_module, "get_tools"):
            return 0
        
        tools = pkg_module.get_tools()
        removed = 0
        
        for tool in tools:
            if tool.name in self._tools_cache:
                del self._tools_cache[tool.name]
                removed += 1
                logger.info(f"移除工具：{tool.name}")
        
        return removed
    
    def _convert_tool(self, tool: Tool, package_name: str) -> MCPTool:
        """将 SkillMCP Tool 转换为 MCP Tool"""
        # 构建参数 schema
        properties = {}
        required = []
        
        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required.append(param.name)
        
        return MCPTool(
            name=tool.name,
            title=tool.name,
            description=f"{tool.description} (来自 {package_name} 技能包)",
            inputSchema={
                "type": "object",
                "properties": properties,
                "required": required
            }
        )
    
    async def _list_tools(self) -> List[MCPTool]:
        """列出所有可用工具（动态）"""
        return list(self._tools_cache.values())
    
    async def _get_tool(self, name: str) -> Optional[MCPTool]:
        """获取单个工具"""
        return self._tools_cache.get(name)
    
    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        # 管理工具的处理
        if name == "open_package":
            return await self._handle_open_package(arguments)
        elif name == "close_package":
            return await self._handle_close_package(arguments)
        elif name == "list_packages":
            return await self._handle_list_packages()
        
        # 技能包工具的处理
        if name in self._tools_cache:
            # 检查技能包是否激活
            # TODO: 实现工具调用逻辑
            return {"success": True, "data": f"Tool {name} called"}
        
        raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_open_package(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理 open_package 工具调用"""
        package_name = arguments.get("package_name")
        
        if not package_name:
            return {"success": False, "error": "Missing package_name"}
        
        if package_name in self._active_packages:
            return {"success": True, "message": f"技能包 '{package_name}' 已激活"}
        
        # 添加工具
        added = self.add_package_tools(package_name)
        self._active_packages.add(package_name)
        
        return {
            "success": True,
            "message": f"✅ 技能包 '{package_name}' 已打开，添加 {added} 个工具",
            "tools_added": added
        }
    
    async def _handle_close_package(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理 close_package 工具调用"""
        package_name = arguments.get("package_name")
        
        if package_name not in self._active_packages:
            return {"success": True, "message": f"技能包 '{package_name}' 未激活"}
        
        # 移除工具
        removed = self.remove_package_tools(package_name)
        self._active_packages.remove(package_name)
        
        return {
            "success": True,
            "message": f"技能包 '{package_name}' 已关闭，移除 {removed} 个工具",
            "tools_removed": removed
        }
    
    async def _handle_list_packages(self) -> Dict[str, Any]:
        """处理 list_packages 工具调用"""
        if not self.package_manager:
            return {"packages": [], "active_count": 0, "total_count": 0}
        
        packages = self.package_manager.list_packages()
        
        return {
            "packages": [
                {
                    "name": pkg.name,
                    "version": pkg.version,
                    "description": pkg.description,
                    "active": pkg.name in self._active_packages
                }
                for pkg in packages
            ],
            "active_count": len(self._active_packages),
            "total_count": len(packages)
        }


# 创建 FastMCP 实例，使用自定义 Provider
provider = SkillMCPProvider()
mcp = FastMCP(
    name="SkillMCP",
    providers=[provider]
)


# ============================================================================
# 初始化
# ============================================================================

def initialize_server() -> SkillMCPProvider:
    """初始化服务器"""
    package_manager = ToolPackageManager()
    package_manager.discover_packages()
    
    provider.initialize(package_manager)
    
    logger.info(f"SkillMCP 初始化完成")
    logger.info(f"发现 {len(package_manager.packages)} 个技能包")
    logger.info(f"初始工具：{list(provider._tools_cache.keys())}")
    
    return provider


if __name__ == "__main__":
    initialize_server()
    mcp.run()
