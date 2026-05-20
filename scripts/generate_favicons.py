#!/usr/bin/env python3
"""Generate portfolio favicon assets (MS initials, brand colors)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "public"
BG = (12, 12, 34)  # #0c0c22
VIOLET = (139, 92, 246)  # #8b5cf6
CYAN = (6, 214, 199)  # #06d6c7
BORDER = (139, 92, 246, 80)


def lerp(a, b, t):
    return int(a + (b - a) * t)


def gradient_color(t):
    return (lerp(VIOLET[0], CYAN[0], t), lerp(VIOLET[1], CYAN[1], t), lerp(VIOLET[2], CYAN[2], t))


def load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = max(1, size // 16)
    radius = max(2, size // 5)
    draw.rounded_rectangle(
        (margin, margin, size - margin - 1, size - margin - 1),
        radius=radius,
        fill=BG,
        outline=(VIOLET[0], VIOLET[1], VIOLET[2], 120),
        width=max(1, size // 32),
    )

    font_size = int(size * 0.42)
    font = load_font(font_size)
    text = "MS"

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1] - max(0, size // 40)

    text_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    gradient = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for px in range(size):
        color = gradient_color(px / max(size - 1, 1)) + (255,)
        grad_draw.line([(px, 0), (px, size)], fill=color)

    colored_text = Image.composite(gradient, Image.new("RGBA", (size, size), BG + (255,)), text_layer)
    mask = text_layer.split()[3]
    img.paste(colored_text, (0, 0), mask)
    return img


def main():
    ROOT.mkdir(parents=True, exist_ok=True)

    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "apple-touch-icon.png": 180,
        "android-chrome-192x192.png": 192,
        "android-chrome-512x512.png": 512,
    }

    icons = {name: render_icon(px) for name, px in sizes.items()}
    for name, icon in icons.items():
        icon.save(ROOT / name, format="PNG", optimize=True)

    ico_sizes = [16, 32, 48]
    ico_images = [render_icon(s) for s in ico_sizes]
    ico_images[0].save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(img.width, img.height) for img in ico_images],
        append_images=ico_images[1:],
    )

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="MS">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="100%" stop-color="#06d6c7"/>
    </linearGradient>
  </defs>
  <rect x="32" y="32" width="448" height="448" rx="96" fill="#0c0c22" stroke="#8b5cf6" stroke-opacity="0.45" stroke-width="8"/>
  <text x="256" y="318" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="220" font-weight="700" fill="url(#g)">MS</text>
</svg>
"""
    (ROOT / "favicon.svg").write_text(svg, encoding="utf-8")
    print("Generated favicons in", ROOT)


if __name__ == "__main__":
    main()
