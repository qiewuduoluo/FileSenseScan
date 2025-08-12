"""
FileSenseScan 版本管理系统
支持版本号管理、变更描述、代码回滚、错误监控和稳定性保护
"""

import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import traceback
import sys


@dataclass
class VersionInfo:
    """版本信息数据类"""
    version: str
    commit_hash: str
    timestamp: str
    author: str
    description: str
    changes: List[str]
    stability_score: float  # 0-100，稳定性评分
    is_stable: bool
    backup_path: Optional[str] = None
    rollback_count: int = 0


@dataclass
class ChangeLog:
    """变更日志数据类"""
    version: str
    date: str
    author: str
    changes: List[str]
    breaking_changes: List[str]
    bug_fixes: List[str]
    new_features: List[str]
    improvements: List[str]


class VersionManager:
    """版本管理器主类"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.version_file = self.project_root / "version_info.json"
        self.backup_dir = self.project_root / "backups"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        self.stable_versions_file = self.project_root / "stable_versions.json"
        
        # 确保目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
        # 初始化日志
        self._setup_logging()
        
        # 加载版本信息
        self.version_info = self._load_version_info()
        self.stable_versions = self._load_stable_versions()
        
        # 当前版本
        self.current_version = self.version_info.get("current_version", "1.0.0")
        
        # 稳定性阈值
        self.stability_threshold = 80.0
        
        # 自动备份设置
        self.auto_backup = True
        self.max_backups = 10
        
        self.logger.info(f"版本管理器初始化完成，当前版本: {self.current_version}")
    
    def _setup_logging(self):
        """设置日志系统"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"version_manager_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_version_info(self) -> Dict:
        """加载版本信息"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载版本信息失败: {e}")
                return self._create_default_version_info()
        else:
            return self._create_default_version_info()
    
    def _create_default_version_info(self) -> Dict:
        """创建默认版本信息"""
        default_info = {
            "current_version": "1.0.0",
            "versions": [],
            "last_update": datetime.now().isoformat(),
            "total_commits": 0,
            "stable_versions": []
        }
        self._save_version_info(default_info)
        return default_info
    
    def _load_stable_versions(self) -> List[Dict]:
        """加载稳定版本列表"""
        if self.stable_versions_file.exists():
            try:
                with open(self.stable_versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载稳定版本失败: {e}")
                return []
        return []
    
    def _save_version_info(self, info: Dict):
        """保存版本信息"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存版本信息失败: {e}")
    
    def _save_stable_versions(self):
        """保存稳定版本列表"""
        try:
            with open(self.stable_versions_file, 'w', encoding='utf-8') as f:
                json.dump(self.stable_versions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存稳定版本失败: {e}")
    
    def get_git_info(self) -> Tuple[str, str]:
        """获取Git信息"""
        try:
            # 获取当前提交哈希
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            commit_hash = result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
            
            # 获取作者信息
            result = subprocess.run(
                ['git', 'config', 'user.name'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            author = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            return commit_hash, author
        except Exception as e:
            self.logger.warning(f"获取Git信息失败: {e}")
            return "unknown", "unknown"
    
    def create_version(self, 
                      version: str, 
                      description: str, 
                      changes: List[str],
                      stability_score: float = 90.0) -> bool:
        """创建新版本"""
        try:
            commit_hash, author = self.get_git_info()
            
            # 创建版本信息
            version_info = VersionInfo(
                version=version,
                commit_hash=commit_hash,
                timestamp=datetime.now().isoformat(),
                author=author,
                description=description,
                changes=changes,
                stability_score=stability_score,
                is_stable=stability_score >= self.stability_threshold
            )
            
            # 自动备份当前版本
            if self.auto_backup:
                backup_path = self._create_backup(version)
                version_info.backup_path = str(backup_path)
            
            # 添加到版本列表
            self.version_info["versions"].append(asdict(version_info))
            self.version_info["current_version"] = version
            self.version_info["last_update"] = datetime.now().isoformat()
            self.version_info["total_commits"] += 1
            
            # 如果是稳定版本，添加到稳定版本列表
            if version_info.is_stable:
                self.stable_versions.append({
                    "version": version,
                    "commit_hash": commit_hash,
                    "timestamp": version_info.timestamp,
                    "stability_score": stability_score,
                    "backup_path": version_info.backup_path
                })
                self._save_stable_versions()
            
            # 保存版本信息
            self._save_version_info(self.version_info)
            
            # 更新变更日志
            self._update_changelog(version_info)
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            self.logger.info(f"成功创建版本 {version}: {description}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建版本失败: {e}")
            return False
    
    def _create_backup(self, version: str) -> Path:
        """创建版本备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{version}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # 检查磁盘空间
            if not self._check_disk_space():
                self.logger.warning("磁盘空间不足，跳过备份创建")
                return Path("backup_skipped_no_space")
            
            # 检查备份目录权限
            if not self._check_backup_permissions():
                self.logger.warning("备份目录权限不足，跳过备份创建")
                return Path("backup_skipped_no_permission")
            
            # 复制项目文件（排除不需要的文件）
            ignore_patterns = shutil.ignore_patterns(
                'backups', 'logs', '__pycache__', '*.pyc', 
                '.git', 'node_modules', 'venv', 'env', '.vscode', '.idea',
                '*.tmp', '*.log', '*.bak'
            )
            
            shutil.copytree(
                self.project_root, 
                backup_path,
                ignore=ignore_patterns
            )
            
            # 验证备份完整性
            if self._verify_backup_integrity(backup_path):
                self.logger.info(f"创建备份成功: {backup_path}")
                return backup_path
            else:
                self.logger.error("备份完整性验证失败")
                shutil.rmtree(backup_path, ignore_errors=True)
                return Path("backup_failed_integrity")
            
        except PermissionError as e:
            self.logger.error(f"创建备份权限不足: {e}")
            return Path("backup_failed_permission")
        except OSError as e:
            self.logger.error(f"创建备份系统错误: {e}")
            return Path("backup_failed_system")
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return Path("backup_failed")
    
    def _check_disk_space(self, required_gb: float = 1.0) -> bool:
        """检查磁盘空间是否足够"""
        try:
            disk_usage = shutil.disk_usage(self.backup_dir)
            available_gb = disk_usage.free / (1024**3)
            return available_gb >= required_gb
        except Exception as e:
            self.logger.warning(f"检查磁盘空间失败: {e}")
            return True  # 如果检查失败，假设空间足够
    
    def _check_backup_permissions(self) -> bool:
        """检查备份目录权限"""
        try:
            test_file = self.backup_dir / "test_permission.tmp"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def _verify_backup_integrity(self, backup_path: Path) -> bool:
        """验证备份完整性"""
        try:
            # 检查关键文件是否存在
            critical_files = [
                'app', 'config.py', 'requirements.txt', 'README.md'
            ]
            
            for file_name in critical_files:
                file_path = backup_path / file_name
                if not file_path.exists():
                    self.logger.warning(f"备份中缺少关键文件: {file_name}")
                    return False
            
            # 检查备份大小是否合理（至少应该有1MB）
            total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            if total_size < 1024 * 1024:  # 1MB
                self.logger.warning("备份文件过小，可能不完整")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证备份完整性失败: {e}")
            return False
    
    def _update_changelog(self, version_info: VersionInfo):
        """更新变更日志"""
        try:
            changelog_content = f"""# 变更日志

## [{version_info.version}] - {datetime.now().strftime('%Y-%m-%d')}

**作者:** {version_info.author}  
**提交:** {version_info.commit_hash}  
**稳定性评分:** {version_info.stability_score}/100  
**状态:** {'稳定' if version_info.is_stable else '测试中'}

### 描述
{version_info.description}

### 变更内容
"""
            
            for change in version_info.changes:
                changelog_content += f"- {change}\n"
            
            changelog_content += "\n---\n\n"
            
            # 读取现有变更日志
            if self.changelog_file.exists():
                with open(self.changelog_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                changelog_content += existing_content
            
            # 写入新的变更日志
            with open(self.changelog_file, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
                
        except Exception as e:
            self.logger.error(f"更新变更日志失败: {e}")
    
    def rollback_to_version(self, target_version: str) -> bool:
        """回滚到指定版本"""
        try:
            # 查找目标版本
            target_version_info = None
            for version in self.version_info["versions"]:
                if version["version"] == target_version:
                    target_version_info = version
                    break
            
            if not target_version_info:
                self.logger.error(f"未找到版本: {target_version}")
                return False
            
            # 检查是否有备份
            if not target_version_info.get("backup_path"):
                self.logger.error(f"版本 {target_version} 没有备份")
                return False
            
            backup_path = Path(target_version_info["backup_path"])
            if not backup_path.exists():
                self.logger.error(f"备份路径不存在: {backup_path}")
                return False
            
            # 创建当前版本的备份
            current_backup = self._create_backup(f"pre_rollback_{self.current_version}")
            
            # 执行回滚
            self._perform_rollback(backup_path)
            
            # 更新版本信息
            self.current_version = target_version
            self.version_info["current_version"] = target_version
            self.version_info["last_update"] = datetime.now().isoformat()
            
            # 增加回滚计数
            for version in self.version_info["versions"]:
                if version["version"] == target_version:
                    version["rollback_count"] = version.get("rollback_count", 0) + 1
                    break
            
            self._save_version_info(self.version_info)
            
            self.logger.info(f"成功回滚到版本 {target_version}")
            return True
            
        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False
    
    def _perform_rollback(self, backup_path: Path):
        """执行回滚操作"""
        try:
            # 检查Git状态，确保没有未提交的更改
            git_status = subprocess.run(
                ['git', 'status', '--porcelain'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            if git_status.stdout.strip():
                self.logger.warning("检测到未提交的Git更改，建议先提交或暂存")
                # 可以选择继续或停止
                if not self._confirm_rollback_with_changes():
                    raise Exception("用户取消了回滚操作")
            
            # 创建回滚前的安全备份
            safety_backup = self._create_safety_backup()
            
            # 安全删除文件（排除重要文件和目录）
            protected_items = {'.git', 'backups', 'logs', 'venv', 'env', '__pycache__', '.vscode', '.idea'}
            
            for item in self.project_root.iterdir():
                if item.name not in protected_items:
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    except PermissionError as e:
                        self.logger.warning(f"无法删除 {item}: {e}")
                        continue
                    except Exception as e:
                        self.logger.error(f"删除 {item} 时出错: {e}")
                        continue
            
            # 从备份恢复文件
            restored_count = 0
            for item in backup_path.iterdir():
                if item.name not in ['backups', 'logs']:
                    try:
                        if item.is_file():
                            shutil.copy2(item, self.project_root / item.name)
                            restored_count += 1
                        elif item.is_dir():
                            shutil.copytree(item, self.project_root / item.name)
                            restored_count += 1
                    except PermissionError as e:
                        self.logger.warning(f"无法恢复 {item}: {e}")
                        continue
                    except Exception as e:
                        self.logger.error(f"恢复 {item} 时出错: {e}")
                        continue
            
            self.logger.info(f"回滚完成，恢复了 {restored_count} 个项目")
                        
        except Exception as e:
            self.logger.error(f"执行回滚失败: {e}")
            # 尝试从安全备份恢复
            if 'safety_backup' in locals() and safety_backup.exists():
                self.logger.info("尝试从安全备份恢复...")
                self._restore_from_safety_backup(safety_backup)
            raise
    
    def _create_safety_backup(self) -> Path:
        """创建回滚前的安全备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_name = f"safety_backup_{timestamp}"
        safety_path = self.backup_dir / safety_name
        
        try:
            # 只备份关键文件
            critical_files = [
                'app', 'config.py', 'requirements.txt', 'README.md',
                'version_info.json', 'CHANGELOG.md'
            ]
            
            safety_path.mkdir(exist_ok=True)
            
            for item_name in critical_files:
                item_path = self.project_root / item_name
                if item_path.exists():
                    if item_path.is_file():
                        shutil.copy2(item_path, safety_path / item_name)
                    elif item_path.is_dir():
                        shutil.copytree(item_path, safety_path / item_name)
            
            self.logger.info(f"创建安全备份: {safety_path}")
            return safety_path
            
        except Exception as e:
            self.logger.error(f"创建安全备份失败: {e}")
            return Path("safety_backup_failed")
    
    def _restore_from_safety_backup(self, safety_backup: Path):
        """从安全备份恢复"""
        try:
            for item in safety_backup.iterdir():
                if item.name not in ['backups', 'logs']:
                    target_path = self.project_root / item.name
                    if item.is_file():
                        shutil.copy2(item, target_path)
                    elif item.is_dir():
                        if target_path.exists():
                            shutil.rmtree(target_path)
                        shutil.copytree(item, target_path)
            
            self.logger.info("从安全备份恢复完成")
            
        except Exception as e:
            self.logger.error(f"从安全备份恢复失败: {e}")
    
    def _confirm_rollback_with_changes(self) -> bool:
        """确认在有未提交更改时是否继续回滚"""
        try:
            # 这里可以添加用户交互逻辑
            # 暂时返回True，允许继续
            self.logger.warning("检测到未提交的更改，继续执行回滚...")
            return True
        except Exception as e:
            self.logger.error(f"确认回滚失败: {e}")
            return False
    
    def rollback_to_stable(self) -> bool:
        """回滚到最近的稳定版本"""
        if not self.stable_versions:
            self.logger.error("没有可用的稳定版本")
            return False
        
        # 按稳定性评分排序，选择最高的
        stable_versions = sorted(
            self.stable_versions, 
            key=lambda x: x["stability_score"], 
            reverse=True
        )
        
        target_version = stable_versions[0]["version"]
        self.logger.info(f"回滚到最稳定版本: {target_version}")
        
        return self.rollback_to_version(target_version)
    
    def get_version_history(self) -> List[Dict]:
        """获取版本历史"""
        return self.version_info.get("versions", [])
    
    def get_stable_versions(self) -> List[Dict]:
        """获取稳定版本列表"""
        return self.stable_versions
    
    def get_current_version_info(self) -> Optional[Dict]:
        """获取当前版本信息"""
        for version in self.version_info["versions"]:
            if version["version"] == self.current_version:
                return version
        return None
    
    def check_stability(self, version: str) -> float:
        """检查版本稳定性"""
        try:
            # 这里可以实现更复杂的稳定性检查逻辑
            # 比如运行测试、检查错误日志等
            
            # 简单示例：基于回滚次数和错误日志
            version_info = None
            for v in self.version_info["versions"]:
                if v["version"] == version:
                    version_info = v
                    break
            
            if not version_info:
                return 0.0
            
            # 基础分数
            base_score = 90.0
            
            # 回滚次数扣分
            rollback_penalty = version_info.get("rollback_count", 0) * 10
            
            # 错误日志扣分（这里简化处理）
            error_penalty = 0
            
            final_score = max(0, base_score - rollback_penalty - error_penalty)
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"检查稳定性失败: {e}")
            return 0.0
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        try:
            if len(list(self.backup_dir.iterdir())) > self.max_backups:
                # 按修改时间排序，删除最旧的
                backups = sorted(
                    self.backup_dir.iterdir(),
                    key=lambda x: x.stat().st_mtime
                )
                
                for backup in backups[:-self.max_backups]:
                    if backup.is_dir():
                        shutil.rmtree(backup)
                    else:
                        backup.unlink()
                    
                    self.logger.info(f"删除旧备份: {backup}")
                    
        except Exception as e:
            self.logger.error(f"清理备份失败: {e}")
    
    def emergency_rollback(self) -> bool:
        """紧急回滚（当项目崩溃时使用）"""
        try:
            self.logger.warning("执行紧急回滚...")
            
            # 尝试回滚到最近的稳定版本
            if self.rollback_to_stable():
                self.logger.info("紧急回滚成功")
                return True
            else:
                # 如果失败，尝试回滚到上一个版本
                versions = self.get_version_history()
                if len(versions) >= 2:
                    previous_version = versions[-2]["version"]
                    self.logger.info(f"尝试回滚到上一个版本: {previous_version}")
                    return self.rollback_to_version(previous_version)
                else:
                    self.logger.error("没有可回滚的版本")
                    return False
                    
        except Exception as e:
            self.logger.error(f"紧急回滚失败: {e}")
            return False
    
    def get_project_status(self) -> Dict:
        """获取项目状态报告"""
        try:
            current_info = self.get_current_version_info()
            
            status = {
                "current_version": self.current_version,
                "total_versions": len(self.version_info["versions"]),
                "stable_versions_count": len(self.stable_versions),
                "last_update": self.version_info.get("last_update"),
                "total_commits": self.version_info.get("total_commits", 0),
                "backup_count": len(list(self.backup_dir.iterdir())),
                "auto_backup_enabled": self.auto_backup,
                "stability_threshold": self.stability_threshold
            }
            
            if current_info:
                status.update({
                    "current_stability_score": current_info.get("stability_score", 0),
                    "current_is_stable": current_info.get("is_stable", False),
                    "current_rollback_count": current_info.get("rollback_count", 0)
                })
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取项目状态失败: {e}")
            return {"error": str(e)}


# 全局版本管理器实例
_version_manager = None

def get_version_manager(project_root: str = None) -> VersionManager:
    """获取全局版本管理器实例"""
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager(project_root)
    return _version_manager


if __name__ == "__main__":
    # 测试代码
    vm = VersionManager()
    
    # 创建测试版本
    vm.create_version(
        version="1.0.1",
        description="添加版本管理系统",
        changes=[
            "新增版本管理核心类",
            "支持版本回滚功能",
            "添加稳定性监控",
            "自动备份机制"
        ],
        stability_score=95.0
    )
    
    # 显示状态
    print("项目状态:", json.dumps(vm.get_project_status(), indent=2, ensure_ascii=False)) 