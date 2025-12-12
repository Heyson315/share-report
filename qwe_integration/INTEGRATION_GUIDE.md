# 🔗 Easy-Ai + qwe Integration Guide

Complete guide for integrating the Easy-Ai M365 Security Toolkit with the HHR CPA website (qwe).

## Overview

This integration connects your public-facing CPA website (`qwe`) with the Easy-Ai security monitoring system, providing real-time security dashboards, compliance status, and alert management in the admin portal.

---

## Architecture

```
qwe Website (ASP.NET)  ←→  Easy-Ai MCP Server (Python)  ←→  M365 Services
     ↓                           ↓                              ↓
Admin Dashboard            Security Analysis              Audit Data
Documents System           Alert Management               Compliance
Client Portal              SharePoint Analysis            Reports
```

---

## Installation Steps

### Step 1: Start Easy-Ai MCP Server

```powershell
# From Easy-Ai repository
cd E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai

# Start MCP server with CORS enabled for qwe
python scripts/start_mcp_for_qwe.py --host localhost --port 8080 --allow-cors

# Server will be available at: http://localhost:8080
```

**Verify server is running:**
```powershell
# Check server health
python scripts/check_mcp_status.py
```

---

### Step 2: Add Integration Files to qwe

1. **Copy service class:**
   ```powershell
   # Copy to qwe project
   Copy-Item "qwe_integration\EasyAiSecurityService.cs" "E:\source\Heyson315\qwe\qwe\Services\"
   ```

2. **Copy controller:**
   ```powershell
   Copy-Item "qwe_integration\AdminSecurityController.cs" "E:\source\Heyson315\qwe\qwe\Controllers\"
   ```

3. **Copy view:**
   ```powershell
   Copy-Item "qwe_integration\Views\Dashboard.cshtml" "E:\source\Heyson315\qwe\qwe\Views\AdminSecurity\"
   ```

---

### Step 3: Update qwe Configuration

Add these settings to `qwe/Web.config`:

```xml
<appSettings>
  <!-- Easy-Ai Security Integration -->
  <add key="EasyAi:McpServerUrl" value="http://localhost:8080" />
  <add key="EasyAi:Enabled" value="true" />
  <add key="EasyAi:DashboardRefreshInterval" value="300000" />
  <add key="EasyAi:ServiceTimeout" value="30" />
</appSettings>
```

---

### Step 4: Install NuGet Packages

```powershell
cd "E:\source\Heyson315\qwe\qwe"

# Install required packages
Install-Package Newtonsoft.Json
Install-Package Microsoft.AspNet.WebApi.Client
```

---

### Step 5: Update Routing

Add to `qwe/App_Start/RouteConfig.cs`:

```csharp
routes.MapRoute(
    name: "AdminSecurity",
    url: "Admin/Security/{action}/{id}",
    defaults: new { 
        controller = "AdminSecurity", 
        action = "Dashboard", 
        id = UrlParameter.Optional 
    }
);
```

---

### Step 6: Add Navigation Link

Add to admin navigation menu in `_AdminLayout.cshtml`:

```html
<li class="nav-item">
    <a class="nav-link" href="@Url.Action("Dashboard", "AdminSecurity")">
        <i class="fa fa-shield"></i> Security Dashboard
    </a>
</li>
```

---

## Usage

### Access Security Dashboard

1. **Login to qwe as administrator**
2. **Navigate to:** `http://localhost:port/Admin/Security/Dashboard`
3. **View security metrics:**
   - Total active alerts
   - Critical/High priority issues
   - M365 compliance score
   - SharePoint analysis
   - Recent security activities

### Run Manual Audit

1. **Click "Run Audit Now" button**
2. **Wait for audit completion** (5-10 minutes)
3. **Dashboard auto-refreshes** with new data

### View Detailed Alerts

1. **Navigate to Alerts page**
2. **Filter by severity/source**
3. **View remediation recommendations**

---

## API Endpoints

### Easy-Ai MCP Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/security/dashboard` | GET | Dashboard summary |
| `/api/security/alerts` | GET | Active alerts |
| `/api/security/compliance` | GET | M365 compliance status |
| `/api/security/sharepoint` | GET | SharePoint analysis |
| `/api/security/audit` | POST | Trigger new audit |

### qwe Website Routes

| Route | Description |
|-------|-------------|
| `/Admin/Security/Dashboard` | Security dashboard |
| `/Admin/Security/Alerts` | Alerts list |
| `/Admin/Security/Compliance` | Compliance report |
| `/Admin/Security/SharePoint` | SharePoint analysis |
| `/Admin/Security/RunAudit` | Trigger audit (POST) |

---

## Configuration Options

### App Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `EasyAi:McpServerUrl` | `http://localhost:8080` | MCP server URL |
| `EasyAi:Enabled` | `true` | Enable/disable integration |
| `EasyAi:DashboardRefreshInterval` | `300000` | Auto-refresh interval (ms) |
| `EasyAi:ServiceTimeout` | `30` | Service timeout (seconds) |
| `EasyAi:EnableCors` | `false` | Enable CORS |
| `EasyAi:CacheDuration` | `5` | Cache duration (minutes) |

---

## Troubleshooting

### Issue: "Security service is currently unavailable"

**Solution:**
```powershell
# Check if MCP server is running
python scripts/check_mcp_status.py

# If not running, start it
python scripts/start_mcp_for_qwe.py --allow-cors
```

### Issue: "Connection refused" or timeout

**Solutions:**
1. **Check firewall:** Ensure port 8080 is not blocked
2. **Check server URL:** Verify `EasyAi:McpServerUrl` in Web.config
3. **Check CORS:** Enable CORS if needed (`--allow-cors`)

### Issue: Dashboard shows no data

**Solutions:**
1. **Run initial audit:** Click "Run Audit Now"
2. **Wait for completion:** First audit takes 5-10 minutes
3. **Check MCP logs:** View server logs for errors

---

## Security Considerations

### Authentication

- ✅ Dashboard requires `[Authorize(Roles = "Admin")]`
- ✅ API calls are server-to-server (internal only)
- ✅ No sensitive data exposed to client-side JavaScript

### Network Security

- ✅ MCP server runs on localhost (not exposed externally)
- ✅ Use HTTPS for production deployments
- ✅ Implement API key authentication for production

### Data Privacy

- ✅ Security alerts contain no PII
- ✅ Audit logs are stored securely
- ✅ Dashboard data is cached server-side only

---

## Production Deployment

### Recommended Architecture

```
Production Setup:
1. qwe Website: IIS on web server
2. Easy-Ai MCP Server: Windows Service on app server
3. SQL Server: Database server (optional)

Network:
- qwe → Easy-Ai: Internal network only
- Easy-Ai → M365: HTTPS to Microsoft services
- Users → qwe: HTTPS (public)
```

### Deploy MCP Server as Windows Service

```powershell
# Create Windows Service
New-Service -Name "EasyAi-MCP" `
    -BinaryPathName "pythonw.exe E:\...\start_mcp_for_qwe.py" `
    -DisplayName "Easy-Ai MCP Server" `
    -StartupType Automatic

# Start service
Start-Service "EasyAi-MCP"
```

### Production Web.config

```xml
<appSettings>
  <add key="EasyAi:McpServerUrl" value="http://internal-app-server:8080" />
  <add key="EasyAi:Enabled" value="true" />
  <add key="EasyAi:ServiceTimeout" value="60" />
  <add key="EasyAi:CacheDuration" value="10" />
</appSettings>
```

---

## Testing

### Unit Tests

```csharp
[TestClass]
public class EasyAiSecurityServiceTests
{
    [TestMethod]
    public async Task GetSecurityDashboard_ReturnsData()
    {
        var service = new EasyAiSecurityService();
        var dashboard = await service.GetSecurityDashboardAsync();
        Assert.IsNotNull(dashboard);
    }
}
```

### Integration Test

```powershell
# Test full integration
cd "E:\source\Heyson315\Easy-Ai"

# Start MCP server
Start-Process powershell -ArgumentList "python scripts/start_mcp_for_qwe.py"

# Wait for server to start
Start-Sleep -Seconds 5

# Test API
Invoke-RestMethod -Uri "http://localhost:8080/health"

# Open qwe dashboard
Start-Process "http://localhost:YOUR_QWE_PORT/Admin/Security/Dashboard"
```

---

## Monitoring & Maintenance

### Health Checks

```powershell
# Daily health check script
$mcpHealth = Invoke-RestMethod "http://localhost:8080/health"
if ($mcpHealth.status -ne "healthy") {
    Send-MailMessage -To "admin@hhrcpa.com" -Subject "MCP Server Down" -Body "..."
}
```

### Log Monitoring

```powershell
# View MCP server logs
Get-Content "logs/mcp_server.log" -Tail 50 -Wait
```

### Performance Monitoring

- Monitor dashboard load times
- Track API response times
- Monitor audit completion times
- Alert on service timeouts

---

## Benefits

### For Administrators
- ✅ **Real-time visibility** into M365 security posture
- ✅ **Centralized dashboard** for all security metrics
- ✅ **Automated alerts** for critical issues
- ✅ **One-click audits** from admin panel

### For Security
- ✅ **Continuous monitoring** of M365 environment
- ✅ **Compliance tracking** (CIS controls)
- ✅ **SharePoint permissions** analysis
- ✅ **Audit trail** for all security events

### For Operations
- ✅ **Reduced manual work** (automated audits)
- ✅ **Faster incident response** (real-time alerts)
- ✅ **Better reporting** (visual dashboards)
- ✅ **Integrated workflow** (all in qwe admin)

---

## Next Steps

1. ✅ **Test integration** in development environment
2. ✅ **Review security dashboard**
3. ✅ **Run initial audit**
4. ✅ **Configure alert thresholds**
5. ✅ **Plan production deployment**
6. ✅ **Train administrators** on new features
7. ✅ **Set up monitoring** and alerts

---

## Support

### Documentation
- **Easy-Ai Docs:** `E:\source\Heyson315\Easy-Ai\README.md`
- **qwe Docs:** `E:\source\Heyson315\qwe\README.md`
- **MCP API Docs:** `http://localhost:8080/docs`

### Troubleshooting
- **Check MCP status:** `python scripts/check_mcp_status.py`
- **View logs:** Check `logs/mcp_server.log`
- **Test API:** Use Postman or curl to test endpoints

---

**Integration Version:** 1.0.0  
**Last Updated:** 2025-12-11  
**Maintained By:** HHR CPA IT Team
