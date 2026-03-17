#!/usr/bin/env python3
"""Generate OmniDigest app icons."""

import os
from PIL import Image, ImageDraw, ImageFont

# Project root
ROOT = "/home/frank/Documents/code/newssync/frontend/public"

def create_icon(size, filename):
    """Create a simple icon with gradient background and 'O' letter."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background gradient colors (blue to teal)
    bg_color = (59, 130, 246)  # Blue-500

    # Draw rounded rectangle background
    radius = size // 4
    draw.rounded_rectangle(
        [(0, 0), (size-1, size-1)],
        radius=radius,
        fill=bg_color
    )

    # Draw a stylized "O" representing aggregation
    # Outer circle
    center = size // 2
    outer_r = size // 3
    inner_r = size // 5

    # Draw outer ring
    draw.ellipse(
        [(center - outer_r, center - outer_r),
         (center + outer_r, center + outer_r)],
        outline='white',
        width=max(1, size // 16)
    )

    # Draw inner dot (representing aggregated content)
    inner_dot_r = size // 8
    draw.ellipse(
        [(center - inner_dot_r, center - inner_dot_r),
         (center + inner_dot_r, center + inner_dot_r)],
        fill='white'
    )

    # Add sync/aggregation arcs around the outer ring
    arc_width = max(2, size // 20)
    # Top arc
    draw.arc(
        [(center - outer_r - 2, center - outer_r - 2),
         (center + outer_r + 2, center + outer_r + 2)],
        start=200,
        end=340,
        fill='white',
        width=arc_width
    )
    # Bottom arc
    draw.arc(
        [(center - outer_r - 2, center - outer_r - 2),
         (center + outer_r + 2, center + outer_r + 2)],
        start=20,
        end=160,
        fill='white',
        width=arc_width
    )

    img.save(os.path.join(ROOT, filename))
    print(f"Created {filename}")

def create_svg():
    """Create SVG version of the icon."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="100%" style="stop-color:#06b6d4"/>
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="8" fill="url(#grad)"/>
  <circle cx="16" cy="16" r="9" fill="none" stroke="white" stroke-width="2"/>
  <circle cx="16" cy="16" r="3" fill="white"/>
  <path d="M 16 4 A 12 12 0 0 1 26 13" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M 16 28 A 12 12 0 0 1 6 19" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''
    with open(os.path.join(ROOT, 'favicon.svg'), 'w') as f:
        f.write(svg)
    print("Created favicon.svg")

def main():
    os.makedirs(ROOT, exist_ok=True)

    # Create various icon sizes
    create_icon(16, 'favicon-16x16.png')
    create_icon(32, 'favicon-32x32.png')
    create_icon(180, 'apple-touch-icon.png')
    create_icon(192, 'android-chrome-192x192.png')
    create_icon(512, 'android-chrome-512x512.png')

    # Create SVG
    create_svg()

    # Create ICO file (multiple sizes in one)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []

    for ico_size in ico_sizes:
        img = Image.new('RGBA', ico_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        size = ico_size[0]
        bg_color = (59, 130, 246)

        # Scale radius proportionally
        radius = size // 4
        draw.rounded_rectangle(
            [(0, 0), (size-1, size-1)],
            radius=radius,
            fill=bg_color
        )

        center = size // 2
        outer_r = size // 3
        inner_r = size // 5

        # Outer ring
        draw.ellipse(
            [(center - outer_r, center - outer_r),
             (center + outer_r, center + outer_r)],
            outline='white',
            width=max(1, size // 16)
        )

        # Inner dot
        inner_dot_r = size // 8
        draw.ellipse(
            [(center - inner_dot_r, center - inner_dot_r),
             (center + inner_dot_r, center + inner_dot_r)],
            fill='white'
        )

        # Sync arcs
        arc_width = max(2, size // 20)
        draw.arc(
            [(center - outer_r - 2, center - outer_r - 2),
             (center + outer_r + 2, center + outer_r + 2)],
            start=200,
            end=340,
            fill='white',
            width=arc_width
        )
        draw.arc(
            [(center - outer_r - 2, center - outer_r - 2),
             (center + outer_r + 2, center + outer_r + 2)],
            start=20,
            end=160,
            fill='white',
            width=arc_width
        )

        ico_images.append(img)

    # Save as ICO
    ico_images[0].save(
        os.path.join(ROOT, 'favicon.ico'),
        format='ICO',
        sizes=[(s, s) for s in [16, 32, 48, 64, 128, 256]],
        append_images=ico_images[1:]
    )
    print("Created favicon.ico")

    print("\nAll icons created successfully!")

if __name__ == '__main__':
    main()
