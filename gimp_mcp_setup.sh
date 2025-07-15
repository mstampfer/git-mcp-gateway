#!/bin/bash

# GIMP MCP Server Setup Script
# This script sets up the GIMP MCP server for Claude Code integration

set -e

echo "Setting up GIMP MCP Server for Claude Code..."

# Check if GIMP 3.0 is installed
if ! command -v gimp-3.0 &> /dev/null; then
    echo "Error: GIMP 3.0 is not installed. Please install GIMP 3.0 first."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Create directories
GIMP_CONFIG_DIR="${HOME}/.config/GIMP/3.0"
PLUGIN_DIR="${GIMP_CONFIG_DIR}/plug-ins/gimp-mcp-server"
MCP_CONFIG_DIR="${HOME}/.config/claude-code"

mkdir -p "${PLUGIN_DIR}"
mkdir -p "${MCP_CONFIG_DIR}"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user mcp gi-python pygobject

# Copy server files
echo "Installing GIMP MCP server..."
cp gimp_mcp_server.py "${PLUGIN_DIR}/"
chmod +x "${PLUGIN_DIR}/gimp_mcp_server.py"

# Create GIMP plugin manifest
cat > "${PLUGIN_DIR}/gimp-mcp-server.py" << 'EOF'
#!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, GimpUi
from gimp_mcp_server import GimpMCPServer
import sys

def run(procedure, run_mode, image, n_drawables, drawables, args, data):
    """GIMP plugin entry point"""
    if procedure.get_name() == 'python-fu-mcp-server':
        server = GimpMCPServer()
        server.current_image = image
        # Start MCP server in background
        import threading
        import asyncio
        
        def run_server():
            asyncio.run(server.run_mcp_server())
        
        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()
        
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    
    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())

class GimpMCPPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return ['python-fu-mcp-server']
    
    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, run, None)
        procedure.set_image_types("*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        procedure.set_documentation(
            "Start MCP server for Claude Code integration",
            "Starts the Model Context Protocol server to enable Claude Code integration with GIMP",
            name
        )
        procedure.set_menu_label("Start MCP Server")
        procedure.add_menu_path("<Image>/Tools/")
        return procedure

Gimp.main(GimpMCPPlugin, sys.argv)
EOF

chmod +x "${PLUGIN_DIR}/gimp-mcp-server.py"

# Create Claude Code MCP configuration
echo "Configuring Claude Code MCP client..."
cat > "${MCP_CONFIG_DIR}/mcp_servers.json" << EOF
{
  "mcpServers": {
    "gimp": {
      "command": "python3",
      "args": ["${PLUGIN_DIR}/gimp_mcp_server.py"],
      "env": {
        "GIMP_PLUGIN_PATH": "${PLUGIN_DIR}",
        "PYTHONPATH": "${PLUGIN_DIR}:\${PYTHONPATH}"
      }
    }
  }
}
EOF

# Create desktop entry for easy access
cat > "${HOME}/.local/share/applications/gimp-mcp.desktop" << 'EOF'
[Desktop Entry]
Name=GIMP with MCP
Comment=GIMP 3.0 with Model Context Protocol for Claude Code
Exec=gimp-3.0 --batch-interpreter=python-fu-eval --batch='pdb.python_fu_mcp_server()'
Icon=gimp
Type=Application
Categories=Graphics;Photography;
EOF

# Create usage documentation
cat > "${PLUGIN_DIR}/README.md" << 'EOF'
# GIMP MCP Server

This plugin enables Claude Code to interact with GIMP 3.0 through the Model Context Protocol (MCP).

## Features

- Create and manipulate images
- Apply filters and effects
- Paint and draw operations
- Layer management
- Color adjustments
- Selection tools
- Transform operations

## Usage with Claude Code

1. Start GIMP 3.0
2. Go to Tools → Start MCP Server
3. Use Claude Code to interact with GIMP:

```bash
claude-code "Create a 800x600 image with a blue background"
claude-code "Apply a gaussian blur filter with radius 3"
claude-code "Add a new layer called 'Text' and paint some text"
```

## Available Operations

- `create_image`: Create new images
- `open_image`: Open existing image files
- `save_image`: Save images to disk
- `create_layer`: Add new layers
- `apply_filter`: Apply various filters
- `adjust_colors`: Color corrections
- `select_area`: Create selections
- `paint_stroke`: Paint with brushes
- `transform_layer`: Scale, rotate, etc.
- `get_image_info`: Get image metadata
EOF

echo "Setup complete!"
echo ""
echo "To use GIMP with Claude Code:"
echo "1. Start GIMP 3.0"
echo "2. Go to Tools → Start MCP Server"
echo "3. Use Claude Code to interact with GIMP"
echo ""
echo "Example Claude Code commands:"
echo "  claude-code 'Create a new 800x600 image'"
echo "  claude-code 'Open the image at ~/Desktop/photo.jpg'"
echo "  claude-code 'Apply a blur filter to the current layer'"