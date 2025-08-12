#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan 苹果风格版本管理系统启动器
"""

import sys
import os
from pathlib import Path

def main():
    """主函数"""
    print("🚀 启动 FileSenseScan 苹果风格版本管理系统...")
    
    # 添加app目录到Python路径
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir))
    
    try:
        # 导入苹果风格GUI
        from app.gui.version_gui_apple_style import AppleStyleVersionGUI
        
        print("✅ 苹果风格GUI导入成功")
        print("🎨 应用苹果公司用户体验设计规范")
        print("📱 支持浅色/深色主题")
        print("🔧 优化的版本管理功能")
        print("🚨 智能错误监控系统")
        print("💾 自动备份和恢复")
        print("🌐 GitHub集成支持")
        print()
        
        # 启动GUI
        app = AppleStyleVersionGUI()
        print("🎯 GUI启动成功，正在显示主界面...")
        app.run()
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装所需的依赖包")
        print("运行: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查系统配置和依赖")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 