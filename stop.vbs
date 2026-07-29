' 停止所有 Python 服务
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c taskkill /f /im python.exe", 0, False
objShell.Run "cmd /c taskkill /f /im streamlit.exe", 0, False
WScript.Quit