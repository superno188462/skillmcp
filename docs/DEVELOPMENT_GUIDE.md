# SkillMCP 自定义技能包开发指南

## 📚 目录

1. [快速开始](#快速开始)
2. [技能包结构](#技能包结构)
3. [技能包配置](#技能包配置)
4. [工具定义](#工具定义)
5. [自定义初始暴露信息](#自定义初始暴露信息)
6. [完整示例](#完整示例)

---

## 🚀 快速开始

### 1. 创建技能包目录

```bash
cd packages
mkdir my_skill
```

### 2. 创建 `__init__.py`

```python
"""
我的技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any


# 技能包配置
SKILL_PACKAGE = {
    "name": "my_skill",
    "version": "1.0.0",
    "description": "我的技能包 - 提供 XX 功能",
    "author": "Your Name",
    "default_visible": False,
    "category": "custom",
    "tags": ["custom", "example"],
}


# 工具定义
def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="my_tool",
            description="我的工具 - 功能描述",
            parameters=[
                ToolParameter(name="input", type="string", description="输入参数", required=True),
            ],
            handler=my_tool_handler
        ),
    ]


# 工具实现
def my_tool_handler(input: str) -> Dict[str, Any]:
    """工具实现"""
    return {
        "success": True,
        "data": {"result": f"处理：{input}"}
    }
```

### 3. 重启服务器

```bash
skillmcp start
```

技能包会被自动发现！

---

## 📁 技能包结构

### 基础结构

```
packages/
└── my_skill/
    ├── __init__.py       # 必需：技能包配置和工具定义
    └── utils/            # 可选：工具函数
        └── helpers.py
```

### 推荐结构

```
packages/
└── my_skill/
    ├── __init__.py       # 技能包配置
    ├── tools/            # 工具实现
    │   ├── __init__.py
    │   ├── tool1.py
    │   └── tool2.py
    ├── utils/            # 辅助函数
    │   └── helpers.py
    └── tests/            # 测试（可选）
        └── test_tools.py
```

---

## ⚙️ 技能包配置

### 必需字段

```python
SKILL_PACKAGE = {
    "name": "my_skill",           # 技能包名称（唯一）
    "version": "1.0.0",           # 版本号
    "description": "技能包描述",   # 功能描述
    "author": "Your Name",        # 作者
}
```

### 可选字段

```python
SKILL_PACKAGE = {
    "name": "my_skill",
    "version": "1.0.0",
    "description": "技能包描述",
    "author": "Your Name",
    
    # 是否默认启用（默认：False）
    "default_visible": False,
    
    # 分类
    "category": "custom",  # system, network, data, custom, etc.
    
    # 标签（用于搜索和过滤）
    "tags": ["custom", "example", "demo"],
    
    # 依赖的其他技能包
    "dependencies": ["web"],
    
    # 自定义初始暴露信息
    "exposure": {
        "initial_description": "自定义描述",
        "show_in_list": True,
        "priority": 1,
        "icon": "🔧",
    }
}
```

---

## 🛠️ 工具定义

### Tool 参数

```python
from skillmcp.core.interfaces import Tool, ToolParameter

Tool(
    name="tool_name",              # 工具名称（唯一）
    description="工具描述",         # 工具功能描述
    parameters=[                   # 参数列表
        ToolParameter(
            name="param1",
            type="string",         # string, number, integer, boolean, object
            description="参数描述",
            required=True          # 是否必需
        ),
    ],
    handler=tool_handler_function  # 工具实现函数
)
```

### 参数类型

| 类型 | 说明 | Python 对应 |
|------|------|------------|
| `string` | 字符串 | `str` |
| `number` | 数字 | `float` |
| `integer` | 整数 | `int` |
| `boolean` | 布尔值 | `bool` |
| `object` | 对象 | `Dict[str, Any]` |

### 工具实现函数

```python
def my_tool_handler(param1: str, param2: int = 10) -> Dict[str, Any]:
    """工具实现
    
    Args:
        param1: 参数 1
        param2: 参数 2（可选）
        
    Returns:
        返回字典格式的 result
    """
    return {
        "success": True,
        "data": {
            "result": f"处理结果：{param1}, {param2}"
        }
    }
```

---

## 🎨 自定义初始暴露信息

通过 `exposure` 字段自定义技能包的初始暴露信息：

### 配置示例

```python
SKILL_PACKAGE = {
    "name": "my_skill",
    "description": "我的技能包",
    
    # 自定义初始暴露信息
    "exposure": {
        # 初始描述（显示给 AI 看）
        "initial_description": "我的技能包 - 提供强大数据处理功能",
        
        # 是否在技能包列表中显示（默认：True）
        "show_in_list": True,
        
        # 优先级（数字越小越靠前，默认：999）
        "priority": 1,
        
        # 图标（可选，用于 UI 显示）
        "icon": "🔧",
        
        # 使用场景描述（可选）
        "use_cases": [
            "数据处理",
            "格式转换",
            "数据分析"
        ],
        
        # 使用示例（可选）
        "examples": [
            "调用 my_tool(enable=True) 启用技能包",
            "然后使用 process_data 工具处理数据"
        ]
    }
}
```

### 效果

**资源显示**：
```
[○ 未启用] my_skill           - 我的技能包 - 提供强大数据处理功能
       使用：调用 my_skill_tool(enable=True) 启用
```

**工具描述**：
- `my_skill_tool`: "我的技能包 - 提供强大数据处理功能"

---

## 📋 完整示例

### 示例 1：数据处理技能包

```python
"""
数据处理技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


SKILL_PACKAGE = {
    "name": "data_processor",
    "version": "1.0.0",
    "description": "数据处理技能包 - 提供数据清洗、转换、分析功能",
    "author": "Data Team",
    "default_visible": False,
    "category": "data",
    "tags": ["data", "processing", "analysis"],
    
    "exposure": {
        "initial_description": "数据处理技能包 - 提供专业数据清洗和分析工具",
        "priority": 1,
        "icon": "📊",
        "use_cases": ["数据清洗", "格式转换", "统计分析"]
    }
}


def get_tools():
    return [
        Tool(
            name="clean_data",
            description="清洗数据 - 去除无效数据和异常值",
            parameters=[
                ToolParameter(name="data", type="string", description="原始数据", required=True),
                ToolParameter(name="method", type="string", description="清洗方法", required=False),
            ],
            handler=clean_data_handler
        ),
        Tool(
            name="analyze_data",
            description="分析数据 - 统计分析数据特征",
            parameters=[
                ToolParameter(name="data", type="string", description="数据", required=True),
                ToolParameter(name="metrics", type="object", description="统计指标", required=False),
            ],
            handler=analyze_data_handler
        ),
    ]


def clean_data_handler(data: str, method: Optional[str] = "default") -> Dict[str, Any]:
    """数据清洗"""
    return {
        "success": True,
        "data": {
            "original": data,
            "cleaned": f"Cleaned: {data}",
            "method": method
        }
    }


def analyze_data_handler(data: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """数据分析"""
    return {
        "success": True,
        "data": {
            "data": data,
            "metrics": metrics or {"count": 0, "mean": 0},
            "analysis": "Analysis result"
        }
    }
```

### 示例 2：API 调用技能包

```python
"""
API 调用技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional
import requests


SKILL_PACKAGE = {
    "name": "api_client",
    "version": "1.0.0",
    "description": "API 调用技能包 - 提供 HTTP 请求和 API 集成功能",
    "author": "API Team",
    "default_visible": False,
    "category": "network",
    "tags": ["api", "http", "integration"],
    
    "exposure": {
        "initial_description": "API 调用技能包 - 轻松集成各种 REST API",
        "priority": 2,
        "icon": "🌐",
    }
}


def get_tools():
    return [
        Tool(
            name="http_request",
            description="HTTP 请求 - 发送自定义 HTTP 请求",
            parameters=[
                ToolParameter(name="url", type="string", description="请求 URL", required=True),
                ToolParameter(name="method", type="string", description="HTTP 方法", required=False),
                ToolParameter(name="headers", type="object", description="请求头", required=False),
                ToolParameter(name="body", type="object", description="请求体", required=False),
            ],
            handler=http_request_handler
        ),
    ]


def http_request_handler(
    url: str,
    method: Optional[str] = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """HTTP 请求"""
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=body
        )
        
        return {
            "success": True,
            "data": {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 🔍 调试和测试

### 测试技能包

```bash
# 启动服务器
skillmcp start

# 查看技能包列表
skillmcp list-packages

# 测试技能包
skillmcp test-package my_skill
```

### 查看日志

```bash
# 实时查看日志
tail -f /tmp/skillmcp.log
```

---

## 📚 最佳实践

1. **命名规范**
   - 技能包名称使用小写字母和下划线
   - 工具名称使用小写字母和下划线
   - 避免使用保留字

2. **错误处理**
   - 始终返回 `{"success": True/False, ...}` 格式
   - 提供清晰的错误信息
   - 记录详细日志

3. **文档**
   - 提供清晰的工具描述
   - 说明每个参数的用途
   - 添加使用示例

4. **性能**
   - 避免阻塞操作
   - 使用异步函数处理耗时操作
   - 合理设置超时

---

**更新时间**: 2026-03-27  
**版本**: 1.0.0
