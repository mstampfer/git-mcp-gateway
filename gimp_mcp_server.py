#!/usr/bin/env python3
"""
GIMP 3.0 MCP Server - Enables Claude Code to interact with GIMP 3.0
via the Model Context Protocol (MCP)

GIMP 3.0 API Reference: Uses GObject Introspection bindings
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

# GIMP 3.0 Python API imports
try:
    import gi
    gi.require_version('Gimp', '3.0')
    gi.require_version('GimpUi', '3.0') 
    gi.require_version('Gegl', '0.4')
    from gi.repository import Gimp, GimpUi, GObject, GLib, Gio, Gegl
    GIMP_AVAILABLE = True
except ImportError:
    GIMP_AVAILABLE = False
    print("GIMP 3.0 Python bindings not available")

logger = logging.getLogger(__name__)

class GimpMCPServer:
    def __init__(self):
        self.server = Server("gimp-mcp-server")
        self.current_image = None
        self.current_drawable = None
        self.pdb = None
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available GIMP resources"""
            resources = []
            
            if GIMP_AVAILABLE and self.pdb:
                # List open images
                image_list = Gimp.list_images()
                for i, image in enumerate(image_list):
                    if image:
                        resources.append(Resource(
                            uri=f"gimp://image/{i}",
                            name=f"Image {i}: {image.get_name() if hasattr(image, 'get_name') else 'Untitled'}",
                            description=f"GIMP image: {image.get_width()}x{image.get_height()}",
                            mimeType="image/png"
                        ))
                
                # List available procedures
                resources.append(Resource(
                    uri="gimp://procedures",
                    name="GIMP Procedures",
                    description="Available GIMP procedures via PDB",
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
            if not GIMP_AVAILABLE or not self.pdb:
                return json.dumps({"error": "GIMP not available"})
                
            if uri.startswith("gimp://image/"):
                image_id = int(uri.split("/")[-1])
                image_list = Gimp.list_images()
                if image_id < len(image_list) and image_list[image_id]:
                    image = image_list[image_id]
                    layers = image.list_layers()
                    return json.dumps({
                        "name": image.get_name() if hasattr(image, 'get_name') else "Untitled",
                        "width": image.get_width(),
                        "height": image.get_height(),
                        "layers": [layer.get_name() for layer in layers if layer],
                        "base_type": str(image.get_base_type()),
                        "precision": str(image.get_precision())
                    })
                    
            elif uri == "gimp://procedures":
                # Get some common procedures
                procedures = [
                    "gimp-image-new",
                    "gimp-file-load",
                    "gimp-file-save", 
                    "gimp-layer-new",
                    "gimp-image-insert-layer",
                    "plug-in-gauss",
                    "gimp-drawable-brightness-contrast",
                    "gimp-drawable-hue-saturation",
                    "gimp-image-select-rectangle"
                ]
                return json.dumps({"procedures": procedures})
                
            elif uri == "gimp://brushes":
                try:
                    brushes_list = Gimp.brushes_get_list("")
                    if brushes_list and len(brushes_list) > 1:
                        return json.dumps({"brushes": brushes_list[1]})
                except:
                    pass
                return json.dumps({"brushes": []})
                
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
                            "name": {"type": "string", "description": "Image name", "default": "Untitled"},
                            "fill_type": {"type": "string", "enum": ["white", "black", "transparent"], "default": "white"}
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
                            "export_options": {"type": "object", "description": "Export options (quality, compression, etc.)"}
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
                            "layer_type": {"type": "string", "enum": ["RGB", "RGBA", "GRAY", "GRAYA"], "default": "RGBA"},
                            "opacity": {"type": "number", "minimum": 0, "maximum": 100, "default": 100},
                            "mode": {"type": "string", "description": "Blend mode", "default": "normal"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="apply_gaussian_blur",
                    description="Apply Gaussian blur filter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "radius": {"type": "number", "minimum": 0.1, "maximum": 300, "description": "Blur radius"},
                            "horizontal": {"type": "number", "minimum": 0.1, "maximum": 300, "description": "Horizontal radius (optional)"},
                            "vertical": {"type": "number", "minimum": 0.1, "maximum": 300, "description": "Vertical radius (optional)"}
                        },
                        "required": ["radius"]
                    }
                ),
                Tool(
                    name="adjust_brightness_contrast",
                    description="Adjust brightness and contrast",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "brightness": {"type": "number", "minimum": -100, "maximum": 100, "description": "Brightness adjustment"},
                            "contrast": {"type": "number", "minimum": -100, "maximum": 100, "description": "Contrast adjustment"}
                        },
                        "required": ["brightness", "contrast"]
                    }
                ),
                Tool(
                    name="adjust_hue_saturation",
                    description="Adjust hue, saturation, and lightness",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "hue": {"type": "number", "minimum": -180, "maximum": 180, "description": "Hue adjustment"},
                            "saturation": {"type": "number", "minimum": -100, "maximum": 100, "description": "Saturation adjustment"},
                            "lightness": {"type": "number", "minimum": -100, "maximum": 100, "description": "Lightness adjustment"},
                            "channel": {"type": "string", "enum": ["master", "red", "yellow", "green", "cyan", "blue", "magenta"], "default": "master"}
                        }
                    }
                ),
                Tool(
                    name="select_rectangle",
                    description="Create a rectangular selection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "x": {"type": "number", "description": "X coordinate"},
                            "y": {"type": "number", "description": "Y coordinate"},
                            "width": {"type": "number", "description": "Selection width"},
                            "height": {"type": "number", "description": "Selection height"},
                            "operation": {"type": "string", "enum": ["replace", "add", "subtract", "intersect"], "default": "replace"}
                        },
                        "required": ["x", "y", "width", "height"]
                    }
                ),
                Tool(
                    name="scale_image",
                    description="Scale the current image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "minimum": 1, "description": "New width"},
                            "height": {"type": "integer", "minimum": 1, "description": "New height"},
                            "interpolation": {"type": "string", "enum": ["none", "linear", "cubic", "nohalo", "lohalo"], "default": "cubic"}
                        },
                        "required": ["width", "height"]
                    }
                ),
                Tool(
                    name="get_image_info", 
                    description="Get information about the current image",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="run_procedure",
                    description="Run a GIMP procedure directly",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "procedure_name": {"type": "string", "description": "PDB procedure name"},
                            "arguments": {"type": "array", "description": "Procedure arguments"}
                        },
                        "required": ["procedure_name", "arguments"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute GIMP operations"""
            if not GIMP_AVAILABLE or not self.pdb:
                return [TextContent(type="text", text="Error: GIMP not available or not initialized")]
                
            try:
                if name == "create_image":
                    return await self.create_image(arguments)
                elif name == "open_image":
                    return await self.open_image(arguments)
                elif name == "save_image":
                    return await self.save_image(arguments)
                elif name == "create_layer":
                    return await self.create_layer(arguments)
                elif name == "apply_gaussian_blur":
                    return await self.apply_gaussian_blur(arguments)
                elif name == "adjust_brightness_contrast":
                    return await self.adjust_brightness_contrast(arguments)
                elif name == "adjust_hue_saturation":
                    return await self.adjust_hue_saturation(arguments)
                elif name == "select_rectangle":
                    return await self.select_rectangle(arguments)
                elif name == "scale_image":
                    return await self.scale_image(arguments)
                elif name == "get_image_info":
                    return await self.get_image_info(arguments)
                elif name == "run_procedure":
                    return await self.run_procedure(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def create_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new GIMP image using GIMP 3.0 API"""
        width = args["width"]
        height = args["height"]
        name = args.get("name", "Untitled")
        fill_type = args.get("fill_type", "white")
        
        try:
            # Create new image - GIMP 3.0 API
            image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)
            
            if hasattr(image, 'set_name'):
                image.set_name(name)
            
            # Create background layer
            layer = Gimp.Layer.new(image, "Background", width, height, 
                                  Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
            
            # Insert layer into image
            image.insert_layer(layer, None, 0)
            
            # Fill layer based on type
            if fill_type == "white":
                white_color = Gegl.Color.new("white")
                Gimp.Context.set_foreground(white_color)
                Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
            elif fill_type == "black":
                black_color = Gegl.Color.new("black")
                Gimp.Context.set_foreground(black_color)
                Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
            elif fill_type == "transparent":
                Gimp.drawable_edit_clear(layer)
            
            # Create display
            display = Gimp.Display.new(image)
            
            # Update current references
            self.current_image = image
            self.current_drawable = layer
            
            return [TextContent(type="text", text=f"Created new image: {name} ({width}x{height})")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating image: {str(e)}")]
    
    async def open_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Open an image file using GIMP 3.0 API"""
        filepath = args["filepath"]
        
        if not os.path.exists(filepath):
            return [TextContent(type="text", text=f"File not found: {filepath}")]
        
        try:
            # Open image using GIMP 3.0 file loading
            file_obj = Gio.File.new_for_path(filepath)
            image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)
            
            if not image:
                return [TextContent(type="text", text=f"Failed to load image: {filepath}")]
            
            # Create display
            display = Gimp.Display.new(image)
            
            # Update current references
            self.current_image = image
            layers = image.list_layers()
            if layers:
                self.current_drawable = layers[0]
            
            return [TextContent(type="text", text=f"Opened image: {filepath}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error opening image: {str(e)}")]
    
    async def save_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Save image to file using GIMP 3.0 API"""
        filepath = args["filepath"]
        
        if not self.current_image:
            return [TextContent(type="text", text="No image to save")]
        
        try:
            # Get all drawables for export
            drawables = self.current_image.list_layers()
            
            # Export image using GIMP 3.0 export API
            file_obj = Gio.File.new_for_path(filepath)
            Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, self.current_image, drawables, file_obj)
            
            return [TextContent(type="text", text=f"Saved image to: {filepath}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error saving image: {str(e)}")]
    
    async def create_layer(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new layer using GIMP 3.0 API"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        name = args["name"]
        layer_type = args.get("layer_type", "RGBA")
        opacity = args.get("opacity", 100.0)
        mode = args.get("mode", "normal")
        
        try:
            # Map layer type to GIMP 3.0 constants
            type_map = {
                "RGB": Gimp.ImageType.RGB_IMAGE,
                "RGBA": Gimp.ImageType.RGBA_IMAGE,
                "GRAY": Gimp.ImageType.GRAY_IMAGE,
                "GRAYA": Gimp.ImageType.GRAYA_IMAGE
            }
            
            # Map blend mode
            mode_map = {
                "normal": Gimp.LayerMode.NORMAL,
                "multiply": Gimp.LayerMode.MULTIPLY,
                "screen": Gimp.LayerMode.SCREEN,
                "overlay": Gimp.LayerMode.OVERLAY,
                "soft_light": Gimp.LayerMode.SOFTLIGHT_MODE,
                "hard_light": Gimp.LayerMode.HARDLIGHT_MODE
            }
            
            gimp_type = type_map.get(layer_type, Gimp.ImageType.RGBA_IMAGE)
            gimp_mode = mode_map.get(mode, Gimp.LayerMode.NORMAL)
            
            # Create layer
            layer = Gimp.Layer.new(self.current_image, name,
                                  self.current_image.get_width(),
                                  self.current_image.get_height(),
                                  gimp_type, opacity, gimp_mode)
            
            # Insert layer into image
            self.current_image.insert_layer(layer, None, 0)
            
            # Update current drawable
            self.current_drawable = layer
            
            return [TextContent(type="text", text=f"Created layer: {name}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating layer: {str(e)}")]
    
    async def apply_gaussian_blur(self, args: Dict[str, Any]) -> List[TextContent]:
        """Apply Gaussian blur using GIMP 3.0 API"""
        if not self.current_drawable:
            return [TextContent(type="text", text="No drawable selected")]
        
        radius = args["radius"]
        horizontal = args.get("horizontal", radius)
        vertical = args.get("vertical", radius)
        
        try:
            # Use GIMP 3.0 procedure call
            result = self.pdb.run_procedure("plug-in-gauss",
                                          [Gimp.RunMode.NONINTERACTIVE,
                                           self.current_image,
                                           1,
                                           [self.current_drawable],
                                           horizontal,
                                           vertical,
                                           1])  # link horizontal/vertical
            
            if result.index(0) == Gimp.PDBStatusType.SUCCESS:
                return [TextContent(type="text", text=f"Applied Gaussian blur (radius: {radius})")]
            else:
                return [TextContent(type="text", text="Failed to apply Gaussian blur")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error applying blur: {str(e)}")]
    
    async def adjust_brightness_contrast(self, args: Dict[str, Any]) -> List[TextContent]:
        """Adjust brightness and contrast using GIMP 3.0 API"""
        if not self.current_drawable:
            return [TextContent(type="text", text="No drawable selected")]
        
        brightness = args["brightness"]
        contrast = args["contrast"]
        
        try:
            # Use GIMP 3.0 procedure call
            result = self.pdb.run_procedure("gimp-drawable-brightness-contrast",
                                          [self.current_drawable,
                                           brightness / 100.0,  # Convert to -1.0 to 1.0 range
                                           contrast / 100.0])
            
            if result.index(0) == Gimp.PDBStatusType.SUCCESS:
                return [TextContent(type="text", text=f"Adjusted brightness: {brightness}, contrast: {contrast}")]
            else:
                return [TextContent(type="text", text="Failed to adjust brightness/contrast")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error adjusting brightness/contrast: {str(e)}")]
    
    async def adjust_hue_saturation(self, args: Dict[str, Any]) -> List[TextContent]:
        """Adjust hue, saturation, lightness using GIMP 3.0 API"""
        if not self.current_drawable:
            return [TextContent(type="text", text="No drawable selected")]
        
        hue = args.get("hue", 0)
        saturation = args.get("saturation", 0)
        lightness = args.get("lightness", 0)
        channel = args.get("channel", "master")
        
        try:
            # Map channel to GIMP 3.0 constants
            channel_map = {
                "master": Gimp.HueRange.ALL,
                "red": Gimp.HueRange.RED,
                "yellow": Gimp.HueRange.YELLOW,
                "green": Gimp.HueRange.GREEN,
                "cyan": Gimp.HueRange.CYAN,
                "blue": Gimp.HueRange.BLUE,
                "magenta": Gimp.HueRange.MAGENTA
            }
            
            gimp_channel = channel_map.get(channel, Gimp.HueRange.ALL)
            
            # Use GIMP 3.0 procedure call
            result = self.pdb.run_procedure("gimp-drawable-hue-saturation",
                                          [self.current_drawable,
                                           gimp_channel,
                                           hue,
                                           lightness,
                                           saturation,
                                           0])  # overlap
            
            if result.index(0) == Gimp.PDBStatusType.SUCCESS:
                return [TextContent(type="text", text=f"Adjusted hue: {hue}, saturation: {saturation}, lightness: {lightness}")]
            else:
                return [TextContent(type="text", text="Failed to adjust hue/saturation")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error adjusting hue/saturation: {str(e)}")]
    
    async def select_rectangle(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create rectangular selection using GIMP 3.0 API"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        x = args["x"]
        y = args["y"] 
        width = args["width"]
        height = args["height"]
        operation = args.get("operation", "replace")
        
        try:
            # Map operation to GIMP 3.0 constants
            op_map = {
                "replace": Gimp.ChannelOps.REPLACE,
                "add": Gimp.ChannelOps.ADD,
                "subtract": Gimp.ChannelOps.SUBTRACT,
                "intersect": Gimp.ChannelOps.INTERSECT
            }
            
            gimp_op = op_map.get(operation, Gimp.ChannelOps.REPLACE)
            
            # Create rectangular selection
            self.current_image.select_rectangle(gimp_op, x, y, width, height)
            
            return [TextContent(type="text", text=f"Created rectangular selection: {x},{y} {width}x{height}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating selection: {str(e)}")]
    
    async def scale_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Scale image using GIMP 3.0 API"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        width = args["width"]
        height = args["height"]
        interpolation = args.get("interpolation", "cubic")
        
        try:
            # Map interpolation to GIMP 3.0 constants
            interp_map = {
                "none": Gimp.InterpolationType.NONE,
                "linear": Gimp.InterpolationType.LINEAR,
                "cubic": Gimp.InterpolationType.CUBIC,
                "nohalo": Gimp.InterpolationType.NOHALO,
                "lohalo": Gimp.InterpolationType.LOHALO
            }
            
            gimp_interp = interp_map.get(interpolation, Gimp.InterpolationType.CUBIC)
            
            # Scale image
            self.current_image.scale(width, height)
            
            return [TextContent(type="text", text=f"Scaled image to {width}x{height}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error scaling image: {str(e)}")]
    
    async def get_image_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get image information using GIMP 3.0 API"""
        if not self.current_image:
            return [TextContent(type="text", text="No image open")]
        
        try:
            layers = self.current_image.list_layers()
            
            info = {
                "name": self.current_image.get_name() if hasattr(self.current_image, 'get_name') else "Untitled",
                "width": self.current_image.get_width(),
                "height": self.current_image.get_height(),
                "base_type": str(self.current_image.get_base_type()),
                "precision": str(self.current_image.get_precision()),
                "layers": [layer.get_name() for layer in layers if layer],
                "active_layer": self.current_drawable.get_name() if self.current_drawable else None
            }
            
            return [TextContent(type="text", text=json.dumps(info, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting image info: {str(e)}")]
    
    async def run_procedure(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run arbitrary GIMP procedure using GIMP 3.0 API"""
        procedure_name = args["procedure_name"]
        arguments = args["arguments"]
        
        try:
            # Run procedure through PDB
            result = self.pdb.run_procedure(procedure_name, arguments)
            
            if result.index(0) == Gimp.PDBStatusType.SUCCESS:
                return [TextContent(type="text", text=f"Executed procedure: {procedure_name}")]
            else:
                return [TextContent(type="text", text=f"Failed to execute procedure: {procedure_name}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error running procedure: {str(e)}")]
    
    def initialize_gimp(self):
        """Initialize GIMP for plugin execution"""
        if GIMP_AVAILABLE:
            self.pdb = Gimp.get_pdb()
            # Set up context and other initialization
            Gimp.context_push()
            return True
        return False
    
    async def run(self):
        """Run the MCP server"""
        if not self.initialize_gimp():
            print("Warning: Running without GIMP initialization")
        
        # Run MCP server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, 
                                InitializationOptions(
                                    server_name="gimp-mcp-server",
                                    server_version="1.0.0",
                                    capabilities={}
                                ))

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    server = GimpMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
