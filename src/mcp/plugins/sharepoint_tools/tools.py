"""
SharePoint Tools Plugin

Provides tools for analyzing SharePoint Online sites and permissions.
This plugin is loaded dynamically by the MCP server.
"""

from pathlib import Path


def register_tools(server, toolkit_path: Path = None) -> None:
    """
    Register SharePoint tools with the MCP server.

    Args:
        server: The MCP Server instance to register tools with
        toolkit_path: Path to the toolkit root directory (optional)
    """
    if toolkit_path is None:
        # Default to repository root
        toolkit_path = Path(__file__).parent.parent.parent.parent.parent

    @server.tool("analyze_sharepoint_permissions")
    async def analyze_sharepoint_permissions(input_file: str, generate_excel: bool = True) -> str:
        """
        Analyze SharePoint permissions from CSV export.

        Args:
            input_file: Path to SharePoint permissions CSV file
            generate_excel: Whether to generate Excel report

        Returns:
            Analysis summary and report location
        """
        from src.core.sharepoint_utils import analyze_sharepoint_permissions as analyze_sp

        try:
            success, message = await analyze_sp(input_file, toolkit_path, generate_excel)

            if not success:
                raise Exception(message)

            return message

        except Exception as e:
            raise Exception(f"SharePoint analysis failed: {str(e)}")

    @server.tool("get_sharepoint_site_info")
    async def get_sharepoint_site_info(site_url: str) -> str:
        """
        Get information about a SharePoint site.

        Args:
            site_url: The URL of the SharePoint site to analyze

        Returns:
            Site information summary
        """
        # This is a placeholder for future Graph API integration
        return f"""📊 SharePoint Site Information

🌐 **Site URL:** {site_url}

⚠️ **Note:** This feature requires Microsoft Graph API authentication.
Configure your credentials in the .env file:
• M365_TENANT_ID
• M365_CLIENT_ID
• M365_CLIENT_SECRET

💡 **Alternative:**
Export site permissions using SharePoint admin center
and use the 'analyze_sharepoint_permissions' tool."""
