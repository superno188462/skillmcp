# SkillMCP

> **通用模块化技能管理平台** - 让 AI 工具管理更高效、更灵活

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![UV](https://img.shields.io/badge/UV-package%20manager-orange)](https://github.com/astral-sh/uv)

---

## 📖 简介

**SkillMCP** 是一个通用的模块化技能管理平台，采用**技能包（Skill Package）**机制：

| 特性 | 描述 |
|------|------|
| 🎁 **技能包机制** | 按需加载工具，优化上下文使用 |
| ⚙️ **配置驱动** | 通过配置控制默认显示/加载行为 |
| 🔌 **插件化架构** | 框架与业务解耦，支持热插拔 |
| 📦 **通用设计** | 适用于任何 AI 工具和技能管理 |

### 核心概念

- **技能包（Skill Package）** = 工具包（Tool Package）
  - 一组相关工具的集合
  - 通过配置控制是否默认显示/加载
  - 支持分类、标签、依赖管理

---

## ✨ 核心特性

### ⚙️ 配置驱动的工具包管理

通过配置文件或元数据控制工具包的默认行为：

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
    }
  }
}
```

或在技能包元数据中定义：

```python
SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 工具包",
    "default_visible": False,  # 默认不显示
    "category": "network",
    "tags": ["http", "web", "api"],
}
```

---

## 🏗️ 架构

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
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Skill Plugins                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Order   │  │  Payment │  │  User    │   ...        │
│  │  Skill   │  │  Skill   │  │  Skill   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone git@github.com:superno188462/skillmcp.git
cd skillmcp

# 使用 UV 安装依赖
uv sync

# 启动 SkillMCP
uv run skillmcp start
```

### 基本使用

```python
from skillmcp import SkillMCPGateway

# 创建网关实例
gateway = SkillMCPGateway()

# 发现工具包
gateway.package_manager.discover_packages("packages")

# 加载核心工具包（默认）
gateway.open_package("core")

# 处理 AI 请求
response = await gateway.handle_message({
    "role": "user",
    "content": "帮我查询订单状态"
})
```

### AI 对话示例

```
用户：帮我查询一下订单状态

AI: 我需要先打开订单工具包。
     [调用：open_package(package_name="order")]

系统：✅ 工具包 'order' 已打开
      可用工具：create_order, query_order, cancel_order

AI: 现在我可以查询订单了。
     [调用：query_order(order_id="12345")]

系统：订单 12345 状态：已发货

AI: 您的订单 12345 已发货，预计 3 天后到达。
```

---

## 📦 工具包

### 内置工具包

| 工具包 | 描述 | 自动加载 |
|--------|------|---------|
| `core` | 核心工具（包管理、技能管理） | ✅ |
| `web` | Web 相关工具（HTTP 请求、Webhook） | ❌ |
| `data` | 数据处理工具（文件、数据库） | ❌ |
| `system` | 系统工具（进程、文件操作） | ❌ |

### 打开工具包

```python
# 打开 Web 工具包
await gateway.open_package("web")

# 关闭工具包
await gateway.close_package("web")

# 列出所有可用工具包
packages = gateway.package_manager.list_packages()
```

---

## 🔧 开发指南

### 创建新工具包

```bash
# 创建工具包目录
mkdir -p packages/my_package
```

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

---

## 📋 API 参考

### RESTful API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/packages` | GET | 列出所有可用工具包 |
| `/api/v1/packages/:name/open` | POST | 打开工具包 |
| `/api/v1/packages/:name/close` | POST | 关闭工具包 |
| `/api/v1/skills` | GET | 列出所有技能 |
| `/api/v1/skills/:name/load` | POST | 加载技能 |
| `/api/v1/tools` | GET | 获取当前激活的工具 |

### 示例

```bash
# 列出所有工具包
curl http://localhost:8000/api/v1/packages

# 打开 Web 工具包
curl -X POST http://localhost:8000/api/v1/packages/web/open

# 获取当前激活的工具
curl http://localhost:8000/api/v1/tools
```

---

## 📚 文档

- [设计文档](docs/DESIGN.md) - 完整的架构设计
- [开发指南](docs/DEVELOPMENT.md) - 开发环境搭建
- [API 文档](docs/API.md) - API 详细参考
- [示例](examples/) - 使用示例代码

---

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)。

### 开发环境

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest tests/

# 代码格式化
uv run black skillmcp/
uv run ruff check skillmcp/
```

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件

---

## 📞 联系

- **作者**: superno188462
- **GitHub**: https://github.com/superno188462
- **项目**: https://github.com/superno188462/skillmcp

---

**SkillMCP** - 让 AI 工具管理更高效、更灵活！🎉
