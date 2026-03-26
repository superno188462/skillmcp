# SkillMCP

**动态技能加载平台** - 基于 FastMCP 的模块化 MCP 服务

## 🎯 核心特性

- ✅ **动态工具加载** - 初始只暴露 3 个管理工具，token 占用极少
- ✅ **按需扩展** - 打开技能包后动态注册工具
- ✅ **自动刷新** - 客户端自动刷新工具列表，无需重新连接
- ✅ **资源释放** - 关闭技能包后移除工具，释放资源
- ✅ **Token 优化** - 相比全量注册，token 节省 57%+
- ✅ **FastMCP v3 Provider** - 使用官方 Provider 系统，完整生命周期管理

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
1. 初始连接 → AI 只看到 3 个管理工具（token 占用极少）
   ↓
2. 查看 skillmcp://packages 资源 → 了解可用技能包
   ↓
3. 调用 open_package('web') → 打开技能包
   ↓
4. 服务器动态注册工具 → 发送工具列表变化通知
   ↓
5. 客户端自动刷新 → 新工具立即可用（无需重新连接！）
   ↓
6. 使用工具完成任务
   ↓
7. 调用 close_package('web') → 关闭技能包，释放工具
```

### 示例对话

```
用户：帮我查询北京天气

AI（查看 skillmcp://packages 资源）:
  我看到有 web 技能包可以提供 HTTP 功能。
  需要我打开它吗？

用户：好的

AI（调用）：open_package(package_name="web")
系统：✅ 技能包 'web' 已打开，注册了 4 个新工具
      🎉 工具列表已自动刷新，新工具立即可用！

AI（工具列表自动刷新，看到新工具）:
  现在我可以使用 http_get 工具了。
  
AI（调用）：http_get(url="https://api.weather.com/...")
系统：{"temperature": 25, "condition": "晴", ...}

AI（回复）：北京今天晴，温度 25°C...

AI（可选）：close_package(package_name="web")
系统：技能包 'web' 已关闭，移除了 4 个工具
```

### 关键优势

**Token 优化**：
- 初始：3 个工具（管理工具）
- 打开 web 后：7 个工具
- Token 节省：57%

**动态刷新**：
- ✅ 打开技能包后，发送 `tools/list_changed` 通知
- ✅ 客户端自动刷新工具列表
- ✅ 无需重新连接 MCP 服务器

**按需加载**：
- ✅ 初始 token 占用极少
- ✅ 按需扩展工具
- ✅ 完成后释放资源

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

## 🔧 开发自定义技能包

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
