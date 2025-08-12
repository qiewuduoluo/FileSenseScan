# 🔧 FileSenseScan 版本管理系统

> 一个完整的项目版本控制解决方案，提供版本管理、自动备份、错误监控和自动恢复功能。

## 📋 目录

- [🚀 快速开始](#-快速开始)
- [✨ 主要功能](#-主要功能)
- [📖 详细使用说明](#-详细使用说明)
- [⚙️ 配置说明](#️-配置说明)
- [🔍 问题排查](#-问题排查)
- [🛠️ 高级功能](#️-高级功能)
- [📋 系统要求](#-系统要求)

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 启动版本管理系统

| 方法 | 命令 | 说明 |
|------|------|------|
| **批处理文件** | `version_management.bat` | ⭐ 推荐，双击即可运行 |
| **PowerShell** | `.\version_management.ps1` | 功能更丰富，支持参数 |
| **Python GUI** | `python app/version_gui.py` | 图形界面，操作直观 |

### 3️⃣ 创建第一个版本

1. 选择 **"2. 创建新版本"**
2. 输入版本号（如：`1.0.1`）
3. 输入版本描述
4. 输入变更内容（用逗号分隔）
5. 设置稳定性评分（0-100）

### 4️⃣ 同步到GitHub

1. 选择 **"8. 一键同步到GitHub"**
2. 或者直接运行 `version_sync_to_github.bat`

## ✨ 主要功能

### 🔄 版本管理
- **版本创建** - 创建新版本，自动生成变更日志
- **版本历史** - 查看完整的版本历史记录
- **稳定性评分** - 为每个版本分配稳定性评分
- **自动备份** - 创建版本时自动备份当前代码

### 🔙 回滚功能
- **稳定版本回滚** - 回滚到最近的稳定版本
- **紧急回滚** - 当系统崩溃时自动回滚
- **安全回滚** - 回滚前创建安全备份，防止数据丢失

### 📊 错误监控
- **实时监控** - 监控AI处理过程中的错误
- **错误统计** - 统计错误类型和频率
- **自动恢复** - 达到错误阈值时自动触发恢复机制

### 🚀 GitHub同步
- **一键同步** - 自动提交和推送到GitHub
- **智能检测** - 检测未提交的更改
- **错误处理** - 完善的错误处理和用户提示

## 📖 详细使用说明

### 版本管理操作

#### 查看版本状态
```bash
.\version_management.ps1 -Action status
```

#### 创建新版本
```bash
.\version_management.ps1 -Action create -Version "1.0.2" -Description "修复bug" -Changes "修复登录问题,优化性能" -Stability 95
```

#### 查看版本历史
```bash
.\version_management.ps1 -Action history
```

#### 回滚到稳定版本
```bash
.\version_management.ps1 -Action rollback
```

#### 紧急回滚
```bash
.\version_management.ps1 -Action emergency
```

### GitHub同步操作

#### 自动同步
```bash
.\version_sync_to_github.ps1
```

#### 检查同步状态
```bash
git status
git log --oneline -5
```

## ⚙️ 配置说明

### 版本管理器配置

版本管理器的配置存储在 `version_info.json` 文件中：

```json
{
  "current_version": "1.0.1",
  "versions": [...],
  "last_update": "2025-08-11T12:00:00",
  "total_commits": 5,
  "stable_versions": [...]
}
```

### 错误监控配置

错误监控器的配置可以通过以下方法修改：

```python
from app.error_monitor import get_error_monitor

em = get_error_monitor()
em.set_error_threshold(5)      # 设置错误阈值
em.set_auto_rollback(True)     # 启用自动回滚
```

## 🔍 问题排查

### 常见问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| **Python环境问题** | 运行脚本时提示 "python 不是内部或外部命令" | 确保已安装Python并添加到PATH，或使用完整路径：`C:\Python39\python.exe` |
| **依赖包缺失** | 运行时提示模块导入错误 | 运行 `pip install -r requirements.txt` |
| **Git配置问题** | GitHub同步失败 | 配置Git用户信息：`git config --global user.name "用户名"` |
| **权限问题** | 无法创建备份或写入日志 | 以管理员身份运行，检查文件夹权限和磁盘空间 |
| **版本回滚失败** | 回滚操作失败或文件丢失 | 检查Git更改状态，确保备份文件完整 |

### 日志文件位置

| 类型 | 位置 | 说明 |
|------|------|------|
| **版本管理日志** | `logs/version_manager_YYYYMMDD.log` | 版本操作记录 |
| **错误监控日志** | `logs/error_monitor_YYYYMMDD.log` | 错误监控记录 |
| **备份文件** | `backups/` 目录 | 版本备份文件 |

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🛠️ 高级功能

### 自定义错误处理器

```python
from app.error_monitor import get_error_monitor

def custom_error_handler(error_info):
    print(f"自定义错误处理: {error_info}")
    
em = get_error_monitor()
em.register_error_handler("custom_error", custom_error_handler)
```

### 自动备份策略

```python
from app.version_manager import get_version_manager

vm = get_version_manager()
vm.auto_backup = True
vm.max_backups = 20  # 保留20个备份
```

### 稳定性检查

```python
from app.version_manager import get_version_manager

vm = get_version_manager()
score = vm.check_stability("1.0.1")
print(f"版本稳定性评分: {score}")
```

## 📋 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **操作系统** | Windows 10/11, macOS 10.14+, Ubuntu 18.04+ | Windows 11, macOS 12+ |
| **Python** | 3.8+ | 3.9+ |
| **内存** | 4GB | 8GB+ |
| **磁盘空间** | 2GB可用空间 | 5GB+ |
| **网络** | 用于GitHub同步 | 稳定的网络连接 |

## 🆘 技术支持

如果遇到问题，请：

1. 📋 查看日志文件获取详细错误信息
2. 🔍 检查系统要求和依赖是否正确安装
3. 📖 参考问题排查部分
4. 🐛 提交Issue到GitHub仓库

## 📝 更新日志

### v1.0.1 (2025-08-11)
- ✨ 添加版本管理系统
- 💾 实现自动备份功能
- 📊 添加错误监控和自动恢复
- 🔄 集成GitHub同步功能

### v1.0.0
- 🚀 初始版本发布
- 🤖 基础AI文档处理功能

---

<div align="center">

**🎉 感谢使用 FileSenseScan 版本管理系统！**

*如有问题或建议，请在GitHub上提交Issue*

</div> 