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
  "next_step": "现在你可以在工具列表中看到新工具，可以直接调用它们"
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
  "next_step": "现在你可以在工具列表中看到新工具，可以直接调用它们"
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

#### 步骤 5（可选）：关闭不再需要的技能包

**AI 思考**：天气查询完成，可以关闭不再需要的技能包

```json
// 调用
close_package(package_name="weather")

// 返回
{
  "success": true,
  "message": "技能包 'weather' 已关闭",
  "package_name": "weather"
}

// 调用
close_package(package_name="web")

// 返回
{
  "success": true,
  "message": "技能包 'web' 已关闭",
  "package_name": "web"
}
```

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
- 工具数量动态变化

---

## 📋 完整对话示例

```
用户：帮我查询北京今天的天气

AI（思考）：
1. 需要查询天气 → 需要 weather 技能包
2. 天气查询需要 HTTP 请求 → 需要 web 技能包
3. 检查当前状态：两个包都未激活
4. 行动：打开这两个技能包

AI（调用）：open_package(package_name="weather")
系统：✅ 技能包 'weather' 已打开，现在可以使用 2 个新工具

AI（调用）：open_package(package_name="web")
系统：✅ 技能包 'web' 已打开，现在可以使用 4 个新工具

AI（调用）：get_current_weather(city="北京")
系统：{"city": "北京", "temperature": 25, "condition": "晴", ...}

AI（回复）：
北京今天的天气：
- 🌡️ 温度：25°C
- ☀️ 天气：晴
- 💧 湿度：45%
- 💨 风速：10 km/h

适合外出活动！
```

---

## 🔧 配置示例

### 开发环境 - 自动加载所有技能包

```json
{
  "packages": {
    "*": {
      "default_visible": true
    }
  }
}
```

### 生产环境 - 最小化加载

```json
{
  "packages": {
    "base": {
      "default_visible": true
    },
    "*": {
      "default_visible": false
    }
  }
}
```

### 按需加载 - 推荐

```json
{
  "packages": {
    "base": {
      "default_visible": true
    }
  },
  "features": {
    "auto_load_defaults": false
  }
}
```

---

## 💡 最佳实践

1. **初始状态最小化** - 只加载必需的技能包
2. **按需加载** - 根据需求动态打开技能包
3. **及时清理** - 使用完毕后关闭不需要的技能包
4. **错误处理** - 检查 `open_package()` 返回值，确认加载成功
5. **依赖管理** - 注意技能包之间的依赖关系（如 weather 依赖 web）

---

**SkillMCP** - 让 AI 工具管理更高效、更灵活！🎉
