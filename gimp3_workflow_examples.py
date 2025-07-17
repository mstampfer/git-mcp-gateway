#!/usr/bin/env python3
"""
GIMP 3.0 Claude Code Workflow Examples
Complete examples using the correct GIMP 3.0 API
"""

import asyncio
import json
from typing import Dict, List, Any
from pathlib import Path

# GIMP 3.0 imports
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, GimpUi, GObject, GLib, Gio, Gegl

class GIMP3WorkflowExamples:
    """Complete GIMP 3.0 workflow examples for Claude Code"""
    
    def __init__(self):
        self.pdb = Gimp.get_pdb()
    
    async def professional_photo_enhancement(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """Professional photo enhancement using GIMP 3.0 API"""
        try:
            # Load image
            file_obj = Gio.File.new_for_path(image_path)
            image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)
            
            if not image:
                return {"error": f"Failed to load {image_path}"}
            
            # Get the main layer
            layers = image.list_layers()
            if not layers:
                return {"error": "No layers found in image"}
            
            main_layer = layers[0]
            
            # Step 1: Create backup layer
            backup_layer = main_layer.copy()
            backup_layer.set_name("Original Backup")
            image.insert_layer(backup_layer, None, -1)
            
            # Step 2: Auto levels adjustment
            result = self.pdb.run_procedure("gimp-drawable-levels-stretch", [main_layer])
            
            # Step 3: Brightness/Contrast enhancement
            result = self.pdb.run_procedure("gimp-drawable-brightness-contrast",
                                          [main_layer, 0.05, 0.1])  # +5 brightness, +10 contrast
            
            # Step 4: Color saturation boost
            result = self.pdb.run_procedure("gimp-drawable-hue-saturation",
                                          [main_layer,
                                           Gimp.HueRange.ALL,
                                           0,    # hue
                                           0,    # lightness
                                           15,   # saturation
                                           0])   # overlap
            
            # Step 5: Noise reduction (using blur with layer mask)
            noise_layer = main_layer.copy()
            noise_layer.set_name("Noise Reduction")
            image.insert_layer(noise_layer, None, 0)
            
            # Apply slight blur for noise reduction
            result = self.pdb.run_procedure("plug-in-gauss",
                                          [Gimp.RunMode.NONINTERACTIVE,
                                           image,
                                           1,
                                           [noise_layer],
                                           0.8,  # horizontal radius
                                           0.8,  # vertical radius
                                           1])   # link
            
            # Set blend mode and opacity for subtle effect
            noise_layer.set_mode(Gimp.LayerMode.NORMAL)
            noise_layer.set_opacity(30.0)
            
            # Step 6: Unsharp mask for final sharpening
            result = self.pdb.run_procedure("plug-in-unsharp-mask",
                                          [Gimp.RunMode.NONINTERACTIVE,
                                           image,
                                           1,
                                           [main_layer],
                                           1.0,   # radius
                                           0.5,   # amount
                                           0])    # threshold
            
            # Step 7: Flatten and save
            image.flatten()
            final_layers = image.list_layers()
            
            output_file = Gio.File.new_for_path(output_path)
            Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, final_layers, output_file)
            
            # Create display for preview
            display = Gimp.Display.new(image)
            
            return {
                "success": True,
                "input": image_path,
                "output": output_path,
                "operations": [
                    "Created backup layer",
                    "Applied auto levels",
                    "Enhanced brightness/contrast",
                    "Boosted color saturation", 
                    "Applied noise reduction",
                    "Applied unsharp mask sharpening",
                    "Flattened and exported"
                ]
            }
            
        except Exception as e:
            return {"error": f"Enhancement failed: {str(e)}"}
    
    async def create_artistic_oil_painting(self, image_path: str, output_path: str, 
                                         brush_size: int = 8, roughness: int = 1) -> Dict[str, Any]:
        """Create oil painting effect using GIMP 3.0"""
        try:
            # Load image
            file_obj = Gio.File.new_for_path(image_path)
            image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)
            
            layers = image.list_layers()
            if not layers:
                return {"error": "No layers found"}
            
            main_layer = layers[0]
            
            # Create working copy
            oil_layer = main_layer.copy()
            oil_layer.set_name("Oil Painting Effect")
            image.insert_layer(oil_layer, None, 0)
            
            # Apply oil painting filter
            result = self.pdb.run_procedure("plug-in-oilify",
                                          [Gimp.RunMode.NONINTERACTIVE,
                                           image,
                                           1,
                                           [oil_layer],
                                           brush_size,  # mask size
                                           roughness])  # exponent
            
            # Enhance colors for more artistic look
            result = self.pdb.run_procedure("gimp-drawable-hue-saturation",
                                          [oil_layer,
                                           Gimp.HueRange.ALL,
                                           0,    # hue
                                           5,    # lightness
                                           20,   # saturation boost
                                           0])   # overlap
            
            # Add slight contrast
            result = self.pdb.run_procedure("gimp-drawable-brightness-contrast",
                                          [oil_layer, 0.0, 0.15])
            
            # Export result
            output_file = Gio.File.new_for_path(output_path)
            Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, [oil_layer], output_file)
            
            display = Gimp.Display.new(image)
            
            return {
                "success": True,
                "effect": "Oil Painting",
                "input": image_path,
                "output": output_path,
                "parameters": {"brush_size": brush_size, "roughness": roughness}
            }
            
        except Exception as e:
            return {"error": f"Oil painting effect failed: {str(e)}"}
    
    async def batch_resize_and_watermark(self, input_dir: str, output_dir: str, 
                                       watermark_path: str, target_width: int = 800) -> Dict[str, Any]:
        """Batch process images with resize and watermark using GIMP 3.0"""
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Get image files
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']:
                image_files.extend(input_path.glob(ext))
                image_files.extend(input_path.glob(ext.upper()))
            
            if not image_files:
                return {"error": "No image files found"}
            
            # Load watermark
            watermark_file = Gio.File.new_for_path(watermark_path)
            watermark_image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, watermark_file)
            watermark_layers = watermark_image.list_layers()
            
            if not watermark_layers:
                return {"error": "Watermark image has no layers"}
            
            watermark_layer = watermark_layers[0]
            
            processed_files = []
            
            for image_file in image_files:
                try:
                    # Load image
                    file_obj = Gio.File.new_for_path(str(image_file))
                    image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)
                    
                    layers = image.list_layers()
                    if not layers:
                        continue
                    
                    # Resize image
                    original_width = image.get_width()
                    original_height = image.get_height()
                    
                    if original_width > target_width:
                        scale_factor = target_width / original_width
                        new_height = int(original_height * scale_factor)
                        image.scale(target_width, new_height)
                    
                    # Copy watermark layer
                    wm_copy = watermark_layer.copy()
                    wm_copy.set_name("Watermark")
                    image.insert_layer(wm_copy, None, 0)
                    
                    # Position watermark at bottom right
                    img_width = image.get_width()
                    img_height = image.get_height()
                    wm_width = wm_copy.get_width()
                    wm_height = wm_copy.get_height()
                    
                    # Scale watermark if too large
                    max_wm_size = min(img_width // 4, img_height // 4)
                    if wm_width > max_wm_size or wm_height > max_wm_size:
                        scale = max_wm_size / max(wm_width, wm_height)
                        new_wm_width = int(wm_width * scale)
                        new_wm_height = int(wm_height * scale)
                        wm_copy.scale(new_wm_width, new_wm_height, False)
                    
                    # Position watermark
                    wm_x = img_width - wm_copy.get_width() - 20
                    wm_y = img_height - wm_copy.get_height() - 20
                    wm_copy.set_offsets(wm_x, wm_y)
                    
                    # Set watermark opacity
                    wm_copy.set_opacity(70.0)
                    
                    # Flatten image
                    image.flatten()
                    final_layers = image.list_layers()
                    
                    # Save processed image
                    output_file_path = output_path / image_file.name
                    output_file = Gio.File.new_for_path(str(output_file_path))
                    Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, final_layers, output_file)
                    
                    processed_files.append(str(output_file_path))
                    
                    # Clean up
                    image.delete()
                    
                except Exception as e:
                    print(f"Error processing {image_file}: {e}")
                    continue
            
            # Clean up watermark image
            watermark_image.delete()
            
            return {
                "success": True,
                "processed_count": len(processed_files),
                "total_files": len(image_files),
                "output_directory": str(output_path),
                "target_width": target_width
            }
            
        except Exception as e:
            return {"error": f"Batch processing failed: {str(e)}"}
    
    async def create_social_media_variants(self, source_image: str, output_dir: str) -> Dict[str, Any]:
        """Create social media format variants using GIMP 3.0"""
        try:
            # Load source image
            source_file = Gio.File.new_for_path(source_image)
            source_img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, source_file)
            
            source_layers = source_img.list_layers()
            if not source_layers:
                return {"error": "Source image has no layers"}
            
            source_layer = source_layers[0]
            
            # Define social media formats
            formats = {
                "instagram_square": (1080, 1080),
                "instagram_story": (1080, 1920),
                "twitter_post": (1200, 675),
                "facebook_cover": (1200, 630),
                "linkedin_post": (1200, 627)
            }
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            created_variants = []
            
            for format_name, (width, height) in formats.items():
                try:
                    # Create new image with target dimensions
                    new_image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)
                    
                    # Create background layer
                    bg_layer = Gimp.Layer.new(new_image, "Background", width, height,
                                            Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
                    new_image.insert_layer(bg_layer, None, 0)
                    
                    # Fill with white background
                    white_color = Gegl.Color.new("white")
                    Gimp.Context.set_foreground(white_color)
                    Gimp.drawable_edit_fill(bg_layer, Gimp.FillType.FOREGROUND)
                    
                    # Copy and scale source layer
                    scaled_layer = source_layer.copy()
                    scaled_layer.set_name("Content")
                    new_image.insert_layer(scaled_layer, None, 0)
                    
                    # Calculate scaling to fit while maintaining aspect ratio
                    source_width = scaled_layer.get_width()
                    source_height = scaled_layer.get_height()
                    
                    scale_x = width / source_width
                    scale_y = height / source_height
                    scale = min(scale_x, scale_y)  # Maintain aspect ratio
                    
                    # Scale the layer
                    new_width = int(source_width * scale)
                    new_height = int(source_height * scale)
                    scaled_layer.scale(new_width, new_height, False)
                    
                    # Center the scaled layer
                    offset_x = (width - new_width) // 2
                    offset_y = (height - new_height) // 2
                    scaled_layer.set_offsets(offset_x, offset_y)
                    
                    # Flatten image
                    new_image.flatten()
                    final_layers = new_image.list_layers()
                    
                    # Save variant
                    output_file_path = output_path / f"{format_name}.jpg"
                    output_file = Gio.File.new_for_path(str(output_file_path))
                    Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, new_image, final_layers, output_file)
                    
                    created_variants.append({
                        "format": format_name,
                        "dimensions": f"{width}x{height}",
                        "output": str(output_file_path)
                    })
                    
                    # Clean up
                    new_image.delete()
                    
                except Exception as e:
                    print(f"Error creating {format_name}: {e}")
                    continue
            
            # Clean up source image
            source_img.delete()
            
            return {
                "success": True,
                "source": source_image,
                "variants_created": len(created_variants),
                "variants": created_variants
            }
            
        except Exception as e:
            return {"error": f"Social media variants creation failed: {str(e)}"}
    
    async def create_vintage_effect(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """Create vintage film effect using GIMP 3.0"""
        try:
            # Load image
            file_obj = Gio.File.new_for_path(image_path)
            image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)
            
            layers = image.list_layers()
            if not layers:
                return {"error": "No layers found"}
            
            main_layer = layers[0]
            
            # Step 1: Create sepia base
            sepia_layer = main_layer.copy()
            sepia_layer.set_name("Sepia Base")
            image.insert_layer(sepia_layer, None, 0)
            
            # Desaturate
            result = self.pdb.run_procedure("gimp-drawable-desaturate",
                                          [sepia_layer, Gimp.DesaturateMode.LUMINANCE])
            
            # Apply sepia color
            result = self.pdb.run_procedure("gimp-drawable-color-balance",
                                          [sepia_layer,
                                           Gimp.TransferMode.HIGHLIGHTS,
                                           True,  # preserve luminosity
                                           -30,   # cyan-red (towards red)
                                           -20,   # magenta-green (towards magenta)
                                           -40])  # yellow-blue (towards yellow)
            
            # Step 2: Add film grain
            grain_layer = Gimp.Layer.new(image, "Film Grain", 
                                       image.get_width(), image.get_height(),
                                       Gimp.ImageType.RGB_IMAGE, 50.0, Gimp.LayerMode.OVERLAY)
            image.insert_layer(grain_layer, None, 0)
            
            # Fill with neutral gray
            gray_color = Gegl.Color.new("gray50")
            Gimp.Context.set_foreground(gray_color)
            Gimp.drawable_edit_fill(grain_layer, Gimp.FillType.FOREGROUND)
            
            # Add noise for grain effect
            result = self.pdb.run_procedure("plug-in-noise-rgb",
                                          [Gimp.RunMode.NONINTERACTIVE,
                                           image,
                                           1,
                                           [grain_layer],
                                           True,   # independent RGB
                                           0.3,    # noise amount
                                           0.3,    # noise amount
                                           0.3,    # noise amount
                                           0.0])   # gamma
            
            # Step 3: Add vignette effect
            vignette_layer = Gimp.Layer.new(image, "Vignette",
                                          image.get_width(), image.get_height(),
                                          Gimp.ImageType.RGB_IMAGE, 60.0, Gimp.LayerMode.MULTIPLY)
            image.insert_layer(vignette_layer, None, 0)
            
            # Create radial gradient for vignette
            white_color = Gegl.Color.new("white")
            dark_color = Gegl.Color.new("rgb(0.2, 0.2, 0.2)")
            Gimp.Context.set_foreground(white_color)
            Gimp.Context.set_background(dark_color)
            
            # Apply radial gradient from center
            center_x = image.get_width() / 2
            center_y = image.get_height() / 2
            radius = min(image.get_width(), image.get_height()) * 0.7
            
            result = self.pdb.run_procedure("gimp-drawable-edit-gradient-fill",
                                          [vignette_layer,
                                           Gimp.GradientType.RADIAL,
                                           0.0,     # offset
                                           False,   # supersample
                                           0,       # supersample depth
                                           0.0,     # supersample threshold
                                           True,    # dither
                                           center_x - radius, center_y - radius,
                                           center_x + radius, center_y + radius])
            
            # Step 4: Reduce contrast slightly for aged look
            result = self.pdb.run_procedure("gimp-drawable-brightness-contrast",
                                          [sepia_layer, 0.1, -0.15])  # slight brightness, less contrast
            
            # Step 5: Flatten and save
            image.flatten()
            final_layers = image.list_layers()
            
            output_file = Gio.File.new_for_path(output_path)
            Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, final_layers, output_file)
            
            display = Gimp.Display.new(image)
            
            return {
                "success": True,
                "effect": "Vintage Film",
                "input": image_path,
                "output": output_path,
                "operations": [
                    "Applied sepia tone",
                    "Added film grain texture",
                    "Created vignette effect",
                    "Adjusted contrast for aged look"
                ]
            }
            
        except Exception as e:
            return {"error": f"Vintage effect failed: {str(e)}"}

# Claude Code Integration Functions
class ClaudeCodeGIMP3Integration:
    """Claude Code integration helpers for GIMP 3.0"""
    
    def __init__(self):
        self.workflows = GIMP3WorkflowExamples()
    
    def parse_enhancement_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language enhancement commands"""
        command_lower = command.lower()
        
        # Extract file paths
        import re
        
        # Look for file paths
        path_patterns = [
            r'~/[^\s]+',
            r'/[^\s]+',
            r'[a-zA-Z]:[^\s]+',
            r'\./[^\s]+'
        ]
        
        input_path = None
        output_path = None
        
        for pattern in path_patterns:
            matches = re.findall(pattern, command)
            if matches:
                if not input_path:
                    input_path = matches[0]
                elif not output_path:
                    output_path = matches[1] if len(matches) > 1 else None
        
        # Determine workflow type
        if "enhance" in command_lower or "improve" in command_lower:
            workflow = "professional_enhancement"
        elif "oil" in command_lower or "painting" in command_lower:
            workflow = "oil_painting"
        elif "vintage" in command_lower or "sepia" in command_lower:
            workflow = "vintage_effect"
        elif "social" in command_lower or "instagram" in command_lower:
            workflow = "social_media"
        elif "batch" in command_lower or "multiple" in command_lower:
            workflow = "batch_process"
        else:
            workflow = "professional_enhancement"  # default
        
        return {
            "workflow": workflow,
            "input_path": input_path,
            "output_path": output_path,
            "command": command
        }
    
    async def execute_workflow(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the parsed workflow"""
        workflow = parsed_command["workflow"]
        input_path = parsed_command["input_path"]
        output_path = parsed_command["output_path"]
        
        if not input_path:
            return {"error": "No input file specified"}
        
        if not output_path:
            # Generate output path
            from pathlib import Path
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"processed_{input_file.name}")
        
        if workflow == "professional_enhancement":
            return await self.workflows.professional_photo_enhancement(input_path, output_path)
        elif workflow == "oil_painting":
            return await self.workflows.create_artistic_oil_painting(input_path, output_path)
        elif workflow == "vintage_effect":
            return await self.workflows.create_vintage_effect(input_path, output_path)
        elif workflow == "social_media":
            output_dir = str(Path(output_path).parent / "social_media_variants")
            return await self.workflows.create_social_media_variants(input_path, output_dir)
        else:
            return {"error": f"Unknown workflow: {workflow}"}

# Example usage functions
async def example_professional_enhancement():
    """Example: Professional photo enhancement"""
    workflows = GIMP3WorkflowExamples()
    
    result = await workflows.professional_photo_enhancement(
        "~/Photos/portrait.jpg",
        "~/Photos/enhanced_portrait.jpg"
    )
    
    print("Professional Enhancement Result:")
    print(json.dumps(result, indent=2))

async def example_artistic_oil_painting():
    """Example: Create oil painting effect"""
    workflows = GIMP3WorkflowExamples()
    
    result = await workflows.create_artistic_oil_painting(
        "~/Photos/landscape.jpg",
        "~/Photos/oil_painting_landscape.jpg",
        brush_size=12,
        roughness=2
    )
    
    print("Oil Painting Effect Result:")
    print(json.dumps(result, indent=2))

async def example_batch_processing():
    """Example: Batch resize and watermark"""
    workflows = GIMP3WorkflowExamples()
    
    result = await workflows.batch_resize_and_watermark(
        "~/Photos/Products/",
        "~/Photos/Processed/",
        "~/Branding/watermark.png",
        target_width=1000
    )
    
    print("Batch Processing Result:")
    print(json.dumps(result, indent=2))

async def example_social_media_variants():
    """Example: Create social media variants"""
    workflows = GIMP3WorkflowExamples()
    
    result = await workflows.create_social_media_variants(
        "~/Photos/brand_image.jpg",
        "~/Photos/SocialMedia/"
    )
    
    print("Social Media Variants Result:")
    print(json.dumps(result, indent=2))

async def example_claude_code_integration():
    """Example: Claude Code natural language processing"""
    integration = ClaudeCodeGIMP3Integration()
    
    # Example commands
    commands = [
        "Enhance the photo at ~/Photos/portrait.jpg professionally",
        "Create an oil painting effect from ~/Photos/landscape.jpg",
        "Make social media variants of ~/Branding/logo.png",
        "Apply vintage effect to ~/Photos/family.jpg"
    ]
    
    for command in commands:
        print(f"\nProcessing: {command}")
        parsed = integration.parse_enhancement_command(command)
        print(f"Parsed: {parsed}")
        
        # Note: Actual execution would require GIMP to be running
        # result = await integration.execute_workflow(parsed)
        # print(f"Result: {result}")

def main():
    """Main function for testing"""
    print("GIMP 3.0 Claude Code Workflow Examples")
    print("=====================================")
    
    # Run examples (uncomment to test with actual GIMP)
    # asyncio.run(example_professional_enhancement())
    # asyncio.run(example_artistic_oil_painting())
    # asyncio.run(example_batch_processing())
    # asyncio.run(example_social_media_variants())
    
    # Test command parsing
    asyncio.run(example_claude_code_integration())

if __name__ == "__main__":
    main()