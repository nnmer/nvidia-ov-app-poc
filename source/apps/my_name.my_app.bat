@echo off
setlocal
if not exist "%~dp0..\.env" cp "%~dp0..\.env.dist" "%~dp0..\.env"
call "%~dp0..\..\kit\kit.exe" "%%~dp0my_name.my_app.kit"  %*
