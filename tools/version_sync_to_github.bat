@echo off
chcp 65001 >nul
title FileSenseScan GitHub 自动同步

echo 正在启动 GitHub 同步脚本...
echo.

REM 启动PowerShell脚本
powershell.exe -ExecutionPolicy Bypass -File "%~dp0version_sync_to_github.ps1"

echo.
echo 脚本执行完成，按任意键退出...
pause >nul 