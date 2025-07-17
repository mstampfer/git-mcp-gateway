# GIMP 2.x to 3.0 Migration Guide

## Overview

This guide helps developers migrate GIMP Python plugins and scripts from GIMP 2.x to GIMP 3.0. The major changes involve the new GObject Introspection API and color system.

## Major API Changes

### 1. Import System

**GIMP 2.x:**
```python
import gimp
import gimpfu
from gimpfu import *
```

**GIMP 3.0:**
```python
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, GimpUi, Gegl, Gio
```

### 2. Color System

**GIMP 2.x:**
```python
# Create color
color = gimpcolor.RGB(255, 0, 0)  # Red
# or
color = (255, 0, 0)

# Set colors
gimp.set_foreground(color)
gimp.set_background(color)
```

**GIMP 3.0:**
```python
# Create color
red_color = Gegl.Color.new("red")
# or
red_color = Gegl.Color()
red_color.set_rgba(1.0, 0.0, 0.0, 1.0)  # Note: 0.0-1.0 range

# Set colors
Gimp.Context.set_foreground(red_color)
Gimp.Context.set_background(red_color)

# Get colors
current_fg = Gimp.Context.get_foreground()
rgba = current_fg.get_rgba()  # Returns (r, g, b, a) tuple
```

### 3. Image and Layer Creation

**GIMP 2.x:**
```python
# Create image
image = gimp.Image(width, height, RGB)

# Create layer
layer = gimp.Layer(image, "Layer Name", width, height, RGBA_IMAGE, 100, NORMAL_MODE)

# Add layer to image
image.add_layer(layer, 0)
```

**GIMP 3.0:**
```python
# Create image
image = Gimp.Image.new(width, height, Gimp.ImageBaseType.RGB)

# Create layer
layer = Gimp.Layer.new(image, "Layer Name", width, height,
                      Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)

# Add layer to image
image.insert_layer(layer, None, 0)
```

### 4. File Operations

**GIMP 2.x:**
```python
# Load image
image = pdb.gimp_file_load(filename, filename)

# Save image
pdb.gimp_file_save(image, drawable, filename, filename)
```

**GIMP 3.0:**
```python
# Load image
file_obj = Gio.File.new_for_path(filename)
image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, file_obj)

# Export image
output_file = Gio.File.new_for_path(output_filename)
drawables = image.list_layers()  # or specific layers
Gimp.file_export(Gimp.RunMode.NONINTERACTIVE, image, drawables, output_file)
```

### 5. PDB (Procedure Database) Access

**GIMP 2.x:**
```python
# Direct PDB access
pdb.gimp_image_scale(image, new_width, new_height)
pdb.plug_in_gauss_rle(image, drawable, radius, 1, 1, 0)
```

**GIMP 3.0:**
```python
# Get PDB reference
pdb = Gimp.get_pdb()

# Call procedures with explicit argument arrays
result = pdb.run_procedure("gimp-image-scale", [image, new_width, new_height])
result = pdb.run_procedure("plug-in-gauss", 
                          [Gimp.RunMode.NONINTERACTIVE, image, 1, [drawable], 
                           radius, radius, 1])

# Check results
if result.index(0) == Gimp.PDBStatusType.SUCCESS:
    print("Success")
```

### 6. Layer Operations

**GIMP 2.x:**
```python
# Layer positioning
pdb.gimp_layer_set_offsets(layer, x, y)

# Layer scaling
pdb.gimp_layer_scale(layer, new_width, new_height, 0)

# Layer copy
new_layer = layer.copy()
image.add_layer(new_layer, 0)
```

**GIMP 3.0:**
```python
# Layer positioning
layer.set_offsets(x, y)

# Layer scaling
layer.scale(new_width, new_height, False)  # False = don't scale local origin

# Layer copy
new_layer = layer.copy()
image.insert_layer(new_layer, None, 0)
```

### 7. Fill Operations

**GIMP 2.x:**
```python
# Fill with foreground
pdb.gimp_edit_fill(drawable, FOREGROUND_FILL)

# Fill with color
gimp.set_foreground((255, 0, 0))
pdb.gimp_edit_fill(drawable, FOREGROUND_FILL)
```

**GIMP 3.0:**
```python
# Fill with foreground
Gimp.drawable_edit_fill(drawable, Gimp.FillType.FOREGROUND)

# Fill with specific color
red_color = Gegl.Color.new("red")
Gimp.Context.set_foreground(red_color)
Gimp.drawable_edit_fill(drawable, Gimp.FillType.FOREGROUND)

# Clear (transparent fill)
Gimp.drawable_edit_clear(drawable)
```

### 8. Selection Operations

**GIMP 2.x:**
```python
# Rectangle selection
pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, x, y, width, height)

# Selection by color
pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, drawable, color)
```

**GIMP 3.0:**
```python
# Rectangle selection
image.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, width, height)

# Selection by color
color_obj = Gegl.Color.new("blue")
pdb = Gimp.get_pdb()
result = pdb.run_procedure("gimp-image-select-color",
                          [image, Gimp.ChannelOps.REPLACE, drawable, color_obj])
```

## Common Migration Patterns

### Pattern 1: Color Constants

**GIMP 2.x:**
```python
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
```

**GIMP 3.0:**
```python
class Colors:
    WHITE = Gegl.Color.new("white")
    BLACK = Gegl.Color.new("black")
    RED = Gegl.Color.new("red")
    
    @staticmethod
    def rgb(r, g, b, a=1.0):
        color = Gegl.Color()
        color.set_rgba(r, g, b, a)
        return color
```

### Pattern 2: Error Handling

**GIMP 2.x:**
```python
try:
    pdb.some_procedure(args)
except RuntimeError as e:
    print("Error:", e)
```

**GIMP 3.0:**
```python
pdb = Gimp.get_pdb()
result = pdb.run_procedure("some-procedure", [args])
if result.index(0) != Gimp.PDBStatusType.SUCCESS:
    error = result.index(1)  # Get error details
    print("Error:", error.message if error else "Unknown error")
```

### Pattern 3: Plugin Registration

**GIMP 2.x:**
```python
def my_plugin_function(image, drawable):
    # Plugin code here
    pass

register(
    "python-fu-my-plugin",
    "My Plugin Description",
    "Longer description",
    "Author",
    "Copyright",
    "2023",
    "My Plugin",
    "RGB*, GRAY*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    my_plugin_function,
    menu="<Image>/Filters/Custom"
)

main()
```

**GIMP 3.0:**
```python
def run(procedure, run_mode, image, n_drawables, drawables, config, data):
    if procedure.get_name() == 'python-fu-my-plugin':
        # Plugin code here
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
    return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error())

class MyPlugin(Gimp.PlugIn):
    __gtype_name__ = 'MyPlugin'
    
    def do_query_procedures(self):
        return ['python-fu-my-plugin']
    
    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, run, None)
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_documentation("My Plugin", "Longer description", name)
        procedure.set_menu_label("My Plugin")
        procedure.add_menu_path("<Image>/Filters/Custom/")
        return procedure

Gimp.main(MyPlugin, sys.argv)
```

## Migration Checklist

- [ ] Update imports to use `gi.repository`
- [ ] Replace `gimp.RGB` with `Gegl.Color`
- [ ] Convert direct PDB calls to `pdb.run_procedure()`
- [ ] Update file operations to use `Gio.File`
- [ ] Replace `image.add_layer()` with `image.insert_layer()`
- [ ] Update layer operations to use object methods
- [ ] Convert fill operations to `Gimp.drawable_edit_fill()`
- [ ] Update plugin registration system
- [ ] Add proper error handling for PDB results
- [ ] Test with actual GIMP 3.0 installation

## Debugging Tips

1. **Enable Debug Output:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Check Available Procedures:**
```python
pdb = Gimp.get_pdb()
procedures = pdb.query("")
print(f"Available procedures: {len(procedures)}")
```

3. **Inspect Color Objects:**
```python
color = Gegl.Color.new("red")
rgba = color.get_rgba()
print(f"RGBA values: {rgba}")
```

4. **Test in GIMP Console:**
Open GIMP 3.0 → Filters → Python-Fu → Console to test code snippets.

## Common Errors and Solutions

### Error: `'gi.repository.Gimp' object has no attribute 'RGB'`
**Solution:** Use `Gegl.Color` instead:
```python
# Wrong
color = Gimp.RGB(1.0, 0.0, 0.0)

# Correct
color = Gegl.Color.new("red")
```

### Error: `Procedure not found`
**Solution:** Check procedure name and use `run_procedure()`:
```python
# Check if procedure exists
pdb = Gimp.get_pdb()
proc = pdb.lookup_procedure("plug-in-gauss")
if proc:
    result = pdb.run_procedure("plug-in-gauss", [args])
```

### Error: `Wrong number of arguments`
**Solution:** PDB procedures in GIMP 3.0 require explicit argument arrays:
```python
# Include all required arguments
result = pdb.run_procedure("plug-in-gauss",
                          [Gimp.RunMode.NONINTERACTIVE,
                           image,
                           1,  # number of drawables
                           [drawable],  # drawable array
                           radius, radius, 1])
```

This migration guide covers the most common changes needed when moving from GIMP 2.x to 3.0. Always test thoroughly with the actual GIMP 3.0 environment.
