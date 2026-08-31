Option Explicit

Dim shell, fso, scriptDir, pythonPath, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonPath = scriptDir & "\.venv\Scripts\python.exe"

If Not fso.FileExists(pythonPath) Then
    pythonPath = "python"
End If

shell.CurrentDirectory = scriptDir

' Run the local Streamlit server without displaying a command window
command = """" & pythonPath & """ -m streamlit run """ & scriptDir & "\app.py"""
shell.Run command, 0, False

' Wait briefly for the server to spin up, then launch default browser
WScript.Sleep 3500
shell.Run "http://localhost:8501", 1, False
