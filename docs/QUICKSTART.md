# SkillMCP 快速开始指南

## 🚀 5 分钟快速上手

### 1. 安装依赖

```bash
cd skillmcp
uv sync
```

### 2. 创建配置文件（可选）

```bash
# 复制示例配置
cp skillmcp.json.example skillmcp.json

# 编辑配置
vim skillmcp.json
```

示例配置：
```json
{
  "packages": {
    "core": {
      "default_visible": true
    },
    "web": {
      "default_visible": false
    }
  },
  "features": {
    "auto_load_defaults": true
  }
}
```

### 3. 启动服务器

```bash
# 使用默认配置
uv run skillmcp start

# 使用配置文件
uv run skillmcp start --config skillmcp.json

# 自定义参数
uv run skillmcp start --host 0.0.0.0 --port 8000
```

### 4. 查看可用技能包

```bash
# 列出所有技能包
uv run skillmcp list-packages

# 查看技能包详情
uv run skillmcp show-package web
```

### 5. 创建新技能包

```bash
# 创建目录结构
mkdir -p packages/my_package

# 创建 __init__.py
cat > packages/my_package/__init__.py << 'EOF'
SKILL_PACKAGE = {
    "name": "my_package",
    "version": "1.0.0",
    "description": "我的技能包",
    "default_visible": False,  # 默认不加载
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

### 6. 测试技能包

```bash
# 重新启动服务器
uv run skillmcp start

# 在新终端测试
curl http://localhost:8000/api/v1/packages
```

---

## 📚 配置说明

### 技能包元数据字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 技能包名称 |
| `version` | string | ✅ | 版本号 |
| `description` | string | ❌ | 描述信息 |
| `author` | string | ❌ | 作者 |
| `tools` | string[] | ❌ | 工具列表 |
| `dependencies` | string[] | ❌ | 依赖的技能包 |
| `default_visible` | boolean | ❌ | 是否默认显示/加载 |
| `category` | string | ❌ | 分类（general, web, data 等） |
| `tags` | string[] | ❌ | 标签 |

### 配置文件字段

```json
{
  "packages": {
    "<package_name>": {
      "default_visible": true,
      "description": "可选的覆盖描述"
    }
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "INFO"
  },
  "features": {
    "auto_load_defaults": true,
    "allow_dynamic_load": true,
    "tool_timeout": 30
  }
}
```

---

## 🎯 常见使用场景

### 场景 1：开发环境 - 加载所有技能包

```json
{
  "packages": {
    "*": {
      "default_visible": true
    }
  }
}
```

### 场景 2：生产环境 - 最小化加载

```json
{
  "packages": {
    "core": {
      "default_visible": true
    }
  },
  "features": {
    "auto_load_defaults": false
  }
}
```

### 场景 3：按功能模块加载

```json
{
  "packages": {
    "core": {
      "default_visible": true
    },
    "web": {
      "default_visible": true
    },
    "data": {
      "default_visible": false
    }
  }
}
```

---

## 🔧 故障排查

### 问题 1：技能包未被发现

```bash
# 检查目录结构
ls -la packages/

# 检查 __init__.py 是否存在
ls packages/my_package/__init__.py

# 检查 SKILL_PACKAGE 定义
cat packages/my_package/__init__.py
```

### 问题 2：配置文件未生效

```bash
# 检查配置文件路径
ls -la skillmcp.json

# 验证 JSON 格式
python3 -m json.tool skillmcp.json

# 查看启动日志
uv run skillmcp start 2>&1 | grep "配置"
```

### 问题 3：工具无法调用

```bash
# 检查技能包是否已激活
curl http://localhost:8000/api/v1/tools

# 手动打开技能包
curl -X POST http://localhost:8000/api/v1/packages/my_package/open
```

---

## 📖 下一步

- 查看 [设计文档](docs/DESIGN.md) 了解完整架构
- 查看 [API 文档](docs/API.md) 了解接口详情
- 查看 [示例代码](examples/) 学习最佳实践

---

**SkillMCP** - 让 AI 工具管理更高效、更灵活！🎉
