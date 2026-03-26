"""
技能注册表

负责技能的注册、发现、加载和生命周期管理。
"""

import importlib
from pathlib import Path
from typing import Dict, List, Optional, Type
from loguru import logger

from skillmcp.core.interfaces import Skill, SkillInfo


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self, skill_dir: Optional[str] = None):
        """初始化技能注册表
        
        Args:
            skill_dir: 技能目录路径，默认为 skills/
        """
        self.skill_dir = Path(skill_dir) if skill_dir else Path("skills")
        self.skills: Dict[str, SkillInfo] = {}  # skill_name -> SkillInfo
        self.loaded_skills: Dict[str, Skill] = {}  # skill_name -> SkillInstance
        
        # 确保技能目录存在
        self.skill_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_skills(self) -> List[SkillInfo]:
        """发现所有可用的技能
        
        Returns:
            技能信息列表
        """
        skills = []
        
        if not self.skill_dir.exists():
            logger.warning(f"技能目录不存在：{self.skill_dir}")
            return skills
        
        for skill_path in self.skill_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "__init__.py").exists():
                try:
                    skill_info = self._load_skill_info(skill_path)
                    if skill_info:
                        skills.append(skill_info)
                        self.skills[skill_info.name] = skill_info
                        logger.info(f"发现技能：{skill_info.name} v{skill_info.version}")
                except Exception as e:
                    logger.error(f"加载技能 {skill_path.name} 失败：{e}")
        
        return skills
    
    def _load_skill_info(self, skill_path: Path) -> Optional[SkillInfo]:
        """加载技能元数据
        
        Args:
            skill_path: 技能路径
            
        Returns:
            技能信息，加载失败返回 None
        """
        try:
            # 导入技能模块
            module_name = f"{skill_path.parent.name}.{skill_path.name}.skill"
            module = importlib.import_module(module_name)
            
            # 查找 Skill 子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Skill) and 
                    attr is not Skill):
                    # 创建实例获取信息
                    instance = attr()
                    return SkillInfo(
                        name=instance.name,
                        version=instance.version,
                        description=instance.description,
                        module=module_name,
                    )
            
            return None
        except Exception as e:
            logger.error(f"加载技能信息失败 {skill_path}: {e}")
            return None
    
    def register(self, skill_class: Type[Skill]) -> None:
        """注册技能类
        
        Args:
            skill_class: 技能类
        """
        instance = skill_class()
        skill_info = SkillInfo(
            name=instance.name,
            version=instance.version,
            description=instance.description,
            module=skill_class.__module__,
        )
        self.skills[skill_info.name] = skill_info
        logger.info(f"技能已注册：{skill_info.name}")
    
    def load(self, skill_name: str) -> Optional[Skill]:
        """加载技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            技能实例，加载失败返回 None
        """
        if skill_name in self.loaded_skills:
            logger.debug(f"技能已加载：{skill_name}")
            return self.loaded_skills[skill_name]
        
        if skill_name not in self.skills:
            logger.error(f"技能不存在：{skill_name}")
            return None
        
        try:
            skill_info = self.skills[skill_name]
            
            # 导入技能模块
            module = importlib.import_module(skill_info.module)
            
            # 查找 Skill 子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Skill) and 
                    attr is not Skill):
                    # 创建实例并初始化
                    instance = attr()
                    await instance.initialize()
                    self.loaded_skills[skill_name] = instance
                    logger.info(f"技能已加载：{skill_name}")
                    return instance
            
            logger.error(f"技能 {skill_name} 未找到实现类")
            return None
        except Exception as e:
            logger.error(f"加载技能 {skill_name} 失败：{e}")
            return None
    
    async def unload(self, skill_name: str) -> bool:
        """卸载技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            是否成功卸载
        """
        if skill_name not in self.loaded_skills:
            logger.debug(f"技能未加载：{skill_name}")
            return True
        
        try:
            skill = self.loaded_skills[skill_name]
            await skill.shutdown()
            del self.loaded_skills[skill_name]
            logger.info(f"技能已卸载：{skill_name}")
            return True
        except Exception as e:
            logger.error(f"卸载技能 {skill_name} 失败：{e}")
            return False
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取技能实例
        
        Args:
            skill_name: 技能名称
            
        Returns:
            技能实例，未加载返回 None
        """
        return self.loaded_skills.get(skill_name)
    
    def list_skills(self) -> List[SkillInfo]:
        """列出所有已注册技能
        
        Returns:
            技能信息列表
        """
        return list(self.skills.values())
    
    def get_status(self) -> Dict:
        """获取技能状态
        
        Returns:
            技能状态字典
        """
        return {
            "registered": list(self.skills.keys()),
            "loaded": list(self.loaded_skills.keys()),
        }
