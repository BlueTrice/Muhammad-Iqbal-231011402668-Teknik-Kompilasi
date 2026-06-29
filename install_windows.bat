@echo off
setlocal

echo.
echo  ============================================
echo    JogLang Compiler v1.0.0 - Installer
echo    Basa Jawa Dialek Yogyakarta
echo  ============================================
echo.

:: Cek Python tersedia
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [GAGAL] Python tidak ditemukan.
    echo         Unduh Python 3.8+ dari https://python.org
    pause
    exit /b 1
)

:: Tampilkan versi Python
for /f "tokens=*" %%i in ('python --version') do echo [INFO] %%i

:: Cek pip tersedia (lewat python -m pip, lebih konsisten di Windows
:: daripada memanggil 'pip' langsung karena tidak selalu ada di PATH)
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [GAGAL] pip tidak ditemukan.
    echo         Jalankan: python -m ensurepip
    pause
    exit /b 1
)

echo.
echo [INFO] Menginstall JogLang Compiler...
echo.

python -m pip install .
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [GAGAL] Instalasi gagal. Coba jalankan sebagai Administrator.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo    [OK] JogLang Compiler berhasil diinstall!
echo  ============================================
echo.
echo  Cara penggunaan:
echo    joglang examples\01_halo_dunia.jog
echo    joglang examples\01_halo_dunia.jog --run
echo    joglang --help
echo.
echo  Atau tanpa instalasi (jalankan dari source):
echo    python -m joglang_compiler examples\01_halo_dunia.jog
echo    python main.py examples\01_halo_dunia.jog
echo.

pause
endlocal
