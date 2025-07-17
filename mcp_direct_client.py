#!/usr/bin/env python3
"""
Direct MCP client to create 800x600 image
"""

import asyncio
import subprocess
import sys
import os

# Try to use the mcp library
try:
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

async def create_image_direct():
    """Create image using direct MCP client"""
    
    if not MCP_AVAILABLE:
        print("MCP library not available, launching GIMP GUI...")
        subprocess.Popen(["/opt/homebrew/bin/gimp-3.0", "--new-instance"])
        print("GIMP launched. Create image manually: File > New > 800x600")
        return
    
    server_path = "/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server/gimp_mcp_server.py"
    
    try:
        # Start MCP client
        async with stdio_client(
            command="python3",
            args=[server_path],
            env={
                "GIMP_PLUGIN_PATH": "/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server",
                "PYTHONPATH": "/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server"
            }
        ) as streams:
            read_stream, write_stream = streams
            
            # Import the client session
            from mcp.client.session import ClientSession
            
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize
                await session.initialize()
                
                # List tools
                tools = await session.list_tools()
                print("Available tools:")
                for tool in tools:
                    print(f"  - {tool.name}")
                
                # Create image
                result = await session.call_tool(
                    "create_image",
                    {
                        "width": 800,
                        "height": 600,
                        "name": "New 800x600 Image"
                    }
                )
                
                print(f"Image created: {result}")
                
    except Exception as e:
        print(f"MCP error: {e}")
        print("Launching GIMP GUI as fallback...")
        subprocess.Popen(["/opt/homebrew/bin/gimp-3.0", "--new-instance"])
        print("GIMP launched. Create image manually: File > New > 800x600")

if __name__ == "__main__":
    asyncio.run(create_image_direct())