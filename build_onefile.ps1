Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv/Scripts/python.exe")) {
    py -3.11 -m venv .venv
}

& ".venv/Scripts/python.exe" -m pip install --upgrade pip
& ".venv/Scripts/python.exe" -m pip install -r requirements.txt
& ".venv/Scripts/python.exe" -m pip install pyinstaller pillow

& ".venv/Scripts/python.exe" .\tools\generate_icon.py

& ".venv/Scripts/python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name "SecureLabDashboard" --icon "assets\securelab.ico" --collect-all cryptography app.py

Write-Host "One-file build complete. EXE path: dist/SecureLabDashboard.exe"
