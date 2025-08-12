# FileSenseScan GitHub 自动同步脚本
# 双击运行此脚本即可自动同步代码到GitHub

Write-Host "=== FileSenseScan GitHub 自动同步脚本 ===" -ForegroundColor Green
Write-Host "开始同步代码到GitHub..." -ForegroundColor Yellow

# 检查是否在正确的目录
if (-not (Test-Path ".git")) {
    Write-Host "错误：当前目录不是Git仓库！" -ForegroundColor Red
    Write-Host "请确保在 FileSenseScan 项目根目录下运行此脚本" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查Git是否可用
try {
    $gitVersion = git --version
    if ($LASTEXITCODE -ne 0) {
        throw "Git命令不可用"
    }
    Write-Host "Git版本: $gitVersion" -ForegroundColor Cyan
} catch {
    Write-Host "错误：Git未安装或不在PATH中！" -ForegroundColor Red
    Write-Host "请先安装Git: https://git-scm.com/" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查远程仓库配置
try {
    $remote = git remote get-url origin
    if (-not $remote) {
        Write-Host "错误：未配置远程仓库！" -ForegroundColor Red
        Write-Host "请先运行: git remote add origin <你的GitHub仓库URL>" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
    Write-Host "远程仓库: $remote" -ForegroundColor Cyan
} catch {
    Write-Host "错误：获取远程仓库信息失败！" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查网络连接
try {
    $pingResult = Test-NetConnection -ComputerName "github.com" -Port 443 -InformationLevel Quiet
    if (-not $pingResult) {
        Write-Host "警告：无法连接到GitHub，请检查网络连接" -ForegroundColor Yellow
        $continue = Read-Host "是否继续尝试同步？(y/n)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "用户取消操作" -ForegroundColor Yellow
            exit 0
        }
    }
} catch {
    Write-Host "警告：网络连接检查失败" -ForegroundColor Yellow
}

# 获取当前状态
Write-Host "`n检查Git状态..." -ForegroundColor Yellow
try {
    git status
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告：Git状态检查失败" -ForegroundColor Yellow
    }
} catch {
    Write-Host "警告：Git状态检查出错" -ForegroundColor Yellow
}

# 添加所有更改
Write-Host "`n添加所有更改到暂存区..." -ForegroundColor Yellow
try {
    git add .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "文件添加成功" -ForegroundColor Green
    } else {
        Write-Host "文件添加失败" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
} catch {
    Write-Host "文件添加时出错" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查是否有更改需要提交
try {
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "`n没有更改需要提交，工作目录是干净的" -ForegroundColor Green
    } else {
        Write-Host "`n检测到以下更改:" -ForegroundColor Cyan
        $status | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
        
        # 获取提交信息
        $commitMsg = Read-Host "`n请输入提交信息（描述这次更改）"
        if (-not $commitMsg) {
            $commitMsg = "自动同步更新 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        }
        
        # 提交更改
        Write-Host "`n提交更改..." -ForegroundColor Yellow
        git commit -m $commitMsg
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "提交成功！" -ForegroundColor Green
        } else {
            Write-Host "提交失败！" -ForegroundColor Red
            Write-Host "请检查Git配置和提交信息" -ForegroundColor Red
            Read-Host "按任意键退出"
            exit 1
        }
    }
} catch {
    Write-Host "检查Git状态时出错" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 推送到GitHub
Write-Host "`n推送到GitHub..." -ForegroundColor Yellow
try {
    # 尝试推送到main分支
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== 同步成功！ ===" -ForegroundColor Green
        Write-Host "代码已成功推送到GitHub" -ForegroundColor Green
    } else {
        # 如果main分支失败，尝试master分支
        Write-Host "推送到main分支失败，尝试master分支..." -ForegroundColor Yellow
        git push origin master
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n=== 同步成功！ ===" -ForegroundColor Green
            Write-Host "代码已成功推送到GitHub (master分支)" -ForegroundColor Green
        } else {
            Write-Host "`n=== 推送失败！ ===" -ForegroundColor Red
            Write-Host "请检查以下可能的问题：" -ForegroundColor Red
            Write-Host "1. 网络连接是否正常" -ForegroundColor Red
            Write-Host "2. GitHub凭据是否正确" -ForegroundColor Red
            Write-Host "3. 远程仓库是否存在" -ForegroundColor Red
            Write-Host "4. 是否有推送权限" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "`n=== 推送出错！ ===" -ForegroundColor Red
    Write-Host "推送过程中发生错误: $_" -ForegroundColor Red
}

Write-Host "`n按任意键退出..." -ForegroundColor Cyan
Read-Host 