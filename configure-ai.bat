@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0runtime\python\python.exe" goto bundled_python
where py >nul 2>&1
if errorlevel 1 goto try_python
py -3.12 -X utf8 "%~dp0scripts\configure_ai.py" --state "%~dp0state" %*
set "ai_exit=%errorlevel%"
goto finished

:bundled_python
"%~dp0runtime\python\python.exe" -X utf8 "%~dp0scripts\configure_ai.py" --state "%~dp0state" %*
set "ai_exit=%errorlevel%"
goto finished

:try_python
where python >nul 2>&1
if errorlevel 1 goto missing_python
python -X utf8 "%~dp0scripts\configure_ai.py" --state "%~dp0state" %*
set "ai_exit=%errorlevel%"
goto finished

:missing_python
echo Python 3.12 is required. Extract the complete Windows demo ZIP.
set "ai_exit=1"

:finished
echo.
pause
exit /b %ai_exit%
