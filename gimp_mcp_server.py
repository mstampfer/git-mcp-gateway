#!/usr/bin/env python3
"""
GIMP MCP Server - Enables Claude Code to interact with GIMP 3.0
via the Model Context Protocol (MCP)
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

# MCP server dependencies
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    CallToolResult
)

# GIMP Python API imports
try:
    import gi
    gi.require_version('Gimp', '3.0')
    from gi.repository import Gimp, GimpUi, GObject, GLib
    GIMP_AVAILABLE = True
except ImportError:
    GIMP_AVAILABLE = False
    print("GIMP 3.0 Python bindings not available")

logger = logging.getLogger(__name__)

class GimpMCPServer:
    def __init__(self):
        self.server = Server("gimp-mcp-server")
        self.gimp_app = None
        self.current_image = None
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available GIMP resources"""
            resources = []
            
            if GIMP_AVAILABLE and self.gimp_app:
                # List open images
                images = Gimp.list_images()
                for i, image in enumerate(images):
                    resources.append(Resource(
                        uri=f"gimp://image/{i}",
                        name=f"Image {i}: {image.get_name()}",
                        description=f"GIMP image: {image.get_width()}x{image.get_height()}",
                        mimeType="image/png"
                    ))
                
                # List available tools
                resources.append(Resource(
                    uri="gimp://tools",
                    name="GIMP Tools",
                    description="Available GIMP tools and operations",
                    mimeType="application/json"
                ))
                
                # List brushes, patterns, etc.
                resources.append(Resource(
                    uri="gimp://brushes",
                    name="GIMP Brushes",
                    description="Available GIMP brushes",
                    mimeType="application/json"
                ))
                
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a GIMP resource"""
            if not GIMP_AVAILABLE:
                return json.dumps({"error": "GIMP not available"})
                
            if uri.startswith("gimp://image/"):
                image_id = int(uri.split("/")[-1])
                images = Gimp.list_images()
                if image_id < len(images):
                    image = images[image_id]
                    return json.dumps({
                        "name": image.get_name(),
                        "width": image.get_width(),
                        "height": image.get_height(),
                        "layers": [layer.get_name() for layer in image.get_layers()],
                        "colorspace": str(image.get_colorspace()),
                        "precision": str(image.get_precision())
                    })
                    
            elif uri == "gimp://tools":
                return json.dumps({
                    "painting_tools": [
                        "gimp-paintbrush-tool",
                        "gimp-pencil-tool", 
                        "gimp-airbrush-tool",
                        "gimp-eraser-tool",
                        "gimp-clone-tool",
                        "gimp-healing-tool",
                        "gimp-smudge-tool"
                    ],
                    "selection_tools": [
                        "gimp-rectangle-select-tool",
                        "gimp-ellipse-select-tool",
                        "gimp-free-select-tool",
                        "gimp-fuzzy-select-tool"
                    ],
                    "transform_tools": [
                        "gimp-rotate-tool",
                        "gimp-scale-tool",
                        "gimp-shear-tool",
                        "gimp-perspective-tool"
                    ]
                })
                
            elif uri == "gimp://brushes":
                brushes = Gimp.brushes_get_list("")
                return json.dumps({"brushes": brushes[1] if brushes[0] else []})
                
            return json.dumps({"error": "Resource not found"})
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available GIMP tools for Claude Code"""
            return [
                Tool(
                    name="create_image",
                    description="Create a new GIMP image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "description": "Image width in pixels"},
                            "height": {"type": "integer", "description": "Image height in pixels"},
                            "name": {"type": "string", "description": "Image name"}
                        },
                        "required": ["width", "height"]
                    }
                ),
                Tool(
                    name="open_image",
                    description="Open an image file in GIMP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Path to image file"}
                        },
                        "required": ["filepath"]
                    }
                ),
                Tool(
                    name="save_image",
                    description="Save current image to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string", "description": "Output file path"},
                            "image_id": {"type": "integer", "description": "Image ID (optional)"}
                        },
                        "required": ["filepath"]
                    }
                ),
                Tool(
                    name="create_layer",
                    description="Create a new layer in the current image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Layer name"},
                            "layer_type": {"type": "string", "enum": ["RGB", "RGBA", "GRAY", "GRAYA"], "default": "RGBA"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="apply_filter",
                    description="Apply a filter to the current layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter_name": {"type": "string", "description": "Filter name (e.g., 'gaussian-blur', 'sharpen')"},
                            "parameters": {"type": "object", "description": "Filter parameters"}
                        },
                        "required": ["filter_name"]
                    }
                ),
                Tool(
                    name="adjust_colors",
                    description="Adjust color properties of the current layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "adjustment": {"type": "string", "enum": ["brightness-contrast", "hue-saturation", "levels", "curves"]},
                            "parameters": {"type": "object", "description": "Adjustment parameters"}
                        },
                        "required": ["adjustment"]
                    }
                ),
                Tool(
                    name="select_area",
                    description="Create a selection in the image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool": {"type": "string", "enum": ["rectangle", "ellipse", "free", "fuzzy"]},
                            "x": {"type": "number", "description": "X coordinate"},
                            "y": {"type": "number", "description": "Y coordinate"},
                            "width": {"type": "number", "description": "Width (for rectangle/ellipse)"},
                            "height": {"type": "number", "description": "Height (for rectangle/ellipse)"}
                        },
                        "required": ["tool", "x", "y"]
                    }
                ),
                Tool(
                    name="paint_stroke",
                    description="Paint with a brush tool",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool": {"type": "string", "enum": ["paintbrush", "pencil", "airbrush", "eraser"]},
                            "brush": {"type": "string", "description": "Brush name"},
                            "color": {"type": "string", "description": "Color in hex format (#RRGGBB)"},
                            "opacity": {"type": "number", "minimum": 0, "maximum": 100, "default": 100},
                            "size": {"type": "number", "minimum": 1, "description": "Brush size"},
                            "points": {"type": "array", "items": {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}}
                        },
                        "required": ["tool", "points"]
                    }
                ),
                Tool(
                    name="transform_layer",
                    description="Transform the current layer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string", "enum": ["scale", "rotate", "flip", "crop"]},
                            "parameters": {"type": "object", "description": "Transform parameters"}
                        },
                        "required": ["operation"]
                    }
                ),
                Tool(
                    name="get_image_info",
                    description="Get information about the current image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "integer", "description": "Image ID (optional)"}
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute GIMP operations"""
            if not GIMP_AVAILABLE:
                return [TextContent(type="text", text="Error: GIMP not available")]
                
            try:
                if name == "create_image":
                    return await self.create_image(arguments)
                elif name == "open_image":
                    return await self.open_image(arguments)
                elif name == "save_image":
                    return await self.save_image(arguments)
                elif name == "create_layer":
                    return await self.create_layer(arguments)
                elif name == "apply_filter":
                    return await self.apply_filter(arguments)
                elif name == "adjust_colors":
                    return await self.adjust_colors(arguments)
                elif name == "select_area":
                    return await self.select_area(arguments)
                elif name == "paint_stroke":
                    return await self.paint_stroke(arguments)
                elif name == "transform_layer":
                    return await self.transform_layer(arguments)
                elif name == "get_image_info":
                    return await self.get_image_info(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def create_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new GIMP image"""
        width = args["width"]
        height = args["height"]
        name = args.get("name", "Untitled")
        
        # Create new image
        image = Gimp.Image.new(width, height, Gimp.ImageType.RGB)
        image.set_name(name)
        
        # Create background layer
        layer = Gimp.Layer.new(image, "Background", width, height, 
                              Gimp.ImageType.RGB_IMAGE, 100, Gimp.LayerMode.NORMAL)
        image.insert_layer(layer, None, 0)
        
        # Fill with white
        Gimp.Context.set_foreground(Gimp.RGB())
        Gimp.Context.get_foreground().set(1.0, 1.0, 1.0)
        layer.fill(Gimp.FillType.FOREGROUND)
        
        # Display image
        display = Gimp.Display.new(image)
        self.current_image = image
        
        return [TextContent(type="text", text=f"Created new image: {name} ({width}x{height})")]
    
    async def open_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Open an image file"""
        filepath = args["filepath"]
        
        if not os.path.exists(filepath):
            return [TextContent(type="text", text=f"File not found: {filepath}")]
        
        # Open image
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, 
                              Gimp.File.new_for_path(filepath))
        
        # Display image
        display = Gimp.Display.new(image)
        self.current_image = image
        
        return [TextContent(type="text", text=f"Opened image: {filepath}")]
    
    async def save_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Save image to file"""
        filepath = args["filepath"]
        image = self.current_image
        
        if not image:
            return [TextContent(type="text", text="No image to save")]
        
        # Save image
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, 
                      Gimp.File.new_for_path(filepath))
        
        return [TextContent(type="text", text=f"Saved image to: {filepath}")]
    
    async def create_layer(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new layer"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        name = args["name"]
        layer_type = args.get("layer_type", "RGBA")
        
        # Map layer type
        type_map = {
            "RGB": Gimp.ImageType.RGB_IMAGE,
            "RGBA": Gimp.ImageType.RGBA_IMAGE,
            "GRAY": Gimp.ImageType.GRAY_IMAGE,
            "GRAYA": Gimp.ImageType.GRAYA_IMAGE
        }
        
        gimp_type = type_map.get(layer_type, Gimp.ImageType.RGBA_IMAGE)
        
        # Create layer
        layer = Gimp.Layer.new(self.current_image, name, 
                              self.current_image.get_width(),
                              self.current_image.get_height(),
                              gimp_type, 100, Gimp.LayerMode.NORMAL)
        
        self.current_image.insert_layer(layer, None, 0)
        
        return [TextContent(type="text", text=f"Created layer: {name}")]
    
    async def apply_filter(self, args: Dict[str, Any]) -> List[TextContent]:
        """Apply a filter to the current layer"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        filter_name = args["filter_name"]
        parameters = args.get("parameters", {})
        
        # Get active layer
        layer = self.current_image.get_active_layer()
        if not layer:
            return [TextContent(type="text", text="No active layer")]
        
        # Apply common filters
        if filter_name == "gaussian-blur":
            radius = parameters.get("radius", 1.0)
            Gimp.get_pdb().run_procedure("plug-in-gauss",
                                        [layer, radius, radius, 0, 0])
        elif filter_name == "sharpen":
            amount = parameters.get("amount", 0.5)
            Gimp.get_pdb().run_procedure("plug-in-sharpen",
                                        [layer, amount])
        
        return [TextContent(type="text", text=f"Applied filter: {filter_name}")]
    
    async def adjust_colors(self, args: Dict[str, Any]) -> List[TextContent]:
        """Adjust color properties"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        adjustment = args["adjustment"]
        parameters = args.get("parameters", {})
        
        # Get active layer
        layer = self.current_image.get_active_layer()
        if not layer:
            return [TextContent(type="text", text="No active layer")]
        
        # Apply adjustments
        if adjustment == "brightness-contrast":
            brightness = parameters.get("brightness", 0)
            contrast = parameters.get("contrast", 0)
            Gimp.get_pdb().run_procedure("gimp-brightness-contrast",
                                        [layer, brightness, contrast])
        elif adjustment == "hue-saturation":
            hue = parameters.get("hue", 0)
            saturation = parameters.get("saturation", 0)
            lightness = parameters.get("lightness", 0)
            Gimp.get_pdb().run_procedure("gimp-hue-saturation",
                                        [layer, Gimp.HueRange.ALL, hue, lightness, saturation])
        
        return [TextContent(type="text", text=f"Applied adjustment: {adjustment}")]
    
    async def select_area(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a selection"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        tool = args["tool"]
        x = args["x"]
        y = args["y"]
        
        if tool == "rectangle":
            width = args.get("width", 100)
            height = args.get("height", 100)
            self.current_image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, width, height)
        elif tool == "ellipse":
            width = args.get("width", 100)
            height = args.get("height", 100)
            self.current_image.select_ellipse(Gimp.ChannelOps.REPLACE, x, y, width, height)
        
        return [TextContent(type="text", text=f"Created {tool} selection")]
    
    async def paint_stroke(self, args: Dict[str, Any]) -> List[TextContent]:
        """Paint with brush tool"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        tool = args["tool"]
        points = args["points"]
        
        # Get active layer
        layer = self.current_image.get_active_layer()
        if not layer:
            return [TextContent(type="text", text="No active layer")]
        
        # Convert points to coordinate array
        coords = []
        for point in points:
            coords.extend([point["x"], point["y"]])
        
        # Paint stroke
        if tool == "paintbrush":
            Gimp.get_pdb().run_procedure("gimp-paintbrush-default",
                                        [layer, len(coords), coords])
        
        return [TextContent(type="text", text=f"Applied {tool} stroke")]
    
    async def transform_layer(self, args: Dict[str, Any]) -> List[TextContent]:
        """Transform layer"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        operation = args["operation"]
        parameters = args.get("parameters", {})
        
        # Get active layer
        layer = self.current_image.get_active_layer()
        if not layer:
            return [TextContent(type="text", text="No active layer")]
        
        if operation == "scale":
            scale_x = parameters.get("scale_x", 1.0)
            scale_y = parameters.get("scale_y", 1.0)
            layer.scale(layer.get_width() * scale_x, layer.get_height() * scale_y, True)
        elif operation == "rotate":
            angle = parameters.get("angle", 0)
            layer.rotate(angle, True)
        
        return [TextContent(type="text", text=f"Applied {operation} transform")]
    
    async def get_image_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get image information"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        info = {
            "name": self.current_image.get_name(),
            "width": self.current_image.get_width(),
            "height": self.current_image.get_height(),
            "layers": [layer.get_name() for layer in self.current_image.get_layers()],
            "colorspace": str(self.current_image.get_colorspace()),
            "precision": str(self.current_image.get_precision())
        }
        
        return [TextContent(type="text", text=json.dumps(info, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        # Initialize GIMP if available
        if GIMP_AVAILABLE:
            Gimp.main(["gimp-mcp-server"], self.gimp_main)
        else:
            # Run without GIMP for testing
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, 
                                    InitializationOptions(
                                        server_name="gimp-mcp-server",
                                        server_version="0.1.0",
                                        capabilities={}
                                    ))
    
    def gimp_main(self, *args):
        """GIMP main entry point"""
        self.gimp_app = Gimp.get_pdb()
        # Run MCP server in async context
        asyncio.run(self.run_mcp_server())
    
    async def run_mcp_server(self):
        """Run MCP server within GIMP context"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, 
                                InitializationOptions(
                                    server_name="gimp-mcp-server",
                                    server_version="0.1.0",
                                    capabilities={}
                                ))

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    server = GimpMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
