"""
示例技能包 - 展示如何开发自定义技能包
"""

from skillmcp.core.interfaces import Tool, ToolParameter
from typing import Dict, Any, Optional


# 技能包配置（简化版）
SKILL_PACKAGE = {
    "name": "example",
    "version": "1.0.0",
    "description": "示例技能包 - 提供数据处理和转换工具",
    "author": "Your Name",
    
    # 可选：是否默认启用（默认：False）
    # 设置为 True 则服务器启动时自动启用此技能包
    "default_enabled": False,
}


# 工具定义
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


# 工具实现
def process_data_handler(data: str, format: Optional[str] = "json") -> Dict[str, Any]:
    """数据处理工具实现"""
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
    return {
        "success": True,
        "data": {
            "input": input,
            "from": from_format,
            "to": to_format,
            "output": f"Converted from {from_format} to {to_format}: {input}"
        }
    }
