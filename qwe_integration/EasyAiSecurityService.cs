using System;
using System.Configuration;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace qwe.Services
{
    /// <summary>
    /// Service for integrating with Easy-Ai Security Toolkit MCP Server
    /// 
    /// Provides security dashboard data, compliance status, and alert information
    /// from the Easy-Ai M365 security auditing system.
    /// 
    /// Usage:
    ///     var securityService = new EasyAiSecurityService();
    ///     var dashboard = await securityService.GetSecurityDashboardAsync();
    ///     var alerts = await securityService.GetActiveAlertsAsync();
    /// </summary>
    public class EasyAiSecurityService
    {
        private readonly HttpClient _httpClient;
        private readonly string _mcpServerUrl;

        /// <summary>
        /// Initialize the security service
        /// </summary>
        public EasyAiSecurityService()
        {
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };

            // Read MCP server URL from configuration
            _mcpServerUrl = ConfigurationManager.AppSettings["EasyAi:McpServerUrl"] 
                ?? "http://localhost:8080";

            _httpClient.BaseAddress = new Uri(_mcpServerUrl);
            _httpClient.DefaultRequestHeaders.Accept.Clear();
            _httpClient.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        /// <summary>
        /// Check if MCP server is available
        /// </summary>
        public async Task<bool> IsServerHealthyAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/health");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Get security dashboard summary
        /// </summary>
        public async Task<SecurityDashboard> GetSecurityDashboardAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/security/dashboard");
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<SecurityDashboard>(json);
            }
            catch (Exception ex)
            {
                throw new SecurityServiceException("Failed to retrieve security dashboard", ex);
            }
        }

        /// <summary>
        /// Get active security alerts
        /// </summary>
        public async Task<SecurityAlerts> GetActiveAlertsAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/security/alerts");
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<SecurityAlerts>(json);
            }
            catch (Exception ex)
            {
                throw new SecurityServiceException("Failed to retrieve security alerts", ex);
            }
        }

        /// <summary>
        /// Get M365 CIS compliance status
        /// </summary>
        public async Task<ComplianceStatus> GetComplianceStatusAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/security/compliance");
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<ComplianceStatus>(json);
            }
            catch (Exception ex)
            {
                throw new SecurityServiceException("Failed to retrieve compliance status", ex);
            }
        }

        /// <summary>
        /// Get SharePoint permissions analysis
        /// </summary>
        public async Task<SharePointAnalysis> GetSharePointAnalysisAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/security/sharepoint");
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<SharePointAnalysis>(json);
            }
            catch (Exception ex)
            {
                throw new SecurityServiceException("Failed to retrieve SharePoint analysis", ex);
            }
        }

        /// <summary>
        /// Trigger a new security audit
        /// </summary>
        public async Task<AuditResult> TriggerSecurityAuditAsync()
        {
            try
            {
                var response = await _httpClient.PostAsync("/api/security/audit", null);
                response.EnsureSuccessStatusCode();

                var json = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<AuditResult>(json);
            }
            catch (Exception ex)
            {
                throw new SecurityServiceException("Failed to trigger security audit", ex);
            }
        }
    }

    #region Data Models

    public class SecurityDashboard
    {
        public string Status { get; set; }
        public int TotalAlerts { get; set; }
        public int CriticalAlerts { get; set; }
        public int HighAlerts { get; set; }
        public int MediumAlerts { get; set; }
        public int LowAlerts { get; set; }
        public double ComplianceScore { get; set; }
        public DateTime LastUpdated { get; set; }
        public string[] RecentActivities { get; set; }
    }

    public class SecurityAlerts
    {
        public int TotalCount { get; set; }
        public Alert[] Alerts { get; set; }
    }

    public class Alert
    {
        public string Id { get; set; }
        public string Source { get; set; }
        public string Severity { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class ComplianceStatus
    {
        public double Score { get; set; }
        public int TotalControls { get; set; }
        public int PassedControls { get; set; }
        public int FailedControls { get; set; }
        public int ManualControls { get; set; }
        public string Trend { get; set; }
        public DateTime LastAudit { get; set; }
    }

    public class SharePointAnalysis
    {
        public int TotalSites { get; set; }
        public int TotalUsers { get; set; }
        public int PermissionIssues { get; set; }
        public string[] RiskyPermissions { get; set; }
        public DateTime LastAnalyzed { get; set; }
    }

    public class AuditResult
    {
        public string JobId { get; set; }
        public string Status { get; set; }
        public string Message { get; set; }
        public DateTime StartedAt { get; set; }
    }

    public class SecurityServiceException : Exception
    {
        public SecurityServiceException(string message, Exception innerException)
            : base(message, innerException)
        {
        }
    }

    #endregion
}
