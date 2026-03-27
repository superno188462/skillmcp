"""
工具包管理器

负责发现、加载、管理技能包（工具包）。
"""

import importlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from loguru import logger

from skillmcp.core.interfaces import SkillPackage, Tool


class ToolPackageManager:
    """工具包管理器"""
    
    def __init__(self, package_dir: Optional[str] = None, config_file: Optional[str] = None):
        """初始化工具包管理器
        
        Args:
            package_dir: 工具包目录路径，默认为 packages/
            config_file: 配置文件路径，用于控制默认加载行为
        """
        self.package_dir = Path(package_dir) if package_dir else Path("packages")
        self.config_file = Path(config_file) if config_file else Path("skillmcp.json")
        self.packages: Dict[str, SkillPackage] = {}  # package_name -> SkillPackage
        self.loaded_packages: Dict[str, object] = {}  # package_name -> package_instance
        self.active_packages: Set[str] = set()  # 已激活的工具包名称
        self.config: Dict = {}  # 配置
        
        # 确保工具包目录存在
        self.package_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"已加载配置文件：{self.config_file}")
            except Exception as e:
                logger.warning(f"加载配置文件失败：{e}，使用默认配置")
                self.config = {}
        else:
            self.config = {}
    
    def _get_package_default_visibility(self, package_name: str) -> bool:
        """获取工具包的默认可见性
        
        优先级：配置文件 > 包元数据 > 默认值
        
        Args:
            package_name: 工具包名称
            
        Returns:
            是否可见
        """
        # 1. 检查配置文件
        if "packages" in self.config:
            pkg_config = self.config["packages"].get(package_name, {})
            if "visible" in pkg_config:
                return pkg_config["visible"]
        
        # 2. 使用包元数据中的值
        if package_name in self.packages:
            return self.packages[package_name].visible
        
        # 3. 默认可见
        return True
    
    def discover_packages(self) -> List[SkillPackage]:
        """发现所有可用的工具包
        
        Returns:
            工具包信息列表
        """
        packages = []
        
        if not self.package_dir.exists():
            logger.warning(f"工具包目录不存在：{self.package_dir}")
            return packages
        
        for pkg_path in self.package_dir.iterdir():
            if pkg_path.is_dir() and (pkg_path / "__init__.py").exists():
                try:
                    pkg_info = self._load_package_info(pkg_path)
                    if pkg_info:
                        packages.append(pkg_info)
                        self.packages[pkg_info.name] = pkg_info
                        
                        # 检查是否默认加载
                        if self._get_package_default_visibility(pkg_info.name):
                            logger.info(f"发现工具包：{pkg_info.name} v{pkg_info.version} (默认加载)")
                        else:
                            logger.info(f"发现工具包：{pkg_info.name} v{pkg_info.version}")
                except Exception as e:
                    logger.error(f"加载工具包 {pkg_path.name} 失败：{e}")
        
        return packages
    
    def _load_package_info(self, pkg_path: Path) -> Optional[SkillPackage]:
        """加载工具包元数据
        
        Args:
            pkg_path: 工具包路径
            
        Returns:
            工具包信息，加载失败返回 None
        """
        try:
            # 导入工具包模块
            module_name = f"{pkg_path.parent.name}.{pkg_path.name}"
            module = importlib.import_module(module_name)
            
            # 获取 PACKAGE_INFO 或 SKILL_PACKAGE
            if hasattr(module, "SKILL_PACKAGE"):
                return SkillPackage.from_dict(module.SKILL_PACKAGE)
            elif hasattr(module, "PACKAGE_INFO"):
                # 兼容旧格式
                old_info = PackageInfo.from_dict(module.PACKAGE_INFO)
                return SkillPackage(
                    name=old_info.name,
                    version=old_info.version,
                    description=old_info.description,
                    author=old_info.author,
                    tools=old_info.tools,
                    dependencies=old_info.dependencies,
                    visible=old_info.auto_load if hasattr(old_info, 'auto_load') else True,
                )
            else:
                # 使用默认信息
                return SkillPackage(
                    name=pkg_path.name,
                    version="0.1.0",
                    description=f"工具包：{pkg_path.name}",
                    visible=True,
                )
        except Exception as e:
            logger.error(f"加载工具包信息失败 {pkg_path}: {e}")
            return None
    
    def load_package(self, package_name: str) -> Optional[object]:
        """加载工具包
        
        Args:
            package_name: 工具包名称
            
        Returns:
            工具包实例，加载失败返回 None
        """
        if package_name in self.loaded_packages:
            logger.debug(f"工具包已加载：{package_name}")
            return self.loaded_packages[package_name]
        
        if package_name not in self.packages:
            logger.error(f"工具包不存在：{package_name}")
            return None
        
        try:
            # 导入工具包模块
            module = importlib.import_module(f"packages.{package_name}")
            
            # 获取工具函数（可选）
            if hasattr(module, "get_tools"):
                self.loaded_packages[package_name] = module
                logger.info(f"工具包已加载：{package_name}")
                return module
            else:
                # 没有 get_tools 函数也可以，工具在 server.py 中定义
                self.loaded_packages[package_name] = module
                logger.info(f"工具包已加载：{package_name} (无 get_tools 函数)")
                return module
        except Exception as e:
            logger.error(f"加载工具包 {package_name} 失败：{e}")
            return None
    
    def activate_package(self, package_name: str) -> bool:
        """激活工具包
        
        Args:
            package_name: 工具包名称
            
        Returns:
            是否成功激活
        """
        if package_name in self.active_packages:
            logger.debug(f"工具包已激活：{package_name}")
            return True
        
        # 确保工具包已加载
        if package_name not in self.loaded_packages:
            if not self.load_package(package_name):
                return False
        
        self.active_packages.add(package_name)
        logger.info(f"工具包已激活：{package_name}")
        return True
    
    def deactivate_package(self, package_name: str) -> bool:
        """停用工具包
        
        Args:
            package_name: 工具包名称
            
        Returns:
            是否成功停用
        """
        if package_name not in self.active_packages:
            logger.debug(f"工具包未激活：{package_name}")
            return True
        
        self.active_packages.remove(package_name)
        logger.info(f"工具包已停用：{package_name}")
        return True
    
    def get_active_tools(self) -> List[Tool]:
        """获取所有激活工具包中的工具
        
        Returns:
            工具列表
        """
        tools = []
        
        for pkg_name in self.active_packages:
            if pkg_name in self.loaded_packages:
                pkg_module = self.loaded_packages[pkg_name]
                if hasattr(pkg_module, "get_tools"):
                    pkg_tools = pkg_module.get_tools()
                    tools.extend(pkg_tools)
                    logger.debug(f"从 {pkg_name} 加载 {len(pkg_tools)} 个工具")
        
        return tools
    
    def list_packages(self) -> List[SkillPackage]:
        """列出所有可用工具包
        
        Returns:
            工具包信息列表
        """
        return list(self.packages.values())
    
    def get_package_status(self) -> Dict:
        """获取工具包状态
        
        Returns:
            工具包状态字典
        """
        return {
            "available": list(self.packages.keys()),
            "loaded": list(self.loaded_packages.keys()),
            "active": list(self.active_packages),
        }
