# GitHub 同步使用说明

## 快速同步方法

### 方法1：双击批处理文件（推荐）
直接双击 `同步到GitHub.bat` 文件即可！

### 方法2：使用PowerShell脚本
右键点击 `sync_to_github.ps1` → "使用PowerShell运行"

## 脚本功能

自动同步脚本会：
1. ✅ 检查Git仓库状态
2. ✅ 添加所有更改到暂存区
3. ✅ 提示输入提交信息
4. ✅ 自动提交更改
5. ✅ 推送到GitHub

## 注意事项

- 首次使用需要输入GitHub用户名和密码/Token
- 确保网络连接正常
- 脚本必须在项目根目录下运行

## 手动同步命令

如果脚本有问题，也可以手动执行：

```bash
git add .
git commit -m "更新说明"
git push origin main
```

## 常见问题

**Q: 提示权限错误怎么办？**
A: 需要在GitHub上生成Personal Access Token，用Token代替密码

**Q: 推送失败怎么办？**
A: 检查网络连接，确保GitHub仓库地址正确

**Q: 如何生成Personal Access Token？**
A: GitHub → Settings → Developer settings → Personal access tokens → Generate new token 