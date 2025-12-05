@echo off
REM Получаем путь к текущей папке
set "CUR_DIR=%~dp0"
set "EXE_PATH=%CUR_DIR%ks-server.exe"

REM ---- Ждём 15 секунд перед запуском ----
echo Ждём 15 секунд перед запуском...
timeout /t 15 /nobreak >nul

REM ---- Запуск exe скрыто через PowerShell ----
powershell -WindowStyle Hidden -Command "Start-Process '%EXE_PATH%'"

REM ---- Создание задачи в планировщике для будущих логинов ----
schtasks /create /tn "KsServer" /tr "%EXE_PATH%" /sc onlogon /rl highest /f /it

echo Задача KsServer установлена и запущена скрыто с задержкой.
pause