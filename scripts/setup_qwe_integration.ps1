#!/usr/bin/env powershell
<#
.SYNOPSIS
    Quick Setup Script for Easy-Ai + qwe Integration

.DESCRIPTION
    Automates the integration of Easy-Ai Security Toolkit with qwe website.
    Copies files, updates configuration, and starts services.

.EXAMPLE
    .\setup_qwe_integration.ps1
    .\setup_qwe_integration.ps1 -QwePath "E:\source\Heyson315\qwe"
#>

param(
    [string]$QwePath = "E:\source\Heyson315\qwe",
    [string]$EasyAiPath = "E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai",
    [switch]$SkipFileCopy,
    [switch]$StartMcpServer
)

$ErrorActionPreference = "Stop"

Write-Host "🔗 Easy-Ai + qwe Integration Setup" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Verify paths
Write-Host "📍 Verifying paths..."
if (-not (Test-Path $QwePath)) {
    Write-Error "qwe repository not found at: $QwePath"
    exit 1
}
if (-not (Test-Path $EasyAiPath)) {
    Write-Error "Easy-Ai repository not found at: $EasyAiPath"
    exit 1
}
Write-Host "   ✅ Paths verified" -ForegroundColor Green
Write-Host ""

# Define source and target paths
$integrationPath = Join-Path $EasyAiPath "qwe_integration"
$qweServicesPath = Join-Path $QwePath "qwe\Services"
$qweControllersPath = Join-Path $QwePath "qwe\Controllers"
$qweViewsPath = Join-Path $QwePath "qwe\Views\AdminSecurity"

# Create directories if they don't exist
if (-not (Test-Path $qweServicesPath)) {
    New-Item -Path $qweServicesPath -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path $qweViewsPath)) {
    New-Item -Path $qweViewsPath -ItemType Directory -Force | Out-Null
}

# Copy integration files
if (-not $SkipFileCopy) {
    Write-Host "📁 Copying integration files..."
    
    # Copy service class
    $sourceService = Join-Path $integrationPath "EasyAiSecurityService.cs"
    $targetService = Join-Path $qweServicesPath "EasyAiSecurityService.cs"
    if (Test-Path $sourceService) {
        Copy-Item $sourceService $targetService -Force
        Write-Host "   ✅ Service class copied" -ForegroundColor Green
    } else {
        Write-Warning "   ⚠️  Service class not found, skipping"
    }
    
    # Copy controller
    $sourceController = Join-Path $integrationPath "AdminSecurityController.cs"
    $targetController = Join-Path $qweControllersPath "AdminSecurityController.cs"
    if (Test-Path $sourceController) {
        Copy-Item $sourceController $targetController -Force
        Write-Host "   ✅ Controller copied" -ForegroundColor Green
    } else {
        Write-Warning "   ⚠️  Controller not found, skipping"
    }
    
    # Copy view
    $sourceView = Join-Path $integrationPath "Views\Dashboard.cshtml"
    $targetView = Join-Path $qweViewsPath "Dashboard.cshtml"
    if (Test-Path $sourceView) {
        Copy-Item $sourceView $targetView -Force
        Write-Host "   ✅ View copied" -ForegroundColor Green
    } else {
        Write-Warning "   ⚠️  View not found, skipping"
    }
    
    Write-Host ""
}

# Update Web.config
Write-Host "⚙️  Configuration..."
$webConfigPath = Join-Path $QwePath "qwe\Web.config"
if (Test-Path $webConfigPath) {
    $webConfig = [xml](Get-Content $webConfigPath)
    $appSettings = $webConfig.configuration.appSettings
    
    # Check if EasyAi settings exist
    $easyAiSettings = $appSettings.add | Where-Object { $_.key -like "EasyAi:*" }
    if (-not $easyAiSettings) {
        Write-Host "   ℹ️  Adding EasyAi settings to Web.config" -ForegroundColor Yellow
        Write-Host "   ℹ️  Please add these settings to your Web.config manually:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   <add key=`"EasyAi:McpServerUrl`" value=`"http://localhost:8080`" />"
        Write-Host "   <add key=`"EasyAi:Enabled`" value=`"true`" />"
        Write-Host ""
    } else {
        Write-Host "   ✅ EasyAi settings already exist" -ForegroundColor Green
    }
} else {
    Write-Warning "   ⚠️  Web.config not found, skipping configuration update"
}
Write-Host ""

# Check NuGet packages
Write-Host "📦 NuGet Packages..."
$packagesConfig = Join-Path $QwePath "qwe\packages.config"
if (Test-Path $packagesConfig) {
    $packages = [xml](Get-Content $packagesConfig)
    $hasNewtonsoft = $packages.packages.package | Where-Object { $_.id -eq "Newtonsoft.Json" }
    $hasWebApi = $packages.packages.package | Where-Object { $_.id -eq "Microsoft.AspNet.WebApi.Client" }
    
    if (-not $hasNewtonsoft) {
        Write-Host "   ⚠️  Missing: Newtonsoft.Json" -ForegroundColor Yellow
        Write-Host "      Run: Install-Package Newtonsoft.Json" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ Newtonsoft.Json installed" -ForegroundColor Green
    }
    
    if (-not $hasWebApi) {
        Write-Host "   ⚠️  Missing: Microsoft.AspNet.WebApi.Client" -ForegroundColor Yellow
        Write-Host "      Run: Install-Package Microsoft.AspNet.WebApi.Client" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ WebApi.Client installed" -ForegroundColor Green
    }
} else {
    Write-Warning "   ⚠️  packages.config not found, cannot verify NuGet packages"
}
Write-Host ""

# Start MCP server if requested
if ($StartMcpServer) {
    Write-Host "🚀 Starting Easy-Ai MCP Server..."
    $mcpScript = Join-Path $EasyAiPath "scripts\start_mcp_for_qwe.py"
    if (Test-Path $mcpScript) {
        Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $mcpScript, "--allow-cors"
        Write-Host "   ✅ MCP Server starting in new window" -ForegroundColor Green
        Write-Host "   📍 Server URL: http://localhost:8080" -ForegroundColor Cyan
    } else {
        Write-Warning "   ⚠️  MCP startup script not found"
    }
    Write-Host ""
}

# Summary
Write-Host "=" * 60
Write-Host "✅ Integration setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Build qwe project in Visual Studio"
Write-Host "2. Start MCP server: python scripts/start_mcp_for_qwe.py --allow-cors"
Write-Host "3. Run qwe website"
Write-Host "4. Navigate to: http://localhost:PORT/Admin/Security/Dashboard"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Integration Guide: $integrationPath\INTEGRATION_GUIDE.md"
Write-Host "  - MCP Server Status: python scripts/check_mcp_status.py"
Write-Host ""
Write-Host "=" * 60
