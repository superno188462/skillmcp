# SkillMCP 使用流程示例

## 📖 完整交互流程

### 场景：用户需要查询天气信息

#### 步骤 1：初始状态 - 查看可用技能包

**AI 客户端连接后，首先调用 `list_packages()`：**

```json
// 调用
list_packages()

// 返回
{
  "packages": [
    {
      "name": "base",
      "version": "1.0.0",
      "description": "基础工具包 - 提供包管理工具",
      "category": "system",
      "tags": ["base", "management"],
      "default_visible": true,
      "active": true,
      "tools": ["list_packages", "open_package", "close_package", "get_active_tools"]
    },
    {
      "name": "web",
      "version": "1.0.0",
      "description": "Web 工具包 - 提供 HTTP 请求、Webhook 等工具",
      "category": "network",
      "tags": ["http", "web", "network", "api"],
      "default_visible": false,
      "active": false,
      "tools": ["http_get", "http_post", "http_put", "http_delete"]
    },
    {
      "name": "weather",
      "version": "1.0.0",
      "description": "天气工具包 - 提供天气查询工具",
      "category": "service",
      "tags": ["weather", "api"],
      "default_visible": false,
      "active": false,
      "tools": ["get_current_weather", "get_forecast"]
    }
  ],
  "status": {
    "available": ["base", "web", "weather"],
    "loaded": ["base", "web", "weather"],
    "active": ["base"]
  },
  "total": 3,
  "active_count": 1,
  "message": "当前已激活 1 个技能包，共 3 个可用"
}
```

**AI 分析**：
- ✅ `base` 已激活（基础管理工具）
- ❌ `web` 未激活（包含 HTTP 工具）
- ❌ `weather` 未激活（包含天气查询工具）

---

#### 步骤 2：AI 分析需求，申请加载技能包

**用户提问**："帮我查询北京今天的天气"

**AI 思考**：
1. 需要查询天气 → 需要 `weather` 技能包
2. 天气查询需要 HTTP 请求 → 需要 `web` 技能包
3. 当前这两个包都未激活 → 需要打开

**AI 调用 `open_package()`：**

```json
// 调用 1：打开天气工具包
open_package(package_name="weather")

// 返回
{
  "success": true,
  "message": "✅ 技能包 'weather' 已打开，现在可以使用 2 个新工具",
  "package_name": "weather",
  "tools_loaded": ["get_current_weather", "get_forecast"],
  "tool_count": 2,
  "next_step": "现在你可以在工具列表中看到新工具，可以直接调用它们",
  "reminder": "💡 提示：任务完成后记得调用 close_all_packages() 关闭不需要的技能包"
}

// 调用 2：打开 Web 工具包（天气查询需要 HTTP）
open_package(package_name="web")

// 返回
{
  "success": true,
  "message": "✅ 技能包 'web' 已打开，现在可以使用 4 个新工具",
  "package_name": "web",
  "tools_loaded": ["http_get", "http_post", "http_put", "http_delete"],
  "tool_count": 4,
  "next_step": "现在你可以在工具列表中看到新工具，可以直接调用它们",
  "reminder": "💡 提示：任务完成后记得调用 close_all_packages() 关闭不需要的技能包"
}
```

---

#### 步骤 3：技能包打开，子工具自动暴露

**现在 AI 的工具列表中新增了以下工具：**

从 `weather` 技能包：
- `get_current_weather(city: str)` - 查询当前天气
- `get_forecast(city: str, days: int)` - 查询天气预报

从 `web` 技能包：
- `http_get(url: str, headers: dict, params: dict)` - HTTP GET 请求
- `http_post(url: str, data: dict, json: dict, headers: dict)` - HTTP POST 请求
- `http_put(url: str, data: dict, json: dict, headers: dict)` - HTTP PUT 请求
- `http_delete(url: str, headers: dict)` - HTTP DELETE 请求

**AI 调用天气查询工具：**

```json
// 调用
get_current_weather(city="北京")

// 返回
{
  "success": true,
  "data": {
    "city": "北京",
    "temperature": 25,
    "condition": "晴",
    "humidity": 45,
    "wind_speed": 10
  }
}
```

---

#### 步骤 4：回复用户

**AI 回复用户**：

> 北京今天的天气：
> - 🌡️ 温度：25°C
> - ☀️ 天气：晴
> - 💧 湿度：45%
> - 💨 风速：10 km/h
> 
> 适合外出活动！

---

#### 步骤 5：清理技能包（重要！）

**任务完成后，AI 主动清理：**

```json
// 调用
close_all_packages(exclude=["base"])

// 返回
{
  "success": true,
  "message": "已关闭 2 个技能包",
  "closed_packages": ["weather", "web"],
  "remaining": ["base"],
  "suggestion": "建议：任务完成后调用此工具清理不需要的技能包"
}
```

---

## ⚠️ 工具累积问题

### 问题描述

如果 AI 不主动关闭技能包，工具会越积越多：

```
任务 1: 查询天气 → 打开 weather + web (6 个工具)
任务 2: 处理文件 → 打开 file (4 个工具) → 累计 10 个工具
任务 3: 数据库操作 → 打开 database (8 个工具) → 累计 18 个工具
任务 4: 图像处理 → 打开 image (5 个工具) → 累计 23 个工具 ⚠️
...
```

**影响**：
- ❌ Token 消耗增加（每个工具约 50-100 tokens）
- ❌ 响应速度变慢
- ❌ 工具选择混淆风险增加
- ❌ 上下文窗口占用过大

### 解决方案

#### 1. 手动清理（推荐）

每个任务完成后，主动关闭不需要的技能包：

```python
# 任务完成后
close_all_packages(exclude=["base"])
```

#### 2. 定期检查

使用 `get_usage_stats()` 查看工具使用情况：

```python
# 查看统计
get_usage_stats()

# 返回示例
{
  "active_packages": ["base", "weather", "web", "file"],
  "active_package_count": 4,
  "active_tools_count": 18,
  "estimated_token_usage": 1350,
  "warning": "⚠️ 工具数量过多可能影响性能",
  "suggestion": "建议调用 close_all_packages() 关闭不需要的技能包"
}
```

#### 3. 设置阈值

当工具数量超过阈值时，主动清理：

```python
# 检查工具数量
stats = get_usage_stats()
if stats["active_tools_count"] > 20:
    # 关闭不需要的技能包
    close_all_packages(exclude=["base"])
```

### 最佳实践

```python
# 开始任务
open_package("weather")
open_package("web")

# 使用工具
result = get_current_weather(city="北京")

# 回复用户
print(f"北京天气：{result}")

# ✅ 任务完成，立即清理
close_all_packages(exclude=["base"])

# 或者单独关闭
close_package("weather")
close_package("web")
```

### 清理策略建议

| 场景 | 清理策略 |
|------|---------|
| 单次任务 | 任务完成后立即 `close_all_packages()` |
| 连续相关任务 | 一批任务完成后统一清理 |
| 长时间会话 | 每 30 分钟或每 5 个任务清理一次 |
| 工具数 > 20 | 立即清理，保留必需的包 |

---

## 🎯 关键设计点

### 1. 初始状态最小化

- 只激活 `base` 技能包（基础管理工具）
- 其他技能包默认不激活
- 减少初始工具数量，优化上下文

### 2. 按需加载

- AI 分析需求后，主动调用 `open_package()`
- 技能包打开后，工具自动可用
- 无需重启或重新连接

### 3. 工具自动暴露

- 技能包打开后，工具立即出现在工具列表
- AI 可以直接调用，无需额外步骤
- 符合 MCP 协议标准

### 4. 动态管理

- 可以随时打开/关闭技能包
- 支持多个技能包同时激活
- **工具会累积，需要主动清理** ⚠️

---

**SkillMCP** - 让 AI 工具管理更高效、更灵活！🎉
