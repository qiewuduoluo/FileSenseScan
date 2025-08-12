# FileSenseScan 项目结构重构计划

## 🎯 重构目标
重新组织项目文件结构，消除重复冗余，提高代码可维护性和项目清晰度。

## 📁 新的目录结构

```
FileSenseScan/
├── 📱 app/                          # 核心应用代码
│   ├── core/                        # 核心功能模块
│   │   ├── version_manager.py       # 版本管理器
│   │   ├── error_monitor.py         # 错误监控器
│   │   └── pdf_utils.py            # PDF处理工具
│   ├── gui/                         # 图形界面模块
│   │   ├── main_gui.py             # 主GUI应用（合并后的版本）
│   │   ├── version_gui.py          # 版本管理GUI
│   │   └── apple_style_config.py   # 苹果风格配置
│   ├── services/                    # 服务模块
│   │   ├── baidu_ocr.py            # OCR服务
│   │   └── llm/                    # AI模型服务
│   └── batch/                       # 批处理模块
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
│   └── version_file_rename_summary.md # 文件重命名总结
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
└── 🗑️ legacy/                       # 旧版本代码（待清理）
```

## 🧹 清理计划

### 第一阶段：文件重命名和移动
1. 创建新的目录结构
2. 移动文件到对应目录
3. 重命名重复文件

### 第二阶段：代码合并和优化
1. 合并重复的GUI文件
2. 清理legacy目录
3. 优化导入路径

### 第三阶段：文档整理
1. 整理文档到docs目录
2. 更新所有文件引用
3. 清理重复文档

### 第四阶段：测试和验证
1. 测试所有功能
2. 验证文件引用
3. 提交到GitHub

## ✅ 重构完成检查清单

- [ ] 创建新的目录结构
- [ ] 移动所有文件到对应目录
- [ ] 合并重复的代码文件
- [ ] 更新所有文件引用和导入
- [ ] 清理legacy目录
- [ ] 整理文档结构
- [ ] 测试所有功能
- [ ] 提交到GitHub

---
*重构计划创建时间: 2025年8月11日* 