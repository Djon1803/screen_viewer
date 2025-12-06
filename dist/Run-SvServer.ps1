# Start sv-server.exe hidden, verify via GET /monitors, then show local and public URLs.

$exePath   = Join-Path $PSScriptRoot "sv-server.exe"
$configPath = Join-Path $PSScriptRoot "config.txt"

if (-not (Test-Path $configPath)) {
    Write-Host "Ошибка: config.txt не найден"
    exit 1
}

# Чтение порта из config.txt
$portLine = Get-Content $configPath | Where-Object { $_ -match '^PORT=' }
if (-not $portLine) {
    Write-Host "Ошибка: PORT не найден в config.txt"
    exit 1
}

$port = ($portLine -split '=')[1].Trim()
$baseUrl = "http://127.0.0.1:$port"

Write-Host "Запуск sv-server на порту $port..."
Start-Process -FilePath $exePath -ArgumentList "--port $port" -WindowStyle Hidden

Start-Sleep -Seconds 3

# Проверка запуска
try {
    $monitorUrl = "$baseUrl/monitors"
    Invoke-WebRequest -Uri $monitorUrl -TimeoutSec 3 | Out-Null
    Write-Host "Сервер успешно запущен!"
}
catch {
    Write-Host "Ошибка: сервер не отвечает на /monitors"
    exit 1
}

# Получение всех локальных IPv4
$localIPs = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike "169.*" -and $_.IPAddress -ne "127.0.0.1" } |
    Select-Object -ExpandProperty IPAddress

# Получение внешнего IP
try {
    $globalIP = Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 3
}
catch {
    $globalIP = "Не удалось получить внешний IP"
}

Write-Host "--- Доступ к серверу ---"

foreach ($ip in $localIPs) {
    Write-Host "Локальный: http://${ip}:$port/"
}

Write-Host "Localhost: http://127.0.0.1:$port/"
Write-Host "Глобальный: http://${globalIP}:$port/"
pause