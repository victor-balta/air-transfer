import os
from PIL import Image, ImageDraw, ImageOps

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

def create_symbol(size, color, padding=0):
    """Creates a transparent image with the transfer symbol."""
    # Canvas
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Coordinates
    center = size // 2
    w = size - (padding * 2)
    h = size - (padding * 2)
    left = padding
    top = padding
    
    # 1. The Arrow (pointing up)
    arrow_w = w * 0.4
    arrow_h = h * 0.5
    arrow_stem_w = arrow_w * 0.35
    
    # Arrow points
    # Tip
    tip = (center, top + h * 0.1)
    # Base corners of the triangle part
    tri_left = (center - arrow_w//2, top + h * 0.4)
    tri_right = (center + arrow_w//2, top + h * 0.4)
    
    # Draw arrow head
    draw.polygon([tip, tri_left, tri_right], fill=color)
    
    # Draw arrow stem
    stem_left = center - arrow_stem_w // 2
    stem_right = center + arrow_stem_w // 2
    stem_bottom = top + h * 0.7
    draw.rectangle([stem_left, top + h * 0.39, stem_right, stem_bottom], fill=color)

    # 2. The "Dish" / "Tray" / "Waves" (U-shape underneath)
    # A distinct arc or bracket shape indicating "transfer from/to"
    arc_rect = [left + w*0.15, top + h*0.35, left + w*0.85, top + h*0.85]
    start_angle = 0
    end_angle = 180
    
    # We draw a thick arc by drawing two chords? No, PIL arc is thin.
    # Let's draw a stroke.
    stroke_width = int(size * 0.08)
    
    # Draw the tray (U shape)
    # Left vertical
    draw.line([
        (left + w*0.2, top + h*0.6),
        (left + w*0.2, top + h*0.8)
    ], fill=color, width=stroke_width)
    
    # Right vertical
    draw.line([
        (left + w*0.8, top + h*0.6),
        (left + w*0.8, top + h*0.8)
    ], fill=color, width=stroke_width)
    
    # Bottom horizontal
    draw.line([
        (left + w*0.19, top + h*0.8),
        (left + w*0.81, top + h*0.8)
    ], fill=color, width=stroke_width)

    return img

def create_gradient_icon(size):
    """Creates the colorful app icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Gradient background (Blue #3b82f6 to Purple #8b5cf6)
    # Simple linear interpolation for gradient
    for y in range(size):
        r = int(59 + (139 - 59) * (y / size))
        g = int(130 + (92 - 130) * (y / size))
        b = int(246 + (246 - 246) * (y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b))
        
    # Create mask for rounded corners (iOS style squircle-ish)
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = size // 4.5
    mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=corner_radius, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    # Overlay white symbol
    symbol = create_symbol(int(size * 0.7), (255, 255, 255), padding=0)
    
    # Center the symbol
    offset = ((size - symbol.width) // 2, (size - symbol.height) // 2)
    output.paste(symbol, offset, symbol)
    
    return output

def create_menubar_icon():
    """Creates a monochrome template icon for macOS menu bar."""
    # MacOS menu bar icons are typically 22pt height (44px for retina)
    size = 44
    # Draw strictly black (0,0,0). MacOS uses alpha to determine shape.
    img = create_symbol(size, (0, 0, 0), padding=4)
    return img

def main():
    print("Generating icons...")
    
    # 1. Menu Bar Icon (Template)
    # Naming it 'Template' helps macOS identify it as a mask
    menubar = create_menubar_icon()
    menubar_path = os.path.join(STATIC_DIR, 'menubarTemplate.png')
    menubar.save(menubar_path)
    print(f"Created {menubar_path}")
    
    # 2. App Icons (Colorful)
    sizes = {
        'icon-192.png': 192,
        'icon-512.png': 512,
        'app_icon.png': 1024  # High res for build script
    }
    
    for filename, size in sizes.items():
        icon = create_gradient_icon(size)
        path = os.path.join(STATIC_DIR, filename)
        icon.save(path)
        print(f"Created {path}")

if __name__ == "__main__":
    main()

