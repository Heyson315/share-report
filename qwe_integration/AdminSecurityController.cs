using System;
using System.Threading.Tasks;
using System.Web.Mvc;
using qwe.Services;

namespace qwe.Controllers
{
    /// <summary>
    /// Admin Security Controller
    /// 
    /// Provides administrative interface for viewing security status,
    /// compliance reports, and managing security alerts integrated
    /// from the Easy-Ai Security Toolkit.
    /// 
    /// Routes:
    ///     GET  /Admin/Security/Dashboard      - Security overview
    ///     GET  /Admin/Security/Alerts         - Active alerts list
    ///     GET  /Admin/Security/Compliance     - M365 compliance status
    ///     GET  /Admin/Security/SharePoint     - SharePoint analysis
    ///     POST /Admin/Security/RunAudit       - Trigger new audit
    /// </summary>
    [Authorize(Roles = "Admin")]
    [RoutePrefix("Admin/Security")]
    public class AdminSecurityController : Controller
    {
        private readonly EasyAiSecurityService _securityService;

        public AdminSecurityController()
        {
            _securityService = new EasyAiSecurityService();
        }

        /// <summary>
        /// Security Dashboard Overview
        /// </summary>
        [Route("Dashboard")]
        public async Task<ActionResult> Dashboard()
        {
            try
            {
                // Check if MCP server is available
                var isHealthy = await _securityService.IsServerHealthyAsync();

                if (!isHealthy)
                {
                    ViewBag.Error = "Security service is currently unavailable. Please ensure the Easy-Ai MCP server is running.";
                    return View("SecurityServiceOffline");
                }

                // Get dashboard data
                var dashboard = await _securityService.GetSecurityDashboardAsync();
                var alerts = await _securityService.GetActiveAlertsAsync();
                var compliance = await _securityService.GetComplianceStatusAsync();

                ViewBag.Dashboard = dashboard;
                ViewBag.Alerts = alerts;
                ViewBag.Compliance = compliance;

                return View();
            }
            catch (Exception ex)
            {
                ViewBag.Error = $"Error loading security dashboard: {ex.Message}";
                return View("Error");
            }
        }

        /// <summary>
        /// Active Security Alerts
        /// </summary>
        [Route("Alerts")]
        public async Task<ActionResult> Alerts()
        {
            try
            {
                var alerts = await _securityService.GetActiveAlertsAsync();
                return View(alerts);
            }
            catch (Exception ex)
            {
                ViewBag.Error = $"Error loading alerts: {ex.Message}";
                return View("Error");
            }
        }

        /// <summary>
        /// M365 Compliance Status
        /// </summary>
        [Route("Compliance")]
        public async Task<ActionResult> Compliance()
        {
            try
            {
                var compliance = await _securityService.GetComplianceStatusAsync();
                return View(compliance);
            }
            catch (Exception ex)
            {
                ViewBag.Error = $"Error loading compliance status: {ex.Message}";
                return View("Error");
            }
        }

        /// <summary>
        /// SharePoint Permissions Analysis
        /// </summary>
        [Route("SharePoint")]
        public async Task<ActionResult> SharePoint()
        {
            try
            {
                var analysis = await _securityService.GetSharePointAnalysisAsync();
                return View(analysis);
            }
            catch (Exception ex)
            {
                ViewBag.Error = $"Error loading SharePoint analysis: {ex.Message}";
                return View("Error");
            }
        }

        /// <summary>
        /// Trigger New Security Audit
        /// </summary>
        [Route("RunAudit")]
        [HttpPost]
        public async Task<ActionResult> RunAudit()
        {
            try
            {
                var result = await _securityService.TriggerSecurityAuditAsync();

                TempData["SuccessMessage"] = $"Security audit started successfully. Job ID: {result.JobId}";
                return RedirectToAction("Dashboard");
            }
            catch (Exception ex)
            {
                TempData["ErrorMessage"] = $"Failed to start security audit: {ex.Message}";
                return RedirectToAction("Dashboard");
            }
        }

        /// <summary>
        /// API endpoint for dashboard widget (AJAX)
        /// </summary>
        [Route("Api/Status")]
        public async Task<JsonResult> GetSecurityStatus()
        {
            try
            {
                var dashboard = await _securityService.GetSecurityDashboardAsync();
                return Json(new
                {
                    success = true,
                    data = dashboard
                }, JsonRequestBehavior.AllowGet);
            }
            catch (Exception ex)
            {
                return Json(new
                {
                    success = false,
                    error = ex.Message
                }, JsonRequestBehavior.AllowGet);
            }
        }
    }
}
