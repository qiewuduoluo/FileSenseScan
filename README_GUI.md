# FileSenseScan GUI 版本使用说明

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 生成品牌资源（占位）
```bash
python tools/create_brand_assets.py
```

### 3. 运行GUI应用
```bash
python app/gui_app_modern.py
```

### 4. 打包成exe
```bash
# Windows
build.bat

# 或手动执行
pip install pyinstaller customtkinter pillow
pyinstaller --noconsole --onefile --name FileSenseScan --distpath .\dist --workpath .\build --specpath .\build --icon assets\app.ico --add-data "assets;assets" app\gui_app_modern.py
```

## 🎨 界面特性

### 迅雷风格设计
- **深色蓝系主题**：深灰底 + 亮蓝主色
- **左侧边栏**：LOGO + 操作按钮
- **右侧主面板**：路径设置 + 进度条 + 日志
- **顶部菜单栏**：文件、设置、帮助

### 功能特性
- ✅ **LOGO自定义**：菜单 → 设置 → 更换LOGO
- ✅ **模型切换**：DeepSeek / 通义千问
- ✅ **进度显示**：实时进度条 + 处理状态
- ✅ **批量处理**：自动扫描输入目录所有PDF
- ✅ **日志记录**：详细处理过程记录

## 📁 目录结构

```
FileSenseScan/
├─ app/                    # 主应用代码
│  ├─ gui_app_modern.py   # 现代GUI应用
│  ├─ main_batch.py       # 批量处理逻辑
│  ├─ pdf_utils.py        # PDF处理工具
│  ├─ baidu_ocr.py        # OCR识别
│  └─ llm/                # 大语言模型接口
│     ├─ text_api.py      # 统一文本API
│     └─ vision_deepseek.py # 视觉API（可选）
├─ assets/                # 品牌资源
│  ├─ logo.png           # LOGO图片
│  ├─ app.ico            # 窗口图标
│  └─ brand.json         # 品牌配置
├─ tools/                 # 工具脚本
│  └─ create_brand_assets.py # 生成资源
├─ legacy/               # 历史版本（归档）
├─ Data_Source/          # 输入目录
├─ OutPur_Data_Result/   # 输出目录
├─ config.py             # 配置文件
├─ requirements.txt       # 依赖列表
├─ build.bat            # 打包脚本
└─ README_GUI.md        # 说明文档
```

## ⚙️ 自定义配置

### 修改品牌配置
编辑 `assets/brand.json`：

```json
{
  "app_name": "你的应用名称",
  "logo_path": "assets/logo.png",
  "window_icon": "assets/app.ico",
  "primary": "#2C93FF",    // 主色调
  "bg": "#161A20",         // 背景色
  "panel": "#1E232B",      // 面板色
  "text": "#E8E9EB",       // 文字色
  "muted": "#9AA4B2"       // 次要文字色
}
```

### 更换LOGO
1. 将新LOGO图片放入 `assets/` 目录
2. 菜单 → 设置 → 更换LOGO
3. 或直接修改 `assets/brand.json` 中的 `logo_path`

### 修改菜单
编辑 `app/gui_app_modern.py` 中的 `build_menu()` 方法

## 🎯 使用流程

1. **选择输入目录**：包含PDF文件的目录
2. **选择输出目录**：处理结果保存位置
3. **选择模型**：DeepSeek 或 通义千问
4. **点击开始处理**：自动批量处理所有PDF
5. **查看进度**：实时显示处理状态和日志

## 🔧 故障排除

### 常见问题
1. **找不到模块**：确保在项目根目录运行
2. **LOGO不显示**：检查图片路径和格式
3. **打包失败**：确保已安装所有依赖包

### 依赖包
- `customtkinter`：现代GUI框架
- `pillow`：图像处理
- `pyinstaller`：打包工具
- `PyMuPDF`：PDF处理
- `requests`：网络请求

## 📝 更新日志

- ✅ 重构目录结构，按功能分层
- ✅ 统一LLM接口，支持多模型切换
- ✅ 迅雷风格深色蓝系界面
- ✅ 支持LOGO自定义
- ✅ 菜单栏功能
- ✅ 进度条和状态显示
- ✅ 批量处理支持
- ✅ 相对路径引用
- ✅ 项目目录打包

## 🎉 重构完成

项目已完成重构，主要改进：

1. **目录结构优化**：按功能分层，代码更清晰
2. **统一API接口**：支持DeepSeek和通义千问
3. **现代化GUI**：迅雷风格界面，支持主题切换
4. **一键打包**：支持生成exe文件
5. **文档完善**：详细的使用说明和配置指南

现在可以享受更清晰、更易维护的FileSenseScan项目！ 