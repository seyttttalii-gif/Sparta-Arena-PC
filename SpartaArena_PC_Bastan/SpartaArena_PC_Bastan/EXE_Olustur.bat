@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo    SPARTA ARENA - EXE OLUSTURUCU
echo ========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python bulunamadi. Once Python 3.11 kur ve Add Python to PATH secenegini isaretle.
  pause
  exit /b 1
)
python -m pip install --upgrade pip
if errorlevel 1 goto fail
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto fail
python -m PyInstaller --noconfirm --clean --onedir --windowed --name SpartaArena --collect-all pygame main.py
if errorlevel 1 goto fail
echo.
echo EXE hazir: dist\SpartaArena\SpartaArena.exe
echo Bu klasorun tamamini birlikte tasiman gerekir.
pause
exit /b 0
:fail
echo Derleme basarisiz oldu. Yukaridaki hata mesajini kaydet.
pause
exit /b 1
