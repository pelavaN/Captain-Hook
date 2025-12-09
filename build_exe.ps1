<#!
PowerShell script to build Windows EXE using PyInstaller.
Run from repo root on Windows: ./build_exe.ps1
!>
Set-StrictMode -Version Latest
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

$arguments = @(
  '--noconsole',
  '--onefile',
  '--name','social_scheduler',
  '--add-data','.env.example;.',
  '--add-data','README.md;.',
  'src/main.py'
)

pyinstaller @arguments
Write-Host "Build tamamlandi. dist/social_scheduler.exe hazır."
