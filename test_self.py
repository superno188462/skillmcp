#!/usr/bin/env python3
"""
SkillMCP 自测脚本

测试完整的技能包加载流程。
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from skillmcp.server import mcp, initialize_server, _package_manager, _loaded_tools


def test_initialization():
    """测试 1: 服务器初始化"""
    print("=" * 60)
    print("测试 1: 服务器初始化")
    print("=" * 60)
    
    manager = initialize_server()
    
    assert manager is not None, "管理器初始化失败"
    assert len(manager.packages) > 0, "没有发现任何技能包"
    assert "base" in manager.active_packages, "base 技能包应该默认激活"
    
    print(f"✅ 发现 {len(manager.packages)} 个技能包")
    print(f"✅ 已激活：{manager.active_packages}")
    print()


def test_list_packages():
    """测试 2: 列出技能包"""
    print("=" * 60)
    print("测试 2: 列出技能包")
    print("=" * 60)
    
    from skillmcp.server import list_packages
    
    result = list_packages()
    
    assert result.get("total", 0) > 0, "列出技能包失败"
    print(f"✅ 总技能包数：{result.get('total', 0)}")
    print(f"✅ 已激活：{result.get('active_count', 0)}")
    
    for pkg in result.get("packages", []):
        status = "✓" if pkg["active"] else "○"
        print(f"   [{status}] {pkg['name']:20} - {pkg['description'][:50]}")
    print()


def test_open_package():
    """测试 3: 打开技能包"""
    print("=" * 60)
    print("测试 3: 打开技能包")
    print("=" * 60)
    
    from skillmcp.server import open_package
    
    # 打开 web 技能包
    result = open_package(package_name="web")
    
    assert result["success"], f"打开技能包失败：{result.get('error')}"
    print(f"✅ {result['message']}")
    print(f"✅ 加载的工具：{result.get('tools_loaded', [])}")
    print()


def test_get_usage_stats():
    """测试 4: 查看使用统计"""
    print("=" * 60)
    print("测试 4: 查看使用统计")
    print("=" * 60)
    
    from skillmcp.server import get_usage_stats
    
    stats = get_usage_stats()
    
    print(f"✅ 已激活技能包：{stats['active_packages']}")
    print(f"✅ 技能包数量：{stats['active_package_count']}")
    print(f"✅ 工具数量：{stats['active_tools_count']}")
    print(f"✅ 估算 Token: {stats['estimated_token_usage']}")
    print(f"✅ 状态：{stats.get('warning', '✅ 工具数量合理')}")
    print()


def test_close_all():
    """测试 5: 关闭所有技能包"""
    print("=" * 60)
    print("测试 5: 关闭所有技能包")
    print("=" * 60)
    
    from skillmcp.server import close_all_packages
    
    result = close_all_packages(exclude=["base"])
    
    assert result["success"], f"关闭技能包失败：{result}"
    print(f"✅ {result['message']}")
    print(f"✅ 关闭的包：{result.get('closed_packages', [])}")
    print(f"✅ 剩余包：{result.get('remaining', [])}")
    print()


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "SkillMCP 自测脚本" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        test_initialization()
        test_list_packages()
        test_open_package()
        test_get_usage_stats()
        test_close_all()
        
        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        return 1
    except Exception as e:
        print(f"\n❌ 未知错误：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
