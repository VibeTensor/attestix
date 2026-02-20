"""Generate Attestix (ATX) geometric logo - grid style, 11x11 grid.

Layout: 5x5 cells per letter in a 2-row arrangement with 1-cell divider.
A and T on top row, X centered on bottom row.

     0  1  2  3  4  5  6  7  8  9  10
 0   .  .  X  .  .  .  X  X  X  X  X     A . T
 1   .  X  .  X  .  .  .  .  X  .  .     A . T
 2   X  X  X  X  X  .  .  .  X  .  .     A . T
 3   X  .  .  .  X  .  .  .  X  .  .     A . T
 4   X  .  .  .  X  .  .  .  X  .  .     A . T
 5   .  .  .  .  .  .  .  .  .  .  .     (divider)
 6   .  .  .  X  .  .  .  X  .  .  .     . X .
 7   .  .  .  .  X  .  X  .  .  .  .     . X .
 8   .  .  .  .  .  X  .  .  .  .  .     . X .
 9   .  .  .  .  X  .  X  .  .  .  .     . X .
10   .  .  .  X  .  .  .  X  .  .  .     . X .
"""
import os
from PIL import Image, ImageDraw

U = 180 / 11  # Grid unit = 16.364
SIZE = 512
SCALE = SIZE / 180

# VibeTensor brand colors
BG = (35, 44, 48)       # #232c30 - dark background
GOLD = (225, 163, 44)   # #e1a32c - primary accent
WHITE = (255, 255, 255)
TEAL = (14, 165, 233)   # #0ea5e9 - sky-500
INDIGO = (79, 70, 229)  # #4f46e5 - indigo-600 (Attestix accent)

TEAL_HEX = '#0ea5e9'
INDIGO_HEX = '#4f46e5'
BG_HEX = '#232c30'
GOLD_HEX = '#e1a32c'


def r(val):
    return round(val, 3)


def s(val):
    return round(val * SCALE)


# ---- SVG Path Helpers ----

def svg_rect(col, row, w_u, h_u):
    x, y = r(col * U), r(row * U)
    w, h = r(w_u * U), r(h_u * U)
    return f"M{x} {y}h{w}v{h}h-{w}z"


def svg_filled(col, row):
    x, y, w = r(col * U), r(row * U), r(U)
    return f"M{x} {y}h{w}v{w}h-{w}z"


def svg_wrap(paths_str, fill="#fff", bg=None):
    bg_rect = f'<rect width="180" height="180" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 180 180">'
        f'{bg_rect}'
        f'<g fill="{fill}" fill-rule="evenodd" clip-path="url(#a)">'
        f'<path d="{paths_str}"/>'
        f'</g>'
        f'<defs><clipPath id="a"><path fill="#fff" d="M0 0h180v180H0z"/></clipPath></defs>'
        f'</svg>'
    )


# ---- PNG Drawing Helpers ----

def px_rect(draw, col, row, w_u, h_u, color):
    x1, y1 = s(col * U), s(row * U)
    x2, y2 = s((col + w_u) * U) - 1, s((row + h_u) * U) - 1
    draw.rectangle([x1, y1, x2, y2], fill=color)


def px_filled(draw, col, row, color):
    px_rect(draw, col, row, 1, 1, color)


def new_canvas():
    return Image.new('RGB', (SIZE, SIZE), BG)


# ================================================================
# ATX Logo - A(5x5) T(5x5) X(5x5) in 11x11 grid
# ================================================================
#
# A (5x5):       T (5x5):       X (5x5, centered):
# . . X . .      X X X X X      X . . . X
# . X . X .      . . X . .      . X . X .
# X X X X X      . . X . .      . . X . .
# X . . . X      . . X . .      . X . X .
# X . . . X      . . X . .      X . . . X


def atx_svg():
    return " ".join([
        # --- A (cols 0-4, rows 0-4) ---
        svg_filled(2, 0),           # peak
        svg_filled(1, 1),           # left upper arm
        svg_filled(3, 1),           # right upper arm
        svg_rect(0, 2, 5, 1),      # crossbar
        svg_rect(0, 3, 1, 2),      # left leg
        svg_rect(4, 3, 1, 2),      # right leg

        # --- T (cols 6-10, rows 0-4) ---
        svg_rect(6, 0, 5, 1),      # top bar
        svg_rect(8, 1, 1, 4),      # stem

        # --- X (cols 3-7, rows 6-10) ---
        svg_filled(3, 6),           # top-left
        svg_filled(7, 6),           # top-right
        svg_filled(4, 7),           # upper-inner-left
        svg_filled(6, 7),           # upper-inner-right
        svg_filled(5, 8),           # center
        svg_filled(4, 9),           # lower-inner-left
        svg_filled(6, 9),           # lower-inner-right
        svg_filled(3, 10),          # bottom-left
        svg_filled(7, 10),          # bottom-right
    ])


def atx_png(color=GOLD):
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    # A (cols 0-4, rows 0-4)
    px_filled(draw, 2, 0, color)        # peak
    px_filled(draw, 1, 1, color)        # left upper arm
    px_filled(draw, 3, 1, color)        # right upper arm
    px_rect(draw, 0, 2, 5, 1, color)   # crossbar
    px_rect(draw, 0, 3, 1, 2, color)   # left leg
    px_rect(draw, 4, 3, 1, 2, color)   # right leg

    # T (cols 6-10, rows 0-4)
    px_rect(draw, 6, 0, 5, 1, color)   # top bar
    px_rect(draw, 8, 1, 1, 4, color)   # stem

    # X (cols 3-7, rows 6-10)
    px_filled(draw, 3, 6, color)        # top-left
    px_filled(draw, 7, 6, color)        # top-right
    px_filled(draw, 4, 7, color)        # upper-inner-left
    px_filled(draw, 6, 7, color)        # upper-inner-right
    px_filled(draw, 5, 8, color)        # center
    px_filled(draw, 4, 9, color)        # lower-inner-left
    px_filled(draw, 6, 9, color)        # lower-inner-right
    px_filled(draw, 3, 10, color)       # bottom-left
    px_filled(draw, 7, 10, color)       # bottom-right

    return img


# ================================================================
# Shield + Checkmark Icon (verification/attestation symbol)
# ================================================================

def shield_svg():
    """Shield with checkmark - attestation verification symbol."""
    return " ".join([
        # Shield outline - top section (rows 0-5, cols 1-9)
        svg_rect(2, 0, 7, 1),      # top bar
        svg_rect(1, 1, 1, 5),      # left wall upper
        svg_rect(9, 1, 1, 5),      # right wall upper
        svg_rect(1, 0, 1, 1),      # top-left corner
        svg_rect(9, 0, 1, 1),      # top-right corner

        # Shield taper (rows 6-10)
        svg_rect(2, 6, 1, 1),      # left taper step 1
        svg_rect(8, 6, 1, 1),      # right taper step 1
        svg_rect(3, 7, 1, 1),      # left taper step 2
        svg_rect(7, 7, 1, 1),      # right taper step 2
        svg_rect(4, 8, 1, 1),      # left taper step 3
        svg_rect(6, 8, 1, 1),      # right taper step 3
        svg_filled(5, 9),           # bottom point

        # Checkmark inside shield (rows 2-6)
        svg_filled(7, 2),           # check top
        svg_filled(6, 3),           # check upper-mid
        svg_filled(5, 4),           # check mid
        svg_filled(4, 5),           # check lower
        svg_filled(3, 4),           # check short arm
    ])


def shield_png(color=GOLD):
    """Shield with checkmark as PNG."""
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    # Shield outline - top
    px_rect(draw, 2, 0, 7, 1, color)   # top bar
    px_rect(draw, 1, 1, 1, 5, color)   # left wall
    px_rect(draw, 9, 1, 1, 5, color)   # right wall
    px_filled(draw, 1, 0, color)        # top-left corner
    px_filled(draw, 9, 0, color)        # top-right corner

    # Shield taper
    px_filled(draw, 2, 6, color)
    px_filled(draw, 8, 6, color)
    px_filled(draw, 3, 7, color)
    px_filled(draw, 7, 7, color)
    px_filled(draw, 4, 8, color)
    px_filled(draw, 6, 8, color)
    px_filled(draw, 5, 9, color)

    # Checkmark
    px_filled(draw, 7, 2, color)
    px_filled(draw, 6, 3, color)
    px_filled(draw, 5, 4, color)
    px_filled(draw, 4, 5, color)
    px_filled(draw, 3, 4, color)

    return img


# ================================================================
# App Icon - rounded square with ATX lettermark
# ================================================================

def atx_icon_svg(bg_color=INDIGO_HEX, mark_color='#fff', icon_size=512, corner_r=80):
    """App icon: rounded-corner square with centered ATX lettermark."""
    pad = 30
    inner = icon_size - 2 * pad
    scale = inner / 180
    tx, ty = pad, pad

    paths = atx_svg()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {icon_size} {icon_size}">'
        f'<rect width="{icon_size}" height="{icon_size}" rx="{corner_r}" fill="{bg_color}"/>'
        f'<g transform="translate({tx},{ty}) scale({r(scale)})" fill="{mark_color}" fill-rule="evenodd">'
        f'<path d="{paths}"/>'
        f'</g>'
        f'</svg>'
    )


def atx_favicon_svg(bg_color=INDIGO_HEX, mark_color='#fff'):
    """Favicon (32x32 viewBox) with rounded corners."""
    scale = 22 / 180
    tx, ty = 5, 5
    paths = atx_svg()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        f'<rect width="32" height="32" rx="6" fill="{bg_color}"/>'
        f'<g transform="translate({tx},{ty}) scale({r(scale)})" fill="{mark_color}" fill-rule="evenodd">'
        f'<path d="{paths}"/>'
        f'</g>'
        f'</svg>'
    )


def shield_icon_svg(bg_color=INDIGO_HEX, mark_color='#fff', icon_size=512, corner_r=80):
    """App icon: rounded-corner square with centered shield checkmark."""
    pad = 40
    inner = icon_size - 2 * pad
    scale = inner / 180
    tx, ty = pad, pad

    paths = shield_svg()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {icon_size} {icon_size}">'
        f'<rect width="{icon_size}" height="{icon_size}" rx="{corner_r}" fill="{bg_color}"/>'
        f'<g transform="translate({tx},{ty}) scale({r(scale)})" fill="{mark_color}" fill-rule="evenodd">'
        f'<path d="{paths}"/>'
        f'</g>'
        f'</svg>'
    )


def atx_icon_png(bg_color=INDIGO, mark_color=WHITE):
    """ATX lettermark app icon as PNG with rounded corners."""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cr = 80
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=cr, fill=bg_color)

    pad = 30
    inner_scale = (SIZE - 2 * pad) / 180

    def si(val):
        return round(val * inner_scale) + pad

    def icon_rect(col, row, w_u, h_u, color):
        x1, y1 = si(col * U), si(row * U)
        x2, y2 = si((col + w_u) * U) - 1, si((row + h_u) * U) - 1
        draw.rectangle([x1, y1, x2, y2], fill=color)

    def icon_filled(col, row, color):
        icon_rect(col, row, 1, 1, color)

    c = mark_color

    # A
    icon_filled(2, 0, c)
    icon_filled(1, 1, c)
    icon_filled(3, 1, c)
    icon_rect(0, 2, 5, 1, c)
    icon_rect(0, 3, 1, 2, c)
    icon_rect(4, 3, 1, 2, c)

    # T
    icon_rect(6, 0, 5, 1, c)
    icon_rect(8, 1, 1, 4, c)

    # X
    icon_filled(3, 6, c)
    icon_filled(7, 6, c)
    icon_filled(4, 7, c)
    icon_filled(6, 7, c)
    icon_filled(5, 8, c)
    icon_filled(4, 9, c)
    icon_filled(6, 9, c)
    icon_filled(3, 10, c)
    icon_filled(7, 10, c)

    return img


# ================================================================
# Generate outputs
# ================================================================
if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'assets')
    os.makedirs(out_dir, exist_ok=True)

    paths_atx = atx_svg()
    paths_shield = shield_svg()

    # --- ATX Lettermark SVGs ---
    for variant, fill, bg in [
        ('dark', '#fff', None),
        ('light', BG_HEX, None),
        ('gold', GOLD_HEX, BG_HEX),
        ('indigo', INDIGO_HEX, BG_HEX),
    ]:
        svg = svg_wrap(paths_atx, fill=fill, bg=bg)
        fpath = os.path.join(out_dir, f'atx_{variant}.svg')
        with open(fpath, 'w') as f:
            f.write(svg)
        print(f'SVG: atx_{variant}.svg')

    # --- Shield SVGs ---
    for variant, fill, bg in [
        ('dark', '#fff', None),
        ('gold', GOLD_HEX, BG_HEX),
    ]:
        svg = svg_wrap(paths_shield, fill=fill, bg=bg)
        fpath = os.path.join(out_dir, f'shield_{variant}.svg')
        with open(fpath, 'w') as f:
            f.write(svg)
        print(f'SVG: shield_{variant}.svg')

    # --- ATX Lettermark PNGs ---
    for variant, color in [('gold', GOLD), ('white', WHITE), ('indigo', INDIGO)]:
        img = atx_png(color)
        fpath = os.path.join(out_dir, f'atx_{variant}.png')
        img.save(fpath)
        print(f'PNG: atx_{variant}.png ({SIZE}x{SIZE})')

    # --- Shield PNGs ---
    for variant, color in [('gold', GOLD), ('white', WHITE)]:
        img = shield_png(color)
        fpath = os.path.join(out_dir, f'shield_{variant}.png')
        img.save(fpath)
        print(f'PNG: shield_{variant}.png ({SIZE}x{SIZE})')

    # --- App Icon SVGs ---
    icon_svg = atx_icon_svg()
    fpath = os.path.join(out_dir, 'atx_icon.svg')
    with open(fpath, 'w') as f:
        f.write(icon_svg)
    print('SVG: atx_icon.svg (app icon)')

    shield_icon = shield_icon_svg()
    fpath = os.path.join(out_dir, 'shield_icon.svg')
    with open(fpath, 'w') as f:
        f.write(shield_icon)
    print('SVG: shield_icon.svg (shield app icon)')

    # --- Favicon SVG ---
    fav_svg = atx_favicon_svg()
    fpath = os.path.join(out_dir, 'favicon.svg')
    with open(fpath, 'w') as f:
        f.write(fav_svg)
    print('SVG: favicon.svg (32x32)')

    # --- App Icon PNG ---
    icon_img = atx_icon_png()
    fpath = os.path.join(out_dir, 'atx_icon.png')
    icon_img.save(fpath)
    print(f'PNG: atx_icon.png ({SIZE}x{SIZE})')

    print(f'\nDone! Files saved to {out_dir}')
