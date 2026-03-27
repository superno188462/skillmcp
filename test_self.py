#!/usr/bin/env python3
"""
SkillMCP 自测脚本 - 技能包即工具设计

测试完整的技能包加载流程。
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skillmcp.server import provider, _active_packages, _package_tools


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_initialization():
    """测试 1: 模块加载和初始化"""
    print_section("测试 1: 模块加载和初始化")
    
    # 检查初始工具
    initial_tools = await provider.list_tools()
    
    assert len(initial_tools) > 0, "初始应该有技能包工具"
    assert len(_active_packages) == 0, "初始状态应该没有激活的技能包"
    
    print(f"✅ 模块加载时自动初始化")
    print(f"✅ 初始工具数：{len(initial_tools)}")
    for tool in initial_tools:
        print(f"   - {tool.name}")
    
    # 验证工具命名
    for tool in initial_tools:
        assert tool.name.endswith("_tool"), f"工具名称应该以 _tool 结尾：{tool.name}"
    print(f"✅ 工具命名规范：技能包名_tool")


async def test_web_tool():
    """测试 2: web_tool 工具"""
    print_section("测试 2: web_tool 工具")
    
    # 获取 web_tool
    web_tool = await provider.get_tool('web_tool')
    
    assert web_tool is not None, "web_tool 应该存在"
    print(f"✅ web_tool 存在")
    print(f"   描述：{web_tool.description[:80]}...")
    
    # 检查参数
    params = web_tool.parameters
    print(f"   参数：{params}")
    assert 'properties' in params, "工具应该有参数定义"
    assert 'enable' in params['properties'], "web_tool 应该有 enable 参数"
    print(f"✅ enable 参数存在")


async def test_enable_package():
    """测试 3: 启用技能包"""
    print_section("测试 3: 启用技能包")
    
    # 获取 web_tool
    web_tool = await provider.get_tool('web_tool')
    
    # 启用技能包
    result = await web_tool.fn(enable=True)
    
    print(f"启用结果：{result}")
    assert result['success'], f"启用失败：{result.get('error')}"
    assert result.get('sub_tools_registered', 0) > 0, "应该注册了子工具"
    
    print(f"✅ 技能包启用成功")
    print(f"✅ 注册了 {result['sub_tools_registered']} 个子工具")
    print(f"   子工具：{result.get('sub_tools', [])}")
    
    # 检查工具列表
    all_tools = await provider.list_tools()
    print(f"✅ 当前工具数：{len(all_tools)}")
    
    # 验证子工具已注册
    tool_names = [t.name for t in all_tools]
    assert 'http_get' in tool_names, "http_get 应该已注册"
    assert 'http_post' in tool_names, "http_post 应该已注册"
    print(f"✅ 子工具已正确注册")


async def test_disable_package():
    """测试 4: 禁用技能包"""
    print_section("测试 4: 禁用技能包")
    
    # 先启用
    web_tool = await provider.get_tool('web_tool')
    await web_tool.fn(enable=True)
    
    # 再禁用
    result = await web_tool.fn(enable=False)
    
    print(f"禁用结果：{result}")
    assert result['success'], f"禁用失败：{result.get('error')}"
    
    print(f"✅ 技能包禁用成功")
    print(f"✅ 移除了 {result.get('sub_tools_removed', 0)} 个子工具")
    
    # 检查工具列表
    all_tools = await provider.list_tools()
    print(f"✅ 当前工具数：{len(all_tools)}")
    
    # 验证子工具已移除
    tool_names = [t.name for t in all_tools]
    assert 'http_get' not in tool_names, "http_get 应该已移除"
    assert 'http_post' not in tool_names, "http_post 应该已移除"
    assert 'web_tool' in tool_names, "web_tool 应该保留"
    print(f"✅ 子工具已正确移除，只保留技能包工具")


async def test_workflow():
    """测试 5: 完整工作流程"""
    print_section("测试 5: 完整工作流程")
    
    print("步骤 1: 查看可用技能包")
    initial_tools = await provider.list_tools()
    print(f"✅ 初始工具：{[t.name for t in initial_tools]}")
    
    print("\n步骤 2: 启用 web 技能包")
    web_tool = await provider.get_tool('web_tool')
    result = await web_tool.fn(enable=True)
    print(f"✅ {result['message']}")
    
    print("\n步骤 3: 查看启用后的工具列表")
    tools_after_enable = await provider.list_tools()
    print(f"✅ 工具数：{len(tools_after_enable)}")
    for tool in tools_after_enable:
        print(f"   - {tool.name}")
    
    print("\n步骤 4: 使用子工具（模拟）")
    http_get = await provider.get_tool('http_get')
    assert http_get is not None, "http_get 应该可用"
    print(f"✅ http_get 工具可用")
    
    print("\n步骤 5: 禁用 web 技能包")
    result = await web_tool.fn(enable=False)
    print(f"✅ {result['message']}")
    
    print("\n步骤 6: 查看禁用后的工具列表")
    tools_after_disable = await provider.list_tools()
    print(f"✅ 工具数：{len(tools_after_disable)}")
    for tool in tools_after_disable:
        print(f"   - {tool.name}")
    
    print("\n✅ 完整工作流程测试通过")


async def test_resource():
    """测试 6: 技能包资源"""
    print_section("测试 6: 技能包资源")
    
    from skillmcp.server import list_packages_resource
    
    resource = list_packages_resource()
    
    assert resource is not None, "资源应该存在"
    assert "web_tool" in resource, "资源应该包含 web_tool"
    assert "技能包" in resource or "SkillMCP" in resource, "资源格式应该正确"
    
    print(f"✅ 技能包资源格式正确")
    print("\n资源预览:")
    print("-" * 60)
    lines = resource.split('\n')[:15]
    for line in lines:
        print(line)
    print("-" * 60)


async def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "SkillMCP 自测脚本 (技能包即工具)" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("模块加载和初始化", test_initialization),
        ("web_tool 工具", test_web_tool),
        ("启用技能包", test_enable_package),
        ("禁用技能包", test_disable_package),
        ("完整工作流程", test_workflow),
        ("技能包资源", test_resource),
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
        print("\n📊 设计理念验证:")
        print("   ✅ 技能包 = 工具（带 enable 参数）")
        print("   ✅ 没有管理工具，所有工具都是业务工具")
        print("   ✅ 启用后注册子工具，禁用后移除")
        print("   ✅ Token 优化：初始只有技能包工具")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
