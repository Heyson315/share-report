<#
PostRemediateM365CIS.ps1

Minimal post-remediation helper for CIS M365 L1 controls referenced in audit:
- EXO-2: Disable external auto-forwarding (TransportConfig, HOSFP)
- EXO-4: Disable legacy protocols per mailbox (sample flagged)
- DEF-1: Ensure Safe Links rule is enabled (prefer enabling built-in rule if present)
- SPO-1: Restrict SharePoint external sharing (Tenant level)

Run in an elevated PowerShell session with Exchange/Graph/SPO permissions.
#>

param(
  [string]$SPOAdminUrl = "https://rahmanfinanceandaccounting-admin.sharepoint.com",
  [ValidateSet('Disabled','ExistingExternalUserSharingOnly','ExternalUserSharingOnly','AnonymousLinkSharing')]
  [string]$SharingCapability = 'ExistingExternalUserSharingOnly'
)

Write-Host "[+] Loading modules and connecting..." -ForegroundColor Cyan
try {
  Import-Module ExchangeOnlineManagement -ErrorAction Stop
  Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop | Out-Null
  Write-Host "[+] Connected to Exchange Online" -ForegroundColor Green
} catch {
  Write-Warning "Exchange connection failed: $($_.Exception.Message)"
}

# --- EXO-2: External auto-forwarding off ---
Write-Host "[+] Enforcing EXO-2: External auto-forwarding disabled" -ForegroundColor Cyan
try {
  Set-TransportConfig -ExternalClientForwardingDisabled $true -ErrorAction Stop
  Write-Host "    Set-TransportConfig ExternalClientForwardingDisabled=True" -ForegroundColor Green
} catch { Write-Warning "    Set-TransportConfig failed: $($_.Exception.Message)" }

try {
  # Hosted Outbound Spam Filter Policy (modern control)
  Set-HostedOutboundSpamFilterPolicy -Identity "Default" -AutoForwardingMode Off -ErrorAction Stop
  Write-Host "    Set-HostedOutboundSpamFilterPolicy Default AutoForwardingMode=Off" -ForegroundColor Green
} catch { Write-Warning "    Set-HostedOutboundSpamFilterPolicy failed: $($_.Exception.Message)" }

# --- EXO-4: Disable legacy POP/IMAP/MAPI on flagged mailboxes ---
Write-Host "[+] Enforcing EXO-4: Disable legacy protocols on flagged mailboxes" -ForegroundColor Cyan
$flagged = @(
  'Discovery Search Mailbox',
  'Hassan Rahman'
)
foreach ($mbx in $flagged) {
  try {
    Set-CASMailbox -Identity $mbx -PopEnabled:$false -ImapEnabled:$false -MAPIEnabled:$false -ErrorAction Stop
    Write-Host "    Legacy protocols disabled for '$mbx'" -ForegroundColor Green
  } catch { Write-Warning "    Set-CASMailbox failed for '$mbx': $($_.Exception.Message)" }
}

# --- DEF-1: Ensure Safe Links has an enabled rule ---
Write-Host "[+] Enforcing DEF-1: Ensure Safe Links rule enabled" -ForegroundColor Cyan
try {
  $slRule = Get-SafeLinksRule -Identity "Built-In Protection Rule" -ErrorAction SilentlyContinue
  if ($slRule) {
    try { Enable-SafeLinksRule -Identity $slRule.Name -ErrorAction Stop; Write-Host "    Enabled Safe Links rule: $($slRule.Name)" -ForegroundColor Green } catch { Write-Warning $_ }
  } else {
    # Fallback: attempt to enable any existing disabled rule
    $anyRule = Get-SafeLinksRule | Where-Object { $_.State -ne 'Enabled' -and $_.Enabled -ne $true } | Select-Object -First 1
    if ($anyRule) {
      try { Enable-SafeLinksRule -Identity $anyRule.Name -ErrorAction Stop; Write-Host "    Enabled Safe Links rule: $($anyRule.Name)" -ForegroundColor Green } catch { Write-Warning $_ }
    } else {
      Write-Warning "    No Safe Links rule found to enable. Consider creating a policy+rule in the Defender portal."
    }
  }
} catch {
  Write-Warning "    Safe Links remediation skipped: $($_.Exception.Message)"
}

# --- SPO-1: Restrict SharePoint external sharing ---
Write-Host "[+] Enforcing SPO-1: Restrict SharePoint tenant sharing" -ForegroundColor Cyan
try {
  if ($SPOAdminUrl) {
    if (Get-Module -ListAvailable Microsoft.Online.SharePoint.PowerShell) {
      Import-Module Microsoft.Online.SharePoint.PowerShell -ErrorAction Stop
      Connect-SPOService -Url $SPOAdminUrl -ErrorAction Stop
      Set-SPOTenant -SharingCapability $SharingCapability -ErrorAction Stop
      Write-Host "    Set-SPOTenant SharingCapability=$SharingCapability" -ForegroundColor Green
    } else {
      Write-Warning "    Microsoft.Online.SharePoint.PowerShell not installed. Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser"
    }
  }
} catch {
  Write-Warning "    SPO remediation skipped: $($_.Exception.Message)"
}

Write-Host "[+] Post-remediation steps attempted. Re-run the audit sc
ript to validate results." -ForegroundColor Cyan
