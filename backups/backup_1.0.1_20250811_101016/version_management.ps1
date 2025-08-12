# FileSenseScan 版本管理系统 PowerShell脚本
# 提供完整的版本管理、错误监控和自动恢复功能

param(
    [string]$Action = "menu",
    [string]$Version = "",
    [string]$Description = "",
    [string]$Changes = "",
    [float]$Stability = 90.0
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色定义
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Default = "White"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "Default"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Show-Banner {
    Write-ColorOutput "========================================" $Colors.Info
    Write-ColorOutput "    FileSenseScan 版本管理系统" $Colors.Info
    Write-ColorOutput "========================================" $Colors.Info
    Write-Host ""
}

function Show-Menu {
    Show-Banner
    Write-ColorOutput "请选择操作：" $Colors.Default
    Write-Host ""
    Write-ColorOutput "1. 查看当前版本状态" $Colors.Default
    Write-ColorOutput "2. 创建新版本" $Colors.Default
    Write-ColorOutput "3. 查看版本历史" $Colors.Default
    Write-ColorOutput "4. 回滚到稳定版本" $Colors.Default
    Write-ColorOutput "5. 紧急回滚" $Colors.Default
    Write-ColorOutput "6. 查看错误监控状态" $Colors.Default
    Write-ColorOutput "7. 启动版本管理GUI" $Colors.Default
    Write-ColorOutput "8. 一键同步到GitHub" $Colors.Default
    Write-ColorOutput "9. 系统健康检查" $Colors.Default
    Write-ColorOutput "10. 清理旧备份" $Colors.Default
    Write-ColorOutput "11. 退出" $Colors.Default
    Write-Host ""
}

function Get-UserChoice {
    $choice = Read-Host "请输入选择 (1-11)"
    return $choice
}

function Show-ProjectStatus {
    Write-ColorOutput "正在获取版本状态..." $Colors.Info
    try {
        $statusScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
status = vm.get_project_status()
import json
print('项目状态:')
print(json.dumps(status, indent=2, ensure_ascii=False))
"@
        
        $statusScript | python -c $_
        Write-ColorOutput "状态获取完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "获取状态失败: $_" $Colors.Error
    }
}

function Create-NewVersion {
    Write-ColorOutput "创建新版本..." $Colors.Info
    
    if (-not $Version) {
        $Version = Read-Host "版本号 (例如: 1.0.1)"
    }
    
    if (-not $Description) {
        $Description = Read-Host "版本描述"
    }
    
    if (-not $Changes) {
        $Changes = Read-Host "变更内容 (用逗号分隔)"
    }
    
    if (-not $Stability) {
        $Stability = Read-Host "稳定性评分 (0-100, 默认90)"
        if (-not $Stability) { $Stability = 90.0 }
    }
    
    try {
        $createScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
changes_list = [c.strip() for c in '$Changes'.split(',') if c.strip()]
if vm.create_version('$Version', '$Description', changes_list, float('$Stability')):
    print('版本 $Version 创建成功！')
else:
    print('创建版本失败！')
"@
        
        $createScript | python -c $_
        Write-ColorOutput "版本创建操作完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "创建版本失败: $_" $Colors.Error
    }
}

function Show-VersionHistory {
    Write-ColorOutput "正在获取版本历史..." $Colors.Info
    try {
        $historyScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
versions = vm.get_version_history()
print('版本历史:')
for v in versions:
    print(f'版本: {v["version"]}')
    print(f'  提交: {v["commit_hash"]}')
    print(f'  作者: {v["author"]}')
    print(f'  时间: {v["timestamp"]}')
    print(f'  稳定性: {v["stability_score"]}/100')
    print(f'  状态: {"稳定" if v["is_stable"] else "测试中"}')
    print('---')
"@
        
        $historyScript | python -c $_
        Write-ColorOutput "版本历史获取完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "获取版本历史失败: $_" $Colors.Error
    }
}

function Rollback-ToStable {
    Write-ColorOutput "正在回滚到稳定版本..." $Colors.Warning
    try {
        $rollbackScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
if vm.rollback_to_stable():
    print('回滚到稳定版本成功！')
else:
    print('回滚失败！')
"@
        
        $rollbackScript | python -c $_
        Write-ColorOutput "回滚操作完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "回滚失败: $_" $Colors.Error
    }
}

function Invoke-EmergencyRollback {
    Write-ColorOutput "正在执行紧急回滚..." $Colors.Error
    try {
        $emergencyScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
if vm.emergency_rollback():
    print('紧急回滚成功！')
else:
    print('紧急回滚失败！')
"@
        
        $emergencyScript | python -c $_
        Write-ColorOutput "紧急回滚操作完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "紧急回滚失败: $_" $Colors.Error
    }
}

function Show-ErrorMonitorStatus {
    Write-ColorOutput "正在获取错误监控状态..." $Colors.Info
    try {
        $errorScript = @"
from app.error_monitor import get_error_monitor
em = get_error_monitor()
summary = em.get_error_summary()
import json
print('错误监控状态:')
print(json.dumps(summary, indent=2, ensure_ascii=False))
"@
        
        $errorScript | python -c $_
        Write-ColorOutput "错误监控状态获取完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "获取错误监控状态失败: $_" $Colors.Error
    }
}

function Start-VersionGUI {
    Write-ColorOutput "正在启动版本管理GUI..." $Colors.Info
    try {
        Start-Process python -ArgumentList "app/version_gui.py" -NoNewWindow
        Write-ColorOutput "GUI启动成功！" $Colors.Success
    }
    catch {
        Write-ColorOutput "启动GUI失败: $_" $Colors.Error
    }
}

function Sync-ToGitHub {
    Write-ColorOutput "正在同步到GitHub..." $Colors.Info
    try {
        if (Test-Path "version_sync_to_github.bat") {
            & "version_sync_to_github.bat"
            Write-ColorOutput "GitHub同步完成！" $Colors.Success
        }
        elseif (Test-Path "version_sync_to_github.ps1") {
            & "version_sync_to_github.ps1"
            Write-ColorOutput "GitHub同步完成！" $Colors.Success
        }
        else {
            Write-ColorOutput "未找到GitHub同步脚本！" $Colors.Warning
        }
    }
    catch {
        Write-ColorOutput "GitHub同步失败: $_" $Colors.Error
    }
}

function Invoke-SystemHealthCheck {
    Write-ColorOutput "正在执行系统健康检查..." $Colors.Info
    try {
        # 检查psutil是否安装
        $psutilCheck = python -c "import psutil; print('psutil available')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "警告: psutil库未安装，将跳过系统资源检查" $Colors.Warning
            Write-ColorOutput "建议运行: pip install psutil" $Colors.Info
            
            # 执行基础健康检查
            $basicHealthScript = @"
import os
from pathlib import Path

print('=== 基础系统健康检查报告 ===')
print()

# 当前工作目录
current_dir = Path.cwd()
print(f'当前工作目录: {current_dir}')
print()

# 关键文件检查
critical_files = ['app/gui_app_modern.py', 'app/version_manager.py', 'requirements.txt']
print('关键文件检查:')
for file_path in critical_files:
    full_path = current_dir / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f'  ✅ {file_path} - {size} bytes')
    else:
        print(f'  ❌ {file_path} - 缺失')
print()

# Python环境检查
import sys
print(f'Python版本: {sys.version}')
print(f'Python路径: {sys.executable}')
print()

# 依赖检查
try:
    import customtkinter
    print('✅ customtkinter 可用')
except ImportError:
    print('❌ customtkinter 未安装')
    print('建议运行: pip install customtkinter')

try:
    import tkinter
    print('✅ tkinter 可用')
except ImportError:
    print('❌ tkinter 未安装')

print()
print('基础健康检查完成！')
"@
            
            $basicHealthScript | python -c $_
        } else {
            # 执行完整健康检查
            $healthScript = @"
import psutil
import os
from pathlib import Path

print('=== 系统健康检查报告 ===')
print()

# CPU使用率
try:
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f'CPU使用率: {cpu_percent}%')
    if cpu_percent > 90:
        print('⚠️  CPU使用率过高！')
    print()
except Exception as e:
    print(f'CPU检查失败: {e}')
    print()

# 内存使用
try:
    memory = psutil.virtual_memory()
    print(f'内存使用: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)')
    if memory.percent > 90:
        print('⚠️  内存使用率过高！')
    print()
except Exception as e:
    print(f'内存检查失败: {e}')
    print()

# 磁盘空间
try:
    current_dir = Path.cwd()
    disk_usage = psutil.disk_usage(current_dir)
    print(f'磁盘使用: {disk_usage.percent}% ({disk_usage.free // (1024**3)}GB 可用)')
    if disk_usage.percent > 90:
        print('⚠️  磁盘空间不足！')
    print()
except Exception as e:
    print(f'磁盘检查失败: {e}')
    print()

# 关键文件检查
critical_files = ['app/gui_app_modern.py', 'app/version_manager.py', 'requirements.txt']
print('关键文件检查:')
for file_path in critical_files:
    full_path = current_dir / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f'  ✅ {file_path} - {size} bytes')
    else:
        print(f'  ❌ {file_path} - 缺失')
print()

# Python环境检查
import sys
print(f'Python版本: {sys.version}')
print(f'Python路径: {sys.executable}')
print()

# 依赖检查
try:
    import customtkinter
    print('✅ customtkinter 可用')
except ImportError:
    print('❌ customtkinter 未安装')
    print('建议运行: pip install customtkinter')

try:
    import tkinter
    print('✅ tkinter 可用')
except ImportError:
    print('❌ tkinter 未安装')

print()
print('健康检查完成！')
"@
            
            $healthScript | python -c $_
        }
        
        Write-ColorOutput "系统健康检查完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "系统健康检查失败: $_" $Colors.Error
        Write-ColorOutput "请检查Python环境和依赖是否正确安装" $Colors.Warning
    }
}

function Clear-OldBackups {
    Write-ColorOutput "正在清理旧备份..." $Colors.Info
    try {
        $cleanupScript = @"
from app.version_manager import get_version_manager
vm = get_version_manager()
vm._cleanup_old_backups()
print('旧备份清理完成！')
"@
        
        $cleanupScript | python -c $_
        Write-ColorOutput "备份清理完成！" $Colors.Success
    }
    catch {
        Write-ColorOutput "备份清理失败: $_" $Colors.Error
    }
}

function Main-Loop {
    while ($true) {
        Show-Menu
        $choice = Get-UserChoice
        
        switch ($choice) {
            "1" { 
                Show-ProjectStatus
                Read-Host "按回车键继续"
            }
            "2" { 
                Create-NewVersion
                Read-Host "按回车键继续"
            }
            "3" { 
                Show-VersionHistory
                Read-Host "按回车键继续"
            }
            "4" { 
                Rollback-ToStable
                Read-Host "按回车键继续"
            }
            "5" { 
                Invoke-EmergencyRollback
                Read-Host "按回车键继续"
            }
            "6" { 
                Show-ErrorMonitorStatus
                Read-Host "按回车键继续"
            }
            "7" { 
                Start-VersionGUI
                Read-Host "按回车键继续"
            }
            "8" { 
                Sync-ToGitHub
                Read-Host "按回车键继续"
            }
            "9" { 
                Invoke-SystemHealthCheck
                Read-Host "按回车键继续"
            }
            "10" { 
                Clear-OldBackups
                Read-Host "按回车键继续"
            }
            "11" { 
                Write-ColorOutput "感谢使用 FileSenseScan 版本管理系统！" $Colors.Success
                return
            }
            default { 
                Write-ColorOutput "无效选择，请重新输入！" $Colors.Warning
                Start-Sleep 2
            }
        }
        
        Clear-Host
    }
}

# 主程序入口
try {
    if ($Action -eq "menu") {
        Main-Loop
    }
    elseif ($Action -eq "status") {
        Show-ProjectStatus
    }
    elseif ($Action -eq "create") {
        Create-NewVersion
    }
    elseif ($Action -eq "history") {
        Show-VersionHistory
    }
    elseif ($Action -eq "rollback") {
        Rollback-ToStable
    }
    elseif ($Action -eq "emergency") {
        Invoke-EmergencyRollback
    }
    elseif ($Action -eq "monitor") {
        Show-ErrorMonitorStatus
    }
    elseif ($Action -eq "gui") {
        Start-VersionGUI
    }
    elseif ($Action -eq "sync") {
        Sync-ToGitHub
    }
    elseif ($Action -eq "health") {
        Invoke-SystemHealthCheck
    }
    elseif ($Action -eq "cleanup") {
        Clear-OldBackups
    }
    else {
        Write-ColorOutput "未知操作: $Action" $Colors.Error
        Write-ColorOutput "使用 -Action menu 启动交互式菜单" $Colors.Info
    }
}
catch {
    Write-ColorOutput "程序执行出错: $_" $Colors.Error
    Write-ColorOutput "请检查Python环境和依赖是否正确安装" $Colors.Warning
}
finally {
    if ($Action -eq "menu") {
        Read-Host "按回车键退出"
    }
} 