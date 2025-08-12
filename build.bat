@echo off
setlocal
cd /d %~dp0

echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo 正在打包应用...
pyinstaller ^
  --noconsole --onefile ^
  --name FileSenseScan ^
  --distpath .\dist ^
  --workpath .\build ^
  --specpath .\build ^
  --icon assets\app.ico ^
  --add-data "assets;assets" ^
  --add-data "app;app" ^
  app\gui\main_gui.py

echo.
echo ✅ 打包完成！可执行文件位置：dist\FileSenseScan.exe
pause 