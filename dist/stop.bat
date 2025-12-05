@echo off
chcp 65001 >nul

REM ---- Убираем задачу из планировщика ----
schtasks /delete /tn "KsServer" /f

REM ---- Закрываем exe, если запущен ----
taskkill /im ks-server.exe /f

echo Задача KsServer удалена и процесс остановлен.
pause