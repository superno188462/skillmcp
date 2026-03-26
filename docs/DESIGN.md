# SkillMCP 设计文档

> **版本**: v0.1.0  
> **创建时间**: 2026-03-26  
> **作者**: superno188462  
> **仓库**: https://github.com/superno188462/skillmcp

---

## 📋 目录

1. [项目概述](#项目概述)
2. [核心目标](#核心目标)
3. [架构设计](#架构设计)
4. [模块设计](#模块设计)
5. [工具包机制](#工具包机制)
6. [API 设计](#api 设计)
7. [使用示例](#使用示例)
8. [开发指南](#开发指南)

---

## 项目概述

### 背景

传统的 MCP（Model Context Protocol）服务需要一次性将所有工具暴露给 AI，这会占用大量上下文窗口，导致：
- Token 消耗过大
- 响应速度变慢
- 工具管理混乱
- 扩展性差

### 解决方案

**SkillMCP** 是一个模块化、可扩展的技能管理平台，采用**工具包**（Tool Package）机制：
- 初始仅加载核心工具包
- AI 可以按需打开工具包加载工具
- 支持动态加载/卸载技能模块
- 框架与业务完全解耦

---

## 核心目标

### 主要目的

构建一个**模块化、可扩展的技能管理平台**，解决传统系统开发中的架构耦合问题。

### 核心问题解决

#### 🚫 传统开发的痛点

| 问题 | 描述 |
|------|------|
| 框架与业务耦合 | 框架修改影响业务代码 |
| 代码共享困难 | 不同业务模块相互依赖 |
| 版本管理复杂 | 业务代码和框架版本混乱 |
| 扩展性差 | 添加新功能需要修改核心框架 |
| 上下文占用大 | 所有工具一次性暴露给 AI |

#### ✅ SkillMCP 的解决方案

**1. 架构分离**

- **框架通用化**: 核心框架只提供接口，不包含业务逻辑
- **业务独立化**: 每个业务技能完全独立，可单独开发和部署
- **无依赖耦合**: 业务技能只依赖框架接口，不依赖具体实现

**2. 动态管理**

- **插件化架构**: 支持动态加载/卸载技能模块
- **热插拔能力**: 无需重启即可添加新功能
- **版本隔离**: 每个技能独立版本管理

**3. 工具包机制**

- **按需加载**: 初始仅加载核心工具包
- **动态打开**: AI 可以请求打开特定工具包
- **上下文优化**: 只暴露当前需要的工具

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    AI Client (LLM)                       │
└─────────────────────────────────────────────────────────┘
                            │
                            │ MCP Protocol
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   SkillMCP Gateway                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Tool Package Manager                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │  Core    │  │  Web     │  │  Data    │  ...     │ │
│  │  │ Package  │  │ Package  │  │ Package  │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘          │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Skill Registry                          │ │
│  │  - 技能发现                                         │ │
│  │  - 技能加载                                         │ │
│  │  - 技能生命周期管理                                 │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Plugin Interface
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Skill Plugins                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Order   │  │  Payment │  │  User    │   ...        │
│  │  Skill   │  │  Skill   │  │  Skill   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│  (独立仓库)    (独立仓库)    (独立仓库)                  │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 职责 |
|------|------|
| **Gateway** | MCP 协议网关，处理 AI 请求 |
| **Tool Package Manager** | 工具包管理，按需加载工具 |
| **Skill Registry** | 技能注册表，管理技能生命周期 |
| **Skill Plugins** | 独立技能模块，实现具体业务逻辑 |

### 目录结构

```
skillmcp/
├── core/                      # 核心框架
│   ├── __init__.py
│   ├── gateway.py             # MCP 网关
│   ├── registry.py            # 技能注册表
│   ├── package_manager.py     # 工具包管理器
│   └── interfaces.py          # 接口定义
├── packages/                  # 工具包定义
│   ├── core/                  # 核心工具包（默认加载）
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── web/                   # Web 工具包
│   │   ├── __init__.py
│   │   └── tools.py
│   └── data/                  # 数据工具包
│       ├── __init__.py
│       └── tools.py
├── skills/                    # 技能插件（示例）
│   ├── order_skill/
│   ├── payment_skill/
│   └── user_skill/
├── api/                       # RESTful API
│   ├── __init__.py
│   ├── routes.py
│   └── server.py
├── tests/                     # 测试
├── docs/                      # 文档
├── pyproject.toml             # UV 包管理配置
└── README.md
```

---

## 模块设计

### 1. 核心框架模块 (`core/`)

#### Gateway (`gateway.py`)

```python
class SkillMCPGateway:
    """MCP 协议网关"""
    
    def __init__(self):
        self.package_manager = ToolPackageManager()
        self.registry = SkillRegistry()
        self.active_packages = set()  # 已激活的工具包
    
    async def handle_message(self, message: Message) -> Response:
        """处理 AI 消息"""
        # 1. 检查是否需要打开工具包
        if self._is_package_request(message):
            return await self._handle_package_request(message)
        
        # 2. 获取当前激活的工具
        tools = self.package_manager.get_active_tools()
        
        # 3. 调用 LLM
        response = await self._call_llm(message, tools)
        
        return response
    
    async def open_package(self, package_name: str) -> bool:
        """打开工具包"""
        package = self.package_manager.load_package(package_name)
        if package:
            self.active_packages.add(package_name)
            return True
        return False
    
    async def close_package(self, package_name: str) -> bool:
        """关闭工具包"""
        if package_name in self.active_packages:
            self.active_packages.remove(package_name)
            return True
        return False
```

#### Skill Registry (`registry.py`)

```python
class SkillRegistry:
    """技能注册表"""
    
    def __init__(self):
        self.skills = {}  # skill_name -> SkillInfo
        self.loaded_skills = {}  # skill_name -> SkillInstance
    
    def register(self, skill_info: SkillInfo) -> None:
        """注册技能"""
        self.skills[skill_info.name] = skill_info
    
    def load(self, skill_name: str) -> SkillInstance:
        """加载技能"""
        if skill_name not in self.loaded_skills:
            skill_info = self.skills[skill_name]
            self.loaded_skills[skill_name] = self._instantiate(skill_info)
        return self.loaded_skills[skill_name]
    
    def unload(self, skill_name: str) -> None:
        """卸载技能"""
        if skill_name in self.loaded_skills:
            del self.loaded_skills[skill_name]
```

#### Tool Package Manager (`package_manager.py`)

```python
class ToolPackageManager:
    """工具包管理器"""
    
    def __init__(self):
        self.packages = {}  # package_name -> PackageInfo
        self.loaded_packages = {}  # package_name -> PackageInstance
    
    def discover_packages(self, package_dir: str) -> List[PackageInfo]:
        """发现工具包"""
        packages = []
        for pkg_path in Path(package_dir).iterdir():
            if pkg_path.is_dir() and (pkg_path / "__init__.py").exists():
                pkg_info = self._load_package_info(pkg_path)
                packages.append(pkg_info)
                self.packages[pkg_info.name] = pkg_info
        return packages
    
    def load_package(self, package_name: str) -> PackageInstance:
        """加载工具包"""
        if package_name not in self.loaded_packages:
            pkg_info = self.packages[package_name]
            self.loaded_packages[package_name] = self._instantiate(pkg_info)
        return self.loaded_packages[package_name]
    
    def get_active_tools(self) -> List[Tool]:
        """获取当前激活的工具"""
        tools = []
        for pkg_name, pkg_instance in self.loaded_packages.items():
            tools.extend(pkg_instance.get_tools())
        return tools
```

### 2. 工具包模块 (`packages/`)

#### 核心工具包 (`packages/core/`)

```python
# packages/core/tools.py

from skillmcp.core.interfaces import Tool, ToolParameter

class CoreTools:
    """核心工具包"""
    
    @staticmethod
    def get_tools() -> List[Tool]:
        return [
            Tool(
                name="list_packages",
                description="列出可用的工具包",
                parameters=[],
                handler=list_packages_handler
            ),
            Tool(
                name="open_package",
                description="打开指定的工具包",
                parameters=[
                    ToolParameter(
                        name="package_name",
                        type="string",
                        description="工具包名称",
                        required=True
                    )
                ],
                handler=open_package_handler
            ),
            Tool(
                name="close_package",
                description="关闭指定的工具包",
                parameters=[
                    ToolParameter(
                        name="package_name",
                        type="string",
                        description="工具包名称",
                        required=True
                    )
                ],
                handler=close_package_handler
            ),
        ]
```

#### Web 工具包 (`packages/web/`)

```python
# packages/web/tools.py

from skillmcp.core.interfaces import Tool, ToolParameter

class WebTools:
    """Web 工具包"""
    
    @staticmethod
    def get_tools() -> List[Tool]:
        return [
            Tool(
                name="http_get",
                description="发送 HTTP GET 请求",
                parameters=[
                    ToolParameter(
                        name="url",
                        type="string",
                        description="请求 URL",
                        required=True
                    )
                ],
                handler=http_get_handler
            ),
            Tool(
                name="http_post",
                description="发送 HTTP POST 请求",
                parameters=[
                    ToolParameter(name="url", type="string", required=True),
                    ToolParameter(name="data", type="object", required=True)
                ],
                handler=http_post_handler
            ),
        ]
```

### 3. 技能插件模块 (`skills/`)

#### 技能接口定义

```python
# core/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Any, Dict

class Skill(ABC):
    """技能基类"""
    
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
    
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """获取技能提供的工具"""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化技能"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭技能"""
        pass
```

#### 示例技能：订单管理

```python
# skills/order_skill/skill.py

from skillmcp.core.interfaces import Skill, Tool

class OrderSkill(Skill):
    """订单管理技能"""
    
    @property
    def name(self) -> str:
        return "order"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="create_order",
                description="创建订单",
                parameters=[...],
                handler=self.create_order_handler
            ),
            Tool(
                name="query_order",
                description="查询订单",
                parameters=[...],
                handler=self.query_order_handler
            ),
        ]
    
    async def initialize(self) -> None:
        # 初始化数据库连接等
        pass
    
    async def shutdown(self) -> None:
        # 清理资源
        pass
```

---

## 工具包机制

### 工具包生命周期

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Discover  │────▶│    Load     │────▶│   Activate  │
│   发现      │     │   加载      │     │   激活      │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Remove    │◀────│  Deactivate │◀────│   Use       │
│   移除      │     │   停用      │     │   使用      │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 工具包元数据

```python
# packages/<package_name>/__init__.py

PACKAGE_INFO = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 相关工具包",
    "author": "SkillMCP Team",
    "tools": ["http_get", "http_post", "webhook"],
    "dependencies": [],  # 依赖的其他工具包
    "auto_load": False,  # 是否自动加载
}
```

### 工具包请求协议

```json
// AI 请求打开工具包
{
  "action": "open_package",
  "package_name": "web",
  "reason": "需要发送 HTTP 请求"
}

// 响应
{
  "success": true,
  "package_name": "web",
  "tools_loaded": ["http_get", "http_post", "webhook"],
  "message": "工具包 'web' 已打开，现在可以使用 3 个新工具"
}
```

---

## API 设计

### RESTful API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/packages` | GET | 列出所有可用工具包 |
| `/api/v1/packages/:name` | GET | 获取工具包详情 |
| `/api/v1/packages/:name/open` | POST | 打开工具包 |
| `/api/v1/packages/:name/close` | POST | 关闭工具包 |
| `/api/v1/skills` | GET | 列出所有技能 |
| `/api/v1/skills/:name/load` | POST | 加载技能 |
| `/api/v1/skills/:name/unload` | POST | 卸载技能 |
| `/api/v1/tools` | GET | 获取当前激活的工具 |

### API 示例

```bash
# 列出所有工具包
curl http://localhost:8000/api/v1/packages

# 打开 Web 工具包
curl -X POST http://localhost:8000/api/v1/packages/web/open

# 获取当前激活的工具
curl http://localhost:8000/api/v1/tools

# 加载订单技能
curl -X POST http://localhost:8000/api/v1/skills/order/load
```

---

## 使用示例

### 1. 启动 SkillMCP

```bash
# 使用 UV 启动
uv run skillmcp start

# 或作为 Python 模块
python -m skillmcp start
```

### 2. AI 对话流程

```
AI: 你好，我能帮你做什么？

用户: 帮我查询一下订单状态

AI: 我需要先打开订单工具包。
     [调用工具：open_package(package_name="order")]

系统: 工具包 'order' 已打开，可用工具：create_order, query_order, cancel_order

AI: 现在我可以查询订单了。
     [调用工具：query_order(order_id="12345")]

系统: 订单 12345 状态：已发货

AI: 您的订单 12345 已发货，预计 3 天后到达。
```

### 3. 代码示例

```python
from skillmcp import SkillMCPGateway

# 创建网关实例
gateway = SkillMCPGateway()

# 发现并注册工具包
gateway.package_manager.discover_packages("packages")

# 加载核心工具包（默认）
gateway.open_package("core")

# 处理 AI 请求
response = await gateway.handle_message({
    "role": "user",
    "content": "帮我查询订单状态"
})

print(response)
```

---

## 开发指南

### 创建新工具包

1. **创建工具包目录**

```bash
mkdir -p packages/my_package
touch packages/my_package/__init__.py
touch packages/my_package/tools.py
```

2. **定义工具包元数据**

```python
# packages/my_package/__init__.py

PACKAGE_INFO = {
    "name": "my_package",
    "version": "1.0.0",
    "description": "我的工具包",
    "tools": ["tool1", "tool2"],
    "auto_load": False,
}
```

3. **实现工具**

```python
# packages/my_package/tools.py

from skillmcp.core.interfaces import Tool

def my_tool_handler(param1: str) -> str:
    return f"处理结果：{param1}"

def get_tools() -> list:
    return [
        Tool(
            name="my_tool",
            description="我的工具",
            parameters=[...],
            handler=my_tool_handler
        ),
    ]
```

### 创建新技能

1. **继承 Skill 基类**

```python
from skillmcp.core.interfaces import Skill, Tool

class MySkill(Skill):
    @property
    def name(self) -> str:
        return "my_skill"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_tools(self) -> List[Tool]:
        return [...]
    
    async def initialize(self) -> None:
        pass
    
    async def shutdown(self) -> None:
        pass
```

2. **注册技能**

```python
# skills/my_skill/__init__.py

from .skill import MySkill

__all__ = ["MySkill"]
```

### 测试

```bash
# 运行测试
uv run pytest tests/

# 运行特定测试
uv run pytest tests/test_package_manager.py
```

---

## 附录

### A. 依赖项

```toml
# pyproject.toml

[project]
name = "skillmcp"
version = "0.1.0"
description = "模块化技能管理平台"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "mcp>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]
```

### B. 配置文件

```yaml
# config.yaml

server:
  host: "0.0.0.0"
  port: 8000

packages:
  default:
    - core
  auto_load: false

skills:
  directory: "./skills"
  auto_discover: true

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### C. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2026-03-26 | 初始版本，核心框架和工具包机制 |

---

## 总结

**SkillMCP** 通过以下创新解决了传统 MCP 服务的问题：

1. **工具包机制** - 按需加载，优化上下文使用
2. **插件化架构** - 框架与业务解耦，独立开发部署
3. **动态管理** - 热插拔能力，无需重启
4. **标准化接口** - 统一技能规范，易于扩展

这使得 SkillMCP 成为一个**灵活、高效、可扩展**的技能管理平台。🎉
