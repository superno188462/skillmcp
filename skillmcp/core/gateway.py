"""
MCP 网关

SkillMCP 的核心网关，处理 AI 请求和工具调用。
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from loguru import logger

from skillmcp.core.interfaces import Tool, ToolResult
from skillmcp.core.package_manager import ToolPackageManager
from skillmcp.core.registry import SkillRegistry


class SkillMCPGateway:
    """MCP 协议网关"""
    
    def __init__(self, package_dir: Optional[str] = None, skill_dir: Optional[str] = None):
        """初始化网关
        
        Args:
            package_dir: 工具包目录
            skill_dir: 技能目录
        """
        self.package_manager = ToolPackageManager(package_dir)
        self.registry = SkillRegistry(skill_dir)
        self.active_packages: set = set()
        
        # 内置工具
        self.builtin_tools = self._create_builtin_tools()
    
    def _create_builtin_tools(self) -> List[Tool]:
        """创建内置工具
        
        Returns:
            内置工具列表
        """
        from skillmcp.core.interfaces import ToolParameter
        
        return [
            Tool(
                name="list_packages",
                description="列出所有可用的工具包",
                parameters=[],
                handler=self._list_packages_handler
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
                handler=self._open_package_handler
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
                handler=self._close_package_handler
            ),
            Tool(
                name="get_active_tools",
                description="获取当前激活的所有工具",
                parameters=[],
                handler=self._get_active_tools_handler
            ),
        ]
    
    async def initialize(self, auto_load_defaults: bool = True) -> None:
        """初始化网关
        
        Args:
            auto_load_defaults: 是否自动加载默认可见的工具包
        """
        logger.info("初始化 SkillMCP Gateway...")
        
        # 发现工具包
        self.package_manager.discover_packages()
        
        # 发现技能
        self.registry.discover_skills()
        
        # 加载默认可见的工具包
        if auto_load_defaults:
            for pkg_name, pkg_info in self.package_manager.packages.items():
                if self.package_manager._get_package_default_visibility(pkg_name):
                    await self.open_package(pkg_name)
                    logger.info(f"自动加载默认工具包：{pkg_name}")
        
        logger.info("SkillMCP Gateway 初始化完成")
    
    async def open_package(self, package_name: str) -> ToolResult:
        """打开工具包
        
        Args:
            package_name: 工具包名称
            
        Returns:
            执行结果
        """
        try:
            # 检查是否已激活
            if package_name in self.active_packages:
                return ToolResult(
                    success=True,
                    data={"message": f"工具包 '{package_name}' 已激活"}
                )
            
            # 加载并激活
            if not self.package_manager.load_package(package_name):
                return ToolResult(
                    success=False,
                    error=f"工具包 '{package_name}' 不存在或加载失败"
                )
            
            if not self.package_manager.activate_package(package_name):
                return ToolResult(
                    success=False,
                    error=f"工具包 '{package_name}' 激活失败"
                )
            
            self.active_packages.add(package_name)
            
            # 获取加载的工具
            pkg_module = self.package_manager.loaded_packages[package_name]
            tools = pkg_module.get_tools() if hasattr(pkg_module, "get_tools") else []
            
            return ToolResult(
                success=True,
                data={
                    "message": f"工具包 '{package_name}' 已打开",
                    "tools_loaded": [t.name for t in tools],
                    "tool_count": len(tools)
                }
            )
        except Exception as e:
            logger.error(f"打开工具包 {package_name} 失败：{e}")
            return ToolResult(success=False, error=str(e))
    
    async def close_package(self, package_name: str) -> ToolResult:
        """关闭工具包
        
        Args:
            package_name: 工具包名称
            
        Returns:
            执行结果
        """
        try:
            if package_name not in self.active_packages:
                return ToolResult(
                    success=True,
                    data={"message": f"工具包 '{package_name}' 未激活"}
                )
            
            self.active_packages.remove(package_name)
            self.package_manager.deactivate_package(package_name)
            
            return ToolResult(
                success=True,
                data={"message": f"工具包 '{package_name}' 已关闭"}
            )
        except Exception as e:
            logger.error(f"关闭工具包 {package_name} 失败：{e}")
            return ToolResult(success=False, error=str(e))
    
    def get_all_tools(self) -> List[Tool]:
        """获取所有可用的工具（内置 + 工具包）
        
        Returns:
            工具列表
        """
        tools = list(self.builtin_tools)
        
        # 添加工具包中的工具
        package_tools = self.package_manager.get_active_tools()
        tools.extend(package_tools)
        
        return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        # 查找工具
        tool = None
        for t in self.get_all_tools():
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return ToolResult(
                success=False,
                error=f"工具 '{tool_name}' 不存在"
            )
        
        if not tool.handler:
            return ToolResult(
                success=False,
                error=f"工具 '{tool_name}' 没有处理器"
            )
        
        try:
            # 调用工具处理器
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)
            
            return ToolResult(success=True, data=result)
        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败：{e}")
            return ToolResult(success=False, error=str(e))
    
    # 内置工具处理器
    
    def _list_packages_handler(self) -> Dict:
        """列出所有工具包"""
        packages = self.package_manager.list_packages()
        status = self.package_manager.get_package_status()
        
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
    
    async def _open_package_handler(self, package_name: str) -> Dict:
        """打开工具包"""
        result = await self.open_package(package_name)
        return result.to_dict()
    
    async def _close_package_handler(self, package_name: str) -> Dict:
        """关闭工具包"""
        result = await self.close_package(package_name)
        return result.to_dict()
    
    def _get_active_tools_handler(self) -> Dict:
        """获取激活的工具"""
        tools = self.get_all_tools()
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
    
    async def handle_message(self, message: Dict) -> Dict:
        """处理 AI 消息
        
        Args:
            message: AI 消息
            
        Returns:
            响应
        """
        # 这里实现 MCP 协议的消息处理逻辑
        # 包括工具调用、工具包管理等
        
        logger.debug(f"处理消息：{message}")
        
        # TODO: 实现完整的 MCP 协议处理
        
        return {
            "role": "assistant",
            "content": "SkillMCP Gateway 已就绪"
        }
