from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

size = 256
image = Image.new("RGBA", (size, size), (15, 18, 32, 255))
draw = ImageDraw.Draw(image)

# Outer shield
points = [(128, 22), (210, 58), (192, 168), (128, 232), (64, 168), (46, 58)]
draw.polygon(points, fill=(111, 211, 180, 255), outline=(248, 243, 232, 255))

# Inner lock body
draw.rounded_rectangle((92, 102, 164, 180), radius=14, fill=(21, 26, 45, 255), outline=(248, 243, 232, 255), width=6)
# Lock shackle
draw.arc((92, 60, 164, 132), start=180, end=0, fill=(248, 243, 232, 255), width=10)

# Keyhole
draw.ellipse((120, 126, 136, 142), fill=(215, 222, 239, 255))
draw.rectangle((124, 136, 132, 160), fill=(215, 222, 239, 255))

# Accent line
draw.line((76, 204, 180, 204), fill=(216, 178, 110, 255), width=6)

ico_path = ASSETS / "securelab.ico"
image.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print(f"Created {ico_path}")
