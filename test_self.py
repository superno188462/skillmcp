#!/usr/bin/env python3
"""
SkillMCP 自测脚本 - FastMCP v3 Provider 系统版本

测试完整的技能包加载流程。
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skillmcp.server import (
    mcp, 
    initialize_server, 
    provider,
    _active_packages,
    _package_tools,
    open_package,
    close_package,
    list_packages,
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_initialization():
    """测试 1: 服务器初始化"""
    print_section("测试 1: 服务器初始化")
    
    manager = initialize_server()
    
    assert manager is not None, "管理器初始化失败"
    assert len(manager.packages) > 0, "没有发现任何技能包"
    assert len(_active_packages) == 0, "初始状态应该没有激活的技能包"
    
    # 检查初始工具
    initial_tools = await provider.list_tools()
    assert len(initial_tools) == 3, f"初始应该有 3 个工具，实际有 {len(initial_tools)} 个"
    
    print(f"✅ 发现 {len(manager.packages)} 个技能包")
    print(f"✅ 已激活：{_active_packages}（初始为空）")
    print(f"✅ 初始工具数：{len(initial_tools)}")
    for tool in initial_tools:
        print(f"   - {tool.name}")


async def test_list_packages():
    """测试 2: 列出技能包"""
    print_section("测试 2: 列出技能包")
    
    result = list_packages()
    
    assert result["total_count"] > 0, "列出技能包失败"
    print(f"✅ 总技能包数：{result['total_count']}")
    print(f"✅ 已激活：{result['active_count']}")
    
    for pkg in result.get("packages", []):
        status = "✓" if pkg["active"] else "○"
        print(f"   [{status}] {pkg['name']:20} - {pkg['description'][:50]}")


async def test_open_package():
    """测试 3: 打开技能包"""
    print_section("测试 3: 打开技能包")
    
    # 打开 web 技能包
    result = open_package(package_name="web")
    
    assert result["success"], f"打开技能包失败：{result.get('error')}"
    print(f"✅ {result['message']}")
    
    # 检查工具是否注册
    all_tools = await provider.list_tools()
    print(f"✅ 当前工具数：{len(all_tools)}")
    print(f"✅ 已注册的技能包工具：{_package_tools}")


async def test_close_package():
    """测试 4: 关闭技能包"""
    print_section("测试 4: 关闭技能包")
    
    # 先打开
    open_package(package_name="web")
    
    # 再关闭
    result = close_package(package_name="web")
    
    assert result["success"], f"关闭技能包失败"
    print(f"✅ {result['message']}")
    
    # 检查工具是否移除
    all_tools = await provider.list_tools()
    print(f"✅ 当前工具数：{len(all_tools)}")


async def test_workflow():
    """测试 5: 完整工作流程"""
    print_section("测试 5: 完整工作流程")
    
    print("步骤 1: 初始化服务器")
    manager = initialize_server()
    print("✅ 服务器已初始化")
    
    print("\n步骤 2: 查看技能包列表")
    packages = list_packages()
    print(f"✅ 发现 {packages['total_count']} 个技能包")
    
    print("\n步骤 3: 打开 web 技能包")
    result = open_package(package_name="web")
    assert result["success"]
    print(f"✅ {result['message']}")
    
    print("\n步骤 4: 检查工具列表")
    tools = await provider.list_tools()
    print(f"✅ 当前工具数：{len(tools)}")
    
    print("\n步骤 5: 关闭 web 技能包")
    result = close_package(package_name="web")
    assert result["success"]
    print(f"✅ {result['message']}")
    
    print("\n✅ 完整工作流程测试通过")


async def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "SkillMCP 自测脚本 (FastMCP v3 Provider)" + " " * 5 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("服务器初始化", test_initialization),
        ("列出技能包", test_list_packages),
        ("打开技能包", test_open_package),
        ("关闭技能包", test_close_package),
        ("完整工作流程", test_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {test_name} 失败：{e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} 未知错误：{e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 总结
    print_section("测试总结")
    print(f"✅ 通过：{passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ 失败：{failed}/{len(tests)}")
        return 1
    else:
        print("\n🎉 所有测试通过!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
