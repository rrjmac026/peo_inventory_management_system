@echo off
:: ══════════════════════════════════════════════════════════════════════════════
::  build.bat — One-click build script for Windows
::  Double-click this file OR run it in terminal to build StockMate.exe
:: ══════════════════════════════════════════════════════════════════════════════

echo.
echo  ==========================================
echo   StockMate — Building .exe with PyInstaller
echo  ==========================================
echo.

:: Step 1 — Make sure PyInstaller is installed
echo [1/3] Checking PyInstaller...
pip install pyinstaller customtkinter pillow --quiet
if %errorlevel% neq 0 (
    echo  ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)

:: Step 2 — Clean old build files
echo [2/3] Cleaning old build...
if exist "dist"  rmdir /s /q dist
if exist "build" rmdir /s /q build

:: Step 3 — Build the exe
echo [3/3] Building StockMate.exe...
pyinstaller stockmate.spec

if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Build failed. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   SUCCESS! Your app is ready:
echo   dist\StockMate.exe
echo  ==========================================
echo.
echo  Share the StockMate.exe file with anyone.
echo  No Python installation needed to run it!
echo.
pause