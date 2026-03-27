"""
自定义技能包示例

这个示例展示如何开发一个自定义技能包，包括：
1. 技能包配置
2. 工具定义
3. 自定义初始暴露信息
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


# ============================================================================
# 技能包配置
# ============================================================================

SKILL_PACKAGE = {
    "name": "example",
    "version": "1.0.0",
    "description": "示例技能包 - 展示如何开发自定义技能包",
    "author": "Your Name",
    "dependencies": [],
    "default_visible": False,  # 是否默认启用
    "category": "example",
    "tags": ["example", "demo"],
    
    # 自定义初始暴露信息
    "exposure": {
        "initial_description": "示例技能包 - 提供数据处理和转换工具",
        "show_in_list": True,  # 是否在技能包列表中显示
        "priority": 1,  # 优先级（数字越小越靠前）
        "icon": "🔧",  # 图标（可选）
    }
}


# ============================================================================
# 工具定义
# ============================================================================

def get_tools():
    """返回此技能包包含的工具列表"""
    return [
        Tool(
            name="process_data",
            description="处理数据 - 对输入数据进行转换和处理",
            parameters=[
                ToolParameter(name="data", type="string", description="要处理的数据", required=True),
                ToolParameter(name="format", type="string", description="输出格式 (json/csv)", required=False),
            ],
            handler=process_data_handler
        ),
        Tool(
            name="convert_format",
            description="格式转换 - 在不同数据格式之间转换",
            parameters=[
                ToolParameter(name="input", type="string", description="输入数据", required=True),
                ToolParameter(name="from_format", type="string", description="源格式", required=True),
                ToolParameter(name="to_format", type="string", description="目标格式", required=True),
            ],
            handler=convert_format_handler
        ),
    ]


# ============================================================================
# 工具实现
# ============================================================================

def process_data_handler(data: str, format: Optional[str] = "json") -> Dict[str, Any]:
    """数据处理工具实现"""
    # TODO: 实现实际的数据处理逻辑
    return {
        "success": True,
        "data": {
            "original": data,
            "processed": f"Processed: {data}",
            "format": format
        }
    }


def convert_format_handler(input: str, from_format: str, to_format: str) -> Dict[str, Any]:
    """格式转换工具实现"""
    # TODO: 实现实际的格式转换逻辑
    return {
        "success": True,
        "data": {
            "input": input,
            "from": from_format,
            "to": to_format,
            "output": f"Converted from {from_format} to {to_format}: {input}"
        }
    }
