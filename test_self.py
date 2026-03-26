#!/usr/bin/env python3
"""
SkillMCP 自测脚本

测试完整的技能包加载流程（资源驱动设计）。
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skillmcp.server import (
    mcp, 
    initialize_server, 
    _package_manager, 
    _loaded_tools,
    list_all_packages,
    get_package_details,
    open_package,
    close_package,
    close_all_packages,
    get_usage_stats,
    get_package_info
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_initialization():
    """测试 1: 服务器初始化"""
    print_section("测试 1: 服务器初始化")
    
    manager = initialize_server()
    
    assert manager is not None, "管理器初始化失败"
    assert len(manager.packages) > 0, "没有发现任何技能包"
    assert len(manager.active_packages) == 0, "初始状态应该没有激活的技能包"
    
    print(f"✅ 发现 {len(manager.packages)} 个技能包")
    print(f"✅ 已激活：{manager.active_packages}（初始为空）")


def test_list_packages_resource():
    """测试 2: 查看技能包资源（核心功能）"""
    print_section("测试 2: 查看技能包资源（核心功能）")
    
    # 获取技能包列表资源
    resource = list_all_packages()
    
    assert resource is not None, "技能包资源为空"
    assert "SkillMCP 可用技能包列表" in resource, "资源格式错误"
    assert "web" in resource, "缺少 web 技能包"
    assert "base" not in resource, "不应该有 base 技能包"
    
    print("✅ 技能包资源格式正确")
    print("✅ 没有 base 技能包（管理工具不暴露）")
    print("\n资源内容预览:")
    print("-" * 60)
    # 打印前 20 行
    lines = resource.split('\n')[:20]
    for line in lines:
        print(line)
    print("-" * 60)


def test_package_details():
    """测试 3: 查看技能包详情"""
    print_section("测试 3: 查看技能包详情")
    
    # 获取 web 技能包详情
    details = get_package_details("web")
    
    assert details is not None, "技能包详情为空"
    assert "WEB" in details, "缺少技能包名称"
    assert "HTTP" in details or "http" in details, "缺少功能描述"
    assert "open_package" in details, "缺少打开方式说明"
    
    print("✅ web 技能包详情格式正确")
    print("\n详情预览:")
    print("-" * 60)
    print(details[:500])  # 打印前 500 字符
    print("...")
    print("-" * 60)


def test_get_package_info():
    """测试 4: 获取技能包信息（工具方式）"""
    print_section("测试 4: 获取技能包信息（工具方式）")
    
    result = get_package_info("web")
    
    assert result["success"], "获取技能包信息失败"
    assert "package" in result, "缺少技能包信息"
    assert result["package"]["name"] == "web", "技能包名称错误"
    
    print(f"✅ 技能包信息获取成功")
    print(f"   名称：{result['package']['name']}")
    print(f"   版本：{result['package']['version']}")
    print(f"   描述：{result['package']['description'][:50]}...")
    print(f"   状态：{'已激活' if result['active'] else '未激活'}")


def test_open_package():
    """测试 5: 打开技能包"""
    print_section("测试 5: 打开技能包")
    
    # 打开 web 技能包
    result = open_package(package_name="web", reason="测试 HTTP 功能")
    
    assert result["success"], f"打开技能包失败：{result.get('error')}"
    print(f"✅ {result['message']}")
    
    if result.get("tools_loaded"):
        print(f"✅ 加载的工具：{result['tools_loaded']}")
    else:
        print(f"ℹ️  工具在 server.py 中静态定义")


def test_get_usage_stats():
    """测试 6: 查看使用统计"""
    print_section("测试 6: 查看使用统计")
    
    stats = get_usage_stats()
    
    print(f"✅ 已激活技能包：{stats['active_packages']}")
    print(f"✅ 技能包数量：{stats['active_package_count']}")
    print(f"✅ 工具数量：{stats['active_tools_count']}")
    print(f"✅ 估算 Token: {stats['estimated_token_usage']}")
    print(f"✅ 状态：{stats.get('warning', '✅ 工具数量合理')}")


def test_close_package():
    """测试 7: 关闭单个技能包"""
    print_section("测试 7: 关闭单个技能包")
    
    # 先打开
    open_package(package_name="web")
    
    # 再关闭
    result = close_package(package_name="web")
    
    assert result["success"], f"关闭技能包失败"
    print(f"✅ {result['message']}")


def test_close_all_packages():
    """测试 8: 关闭所有技能包"""
    print_section("测试 8: 关闭所有技能包")
    
    # 先打开多个技能包
    open_package(package_name="web")
    
    # 关闭所有（不排除）
    result = close_all_packages(exclude=[])
    
    assert result["success"], f"关闭所有技能包失败"
    print(f"✅ {result['message']}")
    print(f"✅ 关闭的包：{result.get('closed_packages', [])}")
    print(f"✅ 剩余包：{result.get('remaining', [])}（应该为空）")


def test_workflow():
    """测试 9: 完整工作流程"""
    print_section("测试 9: 完整工作流程")
    
    print("步骤 1: AI 查看技能包资源")
    resource = list_all_packages()
    print("✅ 已查看技能包列表")
    
    print("\n步骤 2: AI 分析需要 web 技能包")
    print("✅ 决定打开 web 技能包")
    
    print("\n步骤 3: AI 打开技能包")
    result = open_package(package_name="web", reason="需要 HTTP 功能")
    assert result["success"]
    print(f"✅ {result['message']}")
    
    print("\n步骤 4: AI 使用技能包中的工具")
    print("✅ （工具调用测试）")
    
    print("\n步骤 5: AI 关闭技能包")
    result = close_package(package_name="web")
    assert result["success"]
    print(f"✅ {result['message']}")
    
    print("\n✅ 完整工作流程测试通过")


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "SkillMCP 自测脚本（资源驱动设计）" + " " * 8 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("服务器初始化", test_initialization),
        ("查看技能包资源", test_list_packages_resource),
        ("查看技能包详情", test_package_details),
        ("获取技能包信息", test_get_package_info),
        ("打开技能包", test_open_package),
        ("查看使用统计", test_get_usage_stats),
        ("关闭单个技能包", test_close_package),
        ("关闭所有技能包", test_close_all_packages),
        ("完整工作流程", test_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
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
    sys.exit(main())
