#!/usr/bin/env python3
"""
Start Easy-Ai MCP Server for qwe Integration

Starts the MCP server with appropriate configuration for
integration with the HHR CPA website.

Usage:
    python scripts/start_mcp_for_qwe.py
    python scripts/start_mcp_for_qwe.py --port 8080 --host 0.0.0.0
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    """Start MCP server with qwe integration settings."""
    parser = argparse.ArgumentParser(description="Start Easy-Ai MCP Server for qwe integration")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--allow-cors", action="store_true", help="Enable CORS for cross-origin requests")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    print("🚀 Starting Easy-Ai MCP Server for qwe Integration")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   CORS: {'Enabled' if args.allow_cors else 'Disabled'}")
    print()
    
    # Prepare environment
    env_vars = {
        "MCP_HOST": args.host,
        "MCP_PORT": str(args.port),
        "MCP_ALLOW_CORS": "true" if args.allow_cors else "false",
        "PYTHONPATH": str(project_root),
    }
    
    # Start the plugin-based MCP server (recommended)
    mcp_server_path = project_root / "src" / "mcp" / "m365_mcp_server.py"
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found: {mcp_server_path}")
        print("   Using simple MCP server instead...")
        mcp_server_path = project_root / "src" / "extensions" / "mcp" / "server.py"
    
    try:
        # Run the server
        cmd = [sys.executable, "-m", "src.mcp.m365_mcp_server"]
        
        print(f"📍 Server URL: http://{args.host}:{args.port}")
        print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
        print(f"🔧 Health Check: http://{args.host}:{args.port}/health")
        print()
        print("Press Ctrl+C to stop the server")
        print("─" * 60)
        
        # Start server process
        process = subprocess.run(
            cmd,
            cwd=str(project_root),
            env={**subprocess.os.environ, **env_vars}
        )
        
        return process.returncode
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
