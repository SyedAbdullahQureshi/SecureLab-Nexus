@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" -m pip install pyinstaller

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name "SecureLabDashboard" --collect-all cryptography app.py

echo Build complete. EXE path: dist\SecureLabDashboard\SecureLabDashboard.exe
endlocal
