@echo off
chcp 65001 >nul

REM ---- Закрываем exe, если запущен ----
taskkill /im sv-server.exe /f 2>nul

if %ERRORLEVEL%==0 (
    echo Процесс sv-server.exe остановлен.
) else (
    echo Процесс sv-server.exe не найден.
)

pause