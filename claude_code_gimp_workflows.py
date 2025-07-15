#!/usr/bin/env python3
"""
Claude Code GIMP Workflow Examples
Advanced automation scripts for GIMP via MCP
"""

import asyncio
import json
from typing import Dict, List, Any
from pathlib import Path

class GimpWorkflowManager:
    """Manages complex GIMP workflows through Claude Code"""
    
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        
    async def photo_enhancement_workflow(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """Complete photo enhancement workflow"""
        workflow_steps = []
        
        # 1. Open image
        result = await self.mcp.call_tool("open_image", {"filepath": image_path})
        workflow_steps.append(f"Opened: {image_path}")
        
        # 2. Duplicate layer for non-destructive editing
        await self.mcp.call_tool("create_layer", {"name": "Original Copy"})
        workflow_steps.append("Created backup layer")
        
        # 3. Basic color correction
        await self.mcp.call_tool("adjust_colors", {
            "adjustment": "levels",
            "parameters": {"shadows": 0.05, "midtones": 1.2, "highlights": 0.95}
        })
        workflow_steps.append("Applied levels adjustment")
        
        # 4. Enhance contrast
        await self.mcp.call_tool("adjust_colors", {
            "adjustment": "brightness-contrast",
            "parameters": {"brightness": 5, "contrast": 15}
        })
        workflow_steps.append("Enhanced contrast")
        
        # 5. Color saturation boost
        await self.mcp.call_tool("adjust_colors", {
            "adjustment": "hue-saturation",
            "parameters": {"saturation": 10}
        })
        workflow_steps.append("Boosted saturation")
        
        # 6. Noise reduction
        await self.mcp.call_tool("apply_filter", {
            "filter_name": "noise-reduction",
            "parameters": {"strength": 0.3}
        })
        workflow_steps.append("Applied noise reduction")
        
        # 7. Sharpen for output
        await self.mcp.call_tool("apply_filter", {
            "filter_name": "unsharp-mask",
            "parameters": {"amount": 0.8, "radius": 1.0, "threshold": 0.05}
        })
        workflow_steps.append("Applied sharpening")
        
        # 8. Save enhanced image
        await self.mcp.call_tool("save_image", {"filepath": output_path})
        workflow_steps.append(f"Saved: {output_path}")
        
        return {
            "workflow": "photo_enhancement",
            "steps": workflow_steps,
            "input": image_path,
            "output": output_path
        }
    
    async def create_social_media_variants(self, image_path: str, output_dir: str) -> List[Dict[str, Any]]:
        """Create multiple social media format variants"""
        variants = []
        
        # Open original image
        await self.mcp.call_tool("open_image", {"filepath": image_path})
        
        # Get image info
        info_result = await self.mcp.call_tool("get_image_info", {})
        original_info = json.loads(info_result[0].text)
        
        # Define social media formats
        formats = {
            "instagram_square": {"width": 1080, "height": 1080},
            "instagram_story": {"width": 1080, "height": 1920},
            "twitter_post": {"width": 1200, "height": 675},
            "facebook_cover": {"width": 1200, "height": 630},
            "linkedin_post": {"width": 1200, "height": 627}
        }
        
        for format_name, dimensions in formats.items():
            # Create new image with specific dimensions
            await self.mcp.call_tool("create_image", {
                "width": dimensions["width"],
                "height": dimensions["height"],
                "name": f"{format_name}_variant"
            })
            
            # Calculate scaling to fit original image
            scale_x = dimensions["width"] / original_info["width"]
            scale_y = dimensions["height"] / original_info["height"]
            scale = min(scale_x, scale_y)  # Maintain aspect ratio
            
            # Open and copy original image
            await self.mcp.call_tool("open_image", {"filepath": image_path})
            
            # Scale to fit
            await self.mcp.call_tool("transform_layer", {
                "operation": "scale",
                "parameters": {"scale_x": scale, "scale_y": scale}
            })
            
            # Center the image
            # (This would require more complex positioning logic)
            
            # Save variant
            output_path = f"{output_dir}/{format_name}.jpg"
            await self.mcp.call_tool("save_image", {"filepath": output_path})
            
            variants.append({
                "format": format_name,
                "dimensions": dimensions,
                "output": output_path
            })
        
        return variants
    
    async def batch_watermark_images(self, image_dir: str, watermark_path: str, output_dir: str) -> Dict[str, Any]:
        """Apply watermark to multiple images"""
        results = []
        
        # Get list of images
        image_files = list(Path(image_dir).glob("*.jpg")) + list(Path(image_dir).glob("*.png"))
        
        for image_file in image_files:
            # Open image
            await self.mcp.call_tool("open_image", {"filepath": str(image_file)})
            
            # Open watermark as new layer
            await self.mcp.call_tool("open_image", {"filepath": watermark_path})
            
            # Position watermark (bottom right)
            await self.mcp.call_tool("transform_layer", {
                "operation": "position",
                "parameters": {"x": "bottom-right", "margin": 20}
            })
            
            # Set watermark opacity
            await self.mcp.call_tool("adjust_layer_opacity", {"opacity": 70})
            
            # Flatten image
            await self.mcp.call_tool("flatten_image", {})
            
            # Save watermarked image
            output_path = f"{output_dir}/watermarked_{image_file.name}"
            await self.mcp.call_tool("save_image", {"filepath": output_path})
            
            results.append({
                "original": str(image_file),
                "watermarked": output_path
            })
        
        return {
            "workflow": "batch_watermark",
            "processed": len(results),
            "results": results
        }
    
    async def create_texture_pattern(self, width: int, height: int, pattern_type: str, output_path: str) -> Dict[str, Any]:
        """Generate procedural texture patterns"""
        
        # Create new image
        await self.mcp.call_tool("create_image", {
            "width": width,
            "height": height,
            "name": f"{pattern_type}_texture"
        })
        
        if pattern_type == "noise":
            # Generate noise texture
            await self.mcp.call_tool("apply_filter", {
                "filter_name": "noise-rgb",
                "parameters": {"amount": 0.8, "independent": True}
            })
            
            # Add blur for smoothing
            await self.mcp.call_tool("apply_filter", {
                "filter_name": "gaussian-blur",
                "parameters": {"radius": 1.5}
            })
        
        elif pattern_type == "wood":
            # Create wood grain texture
            await self.mcp.call_tool("apply_filter", {
                "filter_name": "render-wood",
                "parameters": {"rings": 8, "turbulence": 0.1}
            })
            
        elif pattern_type == "marble":
            # Create marble texture
            await self.mcp.call_tool("apply_filter", {
                "filter_name": "render-marble",
                "parameters": {"size": 2.0, "turbulence": 1.0}
            })
        
        elif pattern_type == "fabric":
            # Create fabric texture
            await self.mcp.call_tool("apply_filter", {
                "filter_name": "render-fabric",
                "parameters": {"weave_type": "plain", "density": 50}
            })
        
        # Apply color adjustment for better appearance
        await self.mcp.call_tool("adjust_colors", {
            "adjustment": "brightness-contrast",
            "parameters": {"brightness": -10, "contrast": 20}
        })
        
        # Save texture
        await self.mcp.call_tool("save_image", {"filepath": output_path})
        
        return {
            "workflow": "texture_generation",
            "pattern_type": pattern_type,
            "dimensions": f"{width}x{height}",
            "output": output_path
        }
    
    async def create_logo_mockup(self, logo_path: str, mockup_template: str, output_path: str) -> Dict[str, Any]:
        """Create logo mockup on various surfaces"""
        
        # Open mockup template
        await self.mcp.call_tool("open_image", {"filepath": mockup_template})
        
        # Create new layer for logo
        await self.mcp.call_tool("create_layer", {"name": "Logo"})
        
        # Open logo image
        await self.mcp.call_tool("open_image", {"filepath": logo_path})
        
        # Scale logo to appropriate size
        await self.mcp.call_tool("transform_layer", {
            "operation": "scale",
            "parameters": {"scale_x": 0.3, "scale_y": 0.3}
        })
        
        # Position logo
        await self.mcp.call_tool("transform_layer", {
            "operation": "position",
            "parameters": {"x": "center", "y": "center"}
        })
        
        # Apply perspective transformation for realism
        await self.mcp.call_tool("transform_layer", {
            "operation": "perspective",
            "parameters": {
                "corners": [
                    {"x": 0.1, "y": 0.1},
                    {"x": 0.9, "y": 0.15},
                    {"x": 0.85, "y": 0.9},
                    {"x": 0.15, "y": 0.85}
                ]
            }
        })
        
        # Apply blend mode for integration
        await self.mcp.call_tool("set_layer_blend_mode", {"mode": "multiply"})
        
        # Add subtle shadow
        await self.mcp.call_tool("apply_filter", {
            "filter_name": "drop-shadow",
            "parameters": {"offset_x": 2, "offset_y": 2, "blur": 3, "opacity": 0.3}
        })
        
        # Save mockup
        await self.mcp.call_tool("save_image", {"filepath": output_path})
        
        return {
            "workflow": "logo_mockup",
            "logo": logo_path,
            "template": mockup_template,
            "output": output_path
        }

# Claude Code Integration Examples
class ClaudeCodeGimpCommands:
    """Example commands for Claude Code integration"""
    
    @staticmethod
    def get_example_commands():
        return {
            "basic_operations": [
                "Create a new 1920x1080 image with white background",
                "Open the file ~/Desktop/photo.jpg",
                "Apply gaussian blur with radius 2.5 to current layer",
                "Adjust brightness by +10 and contrast by +15",
                "Create a new layer called 'Overlay'",
                "Save the current image as ~/Desktop/edited.png"
            ],
            
            "advanced_workflows": [
                "Enhance the photo at ~/photos/portrait.jpg and save as ~/photos/enhanced_portrait.jpg",
                "Create Instagram and Twitter variants of ~/logos/brand.png",
                "Batch watermark all images in ~/products/ with ~/assets/watermark.png",
                "Generate a wood texture pattern 512x512 pixels",
                "Create a logo mockup using ~/logos/logo.png on ~/templates/tshirt.jpg"
            ],
            
            "creative_tasks": [
                "Create a vintage photo effect with sepia tones and vignette",
                "Generate a seamless tile pattern for web backgrounds",
                "Create a double exposure effect combining two images",
                "Design a movie poster layout with text and effects",
                "Create an animated GIF from a series of images"
            ],
            
            "batch_operations": [
                "Resize all images in ~/photos/ to 800x600 maintaining aspect ratio",
                "Convert all PNG files in ~/graphics/ to JPEG format",
                "Apply the same filter preset to all images in a folder",
                "Create thumbnails for all images in ~/gallery/",
                "Batch rename and organize images by date taken"
            ]
        }

# Example Claude Code workflow scripts
example_workflows = {
    "photo_enhancement": """
# Photo Enhancement Workflow
1. Open image file
2. Duplicate layer for backup
3. Apply automatic levels adjustment
4. Enhance contrast and brightness
5. Boost color saturation
6. Apply noise reduction
7. Sharpen for output
8. Save enhanced image
""",
    
    "social_media_prep": """
# Social Media Preparation
1. Open source image
2. Create variants for different platforms:
   - Instagram Square (1080x1080)
   - Instagram Story (1080x1920)
   - Twitter Post (1200x675)
   - Facebook Cover (1200x630)
3. Apply platform-specific optimizations
4. Save all variants
""",
    
    "batch_processing": """
# Batch Image Processing
1. Scan directory for image files
2. For each image:
   - Open file
   - Apply preset adjustments
   - Resize if needed
   - Apply watermark
   - Save to output directory
3. Generate processing report
"""
}

def main():
    """Main function for testing"""
    print("GIMP MCP Workflow Manager")
    print("Example Claude Code commands:")
    
    commands = ClaudeCodeGimpCommands.get_example_commands()
    
    for category, command_list in commands.items():
        print(f"\n{category.upper()}:")
        for i, command in enumerate(command_list, 1):
            print(f"  {i}. {command}")

if __name__ == "__main__":
    main()
