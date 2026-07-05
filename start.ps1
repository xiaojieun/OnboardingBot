param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$Stop
)

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendPort = 8000
$FrontendPort = 5173

function Write-Header {
    param([string]$Text)
    $line = "=" * 50
    Write-Host $line -ForegroundColor DarkGray
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor DarkGray
}

function Stop-Services {
    Write-Header "正在停止服务..."

    $backendProc = Get-Process -Name python -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "uvicorn" }
    $frontendProc = Get-Process -Name node -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "vite" }

    if ($backendProc) {
        $backendProc | Stop-Process -Force
        Write-Host "[后端] 已停止 (PID: $($backendProc.Id -join ', '))" -ForegroundColor Yellow
    } else {
        Write-Host "[后端] 未运行" -ForegroundColor DarkGray
    }

    if ($frontendProc) {
        $frontendProc | Stop-Process -Force
        Write-Host "[前端] 已停止 (PID: $($frontendProc.Id -join ', '))" -ForegroundColor Yellow
    } else {
        Write-Host "[前端] 未运行" -ForegroundColor DarkGray
    }

    Write-Host ""
}

function Test-BackendReady {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-Backend {
    Write-Header "启动后端服务 (FastAPI)"

    $existingProc = Get-Process -Name python -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "uvicorn" }
    if ($existingProc) {
        Write-Host "[后端] 已在运行 (PID: $($existingProc.Id))，跳过" -ForegroundColor Yellow
        return
    }

    if (-not (Test-Path "$BackendDir\src\api\main.py")) {
        Write-Host "[错误] 未找到 backend/src/api/main.py，请确认目录结构" -ForegroundColor Red
        return
    }

    $VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    $PythonExe = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

    $env:PYTHONPATH = $BackendDir
    Start-Process -FilePath $PythonExe `
        -ArgumentList "-m", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", $BackendPort `
        -WorkingDirectory $BackendDir `
        -WindowStyle Minimized

    Write-Host "[后端] 启动中... http://localhost:$BackendPort" -ForegroundColor Green
    Write-Host "[后端] Swagger 文档  : http://localhost:$BackendPort/docs" -ForegroundColor DarkCyan
    Write-Host "[后端] ReDoc 文档    : http://localhost:$BackendPort/redoc" -ForegroundColor DarkCyan
}

function Start-Frontend {
    Write-Header "启动前端服务 (Vite)"

    $existingProc = Get-Process -Name node -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match "vite" }
    if ($existingProc) {
        Write-Host "[前端] 已在运行 (PID: $($existingProc.Id))，跳过" -ForegroundColor Yellow
        return
    }

    if (-not (Test-Path "$FrontendDir\node_modules")) {
        Write-Host "[前端] 首次运行，正在安装依赖..." -ForegroundColor Yellow
        Push-Location $FrontendDir
        npm install
        Pop-Location
    }

    Start-Process -FilePath "npm" `
        -ArgumentList "run", "dev" `
        -WorkingDirectory $FrontendDir `
        -WindowStyle Minimized

    Write-Host "[前端] 启动中... http://localhost:$FrontendPort" -ForegroundColor Green
}

# ============================================================
# 主逻辑
# ============================================================

# 停止模式
if ($Stop) {
    Stop-Services
    exit 0
}

Write-Host ""
Write-Host "  入职智引系统 - 快速启动" -ForegroundColor White
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host ""

# 仅停止
if ($BackendOnly -or $FrontendOnly) {
    # 不做额外处理
} else {
    Stop-Services
}

# 启动服务
if (-not $FrontendOnly) {
    Start-Backend
    Write-Host ""
}

if (-not $BackendOnly) {
    Start-Frontend
    Write-Host ""
}

# 状态汇总
Write-Header "服务状态"
Start-Sleep -Seconds 2

$backendOk = Test-BackendReady
$frontendProc = Get-Process -Name node -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "vite" }

if ($backendOk) {
    Write-Host "[后端] 运行中 - http://localhost:$BackendPort" -ForegroundColor Green
} else {
    Write-Host "[后端] 启动中，请稍候访问 http://localhost:$BackendPort" -ForegroundColor Yellow
}

if ($frontendProc) {
    Write-Host "[前端] 运行中 - http://localhost:$FrontendPort" -ForegroundColor Green
} else {
    Write-Host "[前端] 未检测到进程" -ForegroundColor Red
}

Write-Host ""
Write-Host "快捷操作:" -ForegroundColor DarkGray
Write-Host "  .\start.ps1 -Stop          停止所有服务" -ForegroundColor DarkGray
Write-Host "  .\start.ps1 -BackendOnly   仅启动后端" -ForegroundColor DarkGray
Write-Host "  .\start.ps1 -FrontendOnly  仅启动前端" -ForegroundColor DarkGray
Write-Host ""
