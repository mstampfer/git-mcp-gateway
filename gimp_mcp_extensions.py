#!/usr/bin/env python3
"""
GIMP MCP Extensions - Advanced features and protocol extensions
"""

import asyncio
import json
import base64
import io
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from PIL import Image as PILImage
import numpy as np

# Additional MCP types
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    CallToolResult,
    ResourceTemplate,
    Prompt,
    PromptMessage,
    PromptArgument
)

class GimpMCPExtensions:
    """Advanced GIMP MCP features and extensions"""
    
    def __init__(self, server):
        self.server = server
        self.setup_advanced_handlers()
        self.plugin_registry = {}
        self.macro_registry = {}
        self.preset_registry = {}
    
    def setup_advanced_handlers(self):
        """Setup advanced MCP handlers"""
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available GIMP workflow prompts"""
            return [
                Prompt(
                    name="photo_enhancement",
                    description="Enhance a photo with professional adjustments",
                    arguments=[
                        PromptArgument(
                            name="image_path",
                            description="Path to the image file",
                            required=True
                        ),
                        PromptArgument(
                            name="style",
                            description="Enhancement style (portrait, landscape, product)",
                            required=False
                        ),
                        PromptArgument(
                            name="intensity",
                            description="Enhancement intensity (subtle, moderate, strong)",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="artistic_filter",
                    description="Apply artistic effects to an image",
                    arguments=[
                        PromptArgument(
                            name="effect_type",
                            description="Type of artistic effect (oil_painting, watercolor, sketch, cartoon)",
                            required=True
                        ),
                        PromptArgument(
                            name="strength",
                            description="Effect strength (0.1-1.0)",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="batch_process",
                    description="Process multiple images with the same operations",
                    arguments=[
                        PromptArgument(
                            name="input_directory",
                            description="Directory containing images to process",
                            required=True
                        ),
                        PromptArgument(
                            name="operations",
                            description="JSON array of operations to apply",
                            required=True
                        ),
                        PromptArgument(
                            name="output_directory",
                            description="Directory to save processed images",
                            required=True
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> PromptMessage:
            """Get a specific prompt with arguments"""
            if name == "photo_enhancement":
                return await self.get_photo_enhancement_prompt(arguments)
            elif name == "artistic_filter":
                return await self.get_artistic_filter_prompt(arguments)
            elif name == "batch_process":
                return await self.get_batch_process_prompt(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")
        
        # Add new advanced tools
        self.register_advanced_tools()
    
    def register_advanced_tools(self):
        """Register advanced GIMP tools"""
        
        @self.server.call_tool()
        async def call_advanced_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle advanced tool calls"""
            
            if name == "create_animated_gif":
                return await self.create_animated_gif(arguments)
            elif name == "apply_style_transfer":
                return await self.apply_style_transfer(arguments)
            elif name == "generate_pattern":
                return await self.generate_pattern(arguments)
            elif name == "create_composite":
                return await self.create_composite(arguments)
            elif name == "extract_foreground":
                return await self.extract_foreground(arguments)
            elif name == "create_hdr":
                return await self.create_hdr(arguments)
            elif name == "panorama_stitch":
                return await self.panorama_stitch(arguments)
            elif name == "face_detection":
                return await self.face_detection(arguments)
            elif name == "color_match":
                return await self.color_match(arguments)
            elif name == "create_macro":
                return await self.create_macro(arguments)
            elif name == "run_macro":
                return await self.run_macro(arguments)
            elif name == "save_preset":
                return await self.save_preset(arguments)
            elif name == "load_preset":
                return await self.load_preset(arguments)
            elif name == "batch_process_advanced":
                return await self.batch_process_advanced(arguments)
            else:
                raise ValueError(f"Unknown advanced tool: {name}")
    
    async def get_photo_enhancement_prompt(self, args: Dict[str, str]) -> PromptMessage:
        """Generate photo enhancement prompt"""
        image_path = args["image_path"]
        style = args.get("style", "portrait")
        intensity = args.get("intensity", "moderate")
        
        # Analyze image to suggest enhancements
        image_info = await self.analyze_image(image_path)
        
        prompt_text = f"""
        Enhance the photo at {image_path} with the following specifications:
        
        Style: {style}
        Intensity: {intensity}
        
        Detected characteristics:
        - Dimensions: {image_info['width']}x{image_info['height']}
        - Dominant colors: {', '.join(image_info['dominant_colors'])}
        - Brightness level: {image_info['brightness']}
        - Contrast level: {image_info['contrast']}
        - Noise level: {image_info['noise_level']}
        
        Recommended enhancements:
        {self.get_enhancement_recommendations(image_info, style, intensity)}
        """
        
        return PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_text)
        )
    
    async def get_artistic_filter_prompt(self, args: Dict[str, str]) -> PromptMessage:
        """Generate artistic filter prompt"""
        effect_type = args["effect_type"]
        strength = float(args.get("strength", 0.7))
        
        filter_configs = {
            "oil_painting": {
                "brush_size": int(strength * 10),
                "roughness": strength * 0.8
            },
            "watercolor": {
                "paper_texture": strength,
                "color_bleeding": strength * 0.9
            },
            "sketch": {
                "pencil_hardness": 1.0 - strength,
                "line_density": strength
            },
            "cartoon": {
                "color_reduction": int((1.0 - strength) * 16) + 8,
                "edge_enhancement": strength * 2.0
            }
        }
        
        config = filter_configs.get(effect_type, {})
        
        prompt_text = f"""
        Apply {effect_type} artistic effect with strength {strength}:
        
        Configuration:
        {json.dumps(config, indent=2)}
        
        Steps:
        1. Duplicate current layer for backup
        2. Apply base artistic filter
        3. Adjust filter parameters
        4. Blend with original if needed
        5. Fine-tune colors and contrast
        """
        
        return PromptMessage(
            role="user", 
            content=TextContent(type="text", text=prompt_text)
        )
    
    async def create_animated_gif(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create animated GIF from multiple images or layers"""
        image_paths = args.get("image_paths", [])
        frame_delay = args.get("frame_delay", 100)  # milliseconds
        loop_count = args.get("loop_count", 0)  # 0 = infinite
        output_path = args["output_path"]
        
        if not image_paths:
            return [TextContent(type="text", text="No images provided for animation")]
        
        # Create new image for animation
        first_image = PILImage.open(image_paths[0])
        width, height = first_image.size
        
        await self.server.call_tool("create_image", {
            "width": width,
            "height": height,
            "name": "Animation"
        })
        
        # Add each image as a layer
        for i, image_path in enumerate(image_paths):
            await self.server.call_tool("create_layer", {"name": f"Frame_{i+1}"})
            await self.server.call_tool("import_image_as_layer", {"filepath": image_path})
        
        # Set animation properties
        await self.server.call_tool("set_animation_properties", {
            "frame_delay": frame_delay,
            "loop_count": loop_count
        })
        
        # Export as GIF
        await self.server.call_tool("export_animation", {
            "filepath": output_path,
            "format": "gif"
        })
        
        return [TextContent(type="text", text=f"Created animated GIF: {output_path}")]
    
    async def apply_style_transfer(self, args: Dict[str, Any]) -> List[TextContent]:
        """Apply neural style transfer (if available)"""
        content_image = args["content_image"]
        style_image = args["style_image"]
        output_path = args["output_path"]
        style_strength = args.get("style_strength", 0.7)
        
        # Open content image
        await self.server.call_tool("open_image", {"filepath": content_image})
        
        # Apply style transfer (this would require a neural network plugin)
        result = await self.server.call_tool("apply_filter", {
            "filter_name": "neural-style-transfer",
            "parameters": {
                "style_image": style_image,
                "strength": style_strength,
                "iterations": 100
            }
        })
        
        # Save result
        await self.server.call_tool("save_image", {"filepath": output_path})
        
        return [TextContent(type="text", text=f"Applied style transfer: {output_path}")]
    
    async def generate_pattern(self, args: Dict[str, Any]) -> List[TextContent]:
        """Generate seamless patterns"""
        pattern_type = args["pattern_type"]
        width = args["width"]
        height = args["height"]
        parameters = args.get("parameters", {})
        output_path = args["output_path"]
        
        # Create new image
        await self.server.call_tool("create_image", {
            "width": width,
            "height": height,
            "name": f"{pattern_type}_pattern"
        })
        
        # Generate pattern based on type
        if pattern_type == "geometric":
            await self.generate_geometric_pattern(parameters)
        elif pattern_type == "organic":
            await self.generate_organic_pattern(parameters)
        elif pattern_type == "texture":
            await self.generate_texture_pattern(parameters)
        
        # Make seamless
        await self.server.call_tool("apply_filter", {
            "filter_name": "make-seamless",
            "parameters": {}
        })
        
        # Save pattern
        await self.server.call_tool("save_image", {"filepath": output_path})
        
        return [TextContent(type="text", text=f"Generated pattern: {output_path}")]
    
    async def create_composite(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create complex composites from multiple images"""
        background_image = args["background_image"]
        foreground_images = args["foreground_images"]
        blend_modes = args.get("blend_modes", ["normal"] * len(foreground_images))
        opacities = args.get("opacities", [100] * len(foreground_images))
        output_path = args["output_path"]
        
        # Open background
        await self.server.call_tool("open_image", {"filepath": background_image})
        
        # Add foreground images as layers
        for i, (fg_image, blend_mode, opacity) in enumerate(zip(foreground_images, blend_modes, opacities)):
            await self.server.call_tool("create_layer", {"name": f"Foreground_{i+1}"})
            await self.server.call_tool("import_image_as_layer", {"filepath": fg_image})
            await self.server.call_tool("set_layer_blend_mode", {"mode": blend_mode})
            await self.server.call_tool("set_layer_opacity", {"opacity": opacity})
        
        # Save composite
        await self.server.call_tool("save_image", {"filepath": output_path})
        
        return [TextContent(type="text", text=f"Created composite: {output_path}")]
    
    async def extract_foreground(self, args: Dict[str, Any]) -> List[TextContent]:
        """Extract foreground using various methods"""
        image_path = args["image_path"]
        method = args.get("method", "auto")
        output_path = args["output_path"]
        
        # Open image
        await self.server.call_tool("open_image", {"filepath": image_path})
        
        if method == "auto":
            # Use automatic foreground extraction
            await self.server.call_tool("apply_filter", {
                "filter_name": "foreground-extract",
                "parameters": {"method": "auto"}
            })
        elif method == "color":
            # Use color-based selection
            bg_color = args.get("background_color", "#FFFFFF")
            tolerance = args.get("tolerance", 15)
            
            await self.server.call_tool("select_by_color", {
                "color": bg_color,
                "tolerance": tolerance
            })
            await self.server.call_tool("invert_selection", {})
            await self.server.call_tool("create_layer_from_selection", {})
        
        # Save extracted foreground
        await self.server.call_tool("save_image", {"filepath": output_path})
        
        return [TextContent(type="text", text=f"Extracted foreground: {output_path}")]
    
    async def create_macro(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a reusable macro from a sequence of operations"""
        macro_name = args["macro_name"]
        operations = args["operations"]
        description = args.get("description", "")
        
        # Validate operations
        for op in operations:
            if "tool" not in op or "arguments" not in op:
                return [TextContent(type="text", text="Invalid operation format")]
        
        # Save macro
        macro_data = {
            "name": macro_name,
            "description": description,
            "operations": operations,
            "created_at": asyncio.get_event_loop().time()
        }
        
        self.macro_registry[macro_name] = macro_data
        
        # Persist to disk
        await self.save_macro_to_disk(macro_name, macro_data)
        
        return [TextContent(type="text", text=f"Created macro: {macro_name}")]
    
    async def run_macro(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run a saved macro"""
        macro_name = args["macro_name"]
        
        if macro_name not in self.macro_registry:
            return [TextContent(type="text", text=f"Macro not found: {macro_name}")]
        
        macro = self.macro_registry[macro_name]
        results = []
        
        # Execute each operation in the macro
        for operation in macro["operations"]:
            try:
                result = await self.server.call_tool(operation["tool"], operation["arguments"])
                results.append(f"✓ {operation['tool']}: {result[0].text}")
            except Exception as e:
                results.append(f"✗ {operation['tool']}: {str(e)}")
                break  # Stop on first error
        
        return [TextContent(type="text", text=f"Macro '{macro_name}' executed:\n" + "\n".join(results))]
    
    async def save_preset(self, args: Dict[str, Any]) -> List[TextContent]:
        """Save current settings as a preset"""
        preset_name = args["preset_name"]
        preset_type = args["preset_type"]  # "filter", "adjustment", "brush", etc.
        settings = args["settings"]
        
        preset_data = {
            "name": preset_name,
            "type": preset_type,
            "settings": settings,
            "created_at": asyncio.get_event_loop().time()
        }
        
        self.preset_registry[preset_name] = preset_data
        await self.save_preset_to_disk(preset_name, preset_data)
        
        return [TextContent(type="text", text=f"Saved preset: {preset_name}")]
    
    async def load_preset(self, args: Dict[str, Any]) -> List[TextContent]:
        """Load and apply a saved preset"""
        preset_name = args["preset_name"]
        
        if preset_name not in self.preset_registry:
            return [TextContent(type="text", text=f"Preset not found: {preset_name}")]
        
        preset = self.preset_registry[preset_name]
        
        # Apply preset based on type
        if preset["type"] == "filter":
            await self.server.call_tool("apply_filter", {
                "filter_name": preset["settings"]["filter_name"],
                "parameters": preset["settings"]["parameters"]
            })
        elif preset["type"] == "adjustment":
            await self.server.call_tool("adjust_colors", {
                "adjustment": preset["settings"]["adjustment"],
                "parameters": preset["settings"]["parameters"]
            })
        elif preset["type"] == "brush":
            await self.server.call_tool("set_brush_settings", preset["settings"])
        
        return [TextContent(type="text", text=f"Applied preset: {preset_name}")]
    
    async def batch_process_advanced(self, args: Dict[str, Any]) -> List[TextContent]:
        """Advanced batch processing with complex operations"""
        input_dir = args["input_directory"]
        output_dir = args["output_directory"]
        operations = args["operations"]
        file_pattern = args.get("file_pattern", "*.jpg,*.png,*.tiff")
        parallel = args.get("parallel", False)
        
        # Get list of files
        files = []
        for pattern in file_pattern.split(","):
            files.extend(Path(input_dir).glob(pattern.strip()))
        
        if not files:
            return [TextContent(type="text", text="No files found matching pattern")]
        
        results = []
        
        if parallel:
            # Process files in parallel (limited concurrency)
            semaphore = asyncio.Semaphore(4)  # Limit to 4 concurrent operations
            
            async def process_file(file_path):
                async with semaphore:
                    return await self.process_single_file(file_path, output_dir, operations)
            
            tasks = [process_file(file_path) for file_path in files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Sequential processing
            for file_path in files:
                result = await self.process_single_file(file_path, output_dir, operations)
                results.append(result)
        
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        
        return [TextContent(type="text", text=f"Processed {success_count}/{len(files)} files")]
    
    async def process_single_file(self, file_path: Path, output_dir: str, operations: List[Dict]) -> Dict:
        """Process a single file with given operations"""
        try:
            # Open file
            await self.server.call_tool("open_image", {"filepath": str(file_path)})
            
            # Apply operations
            for operation in operations:
                await self.server.call_tool(operation["tool"], operation["arguments"])
            
            # Save processed file
            output_path = f"{output_dir}/{file_path.name}"
            await self.server.call_tool("save_image", {"filepath": output_path})
            
            return {"success": True, "input": str(file_path), "output": output_path}
            
        except Exception as e:
            return {"success": False, "input": str(file_path), "error": str(e)}
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image properties for enhancement recommendations"""
        # This would implement image analysis
        # For now, return mock data
        return {
            "width": 1920,
            "height": 1080,
            "dominant_colors": ["blue", "green", "white"],
            "brightness": 0.6,
            "contrast": 0.4,
            "noise_level": 0.3,
            "sharpness": 0.7
        }
    
    def get_enhancement_recommendations(self, image_info: Dict, style: str, intensity: str) -> str:
        """Generate enhancement recommendations based on image analysis"""
        recommendations = []
        
        if image_info["brightness"] < 0.4:
            recommendations.append("- Increase brightness")
        elif image_info["brightness"] > 0.8:
            recommendations.append("- Reduce brightness")
        
        if image_info["contrast"] < 0.5:
            recommendations.append("- Enhance contrast")
        
        if image_info["noise_level"] > 0.5:
            recommendations.append("- Apply noise reduction")
        
        if image_info["sharpness"] < 0.5:
            recommendations.append("- Apply sharpening")
        
        if style == "portrait":
            recommendations.append("- Enhance skin tones")
            recommendations.append("- Soften background")
        elif style == "landscape":
            recommendations.append("- Enhance sky contrast")
            recommendations.append("- Boost color saturation")
        
        return "\n".join(recommendations) if recommendations else "- No specific enhancements needed"
    
    async def save_macro_to_disk(self, name: str, macro_data: Dict):
        """Save macro to disk for persistence"""
        macros_dir = Path.home() / ".config" / "gimp-mcp" / "macros"
        macros_dir.mkdir(parents=True, exist_ok=True)
        
        with open(macros_dir / f"{name}.json", "w") as f:
            json.dump(macro_data, f, indent=2)
    
    async def save_preset_to_disk(self, name: str, preset_data: Dict):
        """Save preset to disk for persistence"""
        presets_dir = Path.home() / ".config" / "gimp-mcp" / "presets"
        presets_dir.mkdir(parents=True, exist_ok=True)
        
        with open(presets_dir / f"{name}.json", "w") as f:
            json.dump(preset_data, f, indent=2)
    
    async def load_macros_from_disk(self):
        """Load saved macros from disk"""
        macros_dir = Path.home() / ".config" / "gimp-mcp" / "macros"
        
        if not macros_dir.exists():
            return
        
        for macro_file in macros_dir.glob("*.json"):
            try:
                with open(macro_file, "r") as f:
                    macro_data = json.load(f)
                    self.macro_registry[macro_data["name"]] = macro_data
            except Exception as e:
                print(f"Error loading macro {macro_file}: {e}")
    
    async def load_presets_from_disk(self):
        """Load saved presets from disk"""
        presets_dir = Path.home() / ".config" / "gimp-mcp" / "presets"
        
        if not presets_dir.exists():
            return
        
        for preset_file in presets_dir.glob("*.json"):
            try:
                with open(preset_file, "r") as f:
                    preset_data = json.load(f)
                    self.preset_registry[preset_data["name"]] = preset_data
            except Exception as e:
                print(f"Error loading preset {preset_file}: {e}")

# Claude Code Integration Helper
class ClaudeCodeHelper:
    """Helper for Claude Code integration with GIMP MCP"""
    
    def __init__(self):
        self.command_history = []
        self.current_session = None
    
    def generate_command_suggestions(self, context: str) -> List[str]:
        """Generate command suggestions based on context"""
        suggestions = []
        
        if "photo" in context.lower():
            suggestions.extend([
                "Enhance this photo with professional adjustments",
                "Apply noise reduction to improve image quality",
                "Adjust color balance for better skin tones",
                "Create a black and white artistic version"
            ])
        
        if "batch" in context.lower():
            suggestions.extend([
                "Process all images in this folder with the same adjustments",
                "Resize all images to web-friendly dimensions",
                "Add watermark to all product photos",
                "Convert all images to a consistent format"
            ])
        
        if "creative" in context.lower():
            suggestions.extend([
                "Apply an artistic oil painting effect",
                "Create a vintage film look with grain and colors",
                "Generate a double exposure effect",
                "Add dramatic lighting and shadows"
            ])
        
        return suggestions
    
    def parse_natural_language_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language command into MCP tool calls"""
        # Simple parsing - in practice, this would use NLP
        command_lower = command.lower()
        
        if "create" in command_lower and "image" in command_lower:
            # Extract dimensions if mentioned
            import re
            size_match = re.search(r'(\d+)x(\d+)', command)
            if size_match:
                width, height = int(size_match.group(1)), int(size_match.group(2))
            else:
                width, height = 1920, 1080
            
            return {
                "tool": "create_image",
                "arguments": {"width": width, "height": height}
            }
        
        elif "blur" in command_lower:
            # Extract blur radius
            radius_match = re.search(r'radius\s*(\d+(?:\.\d+)?)', command_lower)
            radius = float(radius_match.group(1)) if radius_match else 2.0
            
            return {
                "tool": "apply_filter",
                "arguments": {
                    "filter_name": "gaussian-blur",
                    "parameters": {"radius": radius}
                }
            }
        
        elif "enhance" in command_lower:
            return {
                "tool": "photo_enhancement",
                "arguments": {
                    "style": "auto",
                    "intensity": "moderate"
                }
            }
        
        # Default fallback
        return {
            "tool": "get_image_info",
            "arguments": {}
        }
    
    def generate_workflow_script(self, workflow_name: str, parameters: Dict) -> str:
        """Generate a complete workflow script"""
        scripts = {
            "photo_enhancement": f"""
# Photo Enhancement Workflow
# Parameters: {json.dumps(parameters, indent=2)}

# 1. Open and prepare image
claude-code "Open image {parameters.get('input_path', 'current image')}"
claude-code "Duplicate current layer as 'Original Backup'"

# 2. Basic corrections
claude-code "Apply automatic levels correction"
claude-code "Adjust brightness +{parameters.get('brightness', 5)} and contrast +{parameters.get('contrast', 10)}"

# 3. Color enhancements
claude-code "Increase saturation by {parameters.get('saturation', 15)}%"
claude-code "Apply selective color correction to enhance skin tones"

# 4. Sharpening and noise reduction
claude-code "Apply noise reduction with strength {parameters.get('noise_reduction', 0.3)}"
claude-code "Apply unsharp mask for final sharpening"

# 5. Save result
claude-code "Save enhanced image to {parameters.get('output_path', 'enhanced_image.jpg')}"
""",
            
            "batch_resize": f"""
# Batch Resize Workflow
# Parameters: {json.dumps(parameters, indent=2)}

# Process all images in directory
claude-code "Process all images in {parameters.get('input_dir', './images')} with operations: [
    {{
        'tool': 'transform_layer',
        'arguments': {{
            'operation': 'scale',
            'parameters': {{
                'width': {parameters.get('width', 800)},
                'height': {parameters.get('height', 600)},
                'maintain_aspect': true
            }}
        }}
    }}
]"
""",
            
            "artistic_effect": f"""
# Artistic Effect Workflow
# Parameters: {json.dumps(parameters, indent=2)}

# Apply artistic transformation
claude-code "Apply {parameters.get('effect', 'oil_painting')} effect with strength {parameters.get('strength', 0.7)}"
claude-code "Adjust colors to enhance artistic appearance"
claude-code "Add subtle texture overlay for more authenticity"
claude-code "Save artistic version to {parameters.get('output_path', 'artistic_result.jpg')}"
"""
        }
        
        return scripts.get(workflow_name, "# Unknown workflow")

# Example usage and testing
async def test_extensions():
    """Test the GIMP MCP extensions"""
    print("Testing GIMP MCP Extensions...")
    
    # Mock server for testing
    class MockServer:
        async def call_tool(self, name, args):
            return [TextContent(type="text", text=f"Mock result for {name}")]
    
    server = MockServer()
    extensions = GimpMCPExtensions(server)
    
    # Test macro creation
    macro_ops = [
        {"tool": "adjust_colors", "arguments": {"adjustment": "brightness-contrast", "parameters": {"brightness": 10, "contrast": 15}}},
        {"tool": "apply_filter", "arguments": {"filter_name": "gaussian-blur", "parameters": {"radius": 1.0}}},
        {"tool": "apply_filter", "arguments": {"filter_name": "sharpen", "parameters": {"amount": 0.5}}}
    ]
    
    result = await extensions.create_macro({
        "macro_name": "photo_enhance",
        "operations": macro_ops,
        "description": "Basic photo enhancement"
    })
    
    print(f"Macro creation result: {result[0].text}")
    
    # Test Claude Code helper
    helper = ClaudeCodeHelper()
    suggestions = helper.generate_command_suggestions("I want to enhance my photos")
    print(f"Command suggestions: {suggestions}")
    
    # Test natural language parsing
    parsed = helper.parse_natural_language_command("Create a 1920x1080 image")
    print(f"Parsed command: {parsed}")

if __name__ == "__main__":
    asyncio.run(test_extensions())