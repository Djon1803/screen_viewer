Write-Host "Остановка процесса sv-server.exe..."

# Попытка завершить процесс
taskkill.exe /im sv-server.exe /f 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Процесс sv-server.exe остановлен."
} else {
    Write-Host "Процесс sv-server.exe не найден."
}

Write-Host "Готово."
pause