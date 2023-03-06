@echo off
if exist source\.env (
    call copy source\.env %~dp0_build\windows-x86_64\release\.env /y
) else (
    call copy source\.env.dist %~dp0_build\windows-x86_64\release\.env /y
)
call "%~dp0_build\windows-x86_64\release\msft.khi.viewer.bat"