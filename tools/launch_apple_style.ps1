# FileSenseScan 苹果风格版本管理系统启动脚本
# 遵循苹果公司用户体验设计规范

Write-Host ""
Write-Host "🚀 启动 FileSenseScan 苹果风格版本管理系统..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🎨 应用苹果公司用户体验设计规范" -ForegroundColor Green
Write-Host "📱 支持浅色/深色主题" -ForegroundColor Green
Write-Host "🔧 优化的版本管理功能" -ForegroundColor Green
Write-Host "🚨 智能错误监控系统" -ForegroundColor Green
Write-Host "💾 自动备份和恢复" -ForegroundColor Green
Write-Host "🌐 GitHub集成支持" -ForegroundColor Green
Write-Host ""
Write-Host "正在启动..." -ForegroundColor Yellow
Write-Host ""

try {
    # 启动苹果风格GUI
    python scripts\launch_apple_style_gui.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 系统已正常退出" -ForegroundColor Green
        Write-Host ""
    } else {
        throw "Python脚本执行失败"
    }
}
catch {
    Write-Host ""
    Write-Host "❌ 启动失败，请检查：" -ForegroundColor Red
    Write-Host "1. Python环境是否正确安装" -ForegroundColor Yellow
    Write-Host "2. 依赖包是否已安装 (pip install -r requirements.txt)" -ForegroundColor Yellow
    Write-Host "3. 系统配置是否正确" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "错误详情: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 