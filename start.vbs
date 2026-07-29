' Local RAG 启动器（防重复打开）
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strPath

' 检查 API 端口是否已被占用（表示服务已在运行）
Set objExec = objShell.Exec("cmd /c netstat -ano | findstr :8000 | findstr LISTENING")
strOutput = objExec.StdOut.ReadAll()

If InStr(strOutput, "LISTENING") > 0 Then
    ' 服务已在运行，直接打开浏览器
    objShell.Run "cmd /c start http://localhost:8501", 0, False
    WScript.Quit
End If

' 服务未运行，正常启动
objShell.Run "cmd /c .venv\Scripts\python.exe api.py > logs\api.log 2>&1", 0, False
WScript.Sleep 8000

objShell.Run "cmd /c .venv\Scripts\streamlit run app.py --server.port=8501", 0, False
WScript.Sleep 3000

objShell.Run "cmd /c start http://localhost:8501", 0, False
WScript.Quit