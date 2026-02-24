@echo off
echo ========================================
echo   AI Daily 一键部署脚本
echo ========================================
echo.
echo 请在浏览器中打开以下链接创建新仓库:
echo https://github.com/new
echo.
echo 1. 输入仓库名: ai-daily
echo 2. 选择 Public
echo 3. 不要勾选任何初始化选项
echo 4. 点击 Create repository
echo.
echo 创建完成后，回到这里按任意键继续...
pause > nul

echo.
echo 正在推送代码到GitHub...
git add .
git commit -m "feat: AI Daily website with cyberpunk style"
git push -u origin main

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 请在仓库设置中启用 GitHub Pages:
echo 1. 进入仓库设置
echo 2. 找到 Pages 页面
echo 3. Source 选择 "Deploy from a branch"
echo 4. Branch 选择 "main" 和 "/(root)"
echo 5. 点击 Save
echo.
echo 你的网站将在几分钟内上线！
echo.
pause
