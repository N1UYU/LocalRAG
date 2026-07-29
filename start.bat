@echo off
chcp 65001 >nul
title Local RAG 启动器

echo ========================================
echo    Local RAG 系统正在启动...
echo ========================================
echo.

:: 进入脚本所在目录（确保路径正确）
cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo 错误：未找到虚拟环境 .venv
    echo 请先运行：python -m venv .venv
    pause
    exit /b
)

echo [1/3] 正在启动 FastAPI 后端服务...
start /B .venv\Scripts\python.exe api.py > logs\api.log 2>&1

echo [2/3] 等待 API 服务启动（10秒）...
timeout /t 5 /nobreak >nul

echo [3/3] 正在启动 Streamlit 界面...
start /B .venv\Scripts\streamlit run app.py --server.port 8501

echo 等待界面加载...
timeout /t 3 /nobreak >nul

echo 正在打开浏览器...
start http://localhost:8501

echo.
echo ========================================
echo    启动完成！
echo    API 服务: http://localhost:8000
echo    管理界面: http://localhost:8501
echo    日志文件: logs\api.log
echo ========================================
echo.
echo 按任意键关闭本窗口（服务会继续运行）
pause >nul