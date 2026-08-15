# install.ps1 - VoxCPM2 Voice Cloner 自動安裝腳本
# 自動偵測加速裝置，安裝對應的 PyTorch + voxcpm
#
# 用法：Windows  .\install.ps1
#       macOS    pwsh -File install.ps1
#
# 裝置偵測邏輯：
#   NVIDIA (CUDA)      → pip install torch --index-url .../cu128
#   Apple Silicon      → pip install torch（PyPI 預設 wheel 已含 MPS，不可加 --index-url）
#   無獨顯 (CPU)       → pip install torch --index-url .../cpu

$ErrorActionPreference = 'Stop'

if ($null -eq $IsWindows) {
    throw '需要 PowerShell 7（pwsh）；5.1 沒有 $IsWindows，平台判斷會靜默走錯分支'
}

$venvName = '.venv'
if ($IsWindows) {
    $venvPython = Join-Path $venvName 'Scripts' 'python.exe'
    $venvPip    = Join-Path $venvName 'Scripts' 'pip.exe'
    $runPrefix  = '.\'
} else {
    $venvPython = Join-Path $venvName 'bin' 'python'
    $venvPip    = Join-Path $venvName 'bin' 'pip'
    $runPrefix  = './'
}

Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  VoxCPM2 Voice Cloner - Auto Installer' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# --- Step 1: 檢查 uv ---
Write-Host '[1/5] 檢查 uv 套件管理器...' -ForegroundColor Yellow
$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
    Write-Host '  uv 未安裝，正在安裝...' -ForegroundColor Yellow
    pip install -U uv
} else {
    Write-Host "  uv 已安裝: $($uv.Source)" -ForegroundColor Green
}

# --- Step 2: 建立 Python 3.12 venv ---
Write-Host '[2/5] 建立 Python 3.12 虛擬環境...' -ForegroundColor Yellow
if (Test-Path $venvPython) {
    Write-Host "  $venvName 已存在，跳過建立。" -ForegroundColor Green
} else {
    uv venv --python 3.12 $venvName
    Write-Host "  venv 建立完成: $venvName" -ForegroundColor Green
}

# --- Step 3: 偵測加速裝置 ---
Write-Host '[3/5] 偵測加速裝置...' -ForegroundColor Yellow
$gpuType = 'cpu'
$gpuName = ''

if ($IsWindows) {
    # Get-CimInstance Win32_VideoController 是 WMI，只有 Windows 有
    $videoControllers = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue
    foreach ($vc in $videoControllers) {
        if ($vc.Name -match 'NVIDIA') {
            $gpuType = 'cuda'
            $gpuName = $vc.Name
            break
        }
    }
} elseif ($IsMacOS) {
    # MPS 只有 Apple Silicon 有；Intel Mac 沒有，維持 cpu
    if ((uname -m) -eq 'arm64') {
        $gpuType = 'mps'
        $gpuName = 'Apple Silicon (Metal)'
    }
}

switch ($gpuType) {
    'cuda' {
        Write-Host "  偵測到 NVIDIA GPU: $gpuName" -ForegroundColor Green
        Write-Host '  → 安裝 CUDA 版 PyTorch' -ForegroundColor Green
        $torchIndex = 'https://download.pytorch.org/whl/cu128'
    }
    'mps' {
        Write-Host "  偵測到 $gpuName" -ForegroundColor Green
        Write-Host '  → 安裝預設版 PyTorch（macOS wheel 內含 MPS 支援）' -ForegroundColor Green
        $torchIndex = $null
    }
    default {
        Write-Host '  未偵測到加速裝置，使用 CPU 模式。' -ForegroundColor Yellow
        Write-Host '  → 安裝 CPU 版 PyTorch（推理會較慢）' -ForegroundColor Yellow
        $torchIndex = 'https://download.pytorch.org/whl/cpu'
    }
}

# --- Step 4: 安裝 PyTorch ---
Write-Host '[4/5] 安裝 PyTorch...' -ForegroundColor Yellow
if ($torchIndex) {
    uv pip install --python $venvPython torch --index-url $torchIndex
} else {
    # macOS 不指定 index：PyTorch 官方的 cpu/cu128 索引沒有 macOS wheel，
    # 指了反而裝不到含 MPS 的那份。
    uv pip install --python $venvPython torch
}
Write-Host "  PyTorch 安裝完成。" -ForegroundColor Green

# --- Step 5: 安裝 voxcpm + sounddevice + resampy ---
Write-Host '[5/5] 安裝 voxcpm + sounddevice + resampy...' -ForegroundColor Yellow
uv pip install --python $venvPython voxcpm sounddevice resampy
Write-Host "  voxcpm + sounddevice + resampy 安裝完成。" -ForegroundColor Green

# --- 驗證 ---
Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  安裝完成！' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '加速裝置: ' -NoNewline
switch ($gpuType) {
    'cuda'  { Write-Host 'NVIDIA CUDA' -ForegroundColor Green }
    'mps'   { Write-Host 'Apple Silicon MPS' -ForegroundColor Green }
    default { Write-Host 'CPU（較慢）' -ForegroundColor Yellow }
}
Write-Host ''
Write-Host '下一步：' -ForegroundColor Cyan
Write-Host "  1. 錄製參考音：$runPrefix$venvPython record.py"
Write-Host "  2. 生成語音：$runPrefix$venvPython clone.py `"你想說的文字`""
Write-Host ''

# 儲存裝置類型供其他腳本讀取
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '.gpu_type'), $gpuType)
