# SkillMCP

**动态技能加载平台** - 基于 FastMCP 的模块化 MCP 服务

## 🎯 核心特性

- ✅ **技能包即工具** - 每个技能包作为一个工具暴露（如 `web_tool`）
- ✅ **开关控制** - 通过 `enable` 参数控制技能包启用/禁用
- ✅ **子工具按需加载** - 启用后自动注册子工具，禁用后移除
- ✅ **无管理工具** - 所有工具都是业务工具，没有"管理"概念
- ✅ **Token 优化** - 初始只有技能包工具，token 占用极少
- ✅ **FastMCP v3 Provider** - 使用官方 Provider 系统

## 🚀 快速开始

### 1. 安装依赖

```bash
cd skillmcp
uv sync  # 或 pip install -e .
```

### 2. 启动服务器

```bash
# STDIO 模式（默认）
python -m skillmcp.server

# 或使用 uv
uv run python -m skillmcp.server
```

### 3. 配置 MCP 客户端

#### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "skillmcp": {
      "command": "python",
      "args": ["-m", "skillmcp.server"],
      "cwd": "/path/to/skillmcp"
    }
  }
}
```

#### Windsurf

在设置中添加 MCP 服务器：

```json
{
  "name": "SkillMCP",
  "type": "stdio",
  "command": "python",
  "args": ["-m", "skillmcp.server"],
  "cwd": "/path/to/skillmcp"
}
```

## 📖 使用流程

### 完整交互流程

```
1. 初始连接 → AI 看到技能包工具（如 web_tool）
   ↓
2. 查看 skillmcp://packages 资源 → 了解可用技能包
   ↓
3. 调用 web_tool(enable=True) → 启用技能包
   ↓
4. 服务器动态注册子工具 → http_get, http_post 等可用
   ↓
5. 使用子工具完成任务
   ↓
6. 调用 web_tool(enable=False) → 禁用技能包，释放子工具
```

### 示例对话

```
用户：帮我查询北京天气

AI（查看 skillmcp://packages 资源）:
  我看到有 web_tool 可以提供 HTTP 功能。
  需要我启用它吗？

用户：好的

AI（调用）：web_tool(enable=True)
系统：✅ 技能包 'web' 已启用，注册了 4 个子工具
      🎉 子工具已立即可用！

AI（工具列表自动刷新，看到新工具）:
  现在我可以使用 http_get 工具了。
  
AI（调用）：http_get(url="https://api.weather.com/...")
系统：{"temperature": 25, "condition": "晴", ...}

AI（回复）：北京今天晴，温度 25°C...

AI（可选）：web_tool(enable=False)
系统：技能包 'web' 已禁用，移除了 4 个子工具
```

### 关键优势

**设计理念**：
- ✅ 技能包 = 工具（带开关参数）
- ✅ 没有"管理工具"概念
- ✅ 所有工具都是业务工具
- ✅ 自然直观，符合 MCP 设计

**Token 优化**：
- 初始：1 个工具（web_tool）
- 启用后：5 个工具（web_tool + 4 个子工具）
- Token 节省：80%

**动态加载**：
- ✅ 启用技能包 → 注册子工具
- ✅ 禁用技能包 → 移除子工具
- ✅ 完全动态，无需重新连接

## 📦 可用技能包

### Web 技能包

提供 HTTP 请求工具：

- `http_get` - HTTP GET 请求
- `http_post` - HTTP POST 请求
- `http_put` - HTTP PUT 请求
- `http_delete` - HTTP DELETE 请求

**打开方式**：
```python
open_package(package_name="web")
```

## 🔧 工作原理

### 工具列表变化通知

SkillMCP 使用 **FastMCP v3 LocalProvider** 的自动通知机制：

```
1. 启用技能包 → provider.tool() 注册子工具
   ↓
2. LocalProvider 自动发送 tools/list_changed 通知
   ↓
3. MCP 客户端收到通知
   ↓
4. 客户端自动刷新工具列表
   ↓
5. 新工具立即可用（无需重新连接！）
```

**关键特性**：
- ✅ 自动通知，无需手动调用
- ✅ 客户端自动刷新
- ✅ 无需重新连接 MCP 服务器
- ✅ FastMCP v3 内置支持

### 1. 创建技能包目录

```bash
mkdir -p packages/myskill
```

### 2. 创建 `__init__.py`

```python
"""
我的技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter


def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="my_tool",
            description="我的工具",
            parameters=[
                ToolParameter(name="param1", type="string", description="参数 1", required=True),
            ],
            handler=my_tool_handler
        ),
    ]


def my_tool_handler(param1: str) -> dict:
    """工具实现"""
    return {"result": f"处理 {param1}"}


SKILL_PACKAGE = {
    "name": "myskill",
    "version": "1.0.0",
    "description": "我的技能包",
    "author": "Your Name",
    "tools": ["my_tool"],
    "category": "custom",
    "tags": ["custom", "example"],
}
```

### 3. 重启服务器

技能包会被自动发现，无需额外配置。

## 📊 性能对比

| 方案 | 初始工具数 | 打开后工具数 | Token 占用 | 需要重连 |
|------|-----------|-------------|-----------|---------|
| 全量注册 | 7 | 7 | 100% | ❌ |
| **动态加载** | **3** | **7** | **43%** | **❌** |
| 静态隔离 | 3 | 需重连 | 43% | ✅ |

## 📚 文档

- [设计文档](docs/DESIGN.md) - 架构设计
- [使用流程](docs/USAGE_FLOW.md) - 详细使用示例
- [快速开始](docs/QUICKSTART.md) - 配置指南
- [注意事项](docs/NOTES.md) - 使用注意事项
- [测试报告](docs/TEST_REPORT.md) - 自测结果

## 🔗 相关资源

- [FastMCP 文档](https://gofastmcp.com/)
- [MCP 协议](https://modelcontextprotocol.io/)
- [GitHub 仓库](https://github.com/superno188462/skillmcp)

## 📄 许可证

MIT License
