# Microsoft 365 Service Principal Setup for MCP Server

This guide will help you set up a Microsoft 365 service principal for the MCP server integration.

## Overview

The MCP server requires a service principal (app registration) in Azure AD to access Microsoft 365 APIs securely. This setup provides the necessary credentials for authentication.

## Prerequisites

- Azure AD tenant with administrative access
- Global Administrator or Application Administrator role
- Access to Azure portal (portal.azure.com)

## Step 1: Create App Registration

1. **Navigate to Azure Portal**
   - Go to [Azure Portal](https://portal.azure.com)
   - Sign in with your administrator account

2. **Access App Registrations**
   - Search for "App registrations" in the search bar
   - Click on "App registrations" service

3. **Create New Registration**
   - Click "New registration"
   - Fill in the following details:
     ```
     Name: M365 Security Toolkit MCP Server
     Supported account types: Accounts in this organizational directory only
     Redirect URI: Not required for this setup
     ```
   - Click "Register"

## Step 2: Get Application Details

After creating the app registration, you'll need three key values:

### Tenant ID
1. In the app registration overview page
2. Copy the "Directory (tenant) ID" value
3. This will be your `M365_TENANT_ID`

### Client ID
1. In the same overview page
2. Copy the "Application (client) ID" value
3. This will be your `M365_CLIENT_ID`

### Client Secret
1. Go to "Certificates & secrets" in the left menu
2. Click "New client secret"
3. Add description: "MCP Server Secret"
4. Set expiration (recommended: 24 months)
5. Click "Add"
6. **IMPORTANT**: Copy the secret value immediately (it won't be shown again)
7. This will be your `M365_CLIENT_SECRET`

## Step 3: Configure API Permissions

The MCP server needs specific permissions to access Microsoft 365 data:

1. **Go to API Permissions**
   - Click "API permissions" in the left menu
   - Click "Add a permission"

2. **Add Microsoft Graph Permissions**
   - Select "Microsoft Graph"
   - Choose "Application permissions"
   - Add the following permissions:
     ```
     Directory.Read.All
     Organization.Read.All
     Policy.Read.All
     User.Read.All
     SecurityEvents.Read.All
     AuditLog.Read.All
     Reports.Read.All
     ```

3. **Grant Admin Consent**
   - Click "Grant admin consent for [Your Organization]"
   - Click "Yes" to confirm
   - Ensure all permissions show "Granted" status

## Step 4: Configure Environment Variables

1. **Open your .env file**
   ```bash
   notepad .env
   ```

2. **Replace the placeholder values**
   ```env
   # Microsoft 365 Configuration
   M365_TENANT_ID=your-actual-tenant-id-here
   M365_CLIENT_ID=your-actual-client-id-here
   M365_CLIENT_SECRET=your-actual-client-secret-here
   ```

3. **Save the file**

## Step 5: Test the Connection

Run the MCP server test to verify your configuration:

```powershell
python setup_mcp_server.py --test-connection
```

If successful, you'll see:
```
✅ MCP Server Dependencies: Installed
✅ Environment Configuration: Valid
✅ Microsoft Graph Connection: Successful
✅ MCP Server: Ready for use
```

## Security Best Practices

### 🔒 **Credential Security**
- Never commit the `.env` file with real credentials to version control
- Store credentials securely (consider Azure Key Vault for production)
- Rotate client secrets regularly (every 12-24 months)

### 🛡️ **Access Control**
- Use least privilege principle
- Regularly review app permissions
- Monitor app usage in Azure AD logs

### 📋 **Compliance**
- Document app registration for compliance audits
- Include in your organization's app inventory
- Follow your organization's app governance policies

## Troubleshooting

### Common Issues

**Authentication Failed**
- Verify tenant ID, client ID, and client secret are correct
- Check that admin consent was granted for all permissions
- Ensure the service principal is not disabled

**Permission Denied**
- Verify all required API permissions are granted
- Check that admin consent was properly applied
- Confirm your account has sufficient privileges

**Connection Timeout**
- Check network connectivity
- Verify firewall settings allow Microsoft Graph API access
- Try again after a few minutes (temporary service issues)

### Getting Help

If you encounter issues:
1. Check the error messages in the MCP server logs
2. Verify permissions in Azure portal
3. Test with a simple Graph API call manually
4. Consult Microsoft Graph documentation

## Next Steps

Once your service principal is configured:

1. **Test MCP Integration**
   ```powershell
   python scripts/test_mcp_integration.py
   ```

2. **Run Security Audit**
   ```powershell
   python -m src.mcp.m365_security_server --audit
   ```

3. **Explore Available Tools**
   - User enumeration and analysis
   - Security policy assessment
   - Conditional access review
   - Audit log analysis

## Reference Links

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Microsoft Graph Permissions Reference](https://docs.microsoft.com/en-us/graph/permissions-reference)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

---

**Security Notice**: This service principal will have read access to your Microsoft 365 tenant data. Ensure proper security controls and monitoring are in place.