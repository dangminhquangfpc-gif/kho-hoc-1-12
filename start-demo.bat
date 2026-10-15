@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0runtime\python\python.exe" goto bundled_python
where py >nul 2>&1
if errorlevel 1 goto try_python
py -3.12 -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if errorlevel 1 goto try_python
py -3.12 -X utf8 "%~dp0scripts\run_local_demo.py" %*
set "demo_exit=%errorlevel%"
goto finished

:bundled_python
"%~dp0runtime\python\python.exe" -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if errorlevel 1 goto damaged_runtime
"%~dp0runtime\python\python.exe" -X utf8 "%~dp0scripts\run_local_demo.py" %*
set "demo_exit=%errorlevel%"
goto finished

:damaged_runtime
echo The bundled Python runtime could not start.
echo Extract a fresh copy of the whole demo ZIP, then run start-demo.bat again.
set "demo_exit=1"
goto finished

:try_python
where python >nul 2>&1
if errorlevel 1 goto missing_python
python -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if errorlevel 1 goto missing_python
python -X utf8 "%~dp0scripts\run_local_demo.py" %*
set "demo_exit=%errorlevel%"
goto finished

:missing_python
echo Python 3.12 is required to start this demo.
echo Install it from https://www.python.org/downloads/
echo Enable "Add Python to PATH" during installation.
echo Then double-click start-demo.bat again.
set "demo_exit=1"

:finished
echo.
pause
exit /b %demo_exit%
