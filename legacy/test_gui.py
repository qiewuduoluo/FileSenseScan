#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI应用测试脚本
"""

import os
import sys

# 添加项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def test_imports():
    """测试所有必要的模块导入"""
    try:
        import customtkinter as ctk
        print("✅ customtkinter 导入成功")
        
        from PIL import Image
        print("✅ PIL 导入成功")
        
        # 测试项目模块
        from config import USE_MODEL
        print(f"✅ config 导入成功，当前模型：{USE_MODEL}")
        
        # 测试批处理模块
        from main_N_带单元总结 import process_pdf
        print("✅ main_N_带单元总结 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        return False

def test_brand_config():
    """测试品牌配置"""
    try:
        import json
        brand_path = os.path.join(BASE_DIR, "brand.json")
        if os.path.exists(brand_path):
            with open(brand_path, "r", encoding="utf-8") as f:
                brand = json.load(f)
            print(f"✅ 品牌配置加载成功：{brand.get('app_name', 'Unknown')}")
            return True
        else:
            print("⚠️ brand.json 不存在，将使用默认配置")
            return True
    except Exception as e:
        print(f"❌ 品牌配置加载失败：{e}")
        return False

def test_assets():
    """测试资源文件"""
    assets_dir = os.path.join(BASE_DIR, "assets")
    if os.path.exists(assets_dir):
        print(f"✅ assets 目录存在：{assets_dir}")
        
        # 检查关键文件
        logo_path = os.path.join(assets_dir, "logo.png")
        icon_path = os.path.join(assets_dir, "app.ico")
        
        if os.path.exists(logo_path):
            print("✅ logo.png 存在")
        else:
            print("⚠️ logo.png 不存在，将显示文字LOGO")
            
        if os.path.exists(icon_path):
            print("✅ app.ico 存在")
        else:
            print("⚠️ app.ico 不存在，将使用默认图标")
    else:
        print("⚠️ assets 目录不存在，将使用默认配置")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始测试 FileSenseScan GUI 应用...")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("品牌配置测试", test_brand_config),
        ("资源文件测试", test_assets),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果：{passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以运行 GUI 应用了")
        print("\n运行命令：")
        print("python gui_app_modern.py")
    else:
        print("⚠️ 部分测试失败，请检查相关配置")

if __name__ == "__main__":
    main() 