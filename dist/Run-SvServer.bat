@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "CUR_DIR=%~dp0"
set "EXE_PATH=%CUR_DIR%sv-server.exe"
set "CONFIG_PATH=%CUR_DIR%config.txt"

REM --- Проверка config.txt ---
if not exist "%CONFIG_PATH%" (
    echo Ошибка: config.txt не найден
    pause
    exit /b 1
)

REM --- Чтение PORT из config.txt ---
set "PORT="

for /f "usebackq tokens=1,2 delims==" %%A in ("%CONFIG_PATH%") do (
    if /I "%%A"=="PORT" set "PORT=%%B"
)

if "%PORT%"=="" (
    echo Ошибка: PORT не найден в config.txt
    pause
    exit /b 1
)

echo Используется порт: %PORT%
echo Ждём 5 секунд перед запуском...
timeout /t 5 /nobreak >nul

REM ---- Запуск exe скрыто через PowerShell ----
powershell -WindowStyle Hidden -Command ^
    "Start-Process '%EXE_PATH%' -ArgumentList '--port %PORT%'"

echo.
echo sv-server.exe запущен на порту %PORT%.
pause