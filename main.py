#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan 主启动脚本
整合所有功能，提供统一的入口点
"""

import sys
import os
from pathlib import Path

def main():
    """主函数"""
    print("🚀 FileSenseScan 智能文件扫描和处理工具")
    print("=" * 50)
    
    # 添加app目录到Python路径
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir))
    
    print("请选择启动模式：")
    print("1. 🖥️  主GUI应用 (PDF处理和OCR)")
    print("2. 🔧 版本管理系统")
    print("3. 📊 批处理模式")
    print("4. 🧪 系统测试")
    print("5. 📖 查看帮助")
    print("6. 🚪 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-6): ").strip()
            
            if choice == "1":
                print("\n正在启动主GUI应用...")
                from app.gui.main_gui import main as gui_main
                gui_main()
                break
                
            elif choice == "2":
                print("\n正在启动版本管理系统...")
                from app.gui.version_gui import VersionManagementGUI
                import customtkinter as ctk
                
                app = ctk.CTk()
                app.withdraw()  # 隐藏主窗口
                
                version_gui = VersionManagementGUI()
                version_gui.root.mainloop()
                break
                
            elif choice == "3":
                print("\n批处理模式")
                pdf_path = input("请输入PDF文件路径: ").strip()
                if pdf_path and os.path.exists(pdf_path):
                    from app.batch.main_batch import process_pdf
                    output_dir = input("请输入输出目录 (回车使用默认): ").strip()
                    if not output_dir:
                        output_dir = os.path.join(os.getcwd(), "data", "OutPur_Data_Result")
                    
                    print(f"开始处理: {pdf_path}")
                    result = process_pdf(pdf_path, output_dir)
                    print(f"处理完成，输出目录: {result}")
                else:
                    print("文件路径无效")
                break
                
            elif choice == "4":
                print("\n正在运行系统测试...")
                from scripts.test_version_system import main as test_main
                test_main()
                break
                
            elif choice == "5":
                print("\n📖 FileSenseScan 使用帮助")
                print("=" * 30)
                print("主GUI应用: 提供PDF处理和OCR功能的图形界面")
                print("版本管理: 管理项目版本、变更日志和代码回滚")
                print("批处理模式: 命令行批量处理PDF文件")
                print("系统测试: 检查系统组件和依赖")
                print("\n更多信息请查看 docs/ 目录下的文档")
                print("启动脚本位于 tools/ 目录")
                continue
                
            elif choice == "6":
                print("👋 再见！")
                return
                
            else:
                print("❌ 无效选择，请输入 1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消，再见！")
            return
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            print("请检查依赖是否正确安装: pip install -r requirements.txt")
            return

if __name__ == "__main__":
    main() 