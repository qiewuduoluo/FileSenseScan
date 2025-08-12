@echo off
chcp 65001 >nul
echo.
echo 🚀 启动 FileSenseScan 苹果风格版本管理系统...
echo.
echo 🎨 应用苹果公司用户体验设计规范
echo 📱 支持浅色/深色主题
echo 🔧 优化的版本管理功能
echo 🚨 智能错误监控系统
echo 💾 自动备份和恢复
echo 🌐 GitHub集成支持
echo.
echo 正在启动...
echo.

python scripts\launch_apple_style_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败，请检查：
    echo 1. Python环境是否正确安装
    echo 2. 依赖包是否已安装 (pip install -r requirements.txt)
    echo 3. 系统配置是否正确
    echo.
    pause
) else (
    echo.
    echo ✅ 系统已正常退出
    echo.
)

pause 