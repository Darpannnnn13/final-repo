' ParentEye Silent Admin Loader
' This VBScript runs ParentEye Client with admin privileges silently
' No CMD window will appear

CreateObject("Shell.Application").ShellExecute "cmd.exe", "/c cd /d """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & """ && start /B ParentEye_Client.exe", "", "runas", 0
