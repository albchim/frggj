@echo off
SETLOCAL
set UV_INSTALL_DIR=%~dp0\thirdparty\python

%~dp0\thirdparty\uv.exe run python source\main.py


ENDLOCAL