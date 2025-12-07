<#
PowerShell script to build a Windows EXE using PyInstaller.
Run in PowerShell on Windows (from repo root):
  .\build_exe.ps1
#>
Set-StrictMode -Version Latest

python -m pip install --upgrade pip
pip install pyinstaller

$add = @(
  "kh_config.json;.",
  "usage_logs.json;.",
  "requirements.txt;."
)


$args = @(
  '--noconsole',
  '--onefile',
  ( $add | ForEach-Object { "--add-data `"$_`"" } ),
  '--name','kirmizi_quickbuttons',
  'kirmizi_quickbuttons.py'
)

Write-Host "PyInstaller çalıştırılıyor..."
pyinstaller @args

Write-Host "Build tamamlandı. Dist klasörü: dist\kirmizi_quickbuttons"
