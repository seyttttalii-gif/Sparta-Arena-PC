@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo       SPARTA ARENA - PC EDITION
echo ========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python bulunamadi.
  echo Windows icin Python 3.11 kur ve kurulumda Add Python to PATH secenegini isaretle.
  echo https://www.python.org/downloads/release/python-3119/
  pause
  exit /b 1
)
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Pygame kurulumu basarisiz oldu.
  pause
  exit /b 1
)
python main.py
if errorlevel 1 pause
