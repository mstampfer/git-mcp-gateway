# GIMP MCP Server - Complete Documentation

## Overview

The GIMP MCP (Model Context Protocol) Server enables seamless integration between GIMP 3.0 and Claude Code, allowing AI-powered image editing workflows through natural language commands.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │◄──►│   MCP Server    │◄──►│   GIMP 3.0      │
│                 │    │                 │    │                 │
│ - Natural Lang  │    │ - Protocol      │    │ - Image Editing │
│ - Workflows     │    │ - Tool Registry │    │ - Filters       │
│ - Automation    │    │ - Extensions    │    │ - Painting      │
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
- GIMP 3.0 installed
- Python 3.8+ with pip
- Claude Code CLI tool

### Step 1: Install Dependencies
```bash
pip install mcp gi-python pygobject pillow numpy
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

## API Reference

### Core Tools

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

### Common Issues

#### GIMP 3.0 Not Found
```bash
# Check GIMP installation
which gimp-3.0
# Install if missing (Ubuntu/Debian)
sudo apt install gimp-3.0
```

#### Python Dependencies Missing
```bash
# Install missing packages
pip install --user mcp gi-python pygobject
```

#### MCP Server Not Starting
```bash
# Check Python path
python3 -c "import gi; print('GI available')"
# Check GIMP Python bindings
python3 -c "import gi; gi.require_version('Gimp', '3.0'); print('GIMP bindings OK')"
```

#### Claude Code Connection Issues
```bash
# Verify MCP configuration
cat ~/.config/claude-code/mcp_servers.json
# Test server manually
python3 ~/.config/GIMP/3.0/plug-ins/gimp-mcp-server/gimp_mcp_server.py
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