# SkillMCP 自定义技能包开发指南

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


# 技能包配置（只需 4 个字段）
SKILL_PACKAGE = {
    "name": "my_skill",
    "version": "1.0.0",
    "description": "我的技能包 - 提供 XX 功能",
    "author": "Your Name",
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

完成！技能包会被自动发现。

---

## 📁 技能包结构

```
packages/
└── my_skill/
    ├── __init__.py       # 必需：技能包配置和工具定义
    └── utils/            # 可选：工具函数
        └── helpers.py
```

---

## ⚙️ 技能包配置

### 必需字段（只有 4 个）

```python
SKILL_PACKAGE = {
    "name": "my_skill",           # 技能包名称（唯一）
    "version": "1.0.0",           # 版本号
    "description": "技能包描述",   # 功能描述
    "author": "Your Name",        # 作者
}
```

### 就这么简单！

不需要：
- ❌ `tools` 列表（自动从 `get_tools()` 获取）
- ❌ `exposure` 配置（使用 description）
- ❌ `category`、`tags`（可选，暂不需要）
- ❌ `dependencies`（可选，暂不需要）

---

## 🛠️ 工具定义

### Tool 参数

```python
from skillmcp.core.interfaces import Tool, ToolParameter

Tool(
    name="tool_name",              # 工具名称（唯一）
    description="工具功能描述",     # 工具描述
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

| 类型 | Python 对应 | 示例 |
|------|------------|------|
| `string` | `str` | `"hello"` |
| `number` | `float` | `3.14` |
| `integer` | `int` | `42` |
| `boolean` | `bool` | `True` |
| `object` | `Dict[str, Any]` | `{"key": "value"}` |

### 工具实现

```python
def my_tool_handler(input: str, optional_param: str = "default") -> Dict[str, Any]:
    """工具实现
    
    Args:
        input: 输入参数
        optional_param: 可选参数
        
    Returns:
        返回字典格式结果
    """
    return {
        "success": True,
        "data": {
            "result": f"处理：{input}"
        }
    }
```

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


def analyze_data_handler(data: str) -> Dict[str, Any]:
    """数据分析"""
    return {
        "success": True,
        "data": {
            "data": data,
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

# 查看日志
tail -f /tmp/skillmcp.log
```

### 查看技能包列表

```bash
skillmcp list-packages
```

---

## 📚 最佳实践

1. **命名规范**
   - 技能包名称：小写字母 + 下划线（如 `my_skill`）
   - 工具名称：小写字母 + 下划线（如 `process_data`）

2. **错误处理**
   - 始终返回 `{"success": True/False, ...}` 格式
   - 提供清晰的错误信息

3. **文档**
   - 提供清晰的工具描述
   - 说明每个参数的用途

4. **性能**
   - 使用异步函数处理耗时操作
   - 合理设置超时

---

**更新时间**: 2026-03-27  
**版本**: 1.0.0
