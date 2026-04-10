@echo off
REM Wrapper for build_integration_bundle.py (Windows)

set "SCRIPT_DIR=%~dp0"
if not defined PYTHON set "PYTHON=python"
set "PYTHONUTF8=0"
set "PYTHONIOENCODING=cp1251"

"%PYTHON%" "%SCRIPT_DIR%build_integration_bundle.py" --output-dir .out --force %*
