"""
核心接口定义

定义 SkillMCP 的核心抽象接口，所有技能和工具包都必须遵循这些接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class ToolParameterType(str, Enum):
    """工具参数类型"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: ToolParameterType
    description: str = ""
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
        }
        if self.required:
            result["required"] = True
        if self.default is not None:
            result["default"] = self.default
        if self.enum:
            result["enum"] = self.enum
        return result


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    handler: Optional[Callable] = None
    
    def to_dict(self) -> Dict:
        """转换为字典格式（用于 MCP 协议）"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type.value,
                        "description": p.description,
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            }
        }


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {"success": self.success}
        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
        return result


class Skill(ABC):
    """技能基类
    
    所有技能插件都必须继承这个基类并实现抽象方法。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """技能版本"""
        pass
    
    @property
    def description(self) -> str:
        """技能描述"""
        return ""
    
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """获取技能提供的工具列表"""
        pass
    
    async def initialize(self) -> None:
        """初始化技能（可选）"""
        pass
    
    async def shutdown(self) -> None:
        """关闭技能，清理资源（可选）"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, version={self.version})"


@dataclass
class PackageInfo:
    """工具包元数据"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    tools: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    auto_load: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PackageInfo":
        """从字典创建 PackageInfo"""
        return cls(
            name=data.get("name", "unknown"),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            tools=data.get("tools", []),
            dependencies=data.get("dependencies", []),
            auto_load=data.get("auto_load", False),
        )


@dataclass
class SkillInfo:
    """技能元数据"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    module: str = ""
    dependencies: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SkillInfo":
        """从字典创建 SkillInfo"""
        return cls(
            name=data.get("name", "unknown"),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            module=data.get("module", ""),
            dependencies=data.get("dependencies", []),
        )
