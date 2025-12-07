@echo off
REM Windows: one-folder EXE build script using PyInstaller
REM Usage: double-click or run from project root in cmd

python -m pip install --upgrade pip
pip install pyinstaller

REM Include config and log files in the onefile EXE (they'll be bundled and
REM extracted at runtime). Note: when using --onefile, data is available
REM via sys._MEIPASS at runtime.
pyinstaller --noconsole --onefile ^
  --add-data "kh_config.json;." ^
  --add-data "usage_logs.json;." ^
  --add-data "requirements.txt;." ^
  --name kirmizi_quickbuttons kirmizi_quickbuttons.py

echo.
echo Build tamamlandı. Çıktı klasörü: dist\kirmizi_quickbuttons
pause
