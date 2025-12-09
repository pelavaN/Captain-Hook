@echo off
REM Windows: build one-file EXE with PyInstaller
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconsole --onefile ^
  --name social_scheduler ^
  --add-data ".env.example;." ^
  --add-data "README.md;." ^
  src/main.py

echo.
echo Build tamamlandi. dist\\social_scheduler.exe dosyasini Inno Setup ile kurulum paketi yapabilirsiniz.
pause
