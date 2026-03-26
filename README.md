# SkillMCP

> **基于 FastMCP 的模块化技能管理平台** - 让 AI 工具管理更高效、更灵活

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastMCP](https://img.shields.io/badge/FastMCP-1.0-green)](https://github.com/jlowin/fastmcp)

---

## 📖 简介

**SkillMCP** 是一个基于 **FastMCP** 的模块化技能管理平台：

| 特性 | 描述 |
|------|------|
| 🎯 **FastMCP 服务** | 对外暴露为标准 FastMCP 服务，兼容所有 MCP 客户端 |
| 🎁 **技能包机制** | 按需加载工具，优化上下文使用 |
| ⚙️ **配置驱动** | 通过配置控制默认显示/加载行为 |
| 🔌 **插件化架构** | 框架与业务解耦，支持热插拔 |

### 什么是 FastMCP？

**FastMCP** 是一个快速构建 MCP（Model Context Protocol）服务的框架，可以被：
- Claude Desktop
- Windsurf
- Cursor
- 其他 MCP 客户端

直接使用。

### SkillMCP vs FastMCP

- **FastMCP**: 基础框架，提供 MCP 协议实现
- **SkillMCP**: 在 FastMCP 之上构建的模块化技能管理平台
  - 动态加载技能包
  - 配置驱动的可见性控制
  - 工具包分类和标签管理

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd skillmcp
uv sync
```

### 2. 配置 FastMCP 客户端

#### Claude Desktop 配置

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "skillmcp": {
      "command": "uv",
      "args": ["run", "skillmcp", "start"],
      "cwd": "/path/to/skillmcp"
    }
  }
}
```

#### Windsurf 配置

在 Windsurf 设置中添加 MCP 服务器：

```json
{
  "name": "SkillMCP",
  "type": "stdio",
  "command": "uv",
  "args": ["run", "skillmcp", "start"],
  "cwd": "/path/to/skillmcp"
}
```

### 3. 启动服务器

```bash
# STDIO 模式（默认，用于 Claude Desktop 等）
uv run skillmcp start

# SSE 模式（用于 Web 客户端）
uv run skillmcp start --transport sse --host 0.0.0.0 --port 8000

# 使用配置文件
uv run skillmcp start --config skillmcp.json
```

### 4. 测试连接

```bash
# 使用 MCP Inspector
npx @modelcontextprotocol/inspector uv run skillmcp start

# 或直接使用 FastMCP CLI
fastmcp dev skillmcp/server.py
```

---

## 📖 使用流程

### 完整交互流程

```
1. 初始连接 → AI 调用 list_packages() 查看可用技能包
2. 分析需求 → AI 确定需要哪个技能包
3. 申请加载 → AI 调用 open_package(package_name)
4. 工具暴露 → 技能包内的工具自动出现在工具列表
5. 使用工具 → AI 调用新加载的工具完成任务
6. 可选清理 → 调用 close_package() 关闭不需要的技能包
```

**详细示例请查看**：[使用流程文档](docs/USAGE_FLOW.md)

### 示例对话

```
用户：帮我查询北京今天的天气

AI（思考）：需要 weather 技能包和 web 技能包
AI（调用）：open_package(package_name="weather")
系统：✅ 技能包 'weather' 已打开，现在可以使用 2 个新工具

AI（调用）：open_package(package_name="web")
系统：✅ 技能包 'web' 已打开，现在可以使用 4 个新工具

AI（调用）：get_current_weather(city="北京")
系统：{"city": "北京", "temperature": 25, "condition": "晴", ...}

AI（回复）：北京今天晴，温度 25°C...
```

---

## ✨ 核心特性

### ⚙️ 配置驱动的技能包管理

通过配置文件或元数据控制技能包的默认行为：

```json
{
  "packages": {
    "base": {
      "default_visible": true,
      "description": "基础技能包，默认可用"
    },
    "web": {
      "default_visible": false,
      "description": "Web 技能包，按需加载"
    }
  }
}
```

或在技能包元数据中定义：

```python
SKILL_PACKAGE = {
    "name": "web",
    "version": "1.0.0",
    "description": "Web 技能包",
    "default_visible": False,  # 默认不显示
    "category": "network",
    "tags": ["http", "web", "api"],
}
```

### 📦 技能包结构

**所有技能包都是平等的**，放在 `packages/` 目录下：

```
packages/
├── base/           # 基础技能包（默认加载）
│   ├── __init__.py
│   └── tools.py
├── web/            # Web 技能包（按需加载）
│   ├── __init__.py
│   └── tools.py
└── data/           # 数据技能包（按需加载）
    ├── __init__.py
    └── tools.py
```

**没有"核心"概念**，只有 `default_visible` 控制是否默认加载。

---

## 🛠️ 内置技能包

| 技能包 | 描述 | 默认加载 |
|--------|------|---------|
| `base` | 基础工具（包管理、技能管理） | ✅ |
| `web` | Web 相关工具（HTTP 请求、Webhook） | ❌ |

---

## 📚 文档

- [设计文档](docs/DESIGN.md) - 完整的架构设计
- [快速开始](docs/QUICKSTART.md) - 5 分钟上手指南
- [配置示例](skillmcp.json.example) - 可直接使用

---

## 🔧 开发指南

### 创建新技能包

```bash
# 创建目录结构
mkdir -p packages/my_package

# 创建 __init__.py
cat > packages/my_package/__init__.py << 'EOF'
SKILL_PACKAGE = {
    "name": "my_package",
    "version": "1.0.0",
    "description": "我的技能包",
    "default_visible": False,
    "category": "general",
    "tags": ["custom"],
}
EOF

# 创建 tools.py
cat > packages/my_package/tools.py << 'EOF'
from skillmcp.core.interfaces import Tool, ToolParameter

def my_tool_handler(param1: str) -> str:
    return f"处理结果：{param1}"

def get_tools() -> list:
    return [
        Tool(
            name="my_tool",
            description="我的工具",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="参数 1",
                    required=True
                )
            ],
            handler=my_tool_handler
        ),
    ]
EOF
```

### 测试技能包

```bash
# 使用 MCP Inspector 测试
npx @modelcontextprotocol/inspector uv run skillmcp start

# 查看日志
uv run skillmcp start 2>&1 | grep "技能包"
```

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

**SkillMCP** - 基于 FastMCP 的模块化技能管理平台！🎉
