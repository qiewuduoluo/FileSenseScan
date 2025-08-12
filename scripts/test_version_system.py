#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSenseScan 版本管理系统测试脚本
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_version_manager():
    """测试版本管理器"""
    print("=== 测试版本管理器 ===")
    try:
        from app.core.version_manager import get_version_manager
        
        vm = get_version_manager()
        print("✅ 版本管理器初始化成功")
        
        # 获取项目状态
        status = vm.get_project_status()
        print("✅ 项目状态获取成功")
        print("项目状态:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 获取版本历史
        versions = vm.get_version_history()
        print(f"✅ 版本历史获取成功，共 {len(versions)} 个版本")
        
        return True
    except Exception as e:
        print(f"❌ 版本管理器测试失败: {e}")
        return False

def test_error_monitor():
    """测试错误监控器"""
    print("\n=== 测试错误监控器 ===")
    try:
        from app.core.error_monitor import get_error_monitor
        
        em = get_error_monitor()
        print("✅ 错误监控器初始化成功")
        
        # 获取错误摘要
        summary = em.get_error_summary()
        print("✅ 错误摘要获取成功")
        print("错误摘要:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"❌ 错误监控器测试失败: {e}")
        return False

def test_version_gui():
    """测试版本管理GUI"""
    print("\n=== 测试版本管理GUI ===")
    try:
        from app.gui.version_gui import VersionManagementGUI
        
        print("✅ 版本管理GUI导入成功")
        
        # 注意：这里不实际启动GUI，只是测试导入
        return True
    except Exception as e:
        print(f"❌ 版本管理GUI测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库"""
    print("\n=== 测试依赖库 ===")
    
    dependencies = [
        ("customtkinter", "GUI界面库"),
        ("psutil", "系统监控库"),
        ("PIL", "图像处理库"),
        ("requests", "网络请求库")
    ]
    
    all_ok = True
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} ({desc}) - 可用")
        except ImportError:
            print(f"❌ {dep} ({desc}) - 未安装")
            all_ok = False
    
    return all_ok

def test_git_integration():
    """测试Git集成"""
    print("\n=== 测试Git集成 ===")
    try:
        import subprocess
        
        # 检查Git状态
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git状态检查成功")
            
            # 检查远程仓库
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            if result.returncode == 0 and 'origin' in result.stdout:
                print("✅ 远程仓库配置正确")
                return True
            else:
                print("❌ 远程仓库配置有问题")
                return False
        else:
            print("❌ Git状态检查失败")
            return False
    except Exception as e:
        print(f"❌ Git集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("FileSenseScan 版本管理系统测试")
    print("=" * 50)
    
    results = []
    
    # 测试各个组件
    results.append(("版本管理器", test_version_manager()))
    results.append(("错误监控器", test_error_monitor()))
    results.append(("版本管理GUI", test_version_gui()))
    results.append(("依赖库", test_dependencies()))
    results.append(("Git集成", test_git_integration()))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！版本管理系统运行正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关组件")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 