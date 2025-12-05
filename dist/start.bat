@echo off
chcp 65001 >nul

set "CUR_DIR=%~dp0"
set "EXE_PATH=%CUR_DIR%ks-server.exe"
set "PORT=1234"

echo Ждём 5 секунд перед запуском...
timeout /t 5 /nobreak >nul

REM ---- Запуск exe скрыто через PowerShell ----
powershell -WindowStyle Hidden -Command "Start-Process '%EXE_PATH%' -ArgumentList '--port %PORT%'"

REM ---- Создание задачи в планировщике ----
schtasks /create /tn "KsServer" /tr "\"%EXE_PATH%\" --port %PORT%" /sc onlogon /rl highest /f /it

echo Задача KsServer установлена и будет запускаться с портом %PORT%.
pause