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

# 检查远程仓库配置
$remote = git remote get-url origin
if (-not $remote) {
    Write-Host "错误：未配置远程仓库！" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "远程仓库: $remote" -ForegroundColor Cyan

# 获取当前状态
Write-Host "`n检查Git状态..." -ForegroundColor Yellow
git status

# 添加所有更改
Write-Host "`n添加所有更改到暂存区..." -ForegroundColor Yellow
git add .

# 检查是否有更改需要提交
$status = git status --porcelain
if (-not $status) {
    Write-Host "`n没有更改需要提交，工作目录是干净的" -ForegroundColor Green
} else {
    # 获取提交信息
    $commitMsg = Read-Host "`n请输入提交信息（描述这次更改）"
    if (-not $commitMsg) {
        $commitMsg = "自动同步更新"
    }
    
    # 提交更改
    Write-Host "`n提交更改..." -ForegroundColor Yellow
    git commit -m $commitMsg
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "提交成功！" -ForegroundColor Green
    } else {
        Write-Host "提交失败！" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

# 推送到GitHub
Write-Host "`n推送到GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== 同步成功！ ===" -ForegroundColor Green
    Write-Host "代码已成功推送到GitHub" -ForegroundColor Green
} else {
    Write-Host "`n=== 推送失败！ ===" -ForegroundColor Red
    Write-Host "请检查网络连接和GitHub凭据" -ForegroundColor Red
}

Write-Host "`n按任意键退出..." -ForegroundColor Cyan
Read-Host 