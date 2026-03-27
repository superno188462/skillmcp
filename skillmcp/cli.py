"""
SkillMCP 命令行接口
"""

import asyncio
import click
from loguru import logger

from skillmcp import SkillMCPGateway


@click.group()
@click.version_option(version="0.1.0")
def main():
    """SkillMCP - 模块化技能管理平台"""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="服务器地址")
@click.option("--port", default=8000, help="服务器端口")
@click.option("--package-dir", default="packages", help="技能包目录")
@click.option("--config", default="skillmcp.json", help="配置文件")
@click.option("--log-level", default="INFO", help="日志级别")
@click.option("--transport", default="sse", type=click.Choice(["stdio", "sse"]), help="传输方式")
def start(host, port, package_dir, config, log_level, transport):
    """启动 SkillMCP FastMCP 服务器"""
    logger.remove()
    logger.add(
        lambda msg: click.echo(msg, nl=True),
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    logger.info(f"启动 SkillMCP FastMCP 服务器 (transport={transport})")
    
    # 设置环境变量
    import os
    os.environ["SKILLMCP_PACKAGE_DIR"] = package_dir
    os.environ["SKILLMCP_CONFIG"] = config
    
    # 导入并运行 FastMCP 服务器
    from skillmcp.server import mcp
    
    logger.info("SkillMCP FastMCP 服务器已就绪")
    logger.info(f"技能包目录：{package_dir}")
    logger.info(f"配置文件：{config}")
    
    # 运行服务器
    if transport == "sse":
        logger.info(f"SSE 模式：http://{host}:{port}/sse")
        mcp.run(transport="sse")
    else:
        logger.info("STDIO 模式：通过标准输入输出通信")
        mcp.run(transport="stdio")


@main.command()
@click.option("--package-dir", default="packages", help="工具包目录")
def list_packages(package_dir):
    """列出所有可用工具包"""
    from skillmcp.core.package_manager import ToolPackageManager
    
    manager = ToolPackageManager(package_dir=package_dir)
    packages = manager.discover_packages()
    
    click.echo("\n可用工具包:")
    click.echo("-" * 60)
    
    for pkg in packages:
        status = "✓" if pkg.auto_load else " "
        click.echo(f"[{status}] {pkg.name:20} v{pkg.version:10} - {pkg.description}")
    
    click.echo("-" * 60)
    click.echo(f"总计：{len(packages)} 个工具包\n")


@main.command()
@click.argument("package_name")
@click.option("--package-dir", default="packages", help="工具包目录")
def show_package(package_name, package_dir):
    """显示工具包详情"""
    from skillmcp.core.package_manager import ToolPackageManager
    
    manager = ToolPackageManager(package_dir=package_dir)
    packages = manager.discover_packages()
    
    pkg = next((p for p in packages if p.name == package_name), None)
    
    if not pkg:
        click.echo(f"错误：工具包 '{package_name}' 不存在")
        return
    
    click.echo(f"\n工具包：{pkg.name}")
    click.echo(f"版本：{pkg.version}")
    click.echo(f"描述：{pkg.description}")
    click.echo(f"作者：{pkg.author or 'N/A'}")
    click.echo(f"自动加载：{'是' if pkg.auto_load else '否'}")
    click.echo(f"工具：{', '.join(pkg.tools) if pkg.tools else 'N/A'}")
    click.echo(f"依赖：{', '.join(pkg.dependencies) if pkg.dependencies else '无'}\n")


@main.command()
def create():
    """创建新工具包模板"""
    click.echo("创建新工具包模板功能开发中...")


if __name__ == "__main__":
    main()
