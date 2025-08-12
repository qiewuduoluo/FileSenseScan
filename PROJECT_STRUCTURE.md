# FileSenseScan 项目结构说明

## 📁 重构后的目录结构

```
FileSenseScan/
├── 📱 app/                          # 核心应用代码
│   ├── core/                        # 核心功能模块
│   │   ├── __init__.py             # 模块初始化
│   │   ├── version_manager.py      # 版本管理器
│   │   ├── error_monitor.py        # 错误监控器
│   │   └── pdf_utils.py            # PDF处理工具
│   ├── gui/                         # 图形界面模块
│   │   ├── __init__.py             # 模块初始化
│   │   ├── main_gui.py             # 主GUI应用（PDF处理）
│   │   ├── version_gui.py          # 版本管理GUI
│   │   └── apple_style_config.py   # 苹果风格配置
│   ├── services/                    # 服务模块
│   │   ├── __init__.py             # 模块初始化
│   │   ├── baidu_ocr.py            # OCR服务
│   │   └── llm/                    # AI模型服务
│   │       ├── __init__.py         # 模块初始化
│   │       ├── text_api.py         # 文本API
│   │       └── vision_deepseek.py  # DeepSeek视觉API
│   └── batch/                       # 批处理模块
│       ├── __init__.py             # 模块初始化
│       └── main_batch.py           # 批量处理脚本
├── 🛠️ tools/                        # 工具脚本
│   ├── version_management.ps1      # 版本管理PowerShell脚本
│   ├── version_management.bat      # 版本管理批处理脚本
│   ├── version_sync_to_github.ps1  # GitHub同步脚本
│   ├── version_sync_to_github.bat  # GitHub同步批处理
│   ├── launch_apple_style.ps1      # 苹果风格启动脚本
│   ├── launch_apple_style.bat      # 苹果风格启动批处理
│   └── create_brand_assets.py      # 品牌资源创建工具
├── 📚 docs/                         # 文档目录
│   ├── README.md                    # 主项目说明
│   ├── README_GUI.md               # GUI使用说明
│   ├── CHANGELOG.md                # 变更日志
│   ├── APPLE_UX_DESIGN_GUIDE.md    # 苹果设计指南
│   ├── UX_IMPROVEMENT_SUMMARY.md   # 用户体验改进总结
│   ├── version_github_sync_guide.md # GitHub同步指南
│   ├── version_file_rename_summary.md # 文件重命名总结
│   └── version_date_update_summary.md # 日期更新总结
├── 🎨 assets/                       # 资源文件
│   ├── app.ico                     # 应用图标
│   ├── logo.png                    # 应用Logo
│   └── brand.json                  # 品牌配置
├── ⚙️ config/                       # 配置文件
│   ├── config.py                   # 主配置文件
│   ├── config.py.example           # 配置示例
│   ├── settings.json               # 应用设置
│   ├── version_info.json           # 版本信息
│   └── stable_versions.json        # 稳定版本信息
├── 📊 data/                         # 数据目录
│   ├── Data_Source/                # 数据源
│   └── OutPur_Data_Result/         # 输出结果
├── 🔄 scripts/                      # 启动脚本
│   ├── launch_apple_style_gui.py   # 苹果风格GUI启动器
│   └── test_version_system.py      # 版本系统测试
├── 📦 build/                        # 构建输出
├── 💾 backups/                      # 备份文件
├── 📝 logs/                         # 日志文件
├── 🗑️ legacy/                       # 旧版本代码（待清理）
├── main.py                          # 主启动脚本
├── requirements.txt                 # 依赖包列表
├── build.bat                        # 构建脚本
└── .gitignore                       # Git忽略文件
```

## 🔄 重构完成的功能

### ✅ 已完成的重构
1. **目录结构重新组织** - 按功能模块分类
2. **重复文件清理** - 合并了重复的GUI文件
3. **导入路径修复** - 更新了所有模块的导入路径
4. **文件移动完成** - 所有文件已移动到对应目录
5. **启动脚本更新** - 修复了所有脚本中的路径引用

### 🧹 清理的重复文件
- `app/gui_app_modern.py` → 删除（与 `app/gui_app_modern_fixed.py` 重复）
- `app/gui_app_modern_fixed.py` → 删除（功能已合并到 `app/gui/main_gui.py`）
- 所有重复的启动脚本已整合

### 📁 新增的目录结构
- `app/core/` - 核心功能模块
- `app/gui/` - 图形界面模块
- `app/services/` - 服务模块
- `app/batch/` - 批处理模块
- `tools/` - 工具脚本
- `docs/` - 文档目录
- `config/` - 配置文件
- `data/` - 数据目录
- `scripts/` - 启动脚本

## 🚀 启动方式

### 1. 主启动脚本（推荐）
```bash
python main.py
```

### 2. 直接启动特定功能
```bash
# 主GUI应用
python app/gui/main_gui.py

# 版本管理系统
python app/gui/version_gui.py

# 批处理模式
python app/batch/main_batch.py
```

### 3. 使用工具脚本
```bash
# Windows批处理
tools\version_management.bat

# PowerShell脚本
tools\version_management.ps1

# 苹果风格启动
tools\launch_apple_style.bat
```

## 🔧 依赖管理

### 安装依赖
```bash
pip install -r requirements.txt
```

### 主要依赖包
- `customtkinter` - 现代化GUI框架
- `PIL` - 图像处理
- `PyMuPDF` - PDF处理
- `requests` - 网络请求
- `psutil` - 系统监控

## 📋 重构检查清单

- [x] 创建新的目录结构
- [x] 移动所有文件到对应目录
- [x] 合并重复的代码文件
- [x] 更新所有文件引用和导入
- [x] 清理legacy目录中的重复文件
- [x] 整理文档结构
- [x] 测试所有功能
- [x] 准备提交到GitHub

## 🎯 重构目标达成

1. **结构清晰** - 按功能模块分类，易于理解和维护
2. **消除重复** - 合并了重复的GUI文件，减少代码冗余
3. **路径统一** - 所有导入路径已更新，避免模块导入错误
4. **功能完整** - 保留了所有原有功能，没有功能丢失
5. **易于扩展** - 新的模块化结构便于添加新功能

---
*重构完成时间: 2025年8月11日* 