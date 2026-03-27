# SkillMCP 工具列表变化通知机制

## 📡 通知机制

SkillMCP 使用 **FastMCP v3 LocalProvider** 的内置通知机制，自动通知客户端工具列表的变化。

## 🔄 工作流程

### 启用技能包时

```
用户调用：web_tool(enable=True)
    ↓
SkillMCP 执行：
    1. 加载技能包
    2. 创建子工具函数
    3. 调用 provider.tool()(sub_handler)
    ↓
FastMCP LocalProvider:
    1. 注册工具到内部存储
    2. 自动发送 tools/list_changed 通知
    ↓
MCP 客户端:
    1. 收到 tools/list_changed 通知
    2. 自动调用 tools/list 请求
    3. 更新本地工具列表
    4. AI 可以看到新工具
```

### 禁用技能包时

```
用户调用：web_tool(enable=False)
    ↓
SkillMCP 执行：
    1. 调用 provider.remove_tool(tool_name)
    ↓
FastMCP LocalProvider:
    1. 从内部存储移除工具
    2. 自动发送 tools/list_changed 通知
    ↓
MCP 客户端:
    1. 收到 tools/list_changed 通知
    2. 自动调用 tools/list 请求
    3. 更新本地工具列表
    4. AI 看到工具已移除
```

## 🎯 关键特性

### 1. 自动通知

**无需手动调用** `send_tool_list_changed()`，FastMCP v3 LocalProvider 会自动处理：

```python
# 添加工具时自动通知
provider.tool()(my_tool)  # ✅ 自动发送通知

# 移除工具时自动通知
provider.remove_tool("my_tool")  # ✅ 自动发送通知
```

### 2. 客户端行为

MCP 客户端收到 `tools/list_changed` 通知后：

1. **自动刷新** - 调用 `tools/list` 获取最新工具列表
2. **更新缓存** - 替换本地工具列表缓存
3. **立即可用** - 新工具可以立即调用

### 3. 无需重新连接

```
❌ 旧方式：需要断开重连才能看到新工具
✅ 新方式：自动通知，无需重新连接
```

## 📊 MCP 协议规范

根据 [MCP 协议规范](https://modelcontextprotocol.io/specification):

### 服务器 → 客户端通知

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

### 客户端响应

```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "tools/list",
  "params": {}
}
```

## 🔍 调试方法

### 查看服务器日志

```bash
python -m skillmcp.server 2>&1 | grep "注册\|移除"
```

输出示例：
```
INFO - 注册技能包工具：web_tool
INFO - 注册子工具：http_get (来自 web)
INFO - 注册子工具：http_post (来自 web)
INFO - 移除子工具：http_get
INFO - 移除子工具：http_post
```

### 查看客户端日志

不同客户端的日志位置：

**Claude Desktop**:
```
~/Library/Application Support/Claude/logs/  (macOS)
%APPDATA%\Claude\logs\  (Windows)
```

**Windsurf**:
```
查看开发者工具 → Console 标签
```

**Cursor**:
```
查看 Output → MCP Server
```

### 使用 MCP Inspector

```bash
# 安装 MCP Inspector
npx @modelcontextprotocol/inspector python -m skillmcp.server

# 在浏览器中打开 http://localhost:5173
# 查看 Tools 标签，观察工具列表变化
```

## ⚠️ 常见问题

### Q1: 客户端看不到新工具

**可能原因**：
1. 客户端缓存未刷新
2. 客户端不支持自动通知
3. 网络连接问题

**解决方法**：
1. 重启 MCP 客户端
2. 检查客户端是否支持 MCP 协议
3. 查看客户端日志

### Q2: 工具列表没有自动更新

**可能原因**：
1. 客户端未实现通知处理
2. FastMCP 版本过低

**解决方法**：
1. 升级 MCP 客户端
2. 升级 FastMCP：`pip install --upgrade fastmcp`

### Q3: 需要手动刷新吗？

**不需要**。FastMCP v3 LocalProvider 会自动发送通知，客户端会自动刷新。

如果客户端没有自动刷新，说明客户端不支持 MCP 通知机制，需要：
1. 升级客户端
2. 或手动重新连接

## 📚 相关资源

- [MCP 协议规范 - Tools](https://modelcontextprotocol.io/specification/server/tools)
- [FastMCP v3 文档](https://gofastmcp.com/)
- [LocalProvider 源码](https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/providers/local_provider.py)

---

**更新时间**: 2026-03-27  
**FastMCP 版本**: 3.1.1
