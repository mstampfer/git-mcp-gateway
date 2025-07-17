#!/usr/bin/env python3
"""
GIMP 3.0 Color Handling Guide
Comprehensive guide for working with colors in GIMP 3.0 using Gegl.Color
"""

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, Gegl

class GIMP3ColorHandler:
    """Handles color operations in GIMP 3.0 using Gegl.Color"""
    
    def __init__(self):
        pass
    
    def create_color_from_name(self, color_name: str) -> Gegl.Color:
        """Create color from CSS color name or hex value"""
        # GIMP 3.0 uses Gegl.Color instead of Gimp.RGB
        return Gegl.Color.new(color_name)
    
    def create_color_from_rgb(self, r: float, g: float, b: float, a: float = 1.0) -> Gegl.Color:
        """Create color from RGB(A) values (0.0-1.0 range)"""
        color = Gegl.Color()
        color.set_rgba(r, g, b, a)
        return color
    
    def create_color_from_hex(self, hex_color: str) -> Gegl.Color:
        """Create color from hex string (#RRGGBB or #RRGGBBAA)"""
        return Gegl.Color.new(hex_color)
    
    def create_color_from_hsv(self, h: float, s: float, v: float, a: float = 1.0) -> Gegl.Color:
        """Create color from HSV values"""
        color = Gegl.Color()
        color.set_hsva(h, s, v, a)
        return color
    
    def set_foreground_color(self, color: Gegl.Color):
        """Set GIMP foreground color"""
        Gimp.Context.set_foreground(color)
    
    def set_background_color(self, color: Gegl.Color):
        """Set GIMP background color"""
        Gimp.Context.set_background(color)
    
    def get_foreground_color(self) -> Gegl.Color:
        """Get current foreground color"""
        return Gimp.Context.get_foreground()
    
    def get_background_color(self) -> Gegl.Color:
        """Get current background color"""
        return Gimp.Context.get_background()
    
    def color_to_rgb_tuple(self, color: Gegl.Color) -> tuple:
        """Convert Gegl.Color to (r, g, b, a) tuple"""
        rgba = color.get_rgba()
        return (rgba[0], rgba[1], rgba[2], rgba[3])
    
    def color_to_hex(self, color: Gegl.Color) -> str:
        """Convert Gegl.Color to hex string"""
        r, g, b, a = self.color_to_rgb_tuple(color)
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        if a < 1.0:
            a_int = int(a * 255)
            return f"#{r_int:02x}{g_int:02x}{b_int:02x}{a_int:02x}"
        else:
            return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

# Common color constants for GIMP 3.0
class GIMP3Colors:
    """Common color constants using Gegl.Color"""
    
    @staticmethod
    def white() -> Gegl.Color:
        return Gegl.Color.new("white")
    
    @staticmethod
    def black() -> Gegl.Color:
        return Gegl.Color.new("black")
    
    @staticmethod
    def red() -> Gegl.Color:
        return Gegl.Color.new("red")
    
    @staticmethod
    def green() -> Gegl.Color:
        return Gegl.Color.new("green")
    
    @staticmethod
    def blue() -> Gegl.Color:
        return Gegl.Color.new("blue")
    
    @staticmethod
    def yellow() -> Gegl.Color:
        return Gegl.Color.new("yellow")
    
    @staticmethod
    def cyan() -> Gegl.Color:
        return Gegl.Color.new("cyan")
    
    @staticmethod
    def magenta() -> Gegl.Color:
        return Gegl.Color.new("magenta")
    
    @staticmethod
    def transparent() -> Gegl.Color:
        return Gegl.Color.new("transparent")
    
    @staticmethod
    def gray(lightness: float = 0.5) -> Gegl.Color:
        """Create gray color with specified lightness (0.0-1.0)"""
        color = Gegl.Color()
        color.set_rgba(lightness, lightness, lightness, 1.0)
        return color

# Updated MCP server methods with correct color handling
class GimpMCPServerColorFixed:
    """Updated MCP server methods with GIMP 3.0 color handling"""
    
    def __init__(self):
        self.color_handler = GIMP3ColorHandler()
    
    async def create_image_with_color(self, width: int, height: int, 
                                    background_color: str = "white") -> Gimp.Image:
        """Create image with specified background color"""
        # Create image
        image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)
        
        # Create background layer
        layer = Gimp.Layer.new(image, "Background", width, height,
                              Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
        image.insert_layer(layer, None, 0)
        
        # Set background color and fill
        if background_color == "transparent":
            # For transparent background, use RGBA layer type
            layer = Gimp.Layer.new(image, "Background", width, height,
                                  Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
            image.insert_layer(layer, None, 0)
            Gimp.drawable_edit_clear(layer)
        else:
            color = self.color_handler.create_color_from_name(background_color)
            self.color_handler.set_foreground_color(color)
            Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
        
        return image
    
    async def fill_layer_with_color(self, layer: Gimp.Layer, color: str):
        """Fill layer with specified color"""
        if color == "transparent":
            Gimp.drawable_edit_clear(layer)
        else:
            color_obj = self.color_handler.create_color_from_name(color)
            self.color_handler.set_foreground_color(color_obj)
            Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
    
    async def create_gradient_fill(self, layer: Gimp.Layer, 
                                 start_color: str, end_color: str,
                                 gradient_type: str = "linear"):
        """Fill layer with gradient using GIMP 3.0 colors"""
        start_color_obj = self.color_handler.create_color_from_name(start_color)
        end_color_obj = self.color_handler.create_color_from_name(end_color)
        
        # Set gradient colors
        self.color_handler.set_foreground_color(start_color_obj)
        self.color_handler.set_background_color(end_color_obj)
        
        # Apply gradient
        width = layer.get_width()
        height = layer.get_height()
        
        if gradient_type == "linear":
            gradient_type_enum = Gimp.GradientType.LINEAR
            start_x, start_y = 0, 0
            end_x, end_y = width, height
        elif gradient_type == "radial":
            gradient_type_enum = Gimp.GradientType.RADIAL
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2
            start_x, start_y = center_x, center_y
            end_x, end_y = center_x + radius, center_y
        
        # Get PDB and run gradient procedure
        pdb = Gimp.get_pdb()
        result = pdb.run_procedure("gimp-drawable-edit-gradient-fill",
                                 [layer,
                                  gradient_type_enum,
                                  0.0,     # offset
                                  False,   # supersample
                                  0,       # supersample depth
                                  0.0,     # supersample threshold
                                  True,    # dither
                                  start_x, start_y,
                                  end_x, end_y])

# Example usage functions
def example_color_operations():
    """Examples of color operations in GIMP 3.0"""
    color_handler = GIMP3ColorHandler()
    
    # Create colors different ways
    red_by_name = color_handler.create_color_from_name("red")
    blue_by_hex = color_handler.create_color_from_hex("#0000FF")
    green_by_rgb = color_handler.create_color_from_rgb(0.0, 1.0, 0.0, 1.0)
    
    # Set context colors
    color_handler.set_foreground_color(red_by_name)
    color_handler.set_background_color(blue_by_hex)
    
    # Get current colors
    current_fg = color_handler.get_foreground_color()
    current_bg = color_handler.get_background_color()
    
    # Convert colors
    fg_hex = color_handler.color_to_hex(current_fg)
    bg_rgb = color_handler.color_to_rgb_tuple(current_bg)
    
    print(f"Foreground hex: {fg_hex}")
    print(f"Background RGB: {bg_rgb}")

def example_paint_operations():
    """Example painting operations with colors"""
    color_handler = GIMP3ColorHandler()
    
    # Create image
    image = Gimp.Image.new(800, 600, Gimp.ImageBaseType.RGB)
    layer = Gimp.Layer.new(image, "Paint Layer", 800, 600,
                          Gimp.ImageType.RGB_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
    image.insert_layer(layer, None, 0)
    
    # Set paint color
    paint_color = color_handler.create_color_from_hex("#FF6B35")  # Orange
    color_handler.set_foreground_color(paint_color)
    
    # Paint with brush (this would require actual brush stroke coordinates)
    # Gimp.drawable_edit_fill(layer, Gimp.FillType.FOREGROUND)
    
    # Create display
    display = Gimp.Display.new(image)

# Color palette for common operations
class CommonColorPalette:
    """Predefined color palette for common operations"""
    
    # Web safe colors
    WEB_COLORS = {
        "white": "#FFFFFF",
        "black": "#000000", 
        "red": "#FF0000",
        "green": "#008000",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        "silver": "#C0C0C0",
        "gray": "#808080",
        "maroon": "#800000",
        "olive": "#808000",
        "lime": "#00FF00",
        "aqua": "#00FFFF",
        "teal": "#008080",
        "navy": "#000080",
        "fuchsia": "#FF00FF",
        "purple": "#800080"
    }
    
    # Photography enhancement colors
    PHOTO_COLORS = {
        "warm_highlight": "#FFF8DC",
        "cool_shadow": "#4682B4",
        "skin_tone": "#FFDBAC",
        "sky_blue": "#87CEEB",
        "grass_green": "#9ACD32",
        "sunset_orange": "#FF7F50"
    }
    
    # Design colors
    DESIGN_COLORS = {
        "brand_primary": "#007ACC",
        "brand_secondary": "#FF6B35",
        "neutral_light": "#F5F5F5",
        "neutral_dark": "#2C3E50",
        "accent_bright": "#E74C3C",
        "accent_muted": "#95A5A6"
    }
    
    @classmethod
    def get_color(cls, color_name: str) -> Gegl.Color:
        """Get color by name from any palette"""
        all_colors = {**cls.WEB_COLORS, **cls.PHOTO_COLORS, **cls.DESIGN_COLORS}
        hex_value = all_colors.get(color_name)
        if hex_value:
            return Gegl.Color.new(hex_value)
        else:
            # Fallback to Gegl color name parsing
            return Gegl.Color.new(color_name)

def main():
    """Main function for testing color operations"""
    print("GIMP 3.0 Color Handling Examples")
    print("=================================")
    
    # Initialize GIMP (would need actual GIMP context)
    # Gimp.main([], main_gimp)
    
    # For now, just show the API
    print("Color creation methods:")
    print("- Gegl.Color.new('color_name')")
    print("- color.set_rgba(r, g, b, a)")
    print("- color.set_hsva(h, s, v, a)")
    print()
    print("Context methods:")
    print("- Gimp.Context.set_foreground(color)")
    print("- Gimp.Context.set_background(color)")
    print("- Gimp.Context.get_foreground()")
    print("- Gimp.Context.get_background()")

if __name__ == "__main__":
    main()
