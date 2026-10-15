@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist "services\api\requirements.lock.txt" (
  echo Không tìm thấy mã máy chủ. Hãy giải nén toàn bộ gói cài đặt trước.
  exit /b 1
)
if exist ".server-venv\Scripts\python.exe" goto install_dependencies
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3 -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,12),(3,13)) else 1)" >nul 2>nul
if errorlevel 1 goto try_python
py -3 -m venv .server-venv
if errorlevel 1 exit /b 1
goto install_dependencies
:try_python
where python >nul 2>nul
if errorlevel 1 goto need_python
python -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,12),(3,13)) else 1)" >nul 2>nul
if errorlevel 1 goto need_python
python -m venv .server-venv
if errorlevel 1 exit /b 1
:install_dependencies
".server-venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r "services\api\requirements.lock.txt"
if errorlevel 1 exit /b 1
".server-venv\Scripts\python.exe" "scripts\prepare_free_server.py" %*
exit /b %errorlevel%
:need_python
echo Cần Python 3.12 hoặc 3.13 để chạy công cụ này.
echo Cài Python từ https://www.python.org/downloads/windows/ rồi mở lại.
echo Công cụ không tự tải hay cài Python.
exit /b 1
