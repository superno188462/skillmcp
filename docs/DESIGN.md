# SkillMCP 设计文档

> **版本**: v0.1.0  
> **创建时间**: 2026-03-26  
> **作者**: superno188462  
> **仓库**: https://github.com/superno188462/skillmcp

---

## 📋 目录

1. [项目概述](#项目概述)
2. [核心概念](#核心概念)
3. [架构设计](#架构设计)
4. [技能包机制](#技能包机制)
5. [配置系统](#配置系统)
6. [模块设计](#模块设计)
7. [API 设计](#api 设计)
8. [使用示例](#使用示例)

---

## 项目概述

### 背景

传统的 MCP（Model Context Protocol）服务需要一次性将所有工具暴露给 AI，这会占用大量上下文窗口，导致：
- Token 消耗过大
- 响应速度变慢
- 工具管理混乱
- 扩展性差

### 解决方案

**SkillMCP** 是一个**通用的模块化技能管理平台**，采用**技能包（Skill Package）**机制：
- 技能包 = 工具包（统一概念）
- 通过配置控制默认显示/加载行为
- 支持按需加载、动态管理
- 框架与业务完全解耦

---

## 核心概念

### 技能包（Skill Package）

**技能包**是 SkillMCP 的基本单位，每个技能包包含一组相关的工具。

```python
SKILL_PACKAGE = {
    "name": "web",              # 技能包名称
    "version": "1.0.0",         # 版本号
    "description": "Web 工具包", # 描述
    "author": "SkillMCP Team",  # 作者
    "tools": ["http_get", ...], # 工具列表
    "dependencies": [],         # 依赖的其他技能包
    "default_visible": False,   # ⭐ 是否默认显示/加载
    "category": "network",      # 分类
    "tags": ["http", "web"],    # 标签
}
```

### 配置优先级

工具包的默认显示/加载行为由以下优先级决定：

1. **配置文件** (`skillmcp.json`) - 最高优先级
2. **技能包元数据** (`__init__.py` 中的 `SKILL_PACKAGE`)
3. **默认值** (`default_visible: False`)

---

## 配置系统

### 配置文件格式

```json
{
  "packages": {
    "core": {
      "default_visible": true,
      "description": "核心工具包，始终可用"
    },
    "web": {
      "default_visible": false,
      "description": "Web 工具包，按需加载"
    },
    "data": {
      "default_visible": false,
      "category": "data",
      "tags": ["database", "file"]
    }
  },
  
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "INFO"
  },
  
  "features": {
    "auto_load_defaults": true,    # 是否自动加载默认可见的技能包
    "allow_dynamic_load": true,    # 允许动态加载
    "tool_timeout": 30             # 工具执行超时（秒）
  }
}
```

### 使用场景

#### 场景 1：开发环境 - 加载所有工具包

```json
{
  "packages": {
    "*": {
      "default_visible": true
    }
  }
}
```

#### 场景 2：生产环境 - 仅加载核心工具包

```json
{
  "packages": {
    "core": {
      "default_visible": true
    },
    "*": {
      "default_visible": false
    }
  }
}
```

#### 场景 3：按分类加载

```json
{
  "packages": {
    "core": {
      "default_visible": true
    },
    "web": {
      "default_visible": true
    }
  },
  "features": {
    "auto_load_defaults": true
  }
}
```

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
│  │              Skill Package Manager                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │  Core    │  │  Web     │  │  Data    │  ...     │ │
│  │  │ Package  │  │ Package  │  │ Package  │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘          │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Configuration System                    │ │
│  │  - skillmcp.json                                    │ │
│  │  - 包元数据 (SKILL_PACKAGE)                          │ │
│  │  - 默认值                                           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 职责 |
|------|------|
| **Gateway** | MCP 协议网关，处理 AI 请求 |
| **Skill Package Manager** | 技能包管理，按需加载工具 |
| **Configuration System** | 配置管理，控制默认行为 |

---

## 技能包机制

### 技能包生命周期

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

### 技能包元数据

```python
# packages/<package_name>/__init__.py

SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 相关工具包",
    "author": "SkillMCP Team",
    "tools": ["http_get", "http_post", "webhook"],
    "dependencies": [],  # 依赖的其他技能包
    "default_visible": False,  # 是否默认显示/加载
    "category": "network",
    "tags": ["http", "web", "api"],
}
```

---

## 模块设计

### 1. 核心框架模块 (`skillmcp/core/`)

#### 接口定义 (`interfaces.py`)

```python
@dataclass
class SkillPackage:
    """技能包元数据"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    tools: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    default_visible: bool = False  # 是否默认显示/加载
    category: str = "general"  # 分类
    tags: List[str] = field(default_factory=list)  # 标签
```

#### 工具包管理器 (`package_manager.py`)

```python
class ToolPackageManager:
    """工具包管理器"""
    
    def __init__(self, package_dir: str = None, config_file: str = None):
        self.package_dir = Path(package_dir) if package_dir else Path("packages")
        self.config_file = Path(config_file) if config_file else Path("skillmcp.json")
        self.config: Dict = {}
        
        # 加载配置
        self._load_config()
    
    def _get_package_default_visibility(self, package_name: str) -> bool:
        """获取工具包的默认可见性
        
        优先级：配置文件 > 包元数据 > 默认值
        """
        # 1. 检查配置文件
        if "packages" in self.config:
            pkg_config = self.config["packages"].get(package_name, {})
            if "default_visible" in pkg_config:
                return pkg_config["default_visible"]
        
        # 2. 使用包元数据中的值
        if package_name in self.packages:
            return self.packages[package_name].default_visible
        
        # 3. 默认不显示
        return False
```

---

## API 设计

### RESTful API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/packages` | GET | 列出所有可用技能包 |
| `/api/v1/packages/:name` | GET | 获取技能包详情 |
| `/api/v1/packages/:name/open` | POST | 打开技能包 |
| `/api/v1/packages/:name/close` | POST | 关闭技能包 |
| `/api/v1/tools` | GET | 获取当前激活的工具 |

### 工具调用协议

```json
// 打开技能包
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
  "message": "技能包 'web' 已打开，现在可以使用 3 个新工具"
}
```

---

## 使用示例

### 1. 启动 SkillMCP

```bash
# 使用配置文件启动
uv run skillmcp start --config skillmcp.json

# 或指定参数
uv run skillmcp start --auto-load-defaults=true
```

### 2. AI 对话流程

```
AI: 你好，我能帮你做什么？

用户：帮我查询一下订单状态

AI: 我需要先打开订单工具包。
     [调用工具：open_package(package_name="order")]

系统：技能包 'order' 已打开，可用工具：create_order, query_order, cancel_order

AI: 现在我可以查询订单了。
     [调用工具：query_order(order_id="12345")]

系统：订单 12345 状态：已发货

AI: 您的订单 12345 已发货，预计 3 天后到达。
```

### 3. 代码示例

```python
from skillmcp import SkillMCPGateway

# 创建网关实例（使用配置文件）
gateway = SkillMCPGateway(
    package_dir="packages",
    config_file="skillmcp.json"
)

# 初始化（自动加载默认可见的技能包）
await gateway.initialize(auto_load_defaults=True)

# 处理 AI 请求
response = await gateway.handle_message({
    "role": "user",
    "content": "帮我查询订单状态"
})

print(response)
```

---

## 总结

**SkillMCP** 通过以下创新解决了传统 MCP 服务的问题：

1. **技能包机制** - 按需加载，优化上下文使用
2. **配置驱动** - 通过配置控制默认显示/加载行为
3. **插件化架构** - 框架与业务解耦，独立开发部署
4. **动态管理** - 热插拔能力，无需重启
5. **标准化接口** - 统一技能规范，易于扩展

这使得 SkillMCP 成为一个**灵活、高效、通用**的技能管理平台。🎉
