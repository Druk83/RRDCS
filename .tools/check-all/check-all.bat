@echo off
REM Wrapper for check_all.py (Windows)

set "SCRIPT_DIR=%~dp0"
if not defined PYTHON set "PYTHON=python"

"%PYTHON%" "%SCRIPT_DIR%check_all.py" %*
