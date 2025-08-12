# FileSenseScan

一个智能的文件扫描和处理工具，支持PDF文档的OCR识别和内容分析。

## 功能特性

- 📄 PDF文档处理
- 🔍 OCR文字识别（支持百度OCR API）
- 🤖 AI内容分析（支持多种LLM模型）
- 🖥️ 现代化GUI界面（基于CustomTkinter）
- 📊 批量处理支持
- 🎨 可自定义品牌和主题

## 系统要求

- Python 3.8+
- Windows 10/11
- 网络连接（用于OCR和AI服务）

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/qiewuduoluo/FileSenseScan.git
cd FileSenseScan
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置设置：
   - 复制 `config.py.example` 为 `config.py`
   - 填入你的API密钥和配置信息

## 使用方法

### 图形界面模式
```bash
python app/gui/main_gui.py
```

### 命令行批量模式
```bash
python app/batch/main_batch.py
```

## 配置说明

在 `config.py` 中配置以下服务：

- **百度OCR API**：用于文字识别
- **AI模型API**：用于内容分析和总结
- **输出目录**：处理结果的保存位置

## 项目结构

```
FileSenseScan/
├── app/                    # 主要应用代码
│   ├── gui_app_modern.py  # 现代化GUI应用
│   ├── main_batch.py      # 批量处理脚本
│   ├── baidu_ocr.py       # 百度OCR集成
│   └── llm/               # AI模型集成
├── assets/                 # 资源文件
├── Data_Source/           # 示例数据源
├── OutPur_Data_Result/    # 输出结果
└── tools/                 # 工具脚本
```

## 快速同步到GitHub

项目包含自动同步脚本，双击以下文件即可：

- `version_sync_to_github.bat` - Windows批处理文件
- `version_sync_to_github.ps1` - PowerShell脚本

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请在GitHub上提交Issue。 