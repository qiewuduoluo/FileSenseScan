@echo off
chcp 65001 >nul
title FileSenseScan 版本管理系统 v1.0.1

:: 设置颜色代码
set "color_reset=[0m"
set "color_title=[1;36m"
set "color_menu=[1;33m"
set "color_success=[1;32m"
set "color_error=[1;31m"
set "color_info=[1;34m"
set "color_warning=[1;35m"

:: 清屏并显示标题
cls
echo %color_title%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    FileSenseScan 版本管理系统                ║
echo ║                         Version 1.0.1                       ║
echo ║                    更新时间: 2025年8月11日                  ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %color_reset%
echo.

:menu
echo %color_menu%请选择操作：%color_reset%
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  1. 📊 查看当前版本状态                                    ║
echo ║  2. 🆕 创建新版本                                          ║
echo ║  3. 📜 查看版本历史                                        ║
echo ║  4. 🔙 回滚到稳定版本                                      ║
echo ║  5. 🚨 紧急回滚                                            ║
echo ║  6. 📈 查看错误监控状态                                    ║
echo ║  7. 🖥️  启动版本管理GUI                                    ║
echo ║  8. 🔄 一键同步到GitHub                                    ║
echo ║  9. 🚪 退出                                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set /p choice=%color_menu%请输入选择 (1-9): %color_reset%

if "%choice%"=="1" goto show_status
if "%choice%"=="2" goto create_version
if "%choice%"=="3" goto show_history
if "%choice%"=="4" goto rollback_stable
if "%choice%"=="5" goto emergency_rollback
if "%choice%"=="6" goto show_error_monitor
if "%choice%"=="7" goto start_gui
if "%choice%"=="8" goto sync_github
if "%choice%"=="9" goto exit
goto invalid_choice

:show_status
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                    正在获取版本状态...                        ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo from app.core.version_manager import get_version_manager > temp_status_script.py
echo vm = get_version_manager() >> temp_status_script.py
echo status = vm.get_project_status() >> temp_status_script.py
echo import json >> temp_status_script.py
echo print('项目状态:') >> temp_status_script.py
echo print(json.dumps(status, indent=2, ensure_ascii=False)) >> temp_status_script.py

python temp_status_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                    获取版本状态时出现错误！                    ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    版本状态获取成功！                        ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

del temp_status_script.py
echo.
pause
goto menu

:create_version
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                      创建新版本                              ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo %color_menu%请输入版本信息：%color_reset%
echo.
set /p version=%color_info%版本号 (例如: 1.0.1): %color_reset%
set /p description=%color_info%版本描述: %color_reset%
set /p changes=%color_info%变更内容 (用逗号分隔): %color_reset%
set /p stability=%color_info%稳定性评分 (0-100, 默认90): %color_reset%

if "%stability%"=="" set stability=90

echo.
echo %color_info%正在创建版本 %version%...%color_reset%
echo.

REM 创建临时Python脚本文件
echo from app.core.version_manager import get_version_manager > temp_version_script.py
echo vm = get_version_manager() >> temp_version_script.py
echo changes_list = [c.strip() for c in '%changes%'.split(',') if c.strip()] >> temp_version_script.py
echo if vm.create_version('%version%', '%description%', changes_list, float('%stability%')): >> temp_version_script.py
echo     print('版本 %version% 创建成功！') >> temp_version_script.py
echo else: >> temp_version_script.py
echo     print('创建版本失败！') >> temp_version_script.py

python temp_version_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                    创建版本时出现错误！                      ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    版本创建完成！                            ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

REM 清理临时文件
del temp_version_script.py
echo.
pause
goto menu

:show_history
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                    正在获取版本历史...                        ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo from app.core.version_manager import get_version_manager > temp_history_script.py
echo vm = get_version_manager() >> temp_history_script.py
echo versions = vm.get_version_history() >> temp_history_script.py
echo print('版本历史:') >> temp_history_script.py
echo for v in versions: >> temp_history_script.py
echo     print(f'版本: {v["version"]}') >> temp_history_script.py
echo     print(f'  提交: {v["commit_hash"]}') >> temp_history_script.py
echo     print(f'  作者: {v["author"]}') >> temp_history_script.py
echo     print(f'  时间: {v["timestamp"]}') >> temp_history_script.py
echo     print(f'  稳定性: {v["stability_score"]}/100') >> temp_history_script.py
echo     print(f'  状态: {"稳定" if v["is_stable"] else "测试中"}') >> temp_history_script.py
echo     print('---') >> temp_history_script.py

python temp_history_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                    获取版本历史时出现错误！                  ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    版本历史获取成功！                        ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

del temp_history_script.py
echo.
pause
goto menu

:rollback_stable
echo.
echo %color_warning%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_warning%║                    正在回滚到稳定版本...                      ║%color_reset%
echo %color_warning%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo from app.core.version_manager import get_version_manager > temp_rollback_script.py
echo vm = get_version_manager() >> temp_rollback_script.py
echo if vm.rollback_to_stable(): >> temp_rollback_script.py
echo     print('回滚到稳定版本成功！') >> temp_rollback_script.py
echo else: >> temp_rollback_script.py
echo     print('回滚失败！') >> temp_rollback_script.py

python temp_rollback_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                    回滚操作时出现错误！                      ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    回滚操作完成！                            ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

del temp_rollback_script.py
echo.
pause
goto menu

:emergency_rollback
echo.
echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_error%║                    正在执行紧急回滚...                        ║%color_reset%
echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo from app.core.version_manager import get_version_manager > temp_emergency_script.py
echo vm = get_version_manager() >> temp_emergency_script.py
echo if vm.emergency_rollback(): >> temp_emergency_script.py
echo     print('紧急回滚成功！') >> temp_emergency_script.py
echo else: >> temp_emergency_script.py
echo     print('紧急回滚失败！') >> temp_emergency_script.py

python temp_emergency_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                    紧急回滚时出现错误！                      ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    紧急回滚完成！                            ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

del temp_emergency_script.py
echo.
pause
goto menu

:show_error_monitor
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                    正在获取错误监控状态...                      ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
echo from app.core.error_monitor import get_error_monitor > temp_error_script.py
echo em = get_error_monitor() >> temp_error_script.py
echo summary = em.get_error_summary() >> temp_error_script.py
echo import json >> temp_error_script.py
echo print('错误监控状态:') >> temp_error_script.py
echo print(json.dumps(summary, indent=2, ensure_ascii=False)) >> temp_error_script.py

python temp_error_script.py
if errorlevel 1 (
    echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_error%║                  获取错误监控状态时出现错误！                ║%color_reset%
    echo %color_error%║              请检查Python环境和依赖是否正确安装              ║%color_reset%
    echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    错误监控状态获取成功！                    ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
)

del temp_error_script.py
echo.
pause
goto menu

:start_gui
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                    正在启动版本管理GUI...                      ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
python app/gui/version_gui.py
goto menu

:sync_github
echo.
echo %color_info%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_info%║                    正在同步到GitHub...                        ║%color_reset%
echo %color_info%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
if exist "version_sync_to_github.bat" (
    call "version_sync_to_github.bat"
    echo %color_success%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_success%║                    GitHub同步完成！                          ║%color_reset%
    echo %color_success%╚══════════════════════════════════════════════════════════════╝%color_reset%
) else (
    echo %color_warning%╔══════════════════════════════════════════════════════════════╗%color_reset%
    echo %color_warning%║              未找到GitHub同步脚本！                          ║%color_reset%
    echo %color_warning%║          请先运行 version_sync_to_github.ps1              ║%color_reset%
    echo %color_warning%╚══════════════════════════════════════════════════════════════╝%color_reset%
)
echo.
pause
goto menu

:invalid_choice
echo.
echo %color_error%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_error%║                      无效选择！                              ║%color_reset%
echo %color_error%║                    请重新输入 (1-9)                          ║%color_reset%
echo %color_error%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
pause
goto menu

:exit
echo.
echo %color_title%╔══════════════════════════════════════════════════════════════╗%color_reset%
echo %color_title%║                感谢使用 FileSenseScan 版本管理系统！            ║%color_reset%
echo %color_title%║                        再见！                                ║%color_reset%
echo %color_title%╚══════════════════════════════════════════════════════════════╝%color_reset%
echo.
pause
exit 