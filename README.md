### Creating Images (GIMP 3.0 Style)
```python
# Create new image
image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)

# Create layer
layer = Gimp.Layer.new(image, "Background", width, height, 
                      Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)

# Insert layer into image
image.insert_layer(layer, None, 0)

# Fill layer with color (GIMP 3.0 uses Gegl.Color)
white_color = Gegl.Color.new("white")
Gimp.Context.set_foreground(white_color)
Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
```

### Color Handling (GIMP 3.0 Style)
```python
# Import Gegl for color operations
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

# Create colors different ways
red_color = Gegl.Color.new("red")
blue_hex = Gegl.Color.new("#0000FF")
green_rgba = Gegl.Color()
green_rgba.set_rgba(0.0, 1.0, 0.0, 1.0)

# Set context colors
Gimp.Context.set_foreground(red_color)
Gimp.Context.set_background(blue_hex)

# Get current colors
current_fg = Gimp.Context.get_foreground()
rgba_values = current_fg.get_rgba()  # Returns (r, g, b, a) tuple
```

### File Operations (GIMP 3.0 Style)
```python
# Load image
file_obj = Gio.File.new_for_path(filepath)
image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)

# Export image
output_file = Gio.File.new_for_path(output_path)
layers = image.list_layers()
Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, layers, output_file)
```

### Using PDB Procedures (GIMP 3.0 Style)
```python
pdb = Gimp.get_pdb()

# Apply Gaussian blur
result = pdb.run_procedure("plug-in-gauss",
                          [Gimp.RunMode.NONINTERACTIVE,
                           image,
                           1,  # number of drawables
                           [layer],  # drawable array
                           radius_h,  # horizontal radius
                           radius_v,  # vertical radius
                           1])  # link radii

# Check result
if result.index(0) == Gimp.PDBStatusType.SUCCESS:
    print("Filter applied successfully")
```# GIMP 3.0 MCP Server - Complete Documentation

## Overview

The GIMP 3.0 MCP (Model Context Protocol) Server enables seamless integration between GIMP 3.0 and Claude Code, allowing AI-powered image editing workflows through natural language commands. This implementation is specifically designed for GIMP 3.0's new GObject Introspection-based Python API.

## Key GIMP 3.0 Compatibility Features

### New API Structure
- **GObject Introspection**: Uses `gi.repository` for all GIMP interactions
- **Procedure Database**: Access via `Gimp.get_pdb().run_procedure()`
- **File Operations**: Uses `Gio.File` objects for file handling
- **Layer Management**: New layer insertion and management methods
- **Display System**: Updated display creation and management

### GIMP 3.0 Specific Changes
- `Gimp.file_load()` and `Gimp.file_export()` with `Gio.File` objects
- `image.insert_layer()` instead of `pdb.gimp_image_add_layer()`
- `layer.set_offsets()` for positioning layers
- `Gimp.drawable_edit_fill()` for layer filling
- Modern blend mode constants (`Gimp.LayerMode.*`)
- **Color Handling**: Uses `Gegl.Color` instead of `Gimp.RGB`

### Color System Updates
GIMP 3.0 uses the Gegl color system:
```python
# OLD (GIMP 2.x): Gimp.RGB.new_with_values(1.0, 0.0, 0.0)
# NEW (GIMP 3.0): 
red_color = Gegl.Color.new("red")
# or
red_color = Gegl.Color()
red_color.set_rgba(1.0, 0.0, 0.0, 1.0)

# Set context colors
Gimp.Context.set_foreground(red_color)
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │◄──►│   MCP Server    │◄──►│   GIMP 3.0      │
│                 │    │                 │    │                 │
│ - Natural Lang  │    │ - Protocol      │    │ - New Python API│
│ - Workflows     │    │ - Tool Registry │    │ - GI Bindings   │
│ - Automation    │    │ - GIMP 3.0 API  │    │ - Modern PDB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

### Core Capabilities
- **Image Management**: Create, open, save images
- **Layer Operations**: Layer creation, manipulation, blending
- **Filters & Effects**: Blur, sharpen, artistic effects
- **Color Adjustments**: Brightness, contrast, hue-saturation
- **Selection Tools**: Rectangle, ellipse, free-form selections
- **Painting Tools**: Brush, pencil, airbrush operations
- **Transform Operations**: Scale, rotate, perspective

### Advanced Features
- **Batch Processing**: Process multiple images with same operations
- **Animated GIFs**: Create animations from image sequences
- **Pattern Generation**: Create seamless patterns and textures
- **Compositing**: Combine multiple images with blend modes
- **Macros**: Record and replay operation sequences
- **Presets**: Save and apply filter/adjustment presets
- **Style Transfer**: Apply artistic styles between images

## Installation

### Prerequisites
- **GIMP 3.0** with Python support
- **Python 3.8+** with pip
- **GObject Introspection** libraries
- **Claude Code** CLI tool

### Step 1: Install GIMP 3.0 and Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install gimp-3.0 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gegl-0.4

# Fedora/RHEL
sudo dnf install gimp python3-gobject python3-cairo-devel

# macOS (using Homebrew)
brew install gimp python3 pygobject3 gtk+3

# Install Python MCP dependencies
pip3 install --user mcp pygobject pillow numpy
```

### Step 2: Verify GIMP 3.0 Python Bindings
```bash
python3 -c "
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, Gegl
print('✓ GIMP 3.0 Python bindings available!')
print('✓ Gegl color system available!')
"
```

### Step 2: Run Setup Script
```bash
chmod +x setup_gimp_mcp.sh
./setup_gimp_mcp.sh
```

### Step 3: Configure Claude Code
Add to your Claude Code configuration:
```json
{
  "mcpServers": {
    "gimp": {
      "command": "python3",
      "args": ["~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/gimp_mcp_server.py"]
    }
  }
}
```

## Usage

### Basic Operations

#### Create New Image
```bash
claude-code "Create a new 1920x1080 image with white background"
```

#### Open Existing Image
```bash
claude-code "Open the image at ~/Photos/sunset.jpg"
```

#### Apply Filters
```bash
claude-code "Apply gaussian blur with radius 2.5 to the current layer"
claude-code "Apply sharpen filter to enhance details"
```

#### Color Adjustments
```bash
claude-code "Increase brightness by 10 and contrast by 15"
claude-code "Boost color saturation by 20%"
```

#### Layer Management
```bash
claude-code "Create a new layer called 'Overlay'"
claude-code "Set the layer blend mode to multiply"
claude-code "Reduce layer opacity to 70%"
```

### Advanced Workflows

#### Photo Enhancement
```bash
claude-code "Enhance the portrait at ~/Photos/portrait.jpg with professional adjustments"
```

#### Batch Processing
```bash
claude-code "Process all images in ~/Products/ by resizing to 800x600 and adding watermark"
```

#### Artistic Effects
```bash
claude-code "Apply oil painting effect with medium strength to create artistic version"
```

#### Create Social Media Variants
```bash
claude-code "Create Instagram square and story variants of the current image"
```

## GIMP 3.0 API Examples

### Creating Images (GIMP 3.0 Style)
```python
# Create new image
image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)

# Create layer
layer = Gimp.Layer.new(image, "Background", width, height, 
                      Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)

# Insert layer into image
image.insert_layer(layer, None, 0)

# Fill layer
Gimp.Context.set_foreground(Gimp.RGB.new_with_values(1.0, 1.0, 1.0))
Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
```

### File Operations (GIMP 3.0 Style)
```python
# Load image
file_obj = Gio.File.new_for_path(filepath)
image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)

# Export image
output_file = Gio.File.new_for_path(output_path)
layers = image.list_layers()
Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, layers, output_file)
```

### Using PDB Procedures (GIMP 3.0 Style)
```python
pdb = Gimp.get_pdb()

# Apply Gaussian blur
result = pdb.run_procedure("plug-in-gauss",
                          [Gimp.RunMode.NONINTERACTIVE,
                           image,
                           1,  # number of drawables
                           [layer],  # drawable array
                           radius_h,  # horizontal radius
                           radius_v,  # vertical radius
                           1])  # link radii

# Check result
if result.index(0) == Gimp.PDBStatusType.SUCCESS:
    print("Filter applied successfully")
```

#### `create_image`
Create a new GIMP image.
```json
{
  "width": 1920,
  "height": 1080,
  "name": "My Image"
}
```

#### `apply_filter`
Apply filters to the current layer.
```json
{
  "filter_name": "gaussian-blur",
  "parameters": {
    "radius": 2.5
  }
}
```

#### `adjust_colors`
Adjust color properties.
```json
{
  "adjustment": "brightness-contrast",
  "parameters": {
    "brightness": 10,
    "contrast": 15
  }
}
```

#### `paint_stroke`
Paint with brush tools.
```json
{
  "tool": "paintbrush",
  "brush": "Circle (03)",
  "color": "#FF0000",
  "opacity": 100,
  "size": 10,
  "points": [
    {"x": 100, "y": 100},
    {"x": 200, "y": 150}
  ]
}
```

### Advanced Tools

#### `create_animated_gif`
Create animated GIF from images.
```json
{
  "image_paths": ["frame1.jpg", "frame2.jpg", "frame3.jpg"],
  "frame_delay": 100,
  "loop_count": 0,
  "output_path": "animation.gif"
}
```

#### `batch_process_advanced`
Process multiple images with complex operations.
```json
{
  "input_directory": "~/Images/",
  "output_directory": "~/Processed/",
  "operations": [
    {
      "tool": "adjust_colors",
      "arguments": {
        "adjustment": "brightness-contrast",
        "parameters": {"brightness": 5, "contrast": 10}
      }
    }
  ],
  "parallel": true
}
```

#### `create_macro`
Create reusable operation sequences.
```json
{
  "macro_name": "photo_enhance",
  "description": "Basic photo enhancement",
  "operations": [
    {
      "tool": "adjust_colors",
      "arguments": {
        "adjustment": "levels",
        "parameters": {"shadows": 0.05, "highlights": 0.95}
      }
    },
    {
      "tool": "apply_filter",
      "arguments": {
        "filter_name": "sharpen",
        "parameters": {"amount": 0.5}
      }
    }
  ]
}
```

## Workflow Examples

### Professional Photo Enhancement
```python
# Multi-step enhancement workflow
workflow = [
    "Open image ~/Photos/raw_photo.jpg",
    "Duplicate layer as 'Original Backup'",
    "Apply automatic levels correction",
    "Adjust brightness +5 and contrast +12",
    "Increase saturation by 15%",
    "Apply noise reduction with strength 0.3",
    "Apply unsharp mask for final sharpening",
    "Save enhanced image to ~/Photos/enhanced_photo.jpg"
]
```

### Batch Product Photo Processing
```python
# Process product photos consistently
batch_workflow = [
    "Resize all images to 1000x1000 maintaining aspect ratio",
    "Apply white background replacement",
    "Enhance contrast and sharpness",
    "Add subtle drop shadow",
    "Save in web-optimized format"
]
```

### Creative Artistic Effects
```python
# Create artistic variations
artistic_workflow = [
    "Apply oil painting effect with strength 0.8",
    "Adjust colors for warmer tones",
    "Add canvas texture overlay",
    "Create vintage film look with grain",
    "Save as high-quality artistic print"
]
```

## Natural Language Commands

The system supports natural language commands that are automatically converted to MCP tool calls:

### Image Creation
- "Create a 1920x1080 image" → `create_image`
- "Make a new square image 800x800" → `create_image`

### Filtering
- "Blur the image with radius 3" → `apply_filter` (gaussian-blur)
- "Make it sharper" → `apply_filter` (sharpen)
- "Add some noise" → `apply_filter` (noise)

### Color Adjustments
- "Make it brighter" → `adjust_colors` (brightness-contrast)
- "Increase the saturation" → `adjust_colors` (hue-saturation)
- "Fix the white balance" → `adjust_colors` (color-balance)

### Transformations
- "Scale it to 50%" → `transform_layer` (scale)
- "Rotate 45 degrees" → `transform_layer` (rotate)
- "Flip horizontally" → `transform_layer` (flip)

## Troubleshooting

## Troubleshooting GIMP 3.0 Integration

### Common Issues

#### GIMP 3.0 Not Found
```bash
# Check GIMP 3.0 installation
which gimp-3.0
gimp-3.0 --version

# Install if missing (Ubuntu/Debian)
sudo apt install gimp-3.0

# Check for development version
which gimp-2.99
```

#### Gegl Color System Missing
```bash
# Install Gegl development packages
sudo apt install libgegl-dev gir1.2-gegl-0.4

# Test Gegl bindings
python3 -c "
import gi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
print('Gegl bindings available')
color = Gegl.Color.new('red')
print('Gegl color system working')
"
```

#### Color Operation Errors
```python
# WRONG (GIMP 2.x style)
color = Gimp.RGB.new_with_values(1.0, 0.0, 0.0)  # Will fail

# CORRECT (GIMP 3.0 style)
color = Gegl.Color.new("red")
# or
color = Gegl.Color()
color.set_rgba(1.0, 0.0, 0.0, 1.0)

# Set context
Gimp.Context.set_foreground(color)
```

#### GIMP 3.0 Plugin Not Loading
```bash
# Check plugin directory
ls ~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/

# Check plugin permissions
chmod +x ~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/*.py

# Test plugin manually
cd ~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/
python3 gimp-mcp-server.py
```

#### MCP Server Connection Issues
```bash
# Verify MCP configuration
cat ~/.config/claude-code/mcp_servers.json

# Test server manually with correct GIMP 3.0 paths
python3 ~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/gimp_mcp_server.py

# Check GIMP 3.0 is running
ps aux | grep gimp-3.0
```

#### Procedure Database Errors
```python
# Debug PDB calls in GIMP 3.0
pdb = Gimp.get_pdb()
procedures = pdb.query("")  # List all procedures
print("Available procedures:", len(procedures))

# Check specific procedure
proc_info = pdb.lookup_procedure("plug-in-gauss")
if proc_info:
    print("Procedure found:", proc_info.get_name())
else:
    print("Procedure not found")
```

### Debug Mode
Enable debug logging:
```bash
export GIMP_MCP_DEBUG=1
claude-code "Create test image"
```

## Performance Optimization

### Memory Management
- Use `duplicate_layer()` for non-destructive editing
- Close unused images to free memory
- Use lower resolution for preview operations

### Batch Processing
- Enable parallel processing for large batches
- Use appropriate thread limits based on system
- Monitor system resources during processing

### Network Optimization
- Use local file paths when possible
- Compress images for transfer if needed
- Cache frequently used assets

## Security Considerations

### File System Access
- MCP server runs with user permissions
- Validate all file paths before operations
- Sanitize user input for commands

### Network Security
- MCP communication uses local sockets
- No external network access required
- Validate all incoming requests

## Extension Development

### Adding New Tools
```python
@server.call_tool()
async def new_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "my_custom_tool":
        return await my_custom_implementation(arguments)
```

### Creating Custom Filters
```python
async def custom_filter(args: Dict[str, Any]) -> List[TextContent]:
    # Implement custom filter logic
    layer = current_image.get_active_layer()
    # Apply custom processing
    return [TextContent(type="text", text="Applied custom filter")]
```

### Plugin System
```python
class GimpMCPPlugin:
    def register_tools(self, server):
        # Register plugin-specific tools
        pass
    
    def register_resources(self, server):
        # Register plugin resources
        pass
```

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Add docstrings for all public methods

### Testing
```bash
# Run tests
python -m pytest tests/
# Test specific functionality
python -m pytest tests/test_filters.py
```

### Documentation
- Update API documentation for new features
- Add examples for complex workflows
- Include troubleshooting steps

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [Project Repository]
- Documentation: [Online Docs]
- Community: [Discord/Forum]

---

*This documentation is for GIMP MCP Server v1.0.0*