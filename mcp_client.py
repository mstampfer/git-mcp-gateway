#!/usr/bin/env python3
"""
MCP client to interact with GIMP MCP server
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path

async def create_image_via_mcp():
    """Create a 1920x1080 image using MCP client"""
    
    # Start the GIMP MCP server
    server_path = Path("/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server/gimp_mcp_server.py")
    
    env = {
        "GIMP_PLUGIN_PATH": "/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server",
        "PYTHONPATH": "/Volumes/OWC Express 1M2/.config/GIMP/3.0/plug-ins/gimp-mcp-server:" + os.environ.get("PYTHONPATH", ""),
        "PATH": os.environ.get("PATH", "")
    }
    
    # Launch GIMP first to ensure the environment is ready
    print("Starting GIMP 3.0...")
    gimp_process = subprocess.Popen([
        "/opt/homebrew/bin/gimp-3.0",
        "--no-splash",
        "--new-instance"
    ], env=env)
    
    # Wait a moment for GIMP to start
    await asyncio.sleep(3)
    
    # Now try to run the MCP server
    print("Starting MCP server...")
    server_process = subprocess.Popen([
        "python3", str(server_path)
    ], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Send MCP initialization
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    server_process.stdin.write((json.dumps(init_message) + '\n').encode())
    server_process.stdin.flush()
    
    # Read response
    response = server_process.stdout.readline().decode().strip()
    print(f"Init response: {response}")
    
    # Send create_image tool call
    create_message = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_image",
            "arguments": {
                "width": 1920,
                "height": 1080,
                "name": "New 1920x1080 Image"
            }
        }
    }
    
    server_process.stdin.write((json.dumps(create_message) + '\n').encode())
    server_process.stdin.flush()
    
    # Read response
    response = server_process.stdout.readline().decode().strip()
    print(f"Create image response: {response}")
    
    # Clean up
    server_process.terminate()
    
    return response

if __name__ == "__main__":
    import os
    asyncio.run(create_image_via_mcp())