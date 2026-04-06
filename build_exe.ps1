Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv/Scripts/python.exe")) {
    py -3.11 -m venv .venv
}

& ".venv/Scripts/python.exe" -m pip install --upgrade pip
& ".venv/Scripts/python.exe" -m pip install -r requirements.txt
& ".venv/Scripts/python.exe" -m pip install pyinstaller

& ".venv/Scripts/python.exe" -m PyInstaller --noconfirm --clean --windowed --name "SecureLabDashboard" --collect-all cryptography app.py

Write-Host "Build complete. EXE path: dist/SecureLabDashboard/SecureLabDashboard.exe"
