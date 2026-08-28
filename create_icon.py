from PIL import Image
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

source = (
    BASE_DIR
    / "tracker"
    / "static"
    / "tracker"
    / "images"
    / "pool-logo.png"
)

output = BASE_DIR / "pool-logo.ico"


image = Image.open(source)

if image.mode != "RGBA":
    image = image.convert("RGBA")

image.save(
    output,
    format="ICO",
    sizes=[
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ],
)

print()
print("==========================================")
print(" ISC POOL TRACKER ICON CREATED")
print("==========================================")
print()
print(f"Source: {source}")
print(f"Icon:   {output}")
print()